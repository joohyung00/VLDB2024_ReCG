
import statistics
import matplotlib.pyplot as plt
import matplotlib
import csv
import argparse

import numpy as np
import sys

from pltUtils import dataset_nums, dataset_to_name, dataset_to_print_name, target_percs
sys.path.insert(1, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import num_to_name
from aggregateExpResults import getMemoryForAlgPerc, getMemoryForAlgPercDataset


def main(argv):
        # Arg: Perc
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    print(args)

    # Set metadata
        # algorithms = ["ReCG", "JXPlain", "KReduce"]
    train_percents = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


    for dataset_num in dataset_nums:
        
        # Per-data metadata
        dataset_name = dataset_to_name[dataset_num]
        
        # 1. Initiate figure
        font = {'size' : 14}
        matplotlib.rc('font', **font)
        width = 6
        height = 4
        fig, ax = plt.subplots(figsize = (width, height))
        
        # 2. Get dataset
        recg =    [getMemoryForAlgPercDataset("ReCG", train_percent, dataset_name) for train_percent in train_percents]
        jxplain = [getMemoryForAlgPercDataset("jxplain", train_percent, dataset_name) for train_percent in train_percents]
        if jxplain == [-1 for _ in range(10)]:
            jxplain = []
        kreduce = [getMemoryForAlgPercDataset("kreduce", train_percent, dataset_name) for train_percent in train_percents]
        lreduce = [getMemoryForAlgPercDataset("lreduce", train_percent, dataset_name) for train_percent in train_percents]
        klettke = [getMemoryForAlgPercDataset("klettke", train_percent, dataset_name) for train_percent in train_percents]
        klettke = [x if x != -1 else None for x in klettke]
        if klettke == [-1 for _ in range(10)]: klettke = []
        frozza = [getMemoryForAlgPercDataset("frozza", train_percent, dataset_name) for train_percent in train_percents]
        if frozza == [-1 for _ in range(10)]: frozza = []
                
        # 3. Plot
        
        plt.plot(range(len(frozza)),    frozza,  linestyle = "-",  marker = "o",  color = "skyblue",    label = "FMC")
        plt.plot(range(len(klettke)),   klettke, linestyle = "-",  marker = "d",  color = "deepskyblue",label = "KSS")
        plt.plot(range(len(lreduce)),   lreduce, linestyle = ":",  marker = "x",  color = "dodgerblue", label = "LReduce")
        plt.plot(range(len(kreduce)),   kreduce, linestyle = "-.", marker = "^",  color = "royalblue",  label = "KReduce")
        plt.plot(range(len(jxplain)),   jxplain, linestyle = "--", marker = "s",  color = "mediumblue", label = "Jxplain")
        plt.plot(range(len(recg)),      recg,    linestyle = "-",  marker = "o",  color = "darkblue",   label = "ReCG")
        
        
        # 4. Ticks and labels
        plt.xticks(ticks = range(10),   labels = [f"{i}0%" for i in range(1, 11)])
        plt.ylabel("Memory Used (KB)", fontsize = 16)
        plt.xlabel("Used data set proportion", fontsize = 16)
        plt.tick_params(axis = 'x', which = 'major', labelsize = 12)
        plt.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0,0))
        
        # 5. Legend
        plt.legend()
        
        # 6. Print plot
        plt.savefig("Memory/" + dataset_name.split("_")[0] + ".pdf", bbox_inches = "tight", pad_inches = 0)
        
        
    
    # 1. Initiate figure
    font = {'size' : 14}
    matplotlib.rc('font', **font)
    width = 6
    height = 4
    fig, ax = plt.subplots(figsize = (width, height))
    
    # 2. Get dataset
    recg =    [getMemoryForAlgPerc("ReCG", train_percent)[0] for train_percent in train_percents]
    jxplain = [getMemoryForAlgPerc("jxplain", train_percent)[0] for train_percent in train_percents]
    if jxplain == [-1 for _ in range(10)]: jxplain = []
    kreduce = [getMemoryForAlgPerc("kreduce", train_percent)[0] for train_percent in train_percents]
    lreduce = [getMemoryForAlgPerc("lreduce", train_percent)[0] for train_percent in train_percents]
    klettke = [getMemoryForAlgPerc("klettke", train_percent)[0] for train_percent in train_percents]
    if klettke == [-1 for _ in range(10)]: klettke = []
    frozza = [getMemoryForAlgPerc("frozza", train_percent)[0] for train_percent in train_percents]
    if frozza == [-1 for _ in range(10)]: frozza = []
    
    print(recg)
    print(jxplain)
    print(kreduce)
    print(lreduce)
    print(klettke)
    print(frozza)
    
            
    # 3. Plot
    plt.plot(range(len(frozza)),    frozza,  linestyle = "-",  marker = "o",  color = "skyblue",    label = "FMC")
    plt.plot(range(len(klettke)),   klettke, linestyle = "-",  marker = "d",  color = "deepskyblue",label = "KSS")
    plt.plot(range(len(lreduce)),   lreduce, linestyle = ":",  marker = "x",  color = "dodgerblue", label = "LReduce")
    plt.plot(range(len(kreduce)),   kreduce, linestyle = "-.", marker = "^",  color = "royalblue",  label = "KReduce")
    plt.plot(range(len(jxplain)),   jxplain, linestyle = "--", marker = "s",  color = "mediumblue", label = "Jxplain")
    plt.plot(range(len(recg)),      recg,    linestyle = "-",  marker = "o",  color = "darkblue",   label = "ReCG")
    
    # 4. Ticks and labels
    plt.xticks(ticks = range(10),   labels = [f"{i}0%" for i in range(1, 11)])
    plt.ylabel("Memory Used (KB)", fontsize = 16)
    plt.xlabel("Used data set proportion", fontsize = 16)
    plt.tick_params(axis = 'x', which = 'major', labelsize = 12)
    plt.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0,0))
    
    # 5. Legend
    plt.legend()
    
    # 6. Print plot
    plt.savefig("Memory/Average.pdf", bbox_inches = "tight", pad_inches = 0)
    

    
if __name__ == "__main__":
    main((sys.argv)[1:])
