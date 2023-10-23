"""
This code sample shows Prebuilt Receipt operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from promptflow.connections import CustomConnection
import os

"""
Remember to remove the key from your code when you're done, and never post it publicly. For production, use
secure methods to store and access your credentials. For more information, see 
https://docs.microsoft.com/en-us/azure/cognitive-services/cognitive-services-security?tabs=command-line%2Ccsharp#environment-variables-and-application-configuration
"""

def set_connection(connection: CustomConnection):
    reckey=""
    endpoint=""
    for key, value in dict(connection).items():
        if key == "endpoint":
            endpoint = value
        elif key == "key":
            reckey = value

    document_analysis_client = DocumentAnalysisClient(
            endpoint=endpoint, credential=AzureKeyCredential(reckey)
        )
    return document_analysis_client



def extract_recipt(filepath:str, connection: CustomConnection,pathtype):
        
    document_analysis_client=set_connection(connection=connection)

    if pathtype=="local":
        filename=""
        with open(filepath, "rb") as f:
            if filepath.find("/")!=-1:
                filename=f.name.split("/")[-1]
            elif filepath.find("\\")!=-1:
                filename=f.name.split("\\")[-1]
                
            print(filename)
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-receipt", document=f, locale="en-US"
            )
        receipts = poller.result()

    elif pathtype=="url":
    
        poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-receipt", document_url=filepath, locale="en-US"
        )
        receipts = poller.result()

    # print(receipts.content.find("TRANS ID",1,5))

    # dict={rec1:{items:[],price:"",trasdate:""},}
    docdict={}
    innerdict={}

    for idx, receipt in enumerate(receipts.documents):
        Documentlist=[]
        print("--------Recognizing receipt #{}--------".format(idx + 1))
        receipt_type = receipt.doc_type
        if receipt_type:
            print(
                "Receipt Type: {}".format(receipt_type)
            )
        merchant_name = receipt.fields.get("MerchantName")
        if merchant_name:
            print(
                "Merchant Name: {} has confidence: {}".format(
                    merchant_name.value, merchant_name.confidence
                )
            )
        transaction_date = receipt.fields.get("TransactionDate")
        if transaction_date:
            print(
                "Transaction Date: {} has confidence: {}".format(
                    transaction_date.value, transaction_date.confidence
                )
            )
        
        transaction_time = receipt.fields.get("TransactionTime")
        if transaction_time:
            print(
                "Transaction Time: {} has confidence: {}".format(
                    transaction_time.value, transaction_time.confidence
                )
            )
        innerdict["Transdate"]=str(transaction_date.value) + " " + str(transaction_time.value)

        if receipt.fields.get("Items"):
            print("Receipt items:")
            for idx, item in enumerate(receipt.fields.get("Items").value):
                tempdict={}
                print("...Item #{}".format(idx + 1))
                item_description = item.value.get("Description")
                if item_description:
                    print(
                        "......Item Description: {} has confidence: {}".format(
                            item_description.value, item_description.confidence
                        )
                    )
                item_quantity = item.value.get("Quantity")
                if item_quantity:
                    print(
                        "......Item Quantity: {} has confidence: {}".format(
                            item_quantity.value, item_quantity.confidence
                        )
                    )
                item_price = item.value.get("Price")
                if item_price:
                    print(
                        "......Individual Item Price: {} has confidence: {}".format(
                            item_price.value, item_price.confidence
                        )
                    )
                item_total_price = item.value.get("TotalPrice")
                if item_total_price:
                    print(
                        "......Total Item Price: {} has confidence: {}".format(
                            item_total_price.value, item_total_price.confidence
                        )
                    )
                # innerdict["Item"]=str(transaction_date.value) + " " + str(transaction_time.value)
                
                tempdict["item_id"]=idx + 1
                tempdict["item_desc"]=item_description.value
                tempdict["price"]=item_total_price.value
                
                Documentlist.append(tempdict)
        
        innerdict["Items"] = Documentlist
        innerdict["MerchantName"] = merchant_name.value

        subtotal = receipt.fields.get("Subtotal")
        if subtotal:
            print(
                "Subtotal: {} has confidence: {}".format(
                    subtotal.value, subtotal.confidence
                )
            )
        tax = receipt.fields.get("TotalTax")
        if tax:
            print("Tax: {} has confidence: {}".format(tax.value, tax.confidence))
        tip = receipt.fields.get("Tip")
        if tip:
            print("Tip: {} has confidence: {}".format(tip.value, tip.confidence))
        total = receipt.fields.get("Total")
    
        if total:
            print("Total: {} has confidence: {}".format(total.value, total.confidence))
        print("--------------------------------------")

        innerdict["TotalSpend"] = total.value
        
    docdict[filename]=innerdict
    print(docdict)

    return docdict


if __name__ == "__main__":
    pass