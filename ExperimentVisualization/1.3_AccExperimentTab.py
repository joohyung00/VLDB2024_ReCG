from __future__ import print_function

import matplotlib.pyplot as plt
from cycler import cycler
import csv

import sys

import json
import argparse

import statistics 
# import negative_sample
sys.path.insert(1, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import dataset_ids, num_to_name
sys.path.insert(2, "/root/jsdReCG/ExperimentVisualization")
from aggregateExpResults import *


line_separator = """ % --------------------------------------------------------------------------------------------------------- % \n"""

algorithms = ["ReCG", "jxplain", "kreduce"]

train_percents = ["1", "10", "50", "90"]

def main():
    for dataset_id in dataset_ids:
        parse_dataset(dataset_id)



def parse_dataset(dataset_id):
    
    def printSwing(dataset_id):
        if dataset_id in ["5"]: print("~~", end = "")
    
    # Get metadata
    dataset_name = num_to_name[dataset_id][0]
    print_name = num_to_name[dataset_id][1]

    # Get dataset
    recg_f1, _, recg_recall, _, recg_precision, _ = getAccForAlgPercDataset("ReCG", 10, dataset_name)
    jxplain_f1, _, jxplain_recall, _, jxplain_precision, _ = getAccForAlgPercDataset("jxplain", 10, dataset_name)
    kreduce_f1, _, kreduce_recall, _, kreduce_precision, _ = getAccForAlgPercDataset("kreduce", 10, dataset_name)
    
    # Process dataset to strings
    recg_f1 = '%.2f' % recg_f1
    recg_recall = '%.2f' % recg_recall
    recg_precision = '%.2f' % recg_precision
    if jxplain_f1 == -1: jxplain_f1 = None
    else: jxplain_f1 = '%.2f' % jxplain_f1
    if jxplain_recall == -1: jxplain_recall = None
    else: jxplain_recall = '%.2f' % jxplain_recall
    if jxplain_precision == -1: jxplain_precision = None
    else: jxplain_precision = '%.2f' % jxplain_precision
    kreduce_f1 = '%.2f' % kreduce_f1
    kreduce_recall = '%.2f' % kreduce_recall
    kreduce_precision = '%.2f' % kreduce_precision

    # Column 1
    if dataset_id in ["5"]: print("~", end = "")
    print("\\texttt{", end = "")
    print(print_name, end = "")
    print("}", end = "")
    if dataset_id in ["5"]: print("~", end = "")
    print(" & ", end = " ")
    
    # Column 2 - ReCG Recall
    printSwing(dataset_id)
    print(recg_recall, end = "")
    printSwing(dataset_id)
    print(" & ", end = " ")
    
    # Column 3 - ReCG Precision
    printSwing(dataset_id)
    print(recg_precision, end = "")
    printSwing(dataset_id)
    print(" & ", end = " ")
    
    # Column 4 - ReCG F1
    printSwing(dataset_id)
    print(recg_f1, end = "")
    printSwing(dataset_id)
    print(" & ", end = " ")
    
    # Jxplain - cases of failures
    if dataset_name in ["6_Wikidata", "31_RedDiscordBot", "44_Plagiarize"]:
        print(r"\multicolumn{3}{c?}{\texttt{Time Out}}", end = " ")
        print(" & ", end = " ")
    elif dataset_name in ["1_NewYorkTimes", "43_Ecosystem"]:
        print(r"\multicolumn{3}{c?}{\texttt{Runtime Error}}", end = " ")
        print(" & ", end = " ")
    else:
        # Column 5 - Jxplain Recall
        printSwing(dataset_id)
        print(jxplain_recall, end = "")
        printSwing(dataset_id)
        print(" & ", end = " ")
        
        # Column 6 - Jxplain Precision
        printSwing(dataset_id)
        print(jxplain_precision, end = "")
        printSwing(dataset_id)
        print(" & ", end = " ")
        
        # Column 7 - Jxplain F1
        printSwing(dataset_id)
        print(jxplain_f1, end = "")
        printSwing(dataset_id)
        print(" & ", end = " ")
        
    # Column 8 - KReduce Recall
    printSwing(dataset_id)
    print(kreduce_recall, end = "")
    printSwing(dataset_id)
    print(" & ", end = " ")
    
    # Column 9 - KReduce Precision
    printSwing(dataset_id)
    print(kreduce_precision, end = "")
    printSwing(dataset_id)
    print(" & ", end = " ")
    
    # Column 10 - KReduce F1
    printSwing(dataset_id)
    print(kreduce_f1, end = "")
    printSwing(dataset_id)
    print(r" \\ \hline", end = " ")
    print()



if __name__ == "__main__":
    main()