from promptflow import log_metric, tool
import numpy as np
from loadSqldb import processInputCategory

@tool
def evaluate(groundtruth:str,prediction:str,evaluation_required:bool) -> str:

    if evaluation_required:
        actual_df=processInputCategory(groundtruth)
        predicted_df=processInputCategory(prediction)
        accuracy_stat=accuracy(actual_df,predicted_df)
        print("Accuracy is " + str(accuracy_stat))
        log_metric("accuracy", accuracy_stat)
        return str(accuracy_stat)
    else:
        return "evaluation was not enabled for this run"

def accuracy(y_true, y_pred):
    y_true.set_index('item_id',inplace=True)
    y_true.sort_index(inplace=True,axis=0)
    y_pred.set_index('item_id',inplace=True)
    y_pred.sort_index(inplace=True,axis=0)
    # print(y_true)
    # print(y_pred)
    return np.mean(np.equal(y_true, y_pred))['category']