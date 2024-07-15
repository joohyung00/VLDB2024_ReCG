

import pandas as pd
import numpy as np
from colorama import Fore, Style

import sys
sys.path.insert(1, '/root/VLDB2024_ReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/VLDB2024_ReCG/Experiment/utils")
from dataset_metadata import dataset_fullnames

from aggregateExpResults import getAccForAlgPerc, getAccForAlgPercDataset, getAccForAlg





    # \hline
    # % ------------------------------------------------ %
    # Method                                          & Recall        & Precision     & F1 score       \\ \hline \hline
    # % ============================================================== % 
    # \texttt{ReCG} (KSE as cost model)               & -0.36         & -0.07         & -0.37          \\ \hline
    # \texttt{ReCG} (Top-down schema generation)      & -0.49         & -0.08         & -0.42          \\ \specialrule{1.0pt}{0.5pt}{0.5pt}
    # \texttt{ReCG}                                   & -0.81         & -0.37         & -0.75          \\ \hline
    #  % ============================================================== % 


F1 = "f1"
RECALL = "recall"
PRECISION = "precision"

RECG = "ReCG"
RECG_KSE = "ReCG(KSE)"
RECG_TOPDOWN = "ReCG(TopDown)"

ALGORITHMS  = [RECG_KSE, RECG_TOPDOWN, RECG]
TARGET_PERC = 10


def main():
    
    # 1. Aggregate data        

    accuracy_perc_alg = {}
    for algorithm in ALGORITHMS:
        accuracy_perc_alg[algorithm] = {
                F1: -1,
                RECALL: -1,
                PRECISION: -1
        }
    for alg in ALGORITHMS:
        accuracy_perc_alg[alg][F1], accuracy_perc_alg[alg][RECALL], accuracy_perc_alg[alg][PRECISION] = getAccForAlg(alg)
    APA = accuracy_perc_alg
    
    accuracy_per_alg_perc = {}
    for algorithm in ALGORITHMS:
        accuracy_per_alg_perc[algorithm] = {}
        for perc in [TARGET_PERC]:
            accuracy_per_alg_perc[algorithm][perc] = {
                F1: -1,
                RECALL: -1,
                PRECISION: -1
            }
    for alg in ALGORITHMS:
        accuracy_per_alg_perc[alg][perc][F1], accuracy_per_alg_perc[alg][perc][RECALL], accuracy_per_alg_perc[alg][perc][PRECISION] = getAccForAlgPerc(alg, TARGET_PERC)
    APAP = accuracy_per_alg_perc

    accurayc_per_alg_perc_dataset = {}
    for algorithm in ALGORITHMS:
        accurayc_per_alg_perc_dataset[algorithm] = {}
        for perc in [TARGET_PERC]:
            accurayc_per_alg_perc_dataset[algorithm][perc] = {}
            for dataset in dataset_fullnames:
                accurayc_per_alg_perc_dataset[algorithm][perc][dataset] = {
                    F1: -1,
                    RECALL: -1,
                    PRECISION: -1
                }
    for alg in ALGORITHMS:
        for dataset in dataset_fullnames:
            accurayc_per_alg_perc_dataset[alg][perc][dataset][F1], _, accurayc_per_alg_perc_dataset[alg][perc][dataset][RECALL], _, accurayc_per_alg_perc_dataset[alg][perc][dataset][PRECISION], _ = getAccForAlgPercDataset(alg, TARGET_PERC, dataset)
    APAPD = accurayc_per_alg_perc_dataset

    for algorithm in ALGORITHMS:

        print("    " + algToPrintName(algorithm) + " & ", end = "")
        print("%.2f"%APA[algorithm][RECALL] + "\t& ", end = "")
        print("%.2f"%APA[algorithm][PRECISION] + "\t& ", end = "")
        print("%.2f"%APA[algorithm][F1] + "\t\\\\", end = "")
        
        if algorithm == ALGORITHMS[-2]:
            print("\\specialrule{1.0pt}{0.5pt}{0.5pt}")
        else:
            print("\\hline")
    print()
            
    
    
    
    
    
    
    def checkSmallerThanReCG(target_algorithm):
        print(target_algorithm)
        for dataset in dataset_fullnames:
            if APAPD[target_algorithm][TARGET_PERC][dataset][F1] < APAPD[RECG][TARGET_PERC][dataset][F1]:
                print(Fore.RED + dataset + " & ", end = "")
        print(Fore.RESET)
        print()
                
    checkSmallerThanReCG(RECG_KSE)
    checkSmallerThanReCG(RECG_TOPDOWN)
            
    
        
        


        
       
       
def algToPrintName(algorithm):
    if algorithm == RECG:           return "\\texttt{ReCG}                                  "
    if algorithm == RECG_KSE:       return "\\texttt{ReCG} (KSE as cost model)              "
    if algorithm == RECG_TOPDOWN:   return "\\texttt{ReCG} (Top-down schema generation)     "
    return "Unknown Algorithm"
            
if __name__ == "__main__":
    main()