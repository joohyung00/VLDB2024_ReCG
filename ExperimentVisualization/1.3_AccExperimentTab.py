#################################################################################
# Input1 : Mode (all, dataset)                                                  #
# Input2 : dataset number                                                       #
# Output: console output                                                        #
#################################################################################                     
# \multirow{4}{*}{NYT} & 1 $\%$    & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    
#                                  & ERROR         & ERROR         & ERROR 
#                                  & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    \\ \cline{2-11}
#                                  
#                      & 10$\%$    & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    
#                                  & ERROR         & ERROR         & ERROR 
#                                  & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    \\ \cline{2-11}
#                                
#                      & 50$\%$    & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    
#                                  & ERROR         & ERROR         & ERROR 
#                                  & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    \\ \cline{2-11}
#                     
#                      & 90$\%$    & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    
#                                  & ERROR         & ERROR         & ERROR 
#                                  & 1.00(0.00)    & 1.00(0.00)    & 1.00(0.00)    \\ \hline
#################################################################################


from __future__ import print_function

import matplotlib.pyplot as plt
from cycler import cycler
import csv

import sys

import json
import argparse

import statistics 
# import negative_sample
sys.path.insert(1, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_fullnames, dataset_ids, num_to_name
sys.path.insert(2, "/root/JsonExplorerSpark/ExperimentVisualization")
from aggregateExpResults import getAccForAlgPercDataset



F1 = "f1"
RECALL = "recall"
PRECISION = "precision"

RECG = "ReCG"
JXPLAIN = "jxplain"
KREDUCE = "kreduce"
LREDUCE = "lreduce"
KLETTKE = "klettke"
FROZZA = "frozza"

ALGORITHMS  = [RECG, JXPLAIN, KREDUCE, LREDUCE, KLETTKE, FROZZA]
TRAIN_PERCS = [1, 10, 50, 90]
TARGET_PERC = 10

LINE_SEP = """ % --------------------------------------------------------------------------------------------------------- % \n"""


accuracy_per_alg_perc_data = {}
for algorithm in ALGORITHMS:
    accuracy_per_alg_perc_data[algorithm] = {}
    for percent in TRAIN_PERCS:
        accuracy_per_alg_perc_data[algorithm][percent] = {}
        for dataset_name in dataset_fullnames:
            accuracy_per_alg_perc_data[algorithm][percent][dataset_name] = {
                F1: -1,
                RECALL: -1,
                PRECISION: -1
            }
for alg in ALGORITHMS:
    for perc in TRAIN_PERCS:
        for data in dataset_fullnames:
            accuracy_per_alg_perc_data[alg][perc][data][F1], _, accuracy_per_alg_perc_data[alg][perc][data][RECALL], _, accuracy_per_alg_perc_data[alg][perc][data][PRECISION], _ = getAccForAlgPercDataset(alg, perc, data)
APAPD = accuracy_per_alg_perc_data



def main():
    
    # Initiate results
    

    

    for dataset_id in dataset_ids:
        printSingleLine(dataset_id)
        
    return







def printSingleLine(dataset_id):
    
    # Get metadata
    d_name = num_to_name[dataset_id][0]
    print_name   = num_to_name[dataset_id][1]

    # Column 1
    # if dataset_id in ["5"]: print("~", end = "")
    print("\\texttt{", end = "")
    print(print_name, end = "")
    print("}", end = "")
    if len(print_name) < 7: print("\t\t", end = "")
    else:                   print("\t", end = "")
    # if dataset_id in ["5"]: print("~", end = "")
    print(" & ", end = " ")
    
    
    for algorithm in ALGORITHMS:
        if algorithm in [JXPLAIN]:
            if d_name in ["6_Wikidata", "31_RedDiscordBot", "44_Plagiarize"]:
                print(r"\multicolumn{3}{c?}{\texttt{Time Out}}", end = " ")
                print(" & ", end = " ")
                continue
            elif d_name in ["1_NewYorkTimes", "43_Ecosystem"]:
                print(r"\multicolumn{3}{c?}{\texttt{Runtime Error}}", end = " ")
                print(" & ", end = " ")
                continue
            
        # Column 2 - ReCG Recall
        printSwing(dataset_id)
        print("%.2f"%APAPD[algorithm][TARGET_PERC][d_name][RECALL], end = "")
        printSwing(dataset_id)
        print(" & ", end = " ")
        
        # Column 3 - ReCG Precision
        printSwing(dataset_id)
        print("%.2f"%APAPD[algorithm][TARGET_PERC][d_name][PRECISION], end = "")
        printSwing(dataset_id)
        print(" & ", end = " ")
        
        # Column 4 - ReCG F1
        printSwing(dataset_id)
        print("%.2f"%APAPD[algorithm][TARGET_PERC][d_name][F1], end = "")
        printSwing(dataset_id)
        
        if algorithm == ALGORITHMS[-1]:
            print(r" \\ \hline", end = " ")
            print()
        else:
            print(" & ", end = " ")
    
    # # Jxplain - cases of failures
    
    # else:
    #     # Column 5 - Jxplain Recall
    #     printSwing(dataset_id)
    #     print(jxplain_recall, end = "")
    #     printSwing(dataset_id)
    #     print(" & ", end = " ")
        
    #     # Column 6 - Jxplain Precision
    #     printSwing(dataset_id)
    #     print(jxplain_precision, end = "")
    #     printSwing(dataset_id)
    #     print(" & ", end = " ")
        
    #     # Column 7 - Jxplain F1
    #     printSwing(dataset_id)
    #     print(jxplain_f1, end = "")
    #     printSwing(dataset_id)
    #     print(" & ", end = " ")
        
    # # Column 8 - KReduce Recall
    # printSwing(dataset_id)
    # print(kreduce_recall, end = "")
    # printSwing(dataset_id)
    # print(" & ", end = " ")
    
    # # Column 9 - KReduce Precision
    # printSwing(dataset_id)
    # print(kreduce_precision, end = "")
    # printSwing(dataset_id)
    # print(" & ", end = " ")
    
    # # Column 10 - KReduce F1
    # printSwing(dataset_id)
    # print(kreduce_f1, end = "")
    # printSwing(dataset_id)
    


def printSwing(dataset_id):
    return
    if dataset_id in ["5"]: print("~~", end = "")


if __name__ == "__main__":
    main()