import sys
import csv
import statistics
import argparse

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from pltUtils import dataset_nums, dataset_to_name

from aggregateExpResults import *





def main(argv):

    variances = ["1%", "10%", "50%", "90%"]

    font = {'size' : 14}
    matplotlib.rc('font', **font)
    width = 4
    height = 3.5
    linewidth = 2
    
    
    #############################################
    # F1 Plot                                   #
    #                                           #
    #                                           #
    #############################################
    
    # 1. Initiate figure

    fig, ax = plt.subplots(figsize = (width, height))
    
    # 2. Get dataset
    x_bar_start = np.arange(len(variances))
    bar_width = 0.27
    x_ticks = x_bar_start + bar_width * 2 / 2
    
    ReCG_f1s    =   [getAccForAlgPerc("ReCG", 1)[F1IDX], 
                     getAccForAlgPerc("ReCG", 10)[F1IDX], 
                     getAccForAlgPerc("ReCG", 50)[F1IDX], 
                     getAccForAlgPerc("ReCG", 90)[F1IDX]]
    JXPlain_f1s =   [getAccForAlgPerc("jxplain", 1)[F1IDX],
                     getAccForAlgPerc("jxplain", 10)[F1IDX], 
                     getAccForAlgPerc("jxplain", 50)[F1IDX], 
                     getAccForAlgPerc("jxplain", 90)[F1IDX]]
    KReduce_f1s =  [getAccForAlgPerc("kreduce", 1)[F1IDX],
                    getAccForAlgPerc("kreduce", 10)[F1IDX], 
                    getAccForAlgPerc("kreduce", 50)[F1IDX], 
                    getAccForAlgPerc("kreduce", 90)[F1IDX]]
    
    
    # 3. Plot
    plt.bar(x_bar_start,                  ReCG_f1s   , bar_width,  color = "#000000", edgecolor = "black", linewidth = linewidth, label = "ReCG"   )
    plt.bar(x_bar_start + bar_width,      JXPlain_f1s, bar_width,  color = "#7f7f7f", edgecolor = "black", linewidth = linewidth, label = "Jxplain")
    plt.bar(x_bar_start + bar_width * 2,  KReduce_f1s, bar_width,  color = "#ffffff", edgecolor = "black", linewidth = linewidth, label = "KReduce")
    
    # 4. Ticks and labels
    plt.xlabel("Used data set proportion", fontsize = 20)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(variances)
    plt.ylabel("F1 Score", fontsize = 20)
    plt.yticks([0.00, 0.25, 0.50, 0.75, 1.00])
    ax.tick_params(axis='x', which='major', labelsize = 18)
    ax.tick_params(axis='y', which='major', labelsize = 12)
    # legend = plt.legend(loc = "lower right")
    # legend.get_frame().set_alpha(1)
    
    # 6. Print plot
    plt.tight_layout()
    plt.savefig("Accuracy/overall_f1_comparison.pdf", bbox_inches = "tight", pad_inches = 0)
    
    
    
    #############################################
    # Recall Plot                               #
    #                                           #
    #                                           #
    #############################################
    
    # 1. Initiate figure
    fig, ax = plt.subplots(figsize = (width, height))
    
    # 2. Get dataset
    x_bar_start = np.arange(len(variances))
    bar_width = 0.27
    x_ticks = x_bar_start + bar_width * 2 / 2
    
    ReCG_recalls =      [getAccForAlgPerc("ReCG", 1)[RECALLIDX], 
                         getAccForAlgPerc("ReCG", 10)[RECALLIDX], 
                         getAccForAlgPerc("ReCG", 50)[RECALLIDX], 
                         getAccForAlgPerc("ReCG", 90)[RECALLIDX]]
    JXPlain_recalls =   [getAccForAlgPerc("jxplain", 1)[RECALLIDX],
                         getAccForAlgPerc("jxplain", 10)[RECALLIDX], 
                         getAccForAlgPerc("jxplain", 50)[RECALLIDX], 
                         getAccForAlgPerc("jxplain", 90)[RECALLIDX]]
    KReduce_recalls =   [getAccForAlgPerc("kreduce", 1)[RECALLIDX],
                         getAccForAlgPerc("kreduce", 10)[RECALLIDX], 
                         getAccForAlgPerc("kreduce", 50)[RECALLIDX], 
                         getAccForAlgPerc("kreduce", 90)[RECALLIDX]]
    
    # color = "#0070c0",
    # color = "#9dc3e6",
    # color = "#deebf7",
    # 3. Plot
    plt.bar(x_bar_start,                  ReCG_recalls   , bar_width, color = "#000000", edgecolor = "black", linewidth = linewidth, label = "ReCG"   )
    plt.bar(x_bar_start + bar_width,      JXPlain_recalls, bar_width, color = "#7f7f7f", edgecolor = "black", linewidth = linewidth, label = "Jxplain")
    plt.bar(x_bar_start + bar_width * 2,  KReduce_recalls, bar_width, color = "#ffffff", edgecolor = "black", linewidth = linewidth, label = "KReduce")
    
    # 4. Ticks and labels
    plt.xlabel("Used data set proportion", fontsize = 20)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(variances)
    plt.ylabel("Recall", fontsize = 20)
    plt.yticks([0.00, 0.25, 0.50, 0.75, 1.00])
    ax.tick_params(axis='x', which='major', labelsize = 18)
    ax.tick_params(axis='y', which='major', labelsize = 12)
    # legend = plt.legend(loc = "lower right")
    # legend.get_frame().set_alpha(1)
    
    # 6. Print plot
    plt.tight_layout()
    plt.savefig("Accuracy/overall_recall_comparison.pdf", bbox_inches = "tight", pad_inches = 0)
    


    #############################################
    # Precision Plot                            #
    #                                           #
    #                                           #
    #############################################
    
    # 1. Initiate figure
    fig, ax = plt.subplots(figsize = (width, height))
    
    # 2. Get dataset
    x_bar_start = np.arange(len(variances))
    bar_width = 0.27
    x_ticks = x_bar_start + bar_width * 2 / 2
    
    ReCG_precisions =       [getAccForAlgPerc("ReCG", 1)[PRECISIONIDX],
                            getAccForAlgPerc("ReCG", 10)[PRECISIONIDX], 
                            getAccForAlgPerc("ReCG", 50)[PRECISIONIDX], 
                            getAccForAlgPerc("ReCG", 90)[PRECISIONIDX]]
    JXPlain_precisions =    [getAccForAlgPerc("jxplain", 1)[PRECISIONIDX],
                            getAccForAlgPerc("jxplain", 10)[PRECISIONIDX], 
                            getAccForAlgPerc("jxplain", 50)[PRECISIONIDX], 
                            getAccForAlgPerc("jxplain", 90)[PRECISIONIDX]]
    KReduce_precisions =    [getAccForAlgPerc("kreduce", 1)[PRECISIONIDX],
                            getAccForAlgPerc("kreduce", 10)[PRECISIONIDX], 
                            getAccForAlgPerc("kreduce", 50)[PRECISIONIDX], 
                            getAccForAlgPerc("kreduce", 90)[PRECISIONIDX]]
    
    # color = "#0070c0",
    # color = "#9dc3e6",
    # color = "#deebf7",
    # 3. Plot
    plt.bar(x_bar_start,                  ReCG_precisions    , bar_width, color = "#000000", edgecolor = "black", linewidth = linewidth, label = "ReCG"   )
    plt.bar(x_bar_start + bar_width,      JXPlain_precisions , bar_width, color = "#7f7f7f", edgecolor = "black", linewidth = linewidth, label = "Jxplain")
    plt.bar(x_bar_start + bar_width * 2,  KReduce_precisions , bar_width, color = "#ffffff", edgecolor = "black", linewidth = linewidth, label = "KReduce")
    
    # 4. Ticks and labels
    plt.xlabel("Used data set proportion", fontsize = 20)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(variances)
    plt.ylabel("Precision", fontsize = 20)
    plt.yticks([0.00, 0.25, 0.50, 0.75, 1.00])
    ax.tick_params(axis='x', which='major', labelsize = 18)
    ax.tick_params(axis='y', which='major', labelsize = 12)
    legend = plt.legend(loc = "lower right")
    legend.get_frame().set_alpha(1)
    
    # 6. Print plot
    plt.tight_layout()
    plt.savefig("Accuracy/overall_precision_comparison.pdf", bbox_inches = "tight", pad_inches = 0)



if __name__ == "__main__":
    main((sys.argv)[1:])