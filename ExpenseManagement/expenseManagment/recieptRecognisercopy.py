import os
import json
import pandas as pd

docdict={'Walmart_Receipt1.pdf': 
             {'Transdate': '2023-10-03 21:09:41', 
              'MerchantName': 'WALMART',
              'Items': [{'item_id':1, 'item_desc':'EQUATE LIDO', 'price':5.94}, 
                       {'item_id':2, 'item_desc':'EQUATE COLD', 'price':3.98}, 
                       {'item_id':3, 'item_desc':'EQ MUC C CHR', 'price':4.98}, 
                       {'item_id':4, 'item_desc':'VAPORUB', 'price':6.44}], 
             'TotalSpend': 22.89
                       }
                       }


def extract_reciept_tool(docdict) -> str:

    # call the entry function
    
    #process docdict to LLM input
    fattenlist=""
    for id, value in docdict.items():
        print("Processing File name" + id)
        merchantName=value['MerchantName']
        # print(merchantName)
        for id, value in value.items():
            if id=="Items":
                merchantName="{'MerchantName':'" + merchantName +"', "
                #print(fattenlist)
                for itemlist in value:
                    fattenlist=fattenlist+merchantName
                    fattenlist=fattenlist+ "'item_id':" + str(itemlist['item_id']) +", "
                    fattenlist=fattenlist+ "'item_desc':'"+ itemlist['item_desc']
                    fattenlist+="}\n"
                #print(fattenlist)
        #print(fattenlist)
    return fattenlist


def extract(reciept_input):
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
            print(outlst)
    totdf=pd.DataFrame(outlst,columns=["filename","Transdate","merchantName","item_id","item_desc","price","TotalSpend"])
    totdf.set_index('item_id',inplace=True)
    print(totdf)
    return totdf




if __name__ == "__main__":
    # print(extract_reciept_tool(docdict))

    modified_datetime = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    modified_datetime = "\"{}\"".format(modified_datetime)
    print(modified_datetime)

    totdf=extract(docdict)
    print(totdf)

    a=['1-H',2,3,4]

    print("list-"+str(a[0:1]))
    str="\"assistant\":{\"item_id\":1, \"category\":\"Pharmacy\"}\n{\"item_id\":2, \"category\":\"Pharmacy\"}\n{\"item_id\":3, \"category\":\"Pharmacy\"}\n{\"item_id\":4, \"category\":\"Pharmacy\"}"
    str2="{\"item_id\":1, \"category\":\"Pharmacy\"},{\"item_id\":2, \"category\":\"Pharmacy\"},{\"item_id\":3, \"category\":\"Pharmacy\"},{\"item_id\":4, \"category\":\"Pharmacy\"}"
   
    #str1="{"rec1":{\"item_id\":1, \"category\":\"Pharmacy\"},"rec2":{\"item_id\":2, \"category\":\"Pharmacy\"},"rec3":{\"item_id\":3,\"category\":\"Pharmacy\"},"rec4":{\"item_id\":4, \"category\":\"Pharmacy\"}}"
   
    outlst=[]
    for dicstr in list(str.split("\n")):
        
        item_id=json.loads(dicstr)["item_id"]
        category=json.loads(dicstr)["category"]

        outlst.append([item_id,category])
    print(outlst)

    outdf=pd.DataFrame(outlst,columns=["item_id","category"])
    
    outdf.set_index('item_id',inplace=True)
    print(outdf)

    findf=totdf.join(outdf,how='left')
    findf.reset_index(inplace=True)
    # print(findf['filename'])
    # findf["filename"].fillna(method="bfill",inplace=True)
    # findf["Transdate"].fillna(method="bfill",inplace=True)
    # findf["merchantName"].fillna(method="bfill",inplace=True)
    # findf["item_id"].fillna(method="bfill",inplace=True)
    # findf["item_desc"].fillna(method="bfill",inplace=True)
    # findf["price"].fillna(method="bfill",inplace=True)
    # findf["TotalSpend"].fillna(method="bfill",inplace=True)

    findf.columns=['item_id','unique_id','trans_datetime','merchant_name','item_desc','item_price','totalspend','expense_category']

    print(findf)

    # print(list(str.split("\n")))
    # for dicstr in list(str.split("\n")):
    #     #print(dicstr)
    #     #print(dicstr["item_id"])
    #     #print(dict(dicstr)["item_id"])
    #     print(json.loads(dicstr)["item_id"])
        #print(dict(dicstr)["item_id"])
    # print(json.loads(str2))
    #print(dict(str1))

            
 
