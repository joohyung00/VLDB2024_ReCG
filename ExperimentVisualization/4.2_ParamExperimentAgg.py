import csv
import statistics
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import argparse
import sys
from pltUtils import dataset_nums, dataset_to_name
sys.path.insert(1, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import num_to_name
from aggregateExpResults import PARAM_EXP, getResultForPercParamDataset, getResultForPercParam



PARAM_EXP = {
    "exp_type": "Parameter",
    "result_path": "/root/JsonExplorerSpark/Experiment/exp4_param.txt",
    "train_percs" : [10, 40, 50, 60, 80, 90, 100],
    
    "param_name_to_values": {
        "beam_width": [1, 2, 3, 4, 5],
        "epsilon": [0.1, 0.3, 0.5, 0.7, 0.9],
        "min_pts_perc": [1, 3, 5, 10, 20, 30],
        "sample_size": [25, 50, 100, 250, 500, 1000],
        "mdl_weights": [(0.01, 0.99), (0.1, 0.9), (0.3, 0.7), (0.5, 0.5), (0.7, 0.3), (0.9, 0.1), (0.99, 0.01)],
    },
    "param_name_to_default_value": {
        "beam_width": 3,
        "epsilon": 0.5,
        "min_pts_perc": 5,
        "sample_size": 500,
        "mdl_weights": (0.5, 0.5)
    },
    
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}  


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

beam_width_cvd = {
    "epsilon": 0.1,
    "min_pts_perc": 1,
    "sample_size": 500,
    "mdl_weights": (0.5, 0.5)
}
# beam_width_cvd = {
#     "epsilon": 0.5,
#     "min_pts_perc": 5,
#     "sample_size": 500,
#     "mdl_weights": (0.5, 0.5)
# }




def parseArgumnets(argv):
    parser = argparse.ArgumentParser() 
    args = parser.parse_args(argv)
    print(args)
    
    return args





def main(argv):
    args = parseArgumnets(argv)
    
    _, _, beam_width_1_f1, _, _, _, _ = getResultForPercParam("beam_width", 10, 1, beam_width_cvd)
    _, _, beam_width_5_f1, _, _, _, _ = getResultForPercParam("beam_width", 10, 5, beam_width_cvd)
    
    print("There was " + "%.2f"%(((beam_width_5_f1 / beam_width_1_f1) - 1) * 100) + " increase in F1 as beam width increased from 1 to 5.")
    print()
    
    _, mdl_weights_55_precision,  mdl_weights_55_f1,  _, _, _, _ = getResultForPercParam("mdl_weights", 10, (0.5, 0.5))
    _, mdl_weights_991_precision, mdl_weights_991_f1, _, _, _, _ = getResultForPercParam("mdl_weights", 10, (0.99, 0.01))
    
    print("There was " + "%.2f"%((1 - (mdl_weights_991_precision / mdl_weights_55_precision)) * 100) + " decrease in Precision as mdl weights changed from (0.5, 0.5) to (0.99, 0.01).")
    print("There was " + "%.2f"%((1 - (mdl_weights_991_f1 / mdl_weights_55_f1)) * 100) + " decrease in F1 as mdl weights changed from (0.5, 0.5) to (0.99, 0.01).")
     
    

if __name__ == "__main__":
    main((sys.argv)[1:])
