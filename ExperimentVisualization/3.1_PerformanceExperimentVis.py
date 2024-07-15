
import statistics
import matplotlib.pyplot as plt
import matplotlib
import csv
import argparse

import numpy as np
import sys

from pltUtils import dataset_nums, dataset_to_name, dataset_to_print_name, target_percs
sys.path.insert(1, "/root/VLDB2024_ReCG/Experiment/utils")
from dataset_metadata import num_to_name
from aggregateExpResults import getRuntimeForAlgPerc, getRuntimeForAlgPercDataset



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
        recg =    [getRuntimeForAlgPercDataset("ReCG", train_percent, dataset_name) for train_percent in train_percents]
        jxplain = [getRuntimeForAlgPercDataset("jxplain", train_percent, dataset_name) for train_percent in train_percents]
        if jxplain == [-1 for _ in range(10)]: jxplain = []
        kreduce = [getRuntimeForAlgPercDataset("kreduce", train_percent, dataset_name) for train_percent in train_percents]
        lreduce = [getRuntimeForAlgPercDataset("lreduce", train_percent, dataset_name) for train_percent in train_percents]
        klettke = [getRuntimeForAlgPercDataset("klettke", train_percent, dataset_name) for train_percent in train_percents]
        klettke = [x if x != -1 else None for x in klettke]
        if klettke == [-1 for _ in range(10)]: klettke = []
        frozza = [getRuntimeForAlgPercDataset("frozza", train_percent, dataset_name) for train_percent in train_percents]
        if frozza == [-1 for _ in range(10)]: frozza = []
                
        # 3. Plot
            # ['royalblue', 'dodgerblue', 'deepskyblue', 'skyblue', 'mediumblue', 'darkblue']
        plt.plot(range(len(frozza)),    frozza,  linestyle = "-",  marker = "o",  color = "skyblue",    label = "Frozza")
        plt.plot(range(len(klettke)),   klettke, linestyle = "-",  marker = "d",  color = "deepskyblue",label = "Klettke")
        plt.plot(range(len(lreduce)),   lreduce, linestyle = ":",  marker = "x",  color = "dodgerblue", label = "LReduce")
        plt.plot(range(len(kreduce)),   kreduce, linestyle = "-.", marker = "^",  color = "royalblue",  label = "KReduce")
        plt.plot(range(len(jxplain)),   jxplain, linestyle = "--", marker = "s",  color = "mediumblue", label = "Jxplain")
        plt.plot(range(len(recg)),      recg,    linestyle = "-",  marker = "o",  color = "darkblue",   label = "ReCG")
        
        
        
        # 4. Ticks and labels
        plt.xticks(ticks = range(10),   labels = [f"{i}0%" for i in range(1, 11)])
        plt.ylabel("Runtime (ms)", fontsize = 16)
        plt.xlabel("Used data set proportion", fontsize = 16)
        plt.tick_params(axis = 'x', which = 'major', labelsize = 12)
        plt.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0,0))
        
        # 5. Legend
        plt.legend()
        
        # 6. Print plot
        plt.savefig("Performance/" + dataset_name.split("_")[0] + ".pdf", bbox_inches = "tight", pad_inches = 0)
    
    
    
    # 1. Initiate figure
    font = {'size' : 14}
    matplotlib.rc('font', **font)
    width = 6
    height = 4
    fig, ax = plt.subplots(figsize = (width, height))
    
    # 2. Get dataset
    recg =    [getRuntimeForAlgPerc("ReCG", train_percent)[0] for train_percent in train_percents]
    jxplain = [getRuntimeForAlgPerc("jxplain", train_percent)[0] for train_percent in train_percents]
    if jxplain == [-1 for _ in range(10)]: jxplain = []
    kreduce = [getRuntimeForAlgPerc("kreduce", train_percent)[0] for train_percent in train_percents]
    lreduce = [getRuntimeForAlgPerc("lreduce", train_percent)[0] for train_percent in train_percents]
    klettke = [getRuntimeForAlgPerc("klettke", train_percent)[0] for train_percent in train_percents]
    klettke = [x if x != -1 else None for x in klettke]
    if klettke == [-1 for _ in range(10)]: klettke = []
    
            
    # 3. Plot
    plt.plot(range(len(frozza)),    frozza,  linestyle = "-",  marker = "o",  color = "skyblue",    label = "Frozza")
    plt.plot(range(len(klettke)),   klettke, linestyle = "-",  marker = "d",  color = "deepskyblue",label = "Klettke")
    plt.plot(range(len(lreduce)),   lreduce, linestyle = ":",  marker = "x",  color = "dodgerblue", label = "LReduce")
    plt.plot(range(len(kreduce)),   kreduce, linestyle = "-.", marker = "^",  color = "royalblue",  label = "KReduce")
    plt.plot(range(len(jxplain)),   jxplain, linestyle = "--", marker = "s",  color = "mediumblue", label = "Jxplain")
    plt.plot(range(len(recg)),      recg,    linestyle = "-",  marker = "o",  color = "darkblue",   label = "ReCG")
    
    
    # print(frozza)
    # print(klettke)
    # print(lreduce)
    # print(kreduce)
    # print(jxplain)
    # print(recg) 
    
    
    # 4. Ticks and labels
    plt.xticks(ticks = range(10),   labels = [f"{i}0%" for i in range(1, 11)])
    plt.ylabel("Runtime (ms)", fontsize = 16)
    plt.xlabel("Used data set proportion", fontsize = 16)
    plt.tick_params(axis = 'x', which = 'major', labelsize = 12)
    plt.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0,0))
    
    # 5. Legend
    plt.legend()
    
    # 6. Print plot
    plt.savefig("Performance/Average.pdf", bbox_inches = "tight", pad_inches = 0)


    
if __name__ == "__main__":
    main((sys.argv)[1:])
