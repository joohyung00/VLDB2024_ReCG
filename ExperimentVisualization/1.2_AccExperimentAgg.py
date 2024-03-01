

import pandas as pd
import numpy as np
from colorama import Fore, Style

import sys
sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames, possible_algorithms_list

from aggregateExpResults import *

print("<< ACCURACY EXPERIMENT SUMMARY >>")
print()

recg_f1, recg_recall, recg_precision = getAccForAlg("ReCG")
jxplain_f1, jxplain_recall, jxplain_precision = getAccForAlg("jxplain")
kreduce_f1, kreduce_recall, kreduce_precision = getAccForAlg("kreduce")

recg_f1_rounded = "%.2f"%(recg_f1)
print("ReCG's average F1 score is ", end = "")
print(Fore.GREEN + recg_f1_rounded, end = "")
print(Style.RESET_ALL, end = "")
print(".")
print()

recg_over_jxplain = "%.0f"%(100 * (recg_f1 / jxplain_f1 - 1))
recg_over_kreduce = "%.0f"%(100 * (recg_f1 / kreduce_f1 - 1))
print("ReCG's F1 score is ", end = "")
print(Fore.GREEN + recg_over_jxplain + "%", end = "")
print(Style.RESET_ALL, end = "")
print(" higher than that of Jxplain.")
print()
print("ReCG's F1 score is ", end = "")
print(Fore.GREEN + recg_over_kreduce + "%", end = "")
print(Style.RESET_ALL, end = "")
print(" higher than that of KReduce.")
print()

jxplain_less_recg = "%.1f"%(100 * (1 - jxplain_f1 / recg_f1))
kreduce_less_recg = "%.1f"%(100 * (1 - kreduce_f1 / recg_f1))
print("Jxplain receieved about ", end = "")
print(Fore.RED + jxplain_less_recg + "%", end = "")
print(Style.RESET_ALL, end = "")
print(" less F1 score than ReCG.")
print()
print("KReduce receieved about ", end = "")
print(Fore.RED + kreduce_less_recg + "%", end = "")
print(Style.RESET_ALL, end = "")
print(" less F1 score than ReCG.")
print()
print()
print()