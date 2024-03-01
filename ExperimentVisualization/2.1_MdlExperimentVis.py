import sys
import csv
import statistics
import argparse

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from pltUtils import dataset_nums, dataset_to_name

sys.path.insert(1, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import num_to_name
from aggregateExpResults import *


def main(argv):

    # Arg: Perc
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", choices = ["True", "False"])
    args = parser.parse_args(argv)
    print(args)
    if args.csv == "True":
        printCSV()
        return
        

    # Set metadata
        # Algorithms
    algorithms = ["GroundTruth", "ReCG", "Jxplain", "KReduce"]
    target_percent = 10

    
    for i, dataset_fullname in enumerate(dataset_fullnames):

        dataset_name = dataset_fullname

        # Get dataset
        gt_src, gt_drc, _ =            getMDLForAlgPercDataset("groundtruth",  target_percent, dataset_name)
        ReCG_src, ReCG_drc, _ =        getMDLForAlgPercDataset("ReCG",         target_percent, dataset_name)
        jxplain_src, jxplain_drc, _ =  getMDLForAlgPercDataset("jxplain",      target_percent, dataset_name)
        kreduce_src, kreduce_drc, _ =  getMDLForAlgPercDataset("kreduce",      target_percent, dataset_name)
        
        ReCG_f1, _, ReCG_recall, _, ReCG_precision, _ =          getAccForAlgPercDataset("ReCG",    target_percent, dataset_name)
        jxplain_f1, _, jxplain_recall, _, jxplain_precision, _ = getAccForAlgPercDataset("jxplain", target_percent, dataset_name)
        kreduce_f1, _, kreduce_recall, _, kreduce_precision, _ = getAccForAlgPercDataset("kreduce", target_percent, dataset_name)

        
        
        # 1. Initiate figure 
        width = 6
        height = 4
        fig, ax = plt.subplots(figsize = (width, height))
        
        # 2. Get dataset
        x_bar_start = np.arange(len(algorithms))
        bar_width = 0.35
        x_ticks = x_bar_start + bar_width * 2 / 2
        
        srcs = [gt_src, ReCG_src, jxplain_src, kreduce_src]
        drcs = [gt_drc, ReCG_drc, jxplain_drc, kreduce_drc]
        
        # 3. Plot
        linewidth = 2
        # color = "lightblue",
        # color = "royalblue",
        ax.bar(x_bar_start,                  srcs, bar_width, edgecolor = "black", linewidth = linewidth, color = "black", label = "SRC")
        ax.bar(x_bar_start + bar_width,      drcs, bar_width, edgecolor = "black", linewidth = linewidth, color = "white", label = "DRC")
        
        
        
        
        
        # 4. Set labels
        ax.set_ylabel("MDL Cost", fontsize = 16)
        ax.set_xlabel("Algorithm", fontsize = 16)    
        ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
        
        ax.set_xticklabels([])
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(algorithms)
        ax.tick_params(axis='x', which='major', labelsize = 14)
        h1, l1 = ax.get_legend_handles_labels()

        # Plotting on another scale
        ax = ax.twinx()
        
        
        # 2. Get dataset
        f1s =           [1.0, ReCG_f1,          jxplain_f1,         kreduce_f1          ]
        recalls =       [1.0, ReCG_recall,      jxplain_recall,     kreduce_recall      ]
        precisions =    [1.0, ReCG_precision,   jxplain_precision,  kreduce_precision   ]
        
        # 3. Plot
        ax.plot(x_ticks, f1s,           linestyle = "-" , marker = "o", color = "royalblue",    label="F1")
        ax.plot(x_ticks, recalls,       linestyle = "--", marker = "s", color = "dodgerblue",   label="Recall")
        ax.plot(x_ticks, precisions,    linestyle = "-.", marker = "^", color = "deepskyblue",  label="Precision")
        
        # 4. Set labels
        ax.set_ylabel("Accuracy", fontsize = 16)
        
        # 5. Legend
        h2, l2 = ax.get_legend_handles_labels()
        legend = ax.legend(handles = [*h1, *h2], loc = 'center left', fontsize = 10)
        legend.get_frame().set_alpha(1)
        
        # 6. Print plot
        plt.savefig("MDL/" + dataset_name.split("_")[0] + ".pdf", bbox_inches = "tight", pad_inches = 0)
        
        
    
    

    
    

    # 1. Initiate figure
    font = {'size' : 14}
    matplotlib.rc('font', **font)
    linewidth = 2
    width = 8
    height = 4.17
    fig, ax = plt.subplots(figsize = (width, height))

    # 2. Get dataset
    
    algorithms = ["GroundTruth", "ReCG", "Jxplain", "KReduce"]
    x_bar_start = np.arange(len(algorithms))
    bar_width = 0.30
    x_ticks = x_bar_start + bar_width / 2
    
    gt_src, gt_drc, _ =            getMDLForAlgPerc("groundtruth",  target_percent)
    ReCG_src, ReCG_drc, _ =        getMDLForAlgPerc("ReCG",         target_percent)
    jxplain_src, jxplain_drc, _ =  getMDLForAlgPerc("jxplain",      target_percent)
    kreduce_src, kreduce_drc, _ =  getMDLForAlgPerc("kreduce",      target_percent)
    
    ReCG_f1, ReCG_recall, ReCG_precision =          getAccForAlgPerc("ReCG",    target_percent)
    jxplain_f1, jxplain_recall, jxplain_precision = getAccForAlgPerc("jxplain", target_percent)
    kreduce_f1, kreduce_recall, kreduce_precision = getAccForAlgPerc("kreduce", target_percent)
    print(f1s)
    print(recalls)
    print(precisions)
    f1s =           [1.0, ReCG_f1, jxplain_f1, kreduce_f1]
    recalls =       [1.0, ReCG_recall, jxplain_recall, kreduce_recall]
    precisions =    [1.0, ReCG_precision, jxplain_precision, kreduce_precision]
    
    srcs = [gt_src, ReCG_src, jxplain_src, kreduce_src]
    drcs = [gt_drc, ReCG_drc, jxplain_drc, kreduce_drc]
    
    # 3. Plot
        # color = "#9dc3e6",
        # color = "#0070c0",
    plt.bar(x_bar_start,              srcs, bar_width, color = "black", edgecolor = "black", linewidth = linewidth, label = "SRC")
    plt.bar(x_bar_start + bar_width,  drcs, bar_width, color = "white", edgecolor = "black", linewidth = linewidth, label = "DRC")

    # 4. Ticks and labels
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(algorithms)
    plt.xlabel("Algorithm", fontsize = 30)
    plt.ylabel("MDL Cost", fontsize = 30)
    ax.tick_params(axis='x', which='major', labelsize = 22)
    ax.tick_params(axis='y', which='major', labelsize = 22)
    plt.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    
    # 5. Legend
    legend = plt.legend(loc = "upper left")
    legend.get_frame().set_alpha(1)
    
    # 6. Print plot
    plt.tight_layout()
    plt.savefig("MDL/AverageMDL.pdf", bbox_inches = "tight", pad_inches = 0)
    

    # 1. Initiate figure
    font = {'size' : 14}
    matplotlib.rc('font', **font)
    width = 8
    height = 4
    fig, ax = plt.subplots(figsize = (width, height))
    
    # 2. Get dataset
    x_bar_start = np.arange(len(algorithms))
    bar_width = 0.27
    x_ticks = x_bar_start + bar_width * 2 / 2
    
    # 3. Plot
    plt.bar(x_bar_start,                  f1s,        bar_width,  color = "black", edgecolor = "black", linewidth = linewidth, label = "F1"        )
    plt.bar(x_bar_start + bar_width,      recalls,    bar_width,  color = "gray",  edgecolor = "black", linewidth = linewidth, label = "Recall"    )
    plt.bar(x_bar_start + bar_width * 2,  precisions, bar_width,  color = "white", edgecolor = "black", linewidth = linewidth, label = "Precision" )
    
    # 4. Ticks and labels
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(algorithms)
    plt.xlabel("Algorithm", fontsize = 30)
    plt.ylabel("Accuracy", fontsize = 30)
    ax.tick_params(axis='x', which='major', labelsize = 22)
    ax.tick_params(axis='y', which='major', labelsize = 22)
    plt.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    
    # 5. Legend
    legend = plt.legend(loc = "lower right")
    legend.get_frame().set_alpha(1)
    
    # 6. Print plot
    plt.tight_layout()
    plt.savefig("MDL/AverageAccuracy.pdf", bbox_inches = "tight", pad_inches = 0)



#####################################################
# printCSV                                          #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################


def printCSV():
    
    with open("MdlExperiment.csv", "w") as file:
        for dataset_num_idx in range(20): 
            dataset = dataset_to_name[dataset_nums[dataset_num_idx]]
            for percentage in ["1", "10", "50", "90"]:
                
                line = ""
                for algorithm in ["groundtruth", "ReCG", "jxplain", "kreduce"]:
                    src, drc = getMDLResult(algorithm, dataset, percentage)
                    if algorithm == "kreduce":
                        line += str(src) + "," + str(drc)
                    else:
                        line += str(src) + "," + str(drc) + ","
                file.write(line + "\n")




if __name__ == "__main__":
    main((sys.argv)[1:])