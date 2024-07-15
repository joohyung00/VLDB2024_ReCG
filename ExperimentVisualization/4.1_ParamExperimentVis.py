import csv
import statistics
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import argparse
import sys
from pltUtils import dataset_nums, dataset_to_name
sys.path.insert(1, "/root/VLDB2024_ReCG/Experiment/utils")
from dataset_metadata import num_to_name
from aggregateExpResults import PARAM_EXP, getResultForPercParamDataset, getResultForPercParam



PARAM_EXP = {
    "exp_type": "Parameter",
    "result_path": "/root/VLDB2024_ReCG/Experiment/exp4_param.txt",
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


FILENAME = "/root/VLDB2024_ReCG/Experiment/exp_param.txt"

FIG_WIDTH = 6
FIG_HEIGHT = 2.5

XTICKS_SIZE = 16
YTICKS_SIZE = 10

LEGEND_SIZE = 14

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
    parser.add_argument("--exp", choices = ["BeamWidth", "Epsilon", "MinPtsPerc", "SampleSize", "MDLWeights"])
    
    args = parser.parse_args(argv)
    
    print(args)
    
    return args





def main(argv):
    
    args = parseArgumnets(argv)
    
    acc_train_perc = 10
    perf_train_percs = [40, 60, 80, 100]
    param_values = PARAM_EXP["param_name_to_values"][argExpToParamName(args.exp)]
    
    
    
    if args.exp == "BeamWidth": cvd = beam_width_cvd
    else:                       cvd = None

    # for dataset_num in dataset_nums:
        
    #     ################################################
    #     ############### Per-data Accuracy ###############
    #     ################################################
        
    #     # Per-data metadata
    #     dataset_name = dataset_to_name[dataset_num]
        
    #     # 1. Initiate figure
    #     font = {'size' : 14}
    #     matplotlib.rc('font', **font)
    #     fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
        
    #     # 2. Get dataset
    #     # 2. Get dataset
        
    #     x_bar_start = np.arange(len(param_values))
    #     bar_width = 0.27
    #     x_ticks = x_bar_start + bar_width * 2 / 2
        
    #     recalls = []
    #     precisions = []
    #     f1s = []
    #     for param_val in param_values:
            
    #         recall, precision, f1, _, _, _, _ = getResultForPercParamDataset(argExpToParamName(args.exp), acc_train_perc, param_val, dataset_name, cvd)
            
    #         recalls.append(recall)
    #         precisions.append(precision)
    #         f1s.append(f1)
            
    #     # 3. Plot

    #     ax.bar(x_bar_start,                  f1s,        bar_width, color = "black", edgecolor = "black", label = "F1")
    #     ax.bar(x_bar_start + bar_width,      recalls,    bar_width, color = "gray",  edgecolor = "black", label = "Recall")
    #     ax.bar(x_bar_start + 2 * bar_width,  precisions, bar_width, color = "white", edgecolor = "black", label = "Precision")
            
    #     # 4. Ticks and labels
    #         # ax.set_xticks(range(len(variances[1])))
    #     ax.set_xticks(x_ticks)
    #     ax.set_xticklabels(param_values)
    #     ax.set_ylabel('Accuracy')
    #     ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    #     ax.set_xlabel(argExpToXLabel(args.exp))
        
    #     # 5. Legend
    #     legend = ax.legend(loc = "lower right", fontsize = 11)
    #     legend.get_frame().set_alpha(1)
        
    #     # 6. Print plot
    #     plt.tight_layout()
    #     plt.savefig("Param/" + args.exp + "/" + dataset_name.split("_")[0] + "_Accuracy.pdf", bbox_inches = "tight", pad_inches = 0)
        
        
        
        
    #     ############################################
    #     ############### Per-data MDL ###############
    #     ############################################
        
    #     # # Per-data metadata
    #     # dataset_name = dataset_to_name[dataset_num]
        
    #     # # 1. Initiate figure
    #     # font = {'size' : 14}
    #     # matplotlib.rc('font', **font)
    #     # fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
        
    #     # # 2. Get dataset
    #     # # 2. Get dataset
        
    #     # x_bar_start = np.arange(len(param_values))
    #     # bar_width = 0.27
    #     # x_ticks = x_bar_start + bar_width * 1 / 2
        
    #     # srcs = []
    #     # drcs = []
    #     # for param_val in param_values:
            
    #     #     _, _, _, _, src, drc, _ = getResultForPercParamDataset(argExpToParamName(args.exp), acc_train_perc, param_val, dataset_name, cvd)
            
    #     #     srcs.append(src)
    #     #     drcs.append(drc)
            
    #     # # 3. Plot

    #     # ax.bar(x_bar_start,                  srcs,      bar_width, color = "black", edgecolor = "black", label = "SRC")
    #     # ax.bar(x_bar_start + 1 * bar_width,  drcs,      bar_width, color = "white", edgecolor = "black", label = "DRC")
            
    #     # # 4. Ticks and labels
    #     #     # ax.set_xticks(range(len(variances[1])))
    #     # ax.set_xticks(x_ticks)
    #     # ax.set_xticklabels(param_values)
    #     # ax.set_ylabel('Representation Cost')
    #     # ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    #     # ax.set_xlabel(argExpToXLabel(args.exp))
        
    #     # # 5. Legend
    #     # legend = ax.legend(loc = "lower right", fontsize = 11)
    #     # legend.get_frame().set_alpha(1)
        
    #     # # 6. Print plot
    #     # plt.tight_layout()
    #     # plt.savefig("Param/" + args.exp + "/" + dataset_name.split("_")[0] + "_MDL.pdf", bbox_inches = "tight", pad_inches = 0)
        
        
    #     ################################################
    #     ############### Per-data Runtime ###############
    #     ################################################
        
    #     # 1. Initiate Figure
    #     height = 2.7
    #     fig, ax = plt.subplots(figsize = (FIG_WIDTH, height))
            
    #     # 2. Generate dataset
    #     x_ = np.arange(len(param_values))
    #     colors = ['royalblue', 'dodgerblue', 'deepskyblue', 'skyblue', 'mediumblue', 'darkblue']
    #     for i, train_perc in enumerate(perf_train_percs):
    #         runtime_per_param = []
    #         for param_val in param_values:
    #             _, _, _, runtime, _, _, _ = getResultForPercParamDataset(argExpToParamName(args.exp), train_perc, param_val, dataset_name, cvd)
    #             runtime_per_param.append(runtime)
    #         ax.plot(x_, runtime_per_param, marker = "^", label=f"{train_perc}%", color = colors[i])

    #     # 4. Ticks and labels
    #     ax.set_xticks(ticks = x_, labels = param_values)
    #     ax.set_xlabel(argExpToXLabel(args.exp))
    #     ax.tick_params(axis='x', which='major', labelsize = 12)
    #     ax.set_ylabel('Algorithm runtime (ms)')
    #     ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
        
    #     # 5. Legend
    #     if "Helm" not in dataset_name:  
    #         legend = ax.legend(loc='upper left', fontsize = 11)
    #     else:
    #         legend = ax.legend(loc='upper center', fontsize = 11)
    #     legend.get_frame().set_alpha(1)
    #     plt.tight_layout()
        
    #     # 6. Print plot
    #     plt.savefig("Param/" + args.exp + "/" + dataset_name.split("_")[0] + "_Performance.pdf", bbox_inches = "tight", pad_inches = 0)

        
        
        
        
        
        
        
        
        
    ################################################
    ############### Average Accuracy ###############
    ################################################
        
    # 1. Initiate figure
    fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
    
    # 2. Generate dataset
    x_bar_start = np.arange(len(param_values))
    if args.exp == "BeamWidth":
        bar_width = 0.22
    else:
        bar_width = 0.3
    if args.exp == "BeamWidth":
        x_ticks = x_bar_start + bar_width * 3 / 2
    else:
        x_ticks = x_bar_start + bar_width * 2 / 2
    recalls = []
    precisions = []
    f1s = []
    
    deinconfig_f1s = []
    deinconfig_barwidth = 0.15
    deinconfig_bar_start = x_bar_start + (bar_width * 0.5) - (deinconfig_barwidth)
    
    for param_val in param_values:
        recall, precision, f1, _, _, _, _ = getResultForPercParam(argExpToParamName(args.exp), acc_train_perc, param_val, cvd)
        if args.exp == "BeamWidth":
            _, _, deinconfig_f1, _, _, _, _ = getResultForPercParamDataset("beam_width", acc_train_perc, param_val, "41_DeinConfig", cvd)
            deinconfig_f1s.append(deinconfig_f1)
        recalls.append(recall)
        precisions.append(precision)
        f1s.append(f1)
    
    # 3. Plot
    plt.bar(x_bar_start,                  f1s,        bar_width,  color = "black", edgecolor = "black", label = "F1")
    if args.exp == "BeamWidth":
        plt.bar(x_bar_start + bar_width , deinconfig_f1s, bar_width, color = "white", edgecolor = "black", hatch = "///", capsize = 10, label = "F1 (DeinConfig)")
        plt.bar(x_bar_start + bar_width * 2,      recalls,    bar_width,  color = "gray",  edgecolor = "black", label = "Recall")
        plt.bar(x_bar_start + bar_width * 3,  precisions, bar_width,  color = "white", edgecolor = "black", label = "Precision")
    else:
        plt.bar(x_bar_start + bar_width,      recalls,    bar_width,  color = "gray",  edgecolor = "black", label = "Recall")
        plt.bar(x_bar_start + bar_width * 2,  precisions, bar_width,  color = "white", edgecolor = "black", label = "Precision")
    
    # print(recalls)
    # print(precisions)
    # print(f1s)
    
    
    # 4. Ticks and Labels
    plt.xlabel("Algorithm", fontsize = 16)
    ax.set_xlabel(argExpToXLabel(args.exp))
    if args.exp == "MDLWeights":
        x_tick_labels = ["1:99", "1:9", "3:7", "5:5", "7:3", "9:1", "99:1"]
    else:
        x_tick_labels = param_values
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels)
    plt.ylabel("Accuracy", fontsize = 16)
    plt.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    ax.tick_params(axis = 'x', which = 'major', labelsize = XTICKS_SIZE)
    ax.tick_params(axis = 'y', which = 'major', labelsize = YTICKS_SIZE)
    
    # 5. Legend
    if args.exp == "MDLWeights":
        legend = plt.legend(loc = "lower left", prop = {"size": LEGEND_SIZE} )
        legend.get_frame().set_alpha(1)
    if args.exp == "BeamWidth":
        legend = plt.legend(loc = "lower right", prop = {"size": 0.8 * LEGEND_SIZE} )
        legend.get_frame().set_alpha(1)
    plt.tight_layout()
    
    # 6. Print plot
    plt.savefig("Param/" + args.exp + "/_Average_Accuracy.pdf", bbox_inches = "tight", pad_inches = 0)

        
    
    
    ############################################
    ############### Average MDL ###############
    ############################################
    
    # # Per-data metadata
   
    # 1. Initiate figure
    font = {'size' : 14}
    matplotlib.rc('font', **font)
    fig, ax = plt.subplots(figsize = (FIG_WIDTH, FIG_HEIGHT))
    
    # 2. Get dataset
    
    x_bar_start = np.arange(len(param_values))
    bar_width = 0.27
    x_ticks = x_bar_start + bar_width * 1 / 2
    
    srcs = []
    drcs = []
    for param_val in param_values:
        
        _, _, _, _, src, drc, _ = getResultForPercParam(argExpToParamName(args.exp), acc_train_perc, param_val, cvd)
        
        # print("SRC: ", src)
        # print("DRC: ", drc)
        
        srcs.append(src)
        drcs.append(drc)
        
    # 3. Plot

    ax.bar(x_bar_start,                  srcs,      bar_width, color = "black", edgecolor = "black", label = "SRC")
    ax.bar(x_bar_start + 1 * bar_width,  drcs,      bar_width, color = "white", edgecolor = "black", label = "DRC")
        
    # 4. Ticks and labels
        # ax.set_xticks(range(len(variances[1])))
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(param_values)
    ax.set_ylabel('Representation Cost')
    ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    ax.set_xlabel(argExpToXLabel(args.exp))
    
    # 5. Legend
    legend = ax.legend(loc = "lower right", fontsize = 11)
    legend.get_frame().set_alpha(1)
    
    # 6. Print plot
    plt.tight_layout()
    plt.savefig("Param/" + args.exp + "/_Average_MDL.pdf", bbox_inches = "tight", pad_inches = 0)
    




    ############### Average Runtime ###############

    # 1. Initiate figure
    width = 6
    height = 3.60
    fig, ax = plt.subplots(figsize = (width, height))
    
    # 2. Generate dataset
    colors = ['royalblue', 'dodgerblue', 'deepskyblue', 'skyblue', 'mediumblue', 'darkblue']
    x_ = np.arange(len(param_values))
    


    for i, train_perc in enumerate(perf_train_percs):
        runtime_per_param = []
        for param_val in param_values:
            _, _, _, runtime, _, _, _ = getResultForPercParam(argExpToParamName(args.exp), train_perc, param_val, cvd)
            runtime_per_param.append(runtime)
        ax.plot(x_, runtime_per_param, marker = "^", label = f"{train_perc}%", color = colors[i])
        
            
    # 4. Ticks and labels
    if args.exp == "MDLWeights":
        x_tick_labels = ["1:99", "1:9", "3:7", "5:5", "7:3", "9:1", "99:1"]
    else:
        x_tick_labels = param_values
    
    plt.xticks(ticks = x_, labels = x_tick_labels)
    plt.ylabel('Algorithm runtime (ms)')
    ax.tick_params(axis = 'x', which='major', labelsize = 12)
    ax.ticklabel_format(axis = 'y', style = 'sci', scilimits = (0, 0))
    ax.set_xlabel(argExpToXLabel(args.exp))
    
    # 5. Legend
    legend = plt.legend(loc='upper left', fontsize = 11)
    legend.get_frame().set_alpha(1)

    # 6. Print plot
    plt.savefig("Param/" + args.exp + "/_Average_Performance.pdf", bbox_inches = "tight", pad_inches = 0)





    return











def argExpToParamName(exp):
    if exp == "BeamWidth":
        return "beam_width"
    elif exp == "Epsilon":
        return "epsilon"
    elif exp == "MinPtsPerc":
        return "min_pts_perc"
    elif exp == "SampleSize":
        return "sample_size"
    elif exp == "MDLWeights":
        return "mdl_weights"
    else: raise ValueError("Unknown exp type")
    
def argExpToXLabel(exp):
    if exp == "BeamWidth":
        return "Beam Width"
    elif exp == "Epsilon":
        return "Epsilon"
    elif exp == "MinPtsPerc":
        return "MinPoints Percentage"
    elif exp == "SampleSize":
        return "Sample size"
    elif exp == "MDLWeights":
        return "MDL Weights (SRC : DRC)"
    else: raise ValueError("Unknown exp type")
    
    
    
    
    
    
    

if __name__ == "__main__":
    main((sys.argv)[1:])
