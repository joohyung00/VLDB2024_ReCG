
import statistics

import numpy as np
import sys

from pltUtils import dataset_nums, dataset_to_name, dataset_to_print_name, target_percs
sys.path.insert(1, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_fullnames
from aggregateExpResults import getRuntimeForAlgPerc



RECG = "ReCG"
JXPLAIN = "jxplain"
KREDUCE = "kreduce"
LREDUCE = "lreduce"
KLETTKE = "klettke"
FROZZA = "frozza"

ALGORITHMS  = [RECG, JXPLAIN, KREDUCE, LREDUCE, KLETTKE, FROZZA]
TRAIN_PERCS = [10, 50, 100]

RUNTIME_MEAN = "runtime_mean"
RUNTIME_STDEV = "runtime_stdev"


def main():
    
    # 1. Aggregate data 
    result_per_alg_perc = {}
    for algorithm in ALGORITHMS:
        result_per_alg_perc[algorithm] = {}
        for percent in TRAIN_PERCS:
            result_per_alg_perc[algorithm][percent] = {
                RUNTIME_MEAN: -1,
                RUNTIME_STDEV: -1
            }
    RPAP = result_per_alg_perc
    
    for alg in ALGORITHMS:
        for perc in TRAIN_PERCS:
            RPAP[alg][perc][RUNTIME_MEAN], RPAP[alg][perc][RUNTIME_STDEV] = getRuntimeForAlgPerc(alg, perc)


    for target_perc in TRAIN_PERCS:
        print(str(target_perc) + "\\% & ", end = "")
        
        for alg in ALGORITHMS:
            print("%.2f"%RPAP[alg][target_perc][RUNTIME_MEAN] + " ms & " + "%.2f"%RPAP[alg][target_perc][RUNTIME_STDEV] + " & " + \
                    "%.2f"%(RPAP[RECG][target_perc][RUNTIME_MEAN] / RPAP[alg][target_perc][RUNTIME_MEAN]), end = "")
            if alg != ALGORITHMS[-1]:
                print(" & ", end = "")
            else:
                print(" \\\\ \hline")        
                
                
                
    RECG_REL_JXPLAIN_MAX = -1
    RECG_REL_JXPLAIN_MIN = 1000000
    
    for target_perc in TRAIN_PERCS:
        RECG_REL_JXPLAIN_MAX = max(RECG_REL_JXPLAIN_MAX, RPAP[JXPLAIN][target_perc][RUNTIME_MEAN] / RPAP[RECG][target_perc][RUNTIME_MEAN])
        RECG_REL_JXPLAIN_MIN = min(RECG_REL_JXPLAIN_MIN, RPAP[JXPLAIN][target_perc][RUNTIME_MEAN] / RPAP[RECG][target_perc][RUNTIME_MEAN])
    
    RECG_REL_KREDUCE_MEAN = 0
    
    for target_perc in TRAIN_PERCS:
        RECG_REL_KREDUCE_MEAN += RPAP[RECG][target_perc][RUNTIME_MEAN] / RPAP[KREDUCE][target_perc][RUNTIME_MEAN]
    RECG_REL_KREDUCE_MEAN /= len(TRAIN_PERCS)
    
    print()
    print("ReCG outperformed Jxplain by a significant margin (" + "%.2f"%RECG_REL_JXPLAIN_MIN + "× to " + "%.2f"%RECG_REL_JXPLAIN_MAX + "×)")
    print()
    print("KReduce was faster than ReCG by about " + "%.2f"%((RECG_REL_KREDUCE_MEAN - 1) * 100) +"%.")
    



    
    
    
if __name__ == "__main__":
    main()