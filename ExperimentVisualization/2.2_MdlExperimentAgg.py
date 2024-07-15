import pandas as pd
import numpy as np
from colorama import Fore, Style

import sys
sys.path.insert(1, '/root/VLDB2024_ReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/VLDB2024_ReCG/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames, possible_algorithms_list

from aggregateExpResults import getMDLForAlgPerc, getAccForAlgPerc, getAccForAlgPercDataset, getMDLForAlgPercDataset

print()
print("<< SUMMARY >>")
print()



# 1. Set metadata
MDL = "mdl"
SRC = "src"
DRC = "drc"
F1 = "f1"
RECALL = "recall"
PRECISION = "precision"

GT = "groundtruth"
RECG = "ReCG"
JXPLAIN = "jxplain"
KREDUCE = "kreduce"
LREDUCE = "lreduce"
KLETTKE = "klettke"
FROZZA = "frozza"


def main():
    algorithms = [GT, RECG, JXPLAIN, KREDUCE, LREDUCE, KLETTKE, FROZZA]
    
    # 1. Fill in results
    results_per_algorithm = {}
    for algorithm in algorithms:
        results_per_algorithm[algorithm] = {
            SRC: -1,
            DRC: -1,
            MDL: -1,
            RECALL: -1,
            PRECISION: -1,
            F1: -1
        }
    for algorithm in algorithms:
        src, drc, mdl = getMDLForAlgPerc(algorithm, 10)
        results_per_algorithm[algorithm][SRC] = src
        results_per_algorithm[algorithm][DRC] = drc
        results_per_algorithm[algorithm][MDL] = mdl
        if algorithm == GT:
            results_per_algorithm[algorithm][RECALL] = 1.0
            results_per_algorithm[algorithm][PRECISION] = 1.0
            results_per_algorithm[algorithm][F1] = 1.0
        else:
            f1, recall, precision = getAccForAlgPerc(algorithm, 10)
            results_per_algorithm[algorithm][RECALL] = recall
            results_per_algorithm[algorithm][PRECISION] = precision
            results_per_algorithm[algorithm][F1] = f1
    RPA = results_per_algorithm
    
    results_per_algorithm_dataset = {}
    for algorithm in algorithms:
        results_per_algorithm_dataset[algorithm] = {}
        for dataset in dataset_fullnames:
            results_per_algorithm_dataset[algorithm][dataset] = {
                SRC: -1,
                DRC: -1,
                MDL: -1,
                RECALL: -1,
                PRECISION: -1,
                F1: -1
            }
    for algorithm in algorithms:
        for dataset in dataset_fullnames:
            src, drc, mdl = getMDLForAlgPercDataset(algorithm, 10, dataset)
            results_per_algorithm_dataset[algorithm][dataset][SRC] = src
            results_per_algorithm_dataset[algorithm][dataset][DRC] = drc
            results_per_algorithm_dataset[algorithm][dataset][MDL] = mdl
            if algorithm == GT:
                results_per_algorithm_dataset[algorithm][dataset][RECALL] = 1.0
                results_per_algorithm_dataset[algorithm][dataset][PRECISION] = 1.0
                results_per_algorithm_dataset[algorithm][dataset][F1] = 1.0
            else:
                f1, _, recall, _, precision, _ = getAccForAlgPercDataset(algorithm, 10, dataset)
                results_per_algorithm_dataset[algorithm][dataset][RECALL] = recall
                results_per_algorithm_dataset[algorithm][dataset][PRECISION] = precision
                results_per_algorithm_dataset[algorithm][dataset][F1] = f1
    RPAD = results_per_algorithm_dataset

    print(RPAD[RECG]["23_MoviesInThailand"][SRC], RPAD[RECG]["23_MoviesInThailand"][DRC])
    print(RPAD[LREDUCE]["23_MoviesInThailand"][SRC], RPAD[LREDUCE]["23_MoviesInThailand"][DRC])
    
    
    #2. Print how much ReCG's MDL cost is within the ground truth
    print("The difference of ReCG's MDL cost is within ", end = "")
    print(Fore.RED + "%.1f"%(100 * (1 - RPA[RECG][MDL] / RPA[GT][MDL])) + r"%", end = "")
    print(Style.RESET_ALL, end = "")
    print(r" difference compared to the ground truth")
    print()
    for algorithm in algorithms:
        if algorithm in ["groundtruth", "ReCG"]: continue
        print("ReCG's MDL is ", end = "")
        print(Fore.GREEN + "%.1f"%(RPA[algorithm][MDL] / RPA[RECG][MDL]) + "x", end = "")
        print(Style.RESET_ALL, end = "")
        print(" times smaller than " + algorithmToPrintName(algorithm))
        print("ReCG's SRC is ", end = "")
        print(Fore.GREEN + "%.2f"%(RPA[algorithm][SRC] / RPA[RECG][SRC]) + "x", end = "")
        print(Style.RESET_ALL, end = "")
        print(" times smaller than " + algorithmToPrintName(algorithm))
        print("ReCG's DRC is ", end = "")
        print(Fore.GREEN + "%.2f"%(RPA[algorithm][DRC] / RPA[RECG][DRC]) + "x", end = "")
        print(Style.RESET_ALL, end = "")
        print(" times smaller than " + algorithmToPrintName(algorithm))
        print()


    #3. Print whether there were cases where other algorithms showed lower MDL cost than ReCG
    for algorithm in algorithms:
        for dataset in dataset_fullnames:
            if algorithm == GT: continue
            if algorithm == RECG: continue
            if RPAD[algorithm][dataset][MDL] < 0: continue
            if RPAD[algorithm][dataset][MDL] < RPAD[RECG][dataset][MDL]:
                print(algorithmToPrintName(algorithm) + " showed lower MDL cost than ReCG in " + dataset)
    print()

    print("ReCG's found schemas show lower MDL cost than groundtruth in the datasets of: ")

    df = pd.DataFrame(columns=["src_gt_ratio", "drc_gt_ratio", "mdl_gt_ratio", RECALL, PRECISION, F1])

    for dataset_fullname in dataset_fullnames:
        # 1. Get MDL Ratios
        gt_src, gt_drc, gt_mdl = getMDLForAlgPercDataset("groundtruth", 10, dataset_fullname)
        
        gt_gt_src_ratio = 1.0
        gt_gt_drc_ratio = 1.0
        gt_gt_mdl_ratio = 1.0
        gt_f1, gt_recall, gt_precision = 1.0, 1.0, 1.0
        
        for algorithm in algorithms:
            if algorithm == GT: continue
            # if algorithm == KLETTKE: continue
            # if algorithm == FROZZA: continue
            # if algorithm == LREDUCE: continue
            
            src, drc, mdl = getMDLForAlgPercDataset(algorithm, 10, dataset_fullname)
            gt_src_ratio = src / gt_src
            gt_drc_ratio = drc / gt_drc
            gt_mdl_ratio = mdl / gt_mdl
            f1, _, recall, _, precision, _ = getAccForAlgPercDataset(algorithm, 10, dataset_fullname)
            if f1 == -1: continue
            df.loc[len(df.index)] = [gt_src_ratio, gt_drc_ratio, gt_mdl_ratio, recall, precision, f1]
            
            if algorithm == RECG:
                if gt_mdl_ratio < 1:
                    print(Fore.GREEN + dataset_fullname, end = ", ")
                    
    for dataset_fullame in dataset_fullnames:
        df.loc[len(df.index)] = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        
    print(Style.RESET_ALL, end = "")
    print()
    print()

    print("<< Correlation Summary >>")
    print()
    corr_frame = df.corr()

    src_recall      = corr_frame["src_gt_ratio"][RECALL]
    src_precision   = corr_frame["src_gt_ratio"][PRECISION]
    src_f1          = corr_frame["src_gt_ratio"][F1]
    drc_recall      = corr_frame["drc_gt_ratio"][RECALL]
    drc_precision   = corr_frame["drc_gt_ratio"][PRECISION]
    drc_f1          = corr_frame["drc_gt_ratio"][F1]
    mdl_recall      = corr_frame["mdl_gt_ratio"][RECALL]
    mdl_precision   = corr_frame["mdl_gt_ratio"][PRECISION]
    mdl_f1          = corr_frame["mdl_gt_ratio"][F1]
    src_recall      = "%.2f"%(src_recall)
    src_precision   = "%.2f"%(src_precision)
    src_f1          = "%.2f"%(src_f1)
    drc_recall      = "%.2f"%(drc_recall)
    drc_precision   = "%.2f"%(drc_precision)
    drc_f1          = "%.2f"%(drc_f1)
    mdl_recall      = "%.2f"%(mdl_recall)
    mdl_precision   = "%.2f"%(mdl_precision)
    mdl_f1          = "%.2f"%(mdl_f1)


    line1 = "    \t& Recall        & Precision     & F1 score \t \\\\ \\hline \\hline"
    line2 = "% ============================================================== % "
    line3 = f"SRC \t& {src_recall} \t& {src_precision} \t& {src_f1} \t \\\\ \\hline"
    line4 = f"DRC \t& {drc_recall} \t& {drc_precision} \t& {drc_f1} \t \\\\ \\hline"
    line5 = f"MDL \t& {mdl_recall} \t& {mdl_precision} \t& {mdl_f1} \t \\\\ \\hline"

    print(line1)
    print(line2)
    print(line3)
    print(line4)
    print(line5)
    
    
def algorithmToPrintName(algorithm):
    if algorithm == GT:
        return "GroundTruth"
    elif algorithm == RECG:
        return "ReCG"
    elif algorithm == JXPLAIN:
        return "Jxplain"
    elif algorithm == KREDUCE:
        return "KReduce"
    elif algorithm == LREDUCE:
        return "LReduce"
    elif algorithm == KLETTKE:
        return "Klettke"
    elif algorithm == FROZZA:
        return "Frozza"
    else:
        raise ValueError("Algorithm not found: " + algorithm)
    
    
    
if __name__ == "__main__":
    main()