import pandas as pd
import numpy as np
from colorama import Fore, Style

import sys
sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames, possible_algorithms_list

from aggregateExpResults import *

print("<< MDL EXPERIMENT SUMMARY >>")
print()

recg_avg_src, recg_avg_drc, recg_avg_mdl = getMDLForAlgPerc("ReCG", 10)
jxplain_avg_src, jxplain_avg_drc, jxplain_avg_mdl = getMDLForAlgPerc("jxplain", 10)
kreduce_avg_src, kreduce_avg_drc, kreduce_avg_mdl = getMDLForAlgPerc("kreduce", 10)
gt_avg_src, gt_avg_drc, gt_avg_mdl = getMDLForAlgPerc("groundtruth", 10)
recg_to_jxplain = "%.1f"%(jxplain_avg_mdl / recg_avg_mdl)
recg_to_kreduce = "%.1f"%(kreduce_avg_mdl / recg_avg_mdl)
recg_diff_gt = "%.1f"%(100 * (1 - recg_avg_mdl/gt_avg_mdl))
print("ReCG's MDL cost is ", end = "")
print(Fore.GREEN + recg_to_jxplain, end = "")
print(Style.RESET_ALL, end = "")
print(" times smaller than Jxplain")
print()
print("ReCG's MDL cost is ", end = "")
print(Fore.GREEN + recg_to_kreduce, end = "")
print(Style.RESET_ALL, end = "")
print(" times smaller than KReduce")
print()
print("The difference of ReCG's MDL cost is within ", end = "")
print(Fore.RED + recg_diff_gt, end = "")
print(Style.RESET_ALL, end = "")
print(" difference compared to the ground truth")
print()

recg_to_jxplain = "%.2f"%(jxplain_avg_src / recg_avg_src)
recg_to_kreduce = "%.2f"%(kreduce_avg_src / recg_avg_src)
print("ReCG's SRC is ", end = "")
print(Fore.GREEN + recg_to_jxplain, end = "")
print(Style.RESET_ALL, end = "")
print(" times smaller than Jxplain")
print()
print("ReCG's SRC is ", end = "")
print(Fore.GREEN + recg_to_kreduce, end = "")
print(Style.RESET_ALL, end = "")
print(" times smaller than KReduce")
print()


print("ReCG's found schemas show lower MDL cost than groundtruth in the datasets of: ")

df = pd.DataFrame(columns=["src_gt_ratio", "drc_gt_ratio", "mdl_gt_ratio", "recall", "precision", "f1"])

for dataset_fullname in dataset_fullnames:
    # 1. Get MDL Ratios
    gt_src, gt_drc, gt_mdl = getMDLForAlgPercDataset("groundtruth", 10, dataset_fullname)
    gt_gt_src_ratio = 1.0
    gt_gt_drc_ratio = 1.0
    gt_gt_mdl_ratio = 1.0
    gt_f1, gt_recall, gt_precision = 1.0, 1.0, 1.0
    
    recg_src, recg_drc, recg_mdl = getMDLForAlgPercDataset("ReCG", 10, dataset_fullname)
    recg_gt_src_ratio = recg_src / gt_src
    recg_gt_drc_ratio = recg_drc / gt_drc
    recg_gt_mdl_ratio = recg_mdl / gt_mdl
    recg_f1, _, recg_recall, _, recg_precision, _ = getAccForAlgPercDataset("ReCG", 10, dataset_fullname)
    df.loc[len(df.index)] = [recg_gt_src_ratio, recg_gt_drc_ratio, recg_gt_mdl_ratio,
                             recg_recall, recg_precision, recg_f1]
    
    if recg_gt_mdl_ratio < 1:
        print(Fore.GREEN + dataset_fullname, end = ", ")
    
    jxplain_src, jxplain_drc, jxplain_mdl = getMDLForAlgPercDataset("jxplain", 10, dataset_fullname)
    jxplain_gt_src_ratio = jxplain_src / gt_src
    jxplain_gt_drc_ratio = jxplain_drc / gt_drc
    jxplain_gt_mdl_ratio = jxplain_mdl / gt_mdl
    jxplain_f1, _, jxplain_recall, _, jxplain_precision, _ = getAccForAlgPercDataset("jxplain", 10, dataset_fullname)
    if jxplain_f1 != -1:
        df.loc[len(df.index)] = [jxplain_gt_src_ratio, jxplain_gt_drc_ratio, jxplain_gt_mdl_ratio,
                                jxplain_recall, jxplain_precision, jxplain_f1]
    
    kreduce_src, kreduce_drc, kreduce_mdl = getMDLForAlgPercDataset("kreduce", 10, dataset_fullname)
    kreduce_gt_src_ratio = kreduce_src / gt_src
    kreduce_gt_drc_ratio = kreduce_drc / gt_drc
    kreduce_gt_mdl_ratio = kreduce_mdl / gt_mdl
    kreduce_f1, _, kreduce_recall, _, kreduce_precision, _ = getAccForAlgPercDataset("kreduce", 10, dataset_fullname)
    df.loc[len(df.index)] = [kreduce_gt_src_ratio, kreduce_gt_drc_ratio, kreduce_gt_mdl_ratio,
                             kreduce_recall, kreduce_precision, kreduce_f1]
    
print(Style.RESET_ALL, end = "")
print()
print()

print("  [ Correlation Summary ]")
print()
# print(df.corr())
corr_frame = df.corr()

src_recall      = corr_frame["src_gt_ratio"]["recall"]
src_precision   = corr_frame["src_gt_ratio"]["precision"]
src_f1          = corr_frame["src_gt_ratio"]["f1"]
drc_recall      = corr_frame["drc_gt_ratio"]["recall"]
drc_precision   = corr_frame["drc_gt_ratio"]["precision"]
drc_f1          = corr_frame["drc_gt_ratio"]["f1"]
mdl_recall      = corr_frame["mdl_gt_ratio"]["recall"]
mdl_precision   = corr_frame["mdl_gt_ratio"]["precision"]
mdl_f1          = corr_frame["mdl_gt_ratio"]["f1"]
src_recall      = "%.2f"%(src_recall)
src_precision   = "%.2f"%(src_precision)
src_f1          = "%.2f"%(src_f1)
drc_recall      = "%.2f"%(drc_recall)
drc_precision   = "%.2f"%(drc_precision)
drc_f1          = "%.2f"%(drc_f1)
mdl_recall      = "%.2f"%(mdl_recall)
mdl_precision   = "%.2f"%(mdl_precision)
mdl_f1          = "%.2f"%(mdl_f1)


line1 = "    & Recall        & Precision     & F1 score \\\\ \\hline \\hline"
line2 = "% ================================================ % "
line3 = f"SRC & {src_recall} & {src_precision} & {src_f1} \\\\ \\hline"
line4 = f"DRC & {drc_recall} & {drc_precision} & {drc_f1} \\\\ \\hline"
line5 = f"MDL & {mdl_recall} & {mdl_precision} & {mdl_f1} \\\\ \\hline"

print(line1)
print(line2)
print(line3)
print(line4)
print(line5)

print()
print()
print()