
import statistics

import numpy as np
import sys

from pltUtils import dataset_nums, dataset_to_name, dataset_to_print_name, target_percs
sys.path.insert(1, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_fullnames
from aggregateExpResults import getMemoryForAlgPerc, getMemoryForAlgPercDataset



RECG = "ReCG"
JXPLAIN = "jxplain"
KREDUCE = "kreduce"
LREDUCE = "lreduce"
KLETTKE = "klettke"
FROZZA = "frozza"

MAX = "max"

ALGORITHMS  = [RECG, JXPLAIN, KREDUCE, LREDUCE, KLETTKE, FROZZA]
TRAIN_PERCS = [10, 50, 100]

MEMORY_MEAN = "memory_mean"
MEMORY_STDEV = "memory_stdev"


def main():
    
    # 1. Aggregate data 
    result_per_alg_perc = {}
    for algorithm in ALGORITHMS:
        result_per_alg_perc[algorithm] = {}
        for percent in TRAIN_PERCS:
            result_per_alg_perc[algorithm][percent] = {
                MEMORY_MEAN: -1,
                MEMORY_STDEV: -1,
                MAX : -1
            }
    RPAP = result_per_alg_perc
    
    for alg in ALGORITHMS:
        for perc in TRAIN_PERCS:
            mean, stdev = getMemoryForAlgPerc(alg, perc)
            RPAP[alg][perc][MEMORY_MEAN] = mean / 1024
            RPAP[alg][perc][MEMORY_STDEV] = stdev / 1024
            
            
            for dataset in dataset_fullnames:
                mean = getMemoryForAlgPercDataset(alg, perc, dataset)
                RPAP[alg][perc][MAX] = max(RPAP[alg][perc][MAX], mean / 1024)
                
                if alg == KREDUCE:
                    print(dataset)
                    print("%.2f"%(mean / 1024))
            
    result_per_alg_perc_dataset = {}
    for algorithm in ALGORITHMS:
        result_per_alg_perc_dataset[algorithm] = {}
        for percent in TRAIN_PERCS:
            result_per_alg_perc_dataset[algorithm][percent] = {}
            for dataset in dataset_fullnames:
                result_per_alg_perc_dataset[algorithm][percent][dataset] = {
                    MEMORY_MEAN: -1
                }
    for alg in ALGORITHMS:
        for perc in TRAIN_PERCS:
            for dataset in dataset_fullnames:
                mean = getMemoryForAlgPercDataset(alg, perc, dataset)
                result_per_alg_perc_dataset[alg][perc][dataset][MEMORY_MEAN] = mean / 1024
    RPAPD = result_per_alg_perc_dataset
    


    # for target_perc in TRAIN_PERCS:
    #     print(str(target_perc) + "\\% & ", end = "")
        
    #     for alg in ALGORITHMS:
    #         print("%.2f"%RPAP[alg][target_perc][MEMORY_MEAN] + " MB & " + "%.2f"%RPAP[alg][target_perc][MEMORY_STDEV] + " & " + \
    #                 "%.2f"%(RPAP[alg][target_perc][MEMORY_MEAN] / RPAP[RECG][target_perc][MEMORY_MEAN]), end = "")
    #         if alg != ALGORITHMS[-1]:
    #             print(" & ", end = "")
    #         else:
    #             print(" \\\\ \hline")
                
    for target_perc in TRAIN_PERCS:
        print(str(target_perc) + "\\% & ", end = "")
        
        for alg in ALGORITHMS:
            # print("%.1f"%RPAP[alg][target_perc][MEMORY_MEAN] + " MB & " + "%.1f"%RPAP[alg][target_perc][MEMORY_STDEV] + " & " + \
            #         "%.2f"%(RPAP[alg][target_perc][MAX] / 1024) + " GB", end = "")
            print("%.1f"%RPAP[alg][target_perc][MEMORY_MEAN] + " MB ", end = "")
            if alg != ALGORITHMS[-1]:
                print(" & ", end = "")
            else:
                print(" \\\\ \hline")
                
    
    # Check if there is an algorithm and dataset percent which Memory usage mean of ReCG is bigger than the other algorithm
    for alg in ALGORITHMS:
        if alg in [RECG, FROZZA, KLETTKE]:
            continue
        for perc in TRAIN_PERCS:
            for dataset in dataset_fullnames:
                if RPAPD[alg][perc][dataset][MEMORY_MEAN] < RPAPD[RECG][perc][dataset][MEMORY_MEAN]:
                    print("ReCG has more memory usage than " + alg + " for " + str(perc) + "% of " + dataset)



    
    
    
if __name__ == "__main__":
    
    main()