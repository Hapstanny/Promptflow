from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import os
import pandas as pd
import pyodbc,json
from promptflow.connections import CustomConnection
from promptflow import tool
import ast

filename=""

def setup(connection: CustomConnection):
    for key, value in dict(connection).items():
        os.environ[key] = value

    db_config = {
                    'drivername': 'mssql+pyodbc',
                    'username': os.environ["SQL_SERVER_USERNAME"] +'@'+ os.environ["SQL_SERVER_ENDPOINT"],
                    'password': os.environ["SQL_SERVER_PASSWORD"],
                    'host': os.environ["SQL_SERVER_ENDPOINT"],
                    'port': 1433,
                    'database': os.environ["SQL_SERVER_DATABASE"],
                    'query': {'driver': 'ODBC Driver 17 for SQL Server'}
                }

    # Create a URL object for connecting to the database
    db_url = URL.create(**db_config)

    # Print the resulting URL string
    # print(db_url)

    # Connect to the Azure SQL Database using the URL string
    engine = create_engine(db_url)

    # Test the connection
    try:
        conn = engine.connect()
        print("Connection successful!")
        result = conn.exec_driver_sql("SELECT @@VERSION;")
        for row in result:
            print(row)
        conn.close()
        return engine
        
    except Exception as e:
        print(e)
        print("Connection failed.")

def processInputReciept(reciept_input:dict):

    outlst=[]
    for id, value in reciept_input.items():
        filename=id
        merchantName=value['MerchantName']
        TotalSpend=value['TotalSpend']
        Transdate=value['Transdate']
        expensecategory=""

        for dicstr in value['Items']:
            item_id=dicstr['item_id']
            item_desc=dicstr['item_desc']
            price=dicstr['price']

            outlst.append([filename,Transdate,merchantName,item_id,item_desc,price,TotalSpend])
            #print(outlst)
    totdf=pd.DataFrame(outlst,columns=["filename","Transdate","merchantName","item_id","item_desc","price","TotalSpend"])
    #print(totdf)
    return totdf

def processInputCategory(category_input:str):

    outlst=[]
    print(category_input)

    for dicstr in list(category_input.split("\n")):
        
        dicstr=ast.literal_eval(dicstr)
        #print(dicstr)
        # dicstr = dicstr.replace("\'", "\"")
        # print(json.loads(json.dumps(dicstr)))
        # item_id=json.loads(dicstr)["item_id"]
        for key in dicstr.keys():
            #print(key)
            if key=="assistant":
                #print(dicstr[key]["item_id"])
                item_id=dicstr[key]["item_id"]
                category=dicstr[key]['category']
            else:
                item_id=dicstr['item_id']
                category=dicstr['category']
        # print(category)

        outlst.append([item_id,category])
        # print(outlst)
    outdf=pd.DataFrame(outlst,columns=["item_id","category"])
    print(outdf)
    return outdf

@tool
def loadExpenses(reciept_input:list,category_input:str,connection: CustomConnection):
    
    try:
        engine=setup(connection)
        conn = engine.connect()

        reciept_input=reciept_input[0]
        totdf=processInputReciept(reciept_input)
        outdf=processInputCategory(category_input)

        outdf.set_index('item_id',inplace=True)
        totdf.set_index('item_id',inplace=True)

        findf=totdf.join(outdf,how='left')
        findf.reset_index(inplace=True)
        findf.columns=['item_id','unique_id','trans_datetime','merchant_name','item_desc','item_price','totalspend','expense_category']

        table_name = 'expenses_temp'
        findf.to_sql(table_name, con=conn, if_exists='replace', index=False)
        print("Data has been loaded successfully to temp table.")

        modified_datetime = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        modified_datetime = "'{}'".format(modified_datetime)
        print(modified_datetime)

        conn = conn.execution_options(autocommit=True)
        result=conn.execute(f"MERGE INTO [dbo].[expenses] AS tgt USING [dbo].[expenses_temp] AS src ON tgt.unique_id=src.unique_id and tgt.item_id = src.item_id WHEN MATCHED THEN UPDATE SET tgt.expense_category = src.expense_category,tgt.modified_datetime={modified_datetime} WHEN NOT MATCHED BY TARGET THEN \
                             INSERT (unique_id, trans_datetime, merchant_name, item_id, item_desc, item_price, totalspend, expense_category,insert_datetime,modified_datetime) \
                             VALUES (src.unique_id, src.trans_datetime, src.merchant_name, src.item_id, src.item_desc, src.item_price, src.totalspend, src.expense_category,{modified_datetime},null);"
                             )
      
        print("Data has been Merged successfully from {} table with Merged:- {} Records".format(table_name,result.rowcount))
        conn.close()
        return "Expenses data has been loaded successfully in {} database".format(os.environ["SQL_SERVER_DATABASE"])
    
    except Exception as e:
        print(e) 


def updateExpenseCategory(category_input:str,connection: CustomConnection):

    conn=setup(connection)
    print(category_input)


    for dicstr in list(category_input.split("\n")):
        
        item_id=json.loads(dicstr)["item_id"]
        category=json.loads(dicstr)["category"]

        sql = "UPDATE dbo.Expenses SET expense_category = ? WHERE unique_id = ?, item_id = ?"
        values = (category,filename,item_id)
        conn.execute(sql,values)
    
    conn.close()


if __name__ == "__main__":
    pass