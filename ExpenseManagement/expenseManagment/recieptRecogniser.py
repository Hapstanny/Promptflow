import os

from promptflow import tool
from promptflow.connections import CustomConnection
from receiptread import extract_recipt


@tool
def extract_reciept_tool(filepath:str,connection: CustomConnection,pathtype) -> list:

    # call the entry function
    docdict=extract_recipt(filepath=filepath,connection=connection,pathtype=pathtype)

    #process docdict to LLM input
    fattenlist=""
    for id, value in docdict.items():
        print("Processing File name" + id)
        merchantName=value['MerchantName']
        value['MerchantName']
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

    outlst=[docdict,fattenlist]
    return outlst
