import sys
import csv
import statistics
import argparse

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

from pltUtils import dataset_nums, dataset_to_name
sys.path.insert(2, "/root/VLDB2024_ReCG/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames, possible_algorithms_list
from aggregateExpResults import getAccForAlgPerc, getAccForAlgPercDataset



ALGORITHMS = ["ReCG", "Jxplain", "KReduce", "LReduce", "KSS", "FMC"]
NUM_ALGORITHMS = len(ALGORITHMS)
TARGET_PERCENTS = [1, 10, 50, 90]
BAR_WIDTH = 0.14
FIG_WIDTH = 6
FIG_HEIGHT = 4
LINE_WIDTH = 2

LEGEND_SIZE = 15
LEGEND_LOC = "lower right"

XLABEL_SIZE = 26
YLABEL_SIZE = 26

XTICK_SIZE = 24
YTICK_SIZE = 24
YTICKS = [0.0, 0.25, 0.5, 0.75, 1.0]

YLIM = 1.03

def main(argv):

    # 1. Plot per dataset
    
    # Arg: Perc
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    print(args)


    # for i, dataset_fullname in enumerate(dataset_fullnames):

    #     dataset_name = dataset_fullname

    #     # Get dataset
    #     recg_f1s = []
    #     recg_precisions = []
    #     recg_recalls = []
    #     jxplain_f1s = []
    #     jxplain_precisions = []
    #     jxplain_recalls = []
    #     kreduce_f1s = []
    #     kreduce_precisions = []
    #     kreduce_recalls = []
    #     lreduce_f1s = []
    #     lreduce_precisions = []
    #     lreduce_recalls = []
    #     klettke_f1s = []
    #     klettke_precisions = []
    #     klettke_recalls = []
    #     frozza_f1s = []
    #     frozza_precisions = []
    #     frozza_recalls = []

    #     for target_percent in TARGET_PERCENTS:
    #         ReCG_f1, _, ReCG_recall, _, ReCG_precision, _ =             getAccForAlgPercDataset("ReCG",      target_percent, dataset_name)
    #         jxplain_f1, _, jxplain_recall, _, jxplain_precision, _ =    getAccForAlgPercDataset("jxplain",   target_percent, dataset_name)
    #         kreduce_f1, _, kreduce_recall, _, kreduce_precision, _ =    getAccForAlgPercDataset("kreduce",   target_percent, dataset_name)
    #         lreduce_f1, _, lreduce_recall, _, lreduce_precision, _ =    getAccForAlgPercDataset("lreduce",   target_percent, dataset_name)
    #         klettke_f1, _, klettke_recall, _, klettke_precision, _ =    getAccForAlgPercDataset("klettke",   target_percent, dataset_name)
    #         frozza_f1, _, frozza_recall, _, frozza_precision, _ =       getAccForAlgPercDataset("frozza",   target_percent, dataset_name)
            
    #         recg_f1s.append(ReCG_f1)
    #         recg_recalls.append(ReCG_recall)
    #         recg_precisions.append(ReCG_precision)
    #         jxplain_f1s.append(jxplain_f1)
    #         jxplain_recalls.append(jxplain_recall)
    #         jxplain_precisions.append(jxplain_precision)
    #         kreduce_f1s.append(kreduce_f1)
    #         kreduce_recalls.append(kreduce_recall)
    #         kreduce_precisions.append(kreduce_precision)
    #         lreduce_f1s.append(lreduce_f1)
    #         lreduce_recalls.append(lreduce_recall)
    #         lreduce_precisions.append(lreduce_precision)
    #         klettke_f1s.append(klettke_f1)
    #         klettke_recalls.append(klettke_recall)
    #         klettke_precisions.append(klettke_precision)
    #         frozza_f1s.append(frozza_f1)
    #         frozza_recalls.append(frozza_recall)
    #         frozza_precisions.append(frozza_precision)
            
    #     recg_f1s = [x if x != -1 else 0 for x in recg_f1s]
    #     recg_recalls = [x if x != -1 else 0 for x in recg_recalls]
    #     recg_precisions = [x if x != -1 else 0 for x in recg_precisions]
    #     jxplain_f1s = [x if x != -1 else 0 for x in jxplain_f1s]
    #     jxplain_recalls = [x if x != -1 else 0 for x in jxplain_recalls]
    #     jxplain_precisions = [x if x != -1 else 0 for x in jxplain_precisions]
    #     kreduce_f1s = [x if x != -1 else 0 for x in kreduce_f1s]
    #     kreduce_recalls = [x if x != -1 else 0 for x in kreduce_recalls]
    #     kreduce_precisions = [x if x != -1 else 0 for x in kreduce_precisions]
    #     lreduce_f1s = [x if x != -1 else 0 for x in lreduce_f1s]
    #     lreduce_recalls = [x if x != -1 else 0 for x in lreduce_recalls]
    #     lreduce_precisions = [x if x != -1 else 0 for x in lreduce_precisions]
    #     klettke_f1s = [x if x != -1 else 0 for x in klettke_f1s]
    #     klettke_recalls = [x if x != -1 else 0 for x in klettke_recalls]
    #     klettke_precisions = [x if x != -1 else 0 for x in klettke_precisions]
    #     frozza_f1s = [x if x != -1 else 0 for x in frozza_f1s]
    #     frozza_recalls = [x if x != -1 else 0 for x in frozza_recalls]
    #     frozza_precisions = [x if x != -1 else 0 for x in frozza_precisions]
        
        
    #     ##############
    #     # F1
    #     ##############
        
    #     # 1. Initiate figure 
    #     fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
        
    #     # 2. Get dataset
    #     x_bar_start = np.arange(len(TARGET_PERCENTS))
    #     x_ticks = x_bar_start + BAR_WIDTH * NUM_ALGORITHMS / 2
        
        
    #     # 3. Plot
        
    #     ax.bar(x_bar_start,                  recg_f1s,     BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(1, NUM_ALGORITHMS), label = "ReCG")
    #     ax.bar(x_bar_start + BAR_WIDTH * 1,  jxplain_f1s,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(2, NUM_ALGORITHMS), label = "Jxplain")
    #     ax.bar(x_bar_start + BAR_WIDTH * 2,  kreduce_f1s,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(3, NUM_ALGORITHMS), label = "KReduce")
    #     ax.bar(x_bar_start + BAR_WIDTH * 3,  lreduce_f1s,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(4, NUM_ALGORITHMS), label = "LReduce")
    #     ax.bar(x_bar_start + BAR_WIDTH * 4,  klettke_f1s,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(5, NUM_ALGORITHMS), label = "Klettke")
    #     ax.bar(x_bar_start + BAR_WIDTH * 5,  frozza_f1s,   BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(6, NUM_ALGORITHMS), label = "Frozza")
        
        
    #     # 4. Set labels
    #     ax.set_ylabel("F1 Score", fontsize = 16)
    #     ax.set_xlabel("Used data set proportion", fontsize = 16)    
    #     ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
        
    #     ax.set_xticks(x_ticks)
    #     ax.set_xticklabels([str(x) + " %" for x in TARGET_PERCENTS])
    #     ax.tick_params(axis = 'x', which = 'major', labelsize = XLABEL_SIZE)
    #     ax.tick_params(axis = 'y', which = 'major', labelsize = YLABEL_SIZE)

    #     # 5. Legend
    #     # plt.legend(loc = LEGEND_LOC, prop = {"size": LEGEND_SIZE} )
        
    #     # 6. Print plot
    #     plt.savefig("Accuracy/" + dataset_name.split("_")[0] + "_F1" + ".pdf", bbox_inches = "tight", pad_inches = 0)
        
        
        
    #     ##############
    #     # Recall
    #     ##############
        
    #     # 1. Initiate figure 
    #     fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
        
    #     # 2. Get dataset
    #     x_bar_start = np.arange(len(TARGET_PERCENTS))
    #     x_ticks = x_bar_start + BAR_WIDTH * NUM_ALGORITHMS / 2
        
    #     # 3. Plot
    #     ax.bar(x_bar_start,                  recg_recalls,     BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(1, NUM_ALGORITHMS), label = "ReCG")
    #     ax.bar(x_bar_start + BAR_WIDTH * 1,  jxplain_recalls,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(2, NUM_ALGORITHMS), label = "Jxplain")
    #     ax.bar(x_bar_start + BAR_WIDTH * 2,  kreduce_recalls,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(3, NUM_ALGORITHMS), label = "KReduce")
    #     ax.bar(x_bar_start + BAR_WIDTH * 3,  lreduce_recalls,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(4, NUM_ALGORITHMS), label = "LReduce")
    #     ax.bar(x_bar_start + BAR_WIDTH * 4,  klettke_recalls,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(5, NUM_ALGORITHMS), label = "Klettke")
    #     ax.bar(x_bar_start + BAR_WIDTH * 5,  frozza_recalls,   BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(6, NUM_ALGORITHMS), label = "Frozza")
        
        
    #     # 4. Set labels
    #     ax.set_ylabel("Recall", fontsize = 16)
    #     ax.set_xlabel("Used data set proportion", fontsize = 16)    
    #     ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
        
    #     ax.set_xticks(x_ticks)
    #     ax.set_xticklabels([str(x) + " %" for x in TARGET_PERCENTS])
    #     ax.tick_params(axis = 'x', which = 'major', labelsize = XLABEL_SIZE)
    #     ax.tick_params(axis = 'y', which = 'major', labelsize = YLABEL_SIZE)

    #     # 5. Legend
    #     # plt.legend(loc = LEGEND_LOC)
        
    #     # 6. Print plot
    #     plt.savefig("Accuracy/" + dataset_name.split("_")[0] + "_Recall" + ".pdf", bbox_inches = "tight", pad_inches = 0)
        
        
    #     ##############
    #     # Precision
    #     ##############
        
    #     # 1. Initiate figure 
    #     fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
        
    #     # 2. Get dataset
    #     x_bar_start = np.arange(len(TARGET_PERCENTS))
    #     x_ticks = x_bar_start + BAR_WIDTH * NUM_ALGORITHMS / 2
        
    #     # 3. Plot
    #     ax.bar(x_bar_start,                  recg_precisions,    BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(1, NUM_ALGORITHMS), label = "ReCG")
    #     ax.bar(x_bar_start + BAR_WIDTH * 1,  jxplain_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(2, NUM_ALGORITHMS), label = "Jxplain")
    #     ax.bar(x_bar_start + BAR_WIDTH * 2,  kreduce_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(3, NUM_ALGORITHMS), label = "KReduce")
    #     ax.bar(x_bar_start + BAR_WIDTH * 3,  lreduce_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(4, NUM_ALGORITHMS), label = "LReduce")
    #     ax.bar(x_bar_start + BAR_WIDTH * 4,  klettke_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(5, NUM_ALGORITHMS), label = "Klettke")
    #     ax.bar(x_bar_start + BAR_WIDTH * 5,  frozza_precisions,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH,  color = getColor(6, NUM_ALGORITHMS), label = "Frozza")
        
        
    #     # 4. Set labels
    #     ax.set_ylabel("Precision", fontsize = 16)
    #     ax.set_xlabel("Used data set proportion", fontsize = 16)    
    #     ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
        
    #     ax.set_xticks(x_ticks)
    #     ax.set_xticklabels([str(x) + " %" for x in TARGET_PERCENTS])
    #     ax.tick_params(axis = 'x', which = 'major', labelsize = XLABEL_SIZE)
    #     ax.tick_params(axis = 'y', which = 'major', labelsize = YLABEL_SIZE)    

    #     # 5. Legend
    #     plt.legend(loc = LEGEND_LOC, prop = {"size": LEGEND_SIZE} )
        
    #     # 6. Print plot
    #     plt.savefig("Accuracy/" + dataset_name.split("_")[0] + "_Precision" + ".pdf", bbox_inches = "tight", pad_inches = 0)
        
        
        
    ##################
    # Average
    ###################
        
    # Get dataset
    recg_f1s = []
    recg_precisions = []
    recg_recalls = []
    jxplain_f1s = []
    jxplain_precisions = []
    jxplain_recalls = []
    kreduce_f1s = []
    kreduce_precisions = []
    kreduce_recalls = []
    lreduce_f1s = []
    lreduce_precisions = []
    lreduce_recalls = []
    klettke_f1s = []
    klettke_precisions = []
    klettke_recalls = []
    frozza_f1s = []
    frozza_precisions = []
    frozza_recalls = []

    for target_percent in TARGET_PERCENTS:
        ReCG_f1,    ReCG_recall,    ReCG_precision    = getAccForAlgPerc("ReCG",      target_percent)
        jxplain_f1, jxplain_recall, jxplain_precision = getAccForAlgPerc("jxplain",   target_percent)
        kreduce_f1, kreduce_recall, kreduce_precision = getAccForAlgPerc("kreduce",   target_percent)
        lreduce_f1, lreduce_recall, lreduce_precision = getAccForAlgPerc("lreduce",   target_percent)
        klettke_f1, klettke_recall, klettke_precision = getAccForAlgPerc("klettke",   target_percent)
        frozza_f1,  frozza_recall,  frozza_precision  = getAccForAlgPerc("frozza",    target_percent)
        
        recg_f1s.append(ReCG_f1)
        recg_recalls.append(ReCG_recall)
        recg_precisions.append(ReCG_precision)
        jxplain_f1s.append(jxplain_f1)
        jxplain_recalls.append(jxplain_recall)
        jxplain_precisions.append(jxplain_precision)
        kreduce_f1s.append(kreduce_f1)
        kreduce_recalls.append(kreduce_recall)
        kreduce_precisions.append(kreduce_precision)
        lreduce_f1s.append(lreduce_f1)
        lreduce_recalls.append(lreduce_recall)
        lreduce_precisions.append(lreduce_precision)
        klettke_f1s.append(klettke_f1)
        klettke_recalls.append(klettke_recall)
        klettke_precisions.append(klettke_precision)
        frozza_f1s.append(frozza_f1)
        frozza_recalls.append(frozza_recall)
        frozza_precisions.append(frozza_precision)
        
    recg_f1s = [x if x != -1 else 0 for x in recg_f1s]
    recg_recalls = [x if x != -1 else 0 for x in recg_recalls]
    recg_precisions = [x if x != -1 else 0 for x in recg_precisions]
    recg_precisions = [x if x != -1 else 0 for x in recg_precisions]
    jxplain_f1s = [x if x != -1 else 0 for x in jxplain_f1s]
    jxplain_recalls = [x if x != -1 else 0 for x in jxplain_recalls]
    jxplain_precisions = [x if x != -1 else 0 for x in jxplain_precisions]
    kreduce_f1s = [x if x != -1 else 0 for x in kreduce_f1s]
    kreduce_recalls = [x if x != -1 else 0 for x in kreduce_recalls]
    kreduce_precisions = [x if x != -1 else 0 for x in kreduce_precisions]
    lreduce_f1s = [x if x != -1 else 0 for x in lreduce_f1s]
    lreduce_recalls = [x if x != -1 else 0 for x in lreduce_recalls]
    lreduce_precisions = [x if x != -1 else 0 for x in lreduce_precisions]
    klettke_f1s = [x if x != -1 else 0 for x in klettke_f1s]
    klettke_recalls = [x if x != -1 else 0 for x in klettke_recalls]
    klettke_precisions = [x if x != -1 else 0 for x in klettke_precisions]
    frozza_f1s = [x if x != -1 else 0 for x in frozza_f1s]
    frozza_recalls = [x if x != -1 else 0 for x in frozza_recalls]
    frozza_precisions = [x if x != -1 else 0 for x in frozza_precisions]
    
    
    ##############
    # F1
    ##############
    
    # 1. Initiate figure 
    fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
    
    # 2. Get dataset
    x_bar_start = np.arange(len(TARGET_PERCENTS))
    x_ticks = x_bar_start + BAR_WIDTH * NUM_ALGORITHMS / 2
    
    # 3. Plot
    ax.bar(x_bar_start,                  recg_f1s,    BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(1, NUM_ALGORITHMS), label = "ReCG")
    ax.bar(x_bar_start + BAR_WIDTH * 1,  jxplain_f1s, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(2, NUM_ALGORITHMS), label = "Jxplain")
    ax.bar(x_bar_start + BAR_WIDTH * 2,  kreduce_f1s, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(3, NUM_ALGORITHMS), label = "KReduce")
    ax.bar(x_bar_start + BAR_WIDTH * 3,  lreduce_f1s, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(4, NUM_ALGORITHMS), label = "LReduce")
    ax.bar(x_bar_start + BAR_WIDTH * 4,  klettke_f1s, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(5, NUM_ALGORITHMS), label = "Klettke")
    ax.bar(x_bar_start + BAR_WIDTH * 5,  frozza_f1s,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(6, NUM_ALGORITHMS), label = "Frozza")
    
    
    # 4. Set labels
    ax.set_ylim(0, YLIM)
    ax.set_yticks(YTICKS)
    ax.set_ylabel("F1 Score", fontsize = YLABEL_SIZE)
    ax.set_xlabel("Used data set proportion", fontsize = XLABEL_SIZE)    
    ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(x) + " %" for x in TARGET_PERCENTS])
    ax.tick_params(axis = 'x', which = 'major', labelsize = XTICK_SIZE)
    ax.tick_params(axis = 'y', which = 'major', labelsize = YTICK_SIZE)

    # 5. Legend
    # plt.legend(loc = LEGEND_LOC)
    
    # 6. Print plot
    plt.savefig("Accuracy/_Average_F1" + ".pdf", bbox_inches = "tight", pad_inches = 0)
    
    
    
    ##############
    # Recall
    ##############
    
    # 1. Initiate figure 
    fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
    
    # 2. Get dataset
    x_bar_start = np.arange(len(TARGET_PERCENTS))
    x_ticks = x_bar_start + BAR_WIDTH * NUM_ALGORITHMS / 2
    
    # 3. Plot
    ax.bar(x_bar_start,                  recg_recalls,    BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(1, NUM_ALGORITHMS), label = "ReCG")
    ax.bar(x_bar_start + BAR_WIDTH * 1,  jxplain_recalls, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(2, NUM_ALGORITHMS), label = "Jxplain")
    ax.bar(x_bar_start + BAR_WIDTH * 2,  kreduce_recalls, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(3, NUM_ALGORITHMS), label = "KReduce")
    ax.bar(x_bar_start + BAR_WIDTH * 3,  lreduce_recalls, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(4, NUM_ALGORITHMS), label = "LReduce")
    ax.bar(x_bar_start + BAR_WIDTH * 4,  klettke_recalls, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(5, NUM_ALGORITHMS), label = "Klettke")
    ax.bar(x_bar_start + BAR_WIDTH * 5,  frozza_recalls,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(6, NUM_ALGORITHMS), label = "Frozza")
    
    
    
    # 4. Set labels
    ax.set_ylim(0, YLIM)
    ax.set_yticks(YTICKS)
    ax.set_ylabel("Recall", fontsize = YLABEL_SIZE)
    ax.set_xlabel("Used data set proportion", fontsize = XLABEL_SIZE)
    ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(x) + " %" for x in TARGET_PERCENTS])
    ax.tick_params(axis = 'x', which = 'major', labelsize = XTICK_SIZE)
    ax.tick_params(axis = 'y', which = 'major', labelsize = YTICK_SIZE)

    # 5. Legend
    # plt.legend(loc = LEGEND_LOC)
    
    # 6. Print plot
    plt.savefig("Accuracy/_Average_Recall" + ".pdf", bbox_inches = "tight", pad_inches = 0)
    
    
    ##############
    # Precision
    ##############
    
    # 1. Initiate figure 
    fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
    
    # 2. Get dataset
    x_bar_start = np.arange(len(TARGET_PERCENTS))
    x_ticks = x_bar_start + BAR_WIDTH * NUM_ALGORITHMS / 2
    
    # 3. Plot
    ax.bar(x_bar_start,                  recg_precisions,    BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(1, NUM_ALGORITHMS), label = "ReCG")
    ax.bar(x_bar_start + BAR_WIDTH * 1,  jxplain_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(2, NUM_ALGORITHMS), label = "Jxplain")
    ax.bar(x_bar_start + BAR_WIDTH * 2,  kreduce_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(3, NUM_ALGORITHMS), label = "KReduce")
    ax.bar(x_bar_start + BAR_WIDTH * 3,  lreduce_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(4, NUM_ALGORITHMS), label = "LReduce")
    ax.bar(x_bar_start + BAR_WIDTH * 4,  klettke_precisions, BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(5, NUM_ALGORITHMS), label = "KSS")
    ax.bar(x_bar_start + BAR_WIDTH * 5,  frozza_precisions,  BAR_WIDTH, edgecolor = "black", linewidth = LINE_WIDTH, color = getColor(6, NUM_ALGORITHMS), label = "FMC")
    
    
    # 4. Set labels
    ax.set_ylim(0, YLIM)
    ax.set_yticks(YTICKS)
    ax.set_ylabel("Precision", fontsize = YLABEL_SIZE)
    ax.set_xlabel("Used data set proportion", fontsize = XLABEL_SIZE)    
    ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(x) + " %" for x in TARGET_PERCENTS])
    ax.tick_params(axis = 'x', which = 'major', labelsize = XTICK_SIZE)
    ax.tick_params(axis = 'y', which = 'major', labelsize = YTICK_SIZE)

    # 5. Legend
    plt.legend(loc = LEGEND_LOC, prop = {"size": LEGEND_SIZE} )
    
    # 6. Print plot
    plt.savefig("Accuracy/_Average_Precision" + ".pdf", bbox_inches = "tight", pad_inches = 0)



def getColor(num, max_num):
    target_num = int(num / max_num * 255)
    
    color = "#" + str(hex(target_num))[2:] + str(hex(target_num))[2:] + str(hex(target_num))[2:]
    # print(color)
    return color



if __name__ == "__main__":
    main((sys.argv)[1:])