

import pandas as pd
import numpy as np
from colorama import Fore, Style

import sys
sys.path.insert(1, '/root/JsonExplorerSpark/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames, possible_algorithms_list
sys.path.insert(3, "/root/JsonExplorerSpark/ExperimentVisualization")
from aggregateExpResults import getAccForAlgPerc, getAcc2ForAlgPerc, getAccForAlgPercDataset, getAcc2ForAlgPercDataset, \
                                getAccForAlg, getAcc2ForAlg




F1 = "f1"
RECALL = "recall"
PRECISION = "precision"

RECG = "ReCG"

TRAIN_PERCS = [1, 10, 50, 90]




def main():

    # Check how much of rise in precision and F1 score we get when we use getAcc2ForAlg compared to getAccForAlg
    f1_1, recall_1, precision_1 = getAccForAlg(RECG)
    f1_2, recall_2, precision_2 = getAcc2ForAlg(RECG)
    
    print("Precision: " + "%.2f"%((precision_2 / precision_1 - 1) * 100) + "%")
    print("F1: " + "%.2f"%((f1_2 / f1_1 - 1) * 100) + "%")



    print("PERC")
    for perc in [1, 10, 50, 90]:
        print(perc)
        recg_f1,  recg_recall,  recg_precision  = getAccForAlgPerc("ReCG", perc)
        recg_f12, recg_recall2, recg_precision2 = getAcc2ForAlgPerc("ReCG", perc)
        print("[1] Recall: " + "%.2f"%(recg_recall * 100) + "%\tPrecision: " + "%.2f"%(recg_precision * 100) + "%\tF1: " + "%.2f"%(recg_f1 * 100) + "%")
        
        print("[2] Recall: ", end = "")
        if recg_recall2 < recg_recall:      print(Fore.RED +   "%.2f"%(recg_recall2 * 100) + "%", end = "")
        elif recg_recall2 == recg_recall:   print(             "%.2f"%(recg_recall2 * 100) + "%", end = "")
        else:                               print(Fore.GREEN + "%.2f"%(recg_recall2 * 100) + "%", end = "")
        print(Style.RESET_ALL, end = "")
        
        print("\tPrecision: ", end = "")
        if recg_precision2 < recg_precision:    print(Fore.RED +   "%.2f"%(recg_precision2 * 100) + "%", end = "")
        elif recg_precision2 == recg_precision: print(             "%.2f"%(recg_precision2 * 100) + "%", end = "")
        else:                                   print(Fore.GREEN + "%.2f"%(recg_precision2 * 100) + "%", end = "")
        print(Style.RESET_ALL, end = "")
        
        print("\tF1: ", end = "")
        if recg_f12 < recg_f1:    print(Fore.RED +   "%.2f"%(recg_f12 * 100) + "%", end = "")
        elif recg_f12 == recg_f1: print(             "%.2f"%(recg_f12 * 100) + "%", end = "")
        else:                     print(Fore.GREEN + "%.2f"%(recg_f12 * 100) + "%", end = "")
        print(Style.RESET_ALL)
        print()
        print()
        
        
    for dataset in dataset_fullnames:
        print(dataset)
        for perc in [1, 10, 50, 90]:
            recg_f1,  _, recg_recall,  _,  recg_precision, _  = getAccForAlgPercDataset("ReCG", perc, dataset)
            recg_f12, _, recg_recall2, _, recg_precision2, _  = getAcc2ForAlgPercDataset("ReCG", perc, dataset)
            
            print("\t[1, " + dataset[:4] + "] Recall: " + "%.2f"%(recg_recall  * 100) + "%\tPrecision: " + "%.2f"%(recg_precision  * 100) + "%\tF1: " + "%.2f"%(recg_f1  * 100) + "%")
            
            print("\t[2, " + dataset[:4] + "] Recall: ", end = "")
            if recg_recall2 < recg_recall:     print(Fore.RED   + "%.2f"%(recg_recall2  * 100) + "%", end = "")
            elif recg_recall2 == recg_recall:  print(             "%.2f"%(recg_recall2  * 100) + "%", end = "")
            else:                              print(Fore.GREEN + "%.2f"%(recg_recall2  * 100) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            
            print("\tPrecision: ", end = "")
            if recg_precision2 < recg_precision:    print(Fore.RED   + "%.2f"%(recg_precision2  * 100) + "%", end = "")
            elif recg_precision2 == recg_precision: print(             "%.2f"%(recg_precision2  * 100) + "%", end = "")
            else:                                   print(Fore.GREEN + "%.2f"%(recg_precision2  * 100) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            
            print("\tF1: ", end = "")
            if recg_f12 <  recg_f1:     print(Fore.RED   + "%.2f"%(recg_f12  * 100) + "%", end = "")
            elif recg_f12 == recg_f1:   print(             "%.2f"%(recg_f12  * 100) + "%", end = "")
            else:                       print(Fore.GREEN + "%.2f"%(recg_f12  * 100) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            print()
            print()
            # print("\t[1, " + dataset[:4] + "] Recall: " + "%.2f"%(recg_recall  * 100) + " \tPrecision: " + "%.2f"%(recg_precision  * 100) + "\tF1: " + "%.2f"%(recg_f1  * 100))
            # print("\t[2, " + dataset[:4] + "] Recall: " + "%.2f"%(recg_recall2 * 100) + " \tPrecision: " + "%.2f"%(recg_precision2 * 100) + "\tF1: " + "%.2f"%(recg_f12 * 100))
            # print()
            
            
if __name__ == "__main__":
    main()