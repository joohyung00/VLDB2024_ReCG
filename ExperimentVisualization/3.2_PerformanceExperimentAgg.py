
import statistics

import numpy as np
import sys

from pltUtils import dataset_nums, dataset_to_name, dataset_to_print_name, target_percs
sys.path.insert(1, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import num_to_name
from aggregateExpResults import *


print("<< PERFORMANCE EXPERIMENT SUMMARY >>")
print()

recg_10_mean, recg_10_stdev = getRuntimeForAlgPerc("ReCG", 10)
recg_50_mean, recg_50_stdev = getRuntimeForAlgPerc("ReCG", 50)
recg_100_mean, recg_100_stdev = getRuntimeForAlgPerc("ReCG", 100)

jxplain_10_mean, jxplain_10_stdev = getRuntimeForAlgPerc("jxplain", 10)
jxplain_recg_10 = jxplain_10_mean / recg_10_mean
jxplain_50_mean, jxplain_50_stdev = getRuntimeForAlgPerc("jxplain", 50)
jxplain_recg_50 = jxplain_50_mean / recg_50_mean
jxplain_100_mean, jxplain_100_stdev = getRuntimeForAlgPerc("jxplain", 100)
jxplain_recg_100 = jxplain_100_mean / recg_100_mean

kreduce_10_mean, kreduce_10_stdev = getRuntimeForAlgPerc("kreduce", 10)
kreduce_recg_10 = kreduce_10_mean / recg_10_mean
kreduce_50_mean, kreduce_50_stdev = getRuntimeForAlgPerc("kreduce", 50)
kreduce_recg_50 = kreduce_50_mean / recg_50_mean
kreduce_100_mean, kreduce_100_stdev = getRuntimeForAlgPerc("kreduce", 100)
kreduce_recg_100 = kreduce_100_mean / recg_100_mean


recg_10_mean = "%.2f"%(recg_10_mean)
recg_10_stdev = "%.2f"%(recg_10_stdev)
recg_50_mean = "%.2f"%(recg_50_mean)
recg_50_stdev = "%.2f"%(recg_50_stdev)
recg_100_mean = "%.2f"%(recg_100_mean)
recg_100_stdev = "%.2f"%(recg_100_stdev)
jxplain_10_mean = "%.2f"%(jxplain_10_mean)
jxplain_10_stdev = "%.2f"%(jxplain_10_stdev)
jxplain_50_mean = "%.2f"%(jxplain_50_mean)
jxplain_50_stdev = "%.2f"%(jxplain_50_stdev)
jxplain_100_mean = "%.2f"%(jxplain_100_mean)
jxplain_100_stdev = "%.2f"%(jxplain_100_stdev)
kreduce_10_mean = "%.2f"%(kreduce_10_mean)
kreduce_10_stdev = "%.2f"%(kreduce_10_stdev)
kreduce_50_mean = "%.2f"%(kreduce_50_mean)
kreduce_50_stdev = "%.2f"%(kreduce_50_stdev)
kreduce_100_mean = "%.2f"%(kreduce_100_mean)
kreduce_100_stdev = "%.2f"%(kreduce_100_stdev)
jxplain_recg_10 = "%.2f"%(jxplain_recg_10)
jxplain_recg_50 = "%.2f"%(jxplain_recg_50)
jxplain_recg_100 = "%.2f"%(jxplain_recg_100)
kreduce_recg_10 = "%.2f"%(kreduce_recg_10)
kreduce_recg_50 = "%.2f"%(kreduce_recg_50)
kreduce_recg_100 = "%.2f"%(kreduce_recg_100)


line1 = f"10\% & {recg_10_mean} ms & {recg_10_stdev} & {jxplain_10_mean} ms &	{jxplain_10_stdev} &	{jxplain_recg_10} &	{kreduce_10_mean} ms &	{kreduce_10_stdev} &	{kreduce_recg_10} \\\\ \hline"
line2 = f"50\% & {recg_50_mean} ms & {recg_50_stdev} & {jxplain_50_mean} ms &	{jxplain_50_stdev} &	{jxplain_recg_50} &	{kreduce_50_mean} ms &	{kreduce_50_stdev} &	{kreduce_recg_50} \\\\ \hline"
line3 = f"100\% & {recg_100_mean} ms & {recg_100_stdev} & {jxplain_100_mean} ms &	{jxplain_100_stdev} &	{jxplain_recg_100} &	{kreduce_100_mean} ms &	{kreduce_100_stdev} &	{kreduce_recg_100} \\\\ \hline"


print(line1)
print(line2)
print(line3)

print()
print()
print()