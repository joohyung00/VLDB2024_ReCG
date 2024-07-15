

import pandas as pd
import numpy as np
from colorama import Fore, Style

import sys
sys.path.insert(1, '/root/VLDB2024_ReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/VLDB2024_ReCG/Experiment/utils")
from dataset_metadata import dataset_fullnames

from aggregateExpResults import getAccForAlg, getAccForAlgPerc, getAccForAlgPercDataset 




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

MIN = "min"
MAX = "max"


def main():
    
    # 1. Aggregate data        

    accuracy_per_alg = {}
    for algorithm in ALGORITHMS:
        accuracy_per_alg[algorithm] = {
            F1: -1,
            RECALL: -1,
            PRECISION: -1
        }
    for alg in ALGORITHMS:
        accuracy_per_alg[alg][F1], accuracy_per_alg[alg][RECALL], accuracy_per_alg[alg][PRECISION] = getAccForAlg(alg)
    APA = accuracy_per_alg

    accuracy_per_alg_perc = {}
    for algorithm in ALGORITHMS:
        accuracy_per_alg_perc[algorithm] = {}
        for percent in TRAIN_PERCS:
            accuracy_per_alg_perc[algorithm][percent] = {
                    F1: -1,
                    RECALL: -1,
                    PRECISION: -1
                }
    for alg in ALGORITHMS:
        for perc in TRAIN_PERCS:
            accuracy_per_alg_perc[alg][perc][F1], accuracy_per_alg_perc[alg][perc][RECALL], accuracy_per_alg_perc[alg][perc][PRECISION] = getAccForAlgPerc(alg, perc)
    APAP = accuracy_per_alg_perc
    
   
    
    print()
    print("<< SUMMARY >>")
    print()
    
    print("ReCG's average F1 score is ", end = "")
    print(Fore.GREEN + "%.2f"%APA[RECG][F1], end = "")
    print(Style.RESET_ALL, end = "")
    print(".")
    print()

    for algorithm in ALGORITHMS:
        if algorithm == RECG: continue
        
        print("ReCG's F1 score is ", end = "")
        print(Fore.GREEN + "%.0f"%(100 * (APA[RECG][F1] / APA[algorithm][F1] - 1)) + "%", end = "")
        print(Style.RESET_ALL, end = "")
        print(" higher than that of " + algToPrintName(algorithm) + ".")

        print(algToPrintName(algorithm) + " receieved about ", end = "")
        print(Fore.RED + "%.1f"%(100 * (1 - APA[algorithm][F1] / APA[RECG][F1])) + "%", end = "")
        print(Style.RESET_ALL, end = "")
        print(" less F1 score than ReCG.")
        print()
    


    minmax_increase_per_algorithm = {}
    MIPA = minmax_increase_per_algorithm
    
    for algorithm in ALGORITHMS:
        if algorithm == RECG: continue
        
        print("[[ " + algToPrintName(algorithm) + " ]]")
        print()
        
        MIPA[algorithm] = {
            F1:         { MIN: 100, MAX: -100 },
            RECALL:     { MIN: 100, MAX: -100 },
            PRECISION:  { MIN: 100, MAX: -100 }
        }
        
        for perc in TRAIN_PERCS:
            
            # Fill in the minmax_increase_per_algorithm
            f1_increase         = "%.2f"%(100 * (APAP[RECG][perc][F1]         / APAP[algorithm][perc][F1] - 1))
            recall_increase     = "%.2f"%(100 * (APAP[RECG][perc][RECALL]     / APAP[algorithm][perc][RECALL] - 1))
            precision_increase  = "%.2f"%(100 * (APAP[RECG][perc][PRECISION]  / APAP[algorithm][perc][PRECISION] - 1))
            
            if float(f1_increase) <         MIPA[algorithm][F1][MIN]:           MIPA[algorithm][F1][MIN] =          float(f1_increase)
            if float(f1_increase) >         MIPA[algorithm][F1][MAX]:           MIPA[algorithm][F1][MAX] =          float(f1_increase)
            if float(recall_increase) <     MIPA[algorithm][RECALL][MIN]:       MIPA[algorithm][RECALL][MIN] =      float(recall_increase)
            if float(recall_increase) >     MIPA[algorithm][RECALL][MAX]:       MIPA[algorithm][RECALL][MAX] =      float(recall_increase)
            if float(precision_increase) <  MIPA[algorithm][PRECISION][MIN]:    MIPA[algorithm][PRECISION][MIN] =   float(precision_increase)
            if float(precision_increase) >  MIPA[algorithm][PRECISION][MAX]:    MIPA[algorithm][PRECISION][MAX] =   float(precision_increase)
            
            
            print("\t" + "ReCG's ", end = "")
            print(Fore.RED + "F1 score ", end = "")
            print(Style.RESET_ALL, end = "")
            print("is \t", end = "")
            print(Fore.GREEN + str(f1_increase) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            print(" higher than that of " + algToPrintName(algorithm) + " in the top ", end = "")
            print(Fore.GREEN + str(perc) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            print(" of the dataset.")
            
            print("\t" + "ReCG's ", end = "")
            print(Fore.RED + "Recall ", end = "")
            print(Style.RESET_ALL, end = "")
            print("is \t", end = "")
            print(Fore.GREEN + str(recall_increase) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            print(" higher than that of " + algToPrintName(algorithm) + " in the top ", end = "")
            print(Fore.GREEN + str(perc) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            print(" of the dataset.")
            
            print("\t" + "ReCG's ", end = "")
            print(Fore.RED + "Precision ", end = "")
            print(Style.RESET_ALL, end = "")
            print("is \t", end = "")
            print(Fore.GREEN + str(precision_increase) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            print(" higher than that of " + algToPrintName(algorithm) + " in the top ", end = "")
            print(Fore.GREEN + str(perc) + "%", end = "")
            print(Style.RESET_ALL, end = "")
            print(" of the dataset.")
            
            print()
            
        print("Increase range in F1 score: \t", end = "")
        print(Fore.GREEN + str(MIPA[algorithm][F1][MIN]) + " ~ "  + str(MIPA[algorithm][F1][MAX]) + "%", end = "")
        print(Style.RESET_ALL)
        print("Increase range in Recall: \t", end = "")
        print(Fore.GREEN + str(MIPA[algorithm][RECALL][MIN]) + " ~ "  + str(MIPA[algorithm][RECALL][MAX]) + "%", end = "")
        print(Style.RESET_ALL)
        print("Increase range in Precision: \t", end = "")
        print(Fore.GREEN + str(MIPA[algorithm][PRECISION][MIN]) + " ~ "  + str(MIPA[algorithm][PRECISION][MAX]) + "%", end = "")
        print(Style.RESET_ALL)
        print()
        print()

        
       
       
def algToPrintName(algorithm):
    if algorithm == RECG: return "ReCG"
    if algorithm == JXPLAIN: return "Jxplain"
    if algorithm == KREDUCE: return "KReduce"
    if algorithm == LREDUCE: return "LReduce"
    if algorithm == KLETTKE: return "Klettke"
    if algorithm == FROZZA: return "Frozza"
    return "Unknown Algorithm"
            
if __name__ == "__main__":
    main()