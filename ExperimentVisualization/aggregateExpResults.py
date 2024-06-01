from contextlib import nullcontext
import numpy as np
import csv
import statistics

import sys
sys.path.insert(1, '/root/JsonExplorerSpark/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames, possible_algorithms_list

from itertools import product

F1IDX = 0
RECALLIDX = 1
PRECISIONIDX = 2
SRCIDX = 0
DRCIDX = 1
MDLIDX = 2

RECALL = 10
PRECISION = 11
F1 = 12
RUNTIME = 13



RESULTS = {}


ACC_EXP = {
    "result_path": "/root/JsonExplorerSpark/Experiment/exp1_accuracy.txt", # HERE
    # "result_path": "/root/JsonExplorerSpark/Experiment/exp1_accuracy_2.txt", # HERE
    "algorithms": ["ReCG", "ReCG(TopDown)", "ReCG(KSE)", "jxplain", "kreduce", "lreduce", "klettke", "frozza"],
    "train_percs" : [1, 10, 50, 90],
    "dataset_names" : dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
ACC2_EXP = {
    "result_path": "/root/JsonExplorerSpark/Experiment/exp1_accuracy_2.txt",
    "algorithms": ["ReCG"],
    "train_percs" : [1, 10, 50, 90],
    "dataset_names" : dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
MDL_EXP = {
    "exp_type": "MDL",
    "result_path": "/root/JsonExplorerSpark/Experiment/exp2_mdl.txt",
    "algorithms": ["ReCG", "jxplain", "kreduce", "lreduce", "klettke", "frozza", "groundtruth"],
    "train_percs" : [10],
    "dataset_names" : dataset_fullnames,
    "exp_nums" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
PERF_EXP = {
    "exp_type": "Performance",
    "result_path": "/root/JsonExplorerSpark/Experiment/exp3_runtime.txt",
    "algorithms": ["ReCG", "jxplain", "kreduce", "lreduce", "klettke", "frozza"],
    "train_percs" : [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    "dataset_names": dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}    
MEMORY_EXP = {
    "exp_type": "MemoryUsage",
    "result_path": "/root/JsonExplorerSpark/Experiment/exp3_memory.txt",
    "algorithms": ["ReCG", "jxplain", "kreduce", "lreduce", "klettke", "frozza"],
    "train_percs" : [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    "dataset_names": dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
PARAM_EXP = {
    "exp_type": "Parameter",
    "result_path": "/root/JsonExplorerSpark/Experiment/exp4_param.txt",
    "train_percs" : [10, 40, 50, 60, 80, 90, 100],
    
    "param_name_to_values": {
        "beam_width": [1, 2, 3, 4, 5],
        "epsilon": [0.1, 0.3, 0.5, 0.7, 0.9],
        "min_pts_perc": [1, 3, 5, 10, 20, 30, 90],
        "sample_size": [25, 30, 50, 100, 250, 500, 1000, 2000],
        "mdl_weights": [(0.01, 0.99), (0.1, 0.9), (0.3, 0.7), (0.5, 0.5), (0.7, 0.3), (0.9, 0.1), (0.99, 0.01)],
    },
    "param_name_to_default_value": {
        "beam_width": 3,
        "epsilon": 0.5,
        "min_pts_perc": 5,
        "sample_size": 500,
        "mdl_weights": (0.5, 0.5)
    },
    
    "dataset_names": dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}  





WEIGHTEDMDL_EXP = {
    "exp_type": "WeightedMDL",
    "result_path": "/root/JsonExplorerSpark/Experiment/exp6_weightedmdl.txt",
    "train_percs" : [10, 50, 90],
    "mdl_weights": [(0.01, 0.99), (0.1, 0.9), (0.3, 0.7), (0.5,0.5), (0.7, 0.3), (0.9, 0.1), (0.99, 0.01)],
    "dataset_names": dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
PARAM_FOR_BEAM_SEARCH_EXP = {
    "exp_type": "Parameter",
    "result_path": "/root/JsonExplorerSpark/Experiment/exp4_param_beamsearch.txt",
    "train_percs" : [10],
    
    "param_name_to_values": {
        "beam_width": [1, 2, 3, 4, 5],
        "epsilon": [0.1, 0.3, 0.9],
        "min_pts_perc": [1, 30, 90],
        "sample_size": [30, 500],
        "mdl_weights": [(0.01, 0.99), (0.99, 0.01)]
    },
    
    "dataset_names": dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}  


















































##########################################################################################
##########################################################################################
# ACCURACY                                                                               #
##########################################################################################
##########################################################################################
# recall : [algorithms, [1, 10, 50, 90], dataset_ids, exp_nums]
# precision : [algorithms, [1, 10, 50, 90], dataset_ids, exp_nums]
# f1 : [algorithms, [1, 10, 50, 90], dataset_ids, exp_nums]

def initiateAccResults():
    
    def fillEntry(algorithms, train_percs, dataset_ids, exp_nums, f1_results, recall_results, precision_results, mainfile):

        with open(mainfile, newline='') as f:
            for s in csv.reader(f):
                if not s:
                    continue
                algo_name = s[0]
                data_name = s[1]
                train_percent = int(s[2])
                exp_num = int(s[3])
                
                if "nan" in s[4]: recall = 0
                elif s[4] == "": recall = 0
                else: recall = float(s[4])
                
                if "nan" in s[5]: precision = 0
                elif s[5] == "": recall = 0
                else: precision = float(s[5])
                
                if "nan" in s[6]: f1 = 0
                elif s[6] == "": recall = 0
                else: f1 = float(s[6])
                
                alg_idx = algorithms.index(algo_name)
                train_idx = train_percs.index(train_percent)
                try: data_idx = dataset_ids.index(data_name)
                except ValueError: continue
                try: exp_idx = exp_nums.index(exp_num)
                except ValueError: continue
                
                f1_results[alg_idx][train_idx][data_idx][exp_idx] = f1
                recall_results[alg_idx][train_idx][data_idx][exp_idx] = recall
                precision_results[alg_idx][train_idx][data_idx][exp_idx] = precision
                
    # 1. Define metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getF1Metadata()
    
    # 2. Initialize results
    f1_results          = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)
    recall_results      = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)
    precision_results   = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)

    # 3. Read results from file
    fillEntry(algorithms, train_percs, dataset_ids, exp_nums, f1_results, recall_results, precision_results, file_path)
            
    RESULTS["1_recall"] = recall_results
    RESULTS["1_precision"] = precision_results
    RESULTS["1_f1"] = f1_results


    
def getF1Metadata():
    return ACC_EXP["result_path"],  ACC_EXP["algorithms"], ACC_EXP["train_percs"], ACC_EXP["dataset_names"], ACC_EXP["exp_nums"]


def getAccForAlgPercDatasetExpnum(algorithm, train_perc, dataset_name, exp_num):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    # exp_num : int
    
    # 1. Initiate if needed
    if "1_f1" not in RESULTS:
        initiateAccResults()
        
    # 2. Get metadata
    _, algorithms, train_percs, dataset_names, exp_nums = getF1Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_idx = train_percs.index(train_perc)
    data_idx = dataset_names.index(dataset_name)
    exp_idx = exp_nums.index(exp_num)
    
    # 4. Fetch result
    f1 = RESULTS["1_f1"][alg_idx][train_idx][data_idx][exp_idx]
    recall = RESULTS["1_recall"][alg_idx][train_idx][data_idx][exp_idx]
    precision = RESULTS["1_precision"][alg_idx][train_idx][data_idx][exp_idx]
    
    # 5. Return results
    return f1, recall, precision

def getAccForAlgPercDataset(algorithm, train_perc, dataset_name):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    
    # 1. Initiate if needed
    if "1_f1" not in RESULTS:
        initiateAccResults()
        
    # 2. Get metadata
    _, algorithms, train_percs, dataset_names, _ = getF1Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    data_idx = dataset_names.index(dataset_name)
    
    target_idx = (alg_idx, train_perc_idx, data_idx)
    
    # 4. Fetch results
    f1s = RESULTS["1_f1"][target_idx]
    recalls = RESULTS["1_recall"][target_idx]
    precisions = RESULTS["1_precision"][target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_f1 = mean_except_minus1(f1s)
    non_m1_recall = mean_except_minus1(recalls)
    non_m1_precision = mean_except_minus1(precisions)
    
    non_m1_f1_stdev = stdev_except_minus1(f1s)
    non_m1_recall_stdev = stdev_except_minus1(recalls)
    non_m1_precision_stdev = stdev_except_minus1(precisions)
    
        
    # 5. Return results
    return non_m1_f1, non_m1_f1_stdev, non_m1_recall, non_m1_recall_stdev, non_m1_precision, non_m1_precision_stdev



def getAccForAlgPerc(algorithm, train_perc):
    # algorithm : str
    # train_perc : int
    
    # 1. Initiate if needed
    if "1_f1" not in RESULTS:
        initiateAccResults()
        
    # 2. Get metadata
    _, algorithms, train_percs, _, _ = getF1Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    
    target_idx = (alg_idx, train_perc_idx)
    
    # 4. Fetch results
    f1s = RESULTS["1_f1"][target_idx]
    recalls = RESULTS["1_recall"][target_idx]
    precisions = RESULTS["1_precision"][target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_f1 = mean_except_minus1(f1s)
    non_m1_recall = mean_except_minus1(recalls)
    non_m1_precision = mean_except_minus1(precisions)
    
        
    # 5. Return results
    return non_m1_f1, non_m1_recall, non_m1_precision

def getAccForAlg(algorithm):
    # algorithm : str
    
    # 1. Initiate if needed
    if "1_f1" not in RESULTS:
        initiateAccResults()
        
    # 2. Get metadata
    _, algorithms, _, _, _ = getF1Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    
    target_idx = (alg_idx)
    
    # 4. Fetch results
    f1s = RESULTS["1_f1"][target_idx]
    recalls = RESULTS["1_recall"][target_idx]
    precisions = RESULTS["1_precision"][target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_f1 = mean_except_minus1(f1s)
    non_m1_recall = mean_except_minus1(recalls)
    non_m1_precision = mean_except_minus1(precisions)

        
    # 5. Return results
    return non_m1_f1, non_m1_recall, non_m1_precision




































def initiateAcc2Results():
    

    # 1. Define metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getF12Metadata()
    
    # 2. Initialize results
    f1_results          = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)
    recall_results      = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)
    precision_results   = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)

    # 3. Read results from file
    with open(file_path, newline='') as f:
        for s in csv.reader(f):
            if not s:
                continue
            algo_name = s[0]
            data_name = s[1]
            train_percent = int(s[2])
            exp_num = int(s[3])
            
            if "nan" in s[4]: recall = 0
            elif s[4] == "": recall = 0
            else: recall = float(s[4])
            
            if "nan" in s[5]: precision = 0
            elif s[5] == "": recall = 0
            else: precision = float(s[5])
            
            if "nan" in s[6]: f1 = 0
            elif s[6] == "": recall = 0
            else: f1 = float(s[6])
            
            alg_idx = algorithms.index(algo_name)
            train_idx = train_percs.index(train_percent)
            try: data_idx = dataset_ids.index(data_name)
            except ValueError: continue
            try: exp_idx = exp_nums.index(exp_num)
            except ValueError: continue
            
            f1_results[alg_idx][train_idx][data_idx][exp_idx] = f1
            recall_results[alg_idx][train_idx][data_idx][exp_idx] = recall
            precision_results[alg_idx][train_idx][data_idx][exp_idx] = precision
            
    RESULTS["1_recall2"] = recall_results
    RESULTS["1_precision2"] = precision_results
    RESULTS["1_f12"] = f1_results


    
def getF12Metadata():
    return ACC2_EXP["result_path"],  ACC2_EXP["algorithms"], ACC2_EXP["train_percs"], ACC2_EXP["dataset_names"], ACC2_EXP["exp_nums"]


def getAcc2ForAlgPercDatasetExpnum(algorithm, train_perc, dataset_name, exp_num):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    # exp_num : int
    
    # 1. Initiate if needed
    if "1_f12" not in RESULTS:
        initiateAcc2Results()
        
    # 2. Get metadata
    _, algorithms, train_percs, dataset_names, exp_nums = getF12Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_idx = train_percs.index(train_perc)
    data_idx = dataset_names.index(dataset_name)
    exp_idx = exp_nums.index(exp_num)
    
    # 4. Fetch result
    f1 = RESULTS["1_f12"][alg_idx][train_idx][data_idx][exp_idx]
    recall = RESULTS["1_recall2"][alg_idx][train_idx][data_idx][exp_idx]
    precision = RESULTS["1_precision2"][alg_idx][train_idx][data_idx][exp_idx]
    
    # 5. Return results
    return f1, recall, precision

def getAcc2ForAlgPercDataset(algorithm, train_perc, dataset_name):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    
    # 1. Initiate if needed
    if "1_f12" not in RESULTS:
        initiateAcc2Results()
        
    # 2. Get metadata
    _, algorithms, train_percs, dataset_names, _ = getF12Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    data_idx = dataset_names.index(dataset_name)
    
    target_idx = (alg_idx, train_perc_idx, data_idx)
    
    # 4. Fetch results
    f1s = RESULTS["1_f12"][target_idx]
    recalls = RESULTS["1_recall2"][target_idx]
    precisions = RESULTS["1_precision2"][target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_f1 = mean_except_minus1(f1s)
    non_m1_recall = mean_except_minus1(recalls)
    non_m1_precision = mean_except_minus1(precisions)
    
    non_m1_f1_stdev = stdev_except_minus1(f1s)
    non_m1_recall_stdev = stdev_except_minus1(recalls)
    non_m1_precision_stdev = stdev_except_minus1(precisions)
    
        
    # 5. Return results
    return non_m1_f1, non_m1_f1_stdev, non_m1_recall, non_m1_recall_stdev, non_m1_precision, non_m1_precision_stdev



def getAcc2ForAlgPerc(algorithm, train_perc):
    # algorithm : str
    # train_perc : int
    
    # 1. Initiate if needed
    if "1_f12" not in RESULTS:
        initiateAcc2Results()
        
    # 2. Get metadata
    _, algorithms, train_percs, _, _ = getF12Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    
    target_idx = (alg_idx, train_perc_idx)
    
    # 4. Fetch results
    f1s = RESULTS["1_f12"][target_idx]
    recalls = RESULTS["1_recall2"][target_idx]
    precisions = RESULTS["1_precision2"][target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_f1 = mean_except_minus1(f1s)
    non_m1_recall = mean_except_minus1(recalls)
    non_m1_precision = mean_except_minus1(precisions)
    
        
    # 5. Return results
    return non_m1_f1, non_m1_recall, non_m1_precision

def getAcc2ForAlg(algorithm):
    # algorithm : str
    
    # 1. Initiate if needed
    if "1_f12" not in RESULTS:
        initiateAcc2Results()
        
    # 2. Get metadata
    _, algorithms, _, _, _ = getF12Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    
    target_idx = (alg_idx)
    
    # 4. Fetch results
    f1s = RESULTS["1_f12"][target_idx]
    recalls = RESULTS["1_recall2"][target_idx]
    precisions = RESULTS["1_precision2"][target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_f1 = mean_except_minus1(f1s)
    non_m1_recall = mean_except_minus1(recalls)
    non_m1_precision = mean_except_minus1(precisions)

        
    # 5. Return results
    return non_m1_f1, non_m1_recall, non_m1_precision
    







































##########################################################################################
##########################################################################################
# MDL                                                                                    #
##########################################################################################
##########################################################################################
# src : [algorithms (with groundtruth), [10], dataset_ids, exp_nums]
# drc : [algorithms (with groundtruth), [10], dataset_ids, exp_nums]

def initiateMDLResults():
    
    # 1. Define metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getMDLMetadata()
    
    # 2. Initialize results
    src_results = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)
    drc_results = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)

    # 3. Read results from file
    with open(file_path, newline='') as f:
        for s in csv.reader(f):

            if not s:
                continue
            algo_name = s[0]
            data_name = s[1]
            train_percent = int(s[2])
            exp_num = int(s[3])
            src = float(s[4])
            drc = float(s[5])
            
            alg_idx = algorithms.index(algo_name)
            train_idx = train_percs.index(train_percent)
            data_idx = dataset_ids.index(data_name)
            exp_idx = exp_nums.index(exp_num)
            
            src_results[alg_idx][train_idx][data_idx][exp_idx] = src
            drc_results[alg_idx][train_idx][data_idx][exp_idx] = drc
            
    RESULTS["2_src"] = src_results
    RESULTS["2_drc"] = drc_results
    
def getMDLMetadata():
    return MDL_EXP["result_path"], MDL_EXP["algorithms"], MDL_EXP["train_percs"], MDL_EXP["dataset_names"], MDL_EXP["exp_nums"]


def getMDLForAlgPercDatasetExpnum(algorithm, train_perc, dataset_name, exp_num):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    # exp_num : int
    
    # 1. Initiate if needed
    if "2_src" not in RESULTS:
        initiateMDLResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getMDLMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_idx = train_percs.index(train_perc)
    data_idx = dataset_ids.index(dataset_name)
    exp_idx = exp_nums.index(exp_num)
    
    # 4. Fetch result
    src = RESULTS["2_src"][alg_idx][train_idx][data_idx][exp_idx]
    drc = RESULTS["2_drc"][alg_idx][train_idx][data_idx][exp_idx]
    mdl = src + drc
    if mdl == -2:  mdl = -1
    
    # 5. Return results
    return src, drc, mdl

def getMDLForAlgPercDataset(algorithm, train_perc, dataset_name):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    
    # 1. Initiate if needed
    if "2_src" not in RESULTS:
        initiateMDLResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getMDLMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    data_idx = dataset_ids.index(dataset_name)
    
    target_idx = (alg_idx, train_perc_idx, data_idx)
    
    # 4. Fetch results
    srcs = RESULTS["2_src"][target_idx]
    drcs = RESULTS["2_drc"][target_idx]
    
    # 5. Calcualte non-(-1) mean
    src_mean = mean_except_minus1(srcs)
    drc_mean = mean_except_minus1(drcs)
    mdl_mean = src_mean + drc_mean
    if mdl_mean == -2:  mdl_mean = -1
        
    # 5. Return results
    return src_mean, drc_mean, mdl_mean


def getMDLForAlgPerc(algorithm, train_perc):
    # algorithm : str
    # train_perc : int
    
    # 1. Initiate if needed
    if "2_src" not in RESULTS:
        initiateMDLResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_names, exp_nums = getMDLMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    
    target_idx = (alg_idx, train_perc_idx)
    
    # 4. Fetch results
    srcs = RESULTS["2_src"][target_idx]
    drcs = RESULTS["2_drc"][target_idx]
    
    # 5. Calcualte non-(-1) mean
    src_mean = mean_except_minus1(srcs)
    drc_mean = mean_except_minus1(drcs)
    mdl_mean = src_mean + drc_mean
    if mdl_mean == -2:  mdl_mean = -1
    
    return src_mean, drc_mean, mdl_mean


















    

































##########################################################################################
##########################################################################################
# Performance                                                                            #
##########################################################################################
##########################################################################################
# runtime : [algorithms, [10, 20, ..., 100], dataset_ids, exp_nums]


def initiateRuntimeResults():
    
    # 1. Define metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getPerfMetadata()
    
    # 2. Initialize results
    runtime_results = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)

    # 3. Read results from file
    with open(file_path, newline='') as f:
        for s in csv.reader(f):

            if not s:
                continue
            algo_name = s[0]
            data_name = s[1]
            train_percent = int(s[2])
            exp_num = int(s[3])
            try:
                runtime = float(s[4])
            except ValueError:
                runtime = -1
            
            alg_idx = algorithms.index(algo_name)
            train_idx = train_percs.index(train_percent)
            data_idx = dataset_ids.index(data_name)
            exp_idx = exp_nums.index(exp_num)
            
            runtime_results[alg_idx][train_idx][data_idx][exp_idx] = runtime
            
    RESULTS["3_runtime"] = runtime_results

    
def getPerfMetadata():
    return PERF_EXP["result_path"], PERF_EXP["algorithms"], PERF_EXP["train_percs"], PERF_EXP["dataset_names"], PERF_EXP["exp_nums"]


def getRuntimeForAlgPercDatasetExpnum(algorithm, train_perc, dataset_name, exp_num):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    # exp_num : int
    
    # 1. Initiate if needed
    if "3_runtime" not in RESULTS:
        initiateRuntimeResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getPerfMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_idx = train_percs.index(train_perc)
    data_idx = dataset_ids.index(dataset_name)
    exp_idx = exp_nums.index(exp_num)
    
    # 4. Fetch result
    runtime = RESULTS["3_runtime"][alg_idx][train_idx][data_idx][exp_idx]
    
    # 5. Return results
    return runtime

def getRuntimeForAlgPercDataset(algorithm, train_perc, dataset_name):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    
    # 1. Initiate if needed
    if "3_runtime" not in RESULTS:
        initiateRuntimeResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getPerfMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    data_idx = dataset_ids.index(dataset_name)
    
    target_idx = (alg_idx, train_perc_idx, data_idx)
    
    # 4. Fetch results
    runtime = RESULTS["3_runtime"][target_idx]

    # 5. Calculate non-(-1) mean
    runtime_mean = mean_except_minus1(runtime)
    
    return runtime_mean


def getRuntimeForAlgPerc(algorithm, train_perc):
    # algorithm : str
    # train_perc : int
    
    # 1. Initiate if needed
    if "3_runtime" not in RESULTS:
        initiateRuntimeResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_names, exp_nums = getPerfMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    
    target_idx = (alg_idx, train_perc_idx)
    
    # 4. Fetch results
    runtime = RESULTS["3_runtime"][target_idx]
    
    # 5. Calculate non-(-1) mean
    runtime_mean = mean_except_minus1(runtime)
    runtime_stdev = stdev_except_minus1(runtime)
    
    return runtime_mean, runtime_stdev


































    














##########################################################################################
##########################################################################################
# Memory Usage                                                                           #
##########################################################################################
##########################################################################################
# memory usage : algorithm, dataset_fullname, train_perc, exp_num, memory_usage


def initiateMemoryUsageResults():
    
    # 1. Define metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getMemoryUsageMetadata()
    
    # 2. Initialize results
    memory_results = np.full( (len(algorithms), len(train_percs), len(dataset_ids), len(exp_nums)), -1, dtype = float)

    # 3. Read results from file
    with open(file_path, newline='') as f:
        for s in csv.reader(f):

            if not s:
                continue
            algo_name = s[0]
            data_name = s[1]
            train_percent = int(s[2])
            exp_num = int(s[3])
            try:
                memory_used = float(s[4])
            except ValueError:
                memory_used = -1
            
            alg_idx = algorithms.index(algo_name)
            train_idx = train_percs.index(train_percent)
            data_idx = dataset_ids.index(data_name)
            exp_idx = exp_nums.index(exp_num)
            
            memory_results[alg_idx][train_idx][data_idx][exp_idx] = memory_used
            
    RESULTS["5_memory"] = memory_results

    
    
def getMemoryUsageMetadata():
    return MEMORY_EXP["result_path"], MEMORY_EXP["algorithms"], MEMORY_EXP["train_percs"], MEMORY_EXP["dataset_names"], MEMORY_EXP["exp_nums"]


def getMemoryForAlgPercDatasetExpnum(algorithm, train_perc, dataset_name, exp_num):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    # exp_num : int

    # 1. Initiate if needed
    if "5_memory" not in RESULTS:
        initiateMemoryUsageResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getMemoryUsageMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_idx = train_percs.index(train_perc)
    data_idx = dataset_ids.index(dataset_name)
    exp_idx = exp_nums.index(exp_num)
    
    # 4. Fetch result
    memory = RESULTS["5_memory"][alg_idx][train_idx][data_idx][exp_idx]
    
    # 5. Return results
    return memory

def getMemoryForAlgPercDataset(algorithm, train_perc, dataset_name):
    # algorithm : str
    # train_perc : int
    # dataset_id : str
    
    # 1. Initiate if needed
    if "5_memory" not in RESULTS:
        initiateMemoryUsageResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getMemoryUsageMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    data_idx = dataset_ids.index(dataset_name)
    
    target_idx = (alg_idx, train_perc_idx, data_idx)
    
    # 4. Fetch results
    memory = RESULTS["5_memory"][target_idx]
    
    # 5. Calculate non-(-1) mean
    memory_mean = mean_except_minus1(memory)
    
    return memory_mean


def getMemoryForAlgPerc(algorithm, train_perc):
    # algorithm : str
    # train_perc : int
    
    # 1. Initiate if needed
    if "5_memory" not in RESULTS:
        initiateMemoryUsageResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_names, exp_nums = getMemoryUsageMetadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    
    target_idx = (alg_idx, train_perc_idx)
    
    # 4. Fetch results
    memory = RESULTS["5_memory"][target_idx]
    
    # 5. Calculate non-(-1) mean
    memory_mean = mean_except_minus1(memory)
    memory_stdev = stdev_except_minus1(memory)
    
    return memory_mean, memory_stdev


def getMemoryForAlg(algorithm):
    # algorithm : str
    
    # 1. Initiate if needed
    if "5_memory" not in RESULTS:
        initiateMemoryUsageResults()
        
    # 2. Get metadata
    file_path, algorithms, train_percs, dataset_names, exp_nums = getMemoryUsageMetadata()
    
    # # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)

    target_idx = (alg_idx)

    # 4. Fetch results
    memory = RESULTS["5_memory"][target_idx]
    
    # 3. Define indices of numpy matrix
    memory_mean = mean_except_minus1(memory)
    memory_stdev = stdev_except_minus1(memory)
    
    return memory_mean, memory_stdev





























    





































##########################################################################################
##########################################################################################
# PARAM                                                                                  #
##########################################################################################
##########################################################################################
# param_recall :    [param_variable, [10], dataset_ids, exp_nums]
# param_precision : [param_variable, [10], dataset_ids, exp_nums]
# param_f1 :        [param_variable, [10], dataset_ids, exp_nums]
# param_runtime :   [param_variable, [40, 60, 80, 100], dataset_ids, exp_nums]


def getParamMetadata():
    return  PARAM_EXP["result_path"], PARAM_EXP["param_name_to_values"], PARAM_EXP["param_name_to_default_value"], \
            PARAM_EXP["train_percs"], PARAM_EXP["dataset_names"], PARAM_EXP["exp_nums"]



def initiateParamResults():
    
    # 1. Define metadata
    file_path, param_name_to_values, _, \
        train_percs, dataset_ids, exp_nums = getParamMetadata()
    
    # 2. Initialize results
        # 0: data_percent
        # 1: param - beam_width
        # 2: param - epsilon
        # 3: param - min_pts_perc
        # 4: param - sample_size
        # 5: param - mdl_weight
        # 6: dataset
        # 7: exp_num
    param_dims = [len(param_name_to_values[param_name]) for param_name in param_name_to_values]

    recall_results    = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    precision_results = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    f1_results        = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    runtime_results   = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    src_results       = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    drc_results       = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    accepted_results  = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)


    # 3. Read results from file
    with open(file_path, newline='') as f:
        for s in csv.reader(f):

            if not s:
                continue
            
            exp_type = s[0]
            data_name = s[1]
            train_percent = int(s[2])
            exp_num  = int(s[3])
            beam_width = int(s[4])
            epsilon = float(s[5])
            min_pts_perc = int(s[6])
            sample_size = int(s[7])
            src_weight = float(s[8])
            drc_weight = float(s[9])
            
            if exp_type == "Accuracy":
                if "nan" in s[10]: recall = 0
                elif s[10] == "": recall = 0
                else: recall = float(s[10])
                
                if "nan" in s[11]: precision = 0
                elif s[11] == "": precision = 0
                else: precision = float(s[11])
                
                if "nan" in s[12]: f1 = 0
                elif s[12] == "": f1 = 0
                else: f1 = float(s[12])
            
            elif exp_type == "Performance":
                if s[10] == "": continue
                runtime = float(s[10])
            
            elif exp_type == "MDL":
                if s[10] == "": continue
                src = float(s[10])
                
                if s[11] == "": continue
                drc = float(s[11])
                
                if s[12] == "": continue
                num_accepted = int(s[12])

            beam_width_idx = param_name_to_values["beam_width"].index(beam_width)
            epsilon_idx = param_name_to_values["epsilon"].index(epsilon)
            min_pts_perc_idx = param_name_to_values["min_pts_perc"].index(min_pts_perc)
            sample_size_idx = param_name_to_values["sample_size"].index(sample_size)
            mdl_weights_idx = param_name_to_values["mdl_weights"].index((src_weight, drc_weight))
            train_idx = train_percs.index(train_percent)
            
            data_idx = dataset_ids.index(data_name)
            exp_idx = exp_nums.index(exp_num)
            
            np_array_idx = (train_idx, beam_width_idx, epsilon_idx, min_pts_perc_idx, sample_size_idx, mdl_weights_idx, data_idx, exp_idx)
            if exp_type == "Accuracy":
                recall_results[np_array_idx]        = recall
                precision_results[np_array_idx]     = precision
                f1_results[np_array_idx]            = f1
            elif exp_type == "Performance":
                runtime_results[np_array_idx]       = runtime
            elif exp_type == "MDL":
                src_results[np_array_idx]           = src
                drc_results[np_array_idx]           = drc
                accepted_results[np_array_idx]      = num_accepted
            else:
                raise Exception("initiateParamResults: Unknown exp_type")
                
    
    RESULTS["4_recall"] = recall_results
    RESULTS["4_precision"] = precision_results
    RESULTS["4_f1"] = f1_results
    RESULTS["4_runtime"] = runtime_results
    RESULTS["4_src"] = src_results
    RESULTS["4_drc"] = drc_results
    RESULTS["4_accepted"] = accepted_results
    


def getArrayForParamWithDefaultValues(param_name):
    #1. Get metadata
    _, param_name_to_values, param_name_to_default_value, _, _, _ = getParamMetadata()
        
    #2. Get default values for params
    def getIdxForParamDefaultValue(param_name):
        return param_name_to_values[param_name].index(param_name_to_default_value[param_name])
    
    dvi = getIdxForParamDefaultValue
    
    # 0: data_percent
    # 1: param - beam_width
    # 2: param - epsilon
    # 3: param - min_pts_perc
    # 4: param - sample_size
    # 5: param - mdl_weights
    # 6: dataset
    # 7: exp_num
    if param_name == "beam_width":
        recall =    RESULTS["4_recall"]   [:, :,                 dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        precision = RESULTS["4_precision"][:, :,                 dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        f1 =        RESULTS["4_f1"]       [:, :,                 dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        runtime =   RESULTS["4_runtime"]  [:, :,                 dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        src =       RESULTS["4_src"]      [:, :,                 dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        drc =       RESULTS["4_drc"]      [:, :,                 dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        accepted =  RESULTS["4_accepted"] [:, :,                 dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "epsilon":
        recall =    RESULTS["4_recall"]   [:, dvi("beam_width"), :,              dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        precision = RESULTS["4_precision"][:, dvi("beam_width"), :,              dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        f1 =        RESULTS["4_f1"]       [:, dvi("beam_width"), :,              dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        runtime =   RESULTS["4_runtime"]  [:, dvi("beam_width"), :,              dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        src =       RESULTS["4_src"]      [:, dvi("beam_width"), :,              dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        drc =       RESULTS["4_drc"]      [:, dvi("beam_width"), :,              dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        accepted =  RESULTS["4_accepted"] [:, dvi("beam_width"), :,              dvi("min_pts_perc"), dvi("sample_size"), dvi("mdl_weights"), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "min_pts_perc":
        recall =    RESULTS["4_recall"]   [:, dvi("beam_width"), dvi("epsilon"), :,                   dvi("sample_size"), dvi("mdl_weights"), :, :]
        precision = RESULTS["4_precision"][:, dvi("beam_width"), dvi("epsilon"), :,                   dvi("sample_size"), dvi("mdl_weights"), :, :]
        f1 =        RESULTS["4_f1"]       [:, dvi("beam_width"), dvi("epsilon"), :,                   dvi("sample_size"), dvi("mdl_weights"), :, :]
        runtime =   RESULTS["4_runtime"]  [:, dvi("beam_width"), dvi("epsilon"), :,                   dvi("sample_size"), dvi("mdl_weights"), :, :]
        src =       RESULTS["4_src"]      [:, dvi("beam_width"), dvi("epsilon"), :,                   dvi("sample_size"), dvi("mdl_weights"), :, :]
        drc =       RESULTS["4_drc"]      [:, dvi("beam_width"), dvi("epsilon"), :,                   dvi("sample_size"), dvi("mdl_weights"), :, :]
        accepted =  RESULTS["4_accepted"] [:, dvi("beam_width"), dvi("epsilon"), :,                   dvi("sample_size"), dvi("mdl_weights"), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "sample_size":
        recall =    RESULTS["4_recall"]   [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), :,                  dvi("mdl_weights"), :, :]
        precision = RESULTS["4_precision"][:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), :,                  dvi("mdl_weights"), :, :]
        f1 =        RESULTS["4_f1"]       [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), :,                  dvi("mdl_weights"), :, :]
        runtime =   RESULTS["4_runtime"]  [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), :,                  dvi("mdl_weights"), :, :]
        src =       RESULTS["4_src"]      [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), :,                  dvi("mdl_weights"), :, :]
        drc =       RESULTS["4_drc"]      [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), :,                  dvi("mdl_weights"), :, :]
        accepted =  RESULTS["4_accepted"] [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), :,                  dvi("mdl_weights"), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "mdl_weights":
        recall =    RESULTS["4_recall"]   [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), :,                  :, :]
        precision = RESULTS["4_precision"][:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), :,                  :, :]
        f1 =        RESULTS["4_f1"]       [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), :,                  :, :]
        runtime =   RESULTS["4_runtime"]  [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), :,                  :, :]
        src =       RESULTS["4_src"]      [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), :,                  :, :]
        drc =       RESULTS["4_drc"]      [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), :,                  :, :]
        accepted =  RESULTS["4_accepted"] [:, dvi("beam_width"), dvi("epsilon"), dvi("min_pts_perc"), dvi("sample_size"), :,                  :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    else:
        print("Something went wrong in getSpecificArrayForParam")
        print()
        exit()


def getArrayForParamWithCustomValues_(param_name, custom_values_dict):
    
    #1. Get metadata
    _, param_name_to_values, _, _, _, _ = getParamMetadata()
    
    def getIdxForCustomValue(param_name, custom_values_dict):
        return param_name_to_values[param_name].index(custom_values_dict[param_name])
        
    cvi = getIdxForCustomValue
    cvd = custom_values_dict
    

    # print(cvi("beam_width", cvd))  
    # 0: data_percent
    # 1: param - beam_width
    # 2: param - epsilon
    # 3: param - min_pts_perc
    # 4: param - sample_size
    # 5: param - mdl_weights
    # 6: dataset
    # 7: exp_num
    if param_name == "beam_width":
        recall =    RESULTS["4_recall"]   [:, :,                      cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        precision = RESULTS["4_precision"][:, :,                      cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        f1 =        RESULTS["4_f1"]       [:, :,                      cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        runtime =   RESULTS["4_runtime"]  [:, :,                      cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        src =       RESULTS["4_src"]      [:, :,                      cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        drc =       RESULTS["4_drc"]      [:, :,                      cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        accepted =  RESULTS["4_accepted"] [:, :,                      cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "epsilon":
        recall =    RESULTS["4_recall"]   [:, cvi("beam_width", cvd), :,                   cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        precision = RESULTS["4_precision"][:, cvi("beam_width", cvd), :,                   cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        f1 =        RESULTS["4_f1"]       [:, cvi("beam_width", cvd), :,                   cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        runtime =   RESULTS["4_runtime"]  [:, cvi("beam_width", cvd), :,                   cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        src =       RESULTS["4_src"]      [:, cvi("beam_width", cvd), :,                   cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        drc =       RESULTS["4_drc"]      [:, cvi("beam_width", cvd), :,                   cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        accepted =  RESULTS["4_accepted"] [:, cvi("beam_width", cvd), :,                   cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "min_pts_perc":
        recall =    RESULTS["4_recall"]   [:, cvi("beam_width", cvd), cvi("epsilon", cvd), :,                        cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        precision = RESULTS["4_precision"][:, cvi("beam_width", cvd), cvi("epsilon", cvd), :,                        cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        f1 =        RESULTS["4_f1"]       [:, cvi("beam_width", cvd), cvi("epsilon", cvd), :,                        cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        runtime =   RESULTS["4_runtime"]  [:, cvi("beam_width", cvd), cvi("epsilon", cvd), :,                        cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        src =       RESULTS["4_src"]      [:, cvi("beam_width", cvd), cvi("epsilon", cvd), :,                        cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        drc =       RESULTS["4_drc"]      [:, cvi("beam_width", cvd), cvi("epsilon", cvd), :,                        cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        accepted =  RESULTS["4_accepted"] [:, cvi("beam_width", cvd), cvi("epsilon", cvd), :,                        cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "sample_size":
        recall =    RESULTS["4_recall"]   [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), :,                       cvi("mdl_weights", cvd), :, :]
        precision = RESULTS["4_precision"][:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), :,                       cvi("mdl_weights", cvd), :, :]
        f1 =        RESULTS["4_f1"]       [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), :,                       cvi("mdl_weights", cvd), :, :]
        runtime =   RESULTS["4_runtime"]  [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), :,                       cvi("mdl_weights", cvd), :, :]
        src =       RESULTS["4_src"]      [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), :,                       cvi("mdl_weights", cvd), :, :]
        drc =       RESULTS["4_drc"]      [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), :,                       cvi("mdl_weights", cvd), :, :]
        accepted =  RESULTS["4_accepted"] [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), :,                       cvi("mdl_weights", cvd), :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    elif param_name == "mdl_weights":
        recall =    RESULTS["4_recall"]   [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), :,                       :, :]
        precision = RESULTS["4_precision"][:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), :,                       :, :]
        f1 =        RESULTS["4_f1"]       [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), :,                       :, :]
        runtime =   RESULTS["4_runtime"]  [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), :,                       :, :]
        src =       RESULTS["4_src"]      [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), :,                       :, :]
        drc =       RESULTS["4_drc"]      [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), :,                       :, :]
        accepted =  RESULTS["4_accepted"] [:, cvi("beam_width", cvd), cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), :,                       :, :]
        return recall, precision, f1, runtime, src, drc, accepted
    else:
        print("Something went wrong in getArrayForParamWithCustomValues")
        print()
        exit()





def getResultForPercParamDatasetExpnum(param_name, train_perc, param_value, dataset_name, exp_num, custom_values_dict = None):
    # param_name : str
    # train_perc : int
    # param_value : int
    # dataset_id : str
    # exp_num : int
    
    # 1. Initiate if needed
    if "4_recall" not in RESULTS:
        initiateParamResults()
    
    if custom_values_dict == None:  recalls, precisions, f1s, runtimes, srcs, drcs, accepteds = getArrayForParamWithDefaultValues(param_name)    
    else:                           recalls, precisions, f1s, runtimes, srcs, drcs, accepteds = getArrayForParamWithCustomValues_(param_name, custom_values_dict)
    
    # 2. Get metadata
    _, param_name_to_values, _, train_percs, dataset_ids, exp_nums = getParamMetadata()
    
    # 3. Define indices of numpy matrix
    train_idx = train_percs.index(train_perc)
    param_idx = param_name_to_values[param_name].index(param_value)
    data_idx = dataset_ids.index(dataset_name)
    exp_idx = exp_nums.index(exp_num)
    
    # 4. Fetch result
    target_idx = (train_idx, param_idx, data_idx, exp_idx)
    recall =    recalls[target_idx]
    precision = precisions[target_idx]
    f1 =        f1s[target_idx]
    runtime =   runtimes[target_idx]
    src =       srcs[target_idx]
    drc =       drcs[target_idx]
    accepted =  accepteds[target_idx]
        
    # 5. Return results
    return recall, precision, f1, runtime, src, drc, accepted

def getResultForPercParamDataset(param_name, train_perc, param_value, dataset_name, custom_values_dict = None):
    # param_name : str
    # train_perc : int
    # param_value : int
    # dataset_id : str

    # 1. Initiate if needed
    if "4_recall" not in RESULTS:
        initiateParamResults()
        
    if custom_values_dict == None:  recalls, precisions, f1s, runtimes, srcs, drcs, accepteds = getArrayForParamWithDefaultValues(param_name)    
    else:                           recalls, precisions, f1s, runtimes, srcs, drcs, accepteds = getArrayForParamWithCustomValues_(param_name, custom_values_dict)
    
    # 2. Get metadata
    _, param_name_to_values, _, train_percs, dataset_fullnames, _ = getParamMetadata()
    
    # 3. Define indices of numpy matrix
    train_idx = train_percs.index(train_perc)
    param_idx = param_name_to_values[param_name].index(param_value)
    data_idx = dataset_fullnames.index(dataset_name)
    
    # 4. Fetch result
    target_idx =        (train_idx, param_idx, data_idx)
    target_recalls =    recalls[target_idx]
    target_precisions = precisions[target_idx]
    target_f1s =        f1s[target_idx]
    target_runtimes =   runtimes[target_idx]
    target_srcs =       srcs[target_idx]
    target_drcs =       drcs[target_idx]
    target_accepteds =  accepteds[target_idx]
        
    # 5. Calculate non-(-1) mean
    non_m1_recall =     mean_except_minus1(target_recalls)
    non_m1_precision =  mean_except_minus1(target_precisions)
    non_m1_f1 =         mean_except_minus1(target_f1s)
    non_m1_runtime =    mean_except_minus1(target_runtimes)
    non_m1_src =        mean_except_minus1(target_srcs)
    non_m1_drc =        mean_except_minus1(target_drcs)
    non_m1_accepted =   mean_except_minus1(target_accepteds)
        
    # 5. Return results
    return non_m1_recall, non_m1_precision, non_m1_f1, non_m1_runtime, non_m1_src, non_m1_drc, non_m1_accepted



def getResultForPercParam(param_name, train_perc, param_value, custom_values_dict = None):
    # param_name : str
    # train_perc : int
    # param_value : int
    
    # 1. Initiate if needed
    if "4_recall" not in RESULTS:
        initiateParamResults()
    
    if custom_values_dict == None:  recalls, precisions, f1s, runtimes, srcs, drcs, accepteds = getArrayForParamWithDefaultValues(param_name)    
    else:                           recalls, precisions, f1s, runtimes, srcs, drcs, accepteds = getArrayForParamWithCustomValues_(param_name, custom_values_dict)
    
    # 2. Get metadata
    _, param_name_to_values, _, train_percs, _, _ = getParamMetadata()
    
    # 3. Define indices of numpy matrix
    train_idx = train_percs.index(train_perc)
    param_idx = param_name_to_values[param_name].index(param_value)
    
    # 4. Fetch result
    target_idx =        (train_idx, param_idx)
    target_recalls =    recalls[target_idx]
    target_precisions = precisions[target_idx]
    target_f1s =        f1s[target_idx]
    target_runtimes =   runtimes[target_idx]
    target_srcs =       srcs[target_idx]
    target_drcs =       drcs[target_idx]
    target_accepteds =  accepteds[target_idx]
        
    # 5. Calculate non-(-1) mean
    non_m1_recall =     mean_except_minus1(target_recalls)
    non_m1_precision =  mean_except_minus1(target_precisions)
    non_m1_f1 =         mean_except_minus1(target_f1s)
    non_m1_runtime =    mean_except_minus1(target_runtimes)
    non_m1_src =        mean_except_minus1(target_srcs)
    non_m1_drc =        mean_except_minus1(target_drcs)
    non_m1_accepted =   mean_except_minus1(target_accepteds)
        
    # 5. Return results
    return non_m1_recall, non_m1_precision, non_m1_f1, non_m1_runtime, non_m1_src, non_m1_drc, non_m1_accepted











































##########################################################################################
##########################################################################################
# UTILS
##########################################################################################
##########################################################################################

def mean_except_minus1(numpy_array):
    shape = numpy_array.shape
    original_array = numpy_array
    
    while(len(shape) > 0):
        
        filtered_new_array = np.zeros(shape[:-1])
        new_array_shape = filtered_new_array.shape
        
        for index in product(*[range(i) for i in new_array_shape]):
            array_at_index = original_array[index]
            filtered_array_at_index = array_at_index[array_at_index != -1]
            
            if len(filtered_array_at_index) == 0:
                filtered_new_array[index] = -1
            else:
                filtered_new_array[index] = np.mean(filtered_array_at_index)
        
        
        original_array = filtered_new_array
        shape = original_array.shape
        
    final_value = original_array
    if final_value == -1:
        return -1
    return float(final_value)


def stdev_except_minus1(numpy_array):
    shape = numpy_array.shape
    original_array = numpy_array
    
    first = True
    while(len(shape) > 0):
        
        filtered_new_array = np.zeros(shape[:-1])
        new_array_shape = filtered_new_array.shape
        
        for index in product(*[range(i) for i in new_array_shape]):
            array_at_index = original_array[index]
            filtered_array_at_index = array_at_index[array_at_index != -1]
            
            if len(filtered_array_at_index) == 0:
                filtered_new_array[index] = -1
            else:
                if first:
                    filtered_new_array[index] = np.std(filtered_array_at_index)
                else:
                    filtered_new_array[index] = np.mean(filtered_array_at_index)
        
        first = False
        original_array = filtered_new_array
        shape = original_array.shape
        
    final_value = original_array
    if final_value == -1:
        return -1
    return float(final_value)














































##########################################################################################
##########################################################################################
# PARAM - BEAMWIDTH                                                                      #
##########################################################################################
##########################################################################################
# param_recall :    [param_variable, [10], dataset_ids, exp_nums]
# param_precision : [param_variable, [10], dataset_ids, exp_nums]
# param_f1 :        [param_variable, [10], dataset_ids, exp_nums]
# param_runtime :   [param_variable, [40, 60, 80, 100], dataset_ids, exp_nums]


def getParamForBeamSearchMetadata():
    return  PARAM_FOR_BEAM_SEARCH_EXP["result_path"], PARAM_FOR_BEAM_SEARCH_EXP["param_name_to_values"], \
            PARAM_FOR_BEAM_SEARCH_EXP["train_percs"], PARAM_FOR_BEAM_SEARCH_EXP["dataset_names"], PARAM_FOR_BEAM_SEARCH_EXP["exp_nums"]



def initiateParamBeamWidthResults():
    
    # 1. Define metadata
    file_path, param_name_to_values, \
        train_percs, dataset_ids, exp_nums = getParamForBeamSearchMetadata()
    
    # 2. Initialize results
    param_dims = [len(param_name_to_values[param_name]) for param_name in param_name_to_values]

    recall_results    = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    precision_results = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)
    f1_results        = np.full( (len(train_percs), *param_dims, len(dataset_ids), len(exp_nums)), -1, dtype = float)


    # 3. Read results from file
    with open(file_path, newline='') as f:
        for s in csv.reader(f):
    
            if not s:
                continue
            exp_type = s[0]
            data_name = s[1]
            train_percent = int(s[2])
            exp_num  = int(s[3])
            beam_width = int(s[4])
            epsilon = float(s[5])
            min_pts_perc = int(s[6])
            sample_size = int(s[7])
            
            src_weight = float(s[8])
            drc_weight = float(s[9])
            
            if exp_type == "Accuracy":
                if "nan" in s[10]: recall = 0
                elif s[10] == "": recall = 0
                else: recall = float(s[10])
                
                if "nan" in s[11]: precision = 0
                elif s[11] == "": recall = 0
                else: precision = float(s[11])
                
                if "nan" in s[12]: f1 = 0
                elif s[12] == "": recall = 0
                else: f1 = float(s[12])
                
                

            beam_width_idx = param_name_to_values["beam_width"].index(beam_width)
            epsilon_idx = param_name_to_values["epsilon"].index(epsilon)
            min_pts_perc_idx = param_name_to_values["min_pts_perc"].index(min_pts_perc)
            sample_size_idx = param_name_to_values["sample_size"].index(sample_size)
            mdl_weight_idx = param_name_to_values["mdl_weights"].index((src_weight, drc_weight))
            train_idx = train_percs.index(train_percent)
            
            data_idx =  dataset_ids.index(data_name)
            exp_idx =   exp_nums.index(exp_num)
            
            np_array_idx = (train_idx, beam_width_idx, epsilon_idx, min_pts_perc_idx, sample_size_idx, mdl_weight_idx, data_idx, exp_idx)
            
            if exp_type == "Accuracy":
                recall_results[np_array_idx]        = recall
                precision_results[np_array_idx]     = precision
                f1_results[np_array_idx]            = f1
    
    RESULTS["4b_recall"] = recall_results
    RESULTS["4b_precision"] = precision_results
    RESULTS["4b_f1"] = f1_results
    



def getArrayForParamWithCustomValues(target_param_name, custom_values_dict):
    
    #1. Get metadata
    _, param_name_to_values, _, _, _ = getParamForBeamSearchMetadata()
    
    def getIdxForCustomValue(param_name, custom_values_dict):
        return param_name_to_values[param_name].index(custom_values_dict[param_name])
        
    cvi = getIdxForCustomValue
    cvd = custom_values_dict
    
    # 0: data_percent
    # 1: param - beam_width
    # 2: param - epsilon
    # 3: param - min_pts_perc
    # 4: param - sample_size
    # 5: param - mdl_weight
    # 6: dataset
    # 7: exp_num
    if target_param_name == "beam_width":
        recall =    RESULTS["4b_recall"]   [:, :, cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        precision = RESULTS["4b_precision"][:, :, cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        f1 =        RESULTS["4b_f1"]       [:, :, cvi("epsilon", cvd), cvi("min_pts_perc", cvd), cvi("sample_size", cvd), cvi("mdl_weights", cvd), :, :]
        return recall, precision, f1

    else:
        print("Something went wrong in getArrayForParamWithCustomValues")
        print()
        exit()






def getResultForBWPercParamDatasetExpnum(param_name, train_perc, param_value, dataset_name, exp_num, custom_values_dict):
    # param_name : str
    # train_perc : int
    # param_value : int
    # dataset_id : str
    # exp_num : int
    
    # 1. Initiate if needed
    if "4b_recall" not in RESULTS:
        initiateParamBeamWidthResults()
    recalls, precisions, f1s = getArrayForParamWithCustomValues(param_name, custom_values_dict)    
    
    # 2. Get metadata
    _, param_name_to_values, train_percs, dataset_ids, exp_nums = getParamForBeamSearchMetadata()
    
    # 3. Define indices of numpy matrix
    train_idx = train_percs.index(train_perc)
    param_idx = param_name_to_values[param_name].index(param_value)
    data_idx = dataset_ids.index(dataset_name)
    exp_idx = exp_nums.index(exp_num)
    
    # 4. Fetch result
    target_idx = (train_idx, param_idx, data_idx, exp_idx)
    recall =    recalls[target_idx]
    precision = precisions[target_idx]
    f1 =        f1s[target_idx]
        
    # 5. Return results
    return recall, precision, f1

def getResultForBWPercParamDataset(param_name, train_perc, param_value, dataset_name, custom_values_dict):
    # param_name : str
    # train_perc : int
    # param_value : int
    # dataset_id : str

    # 1. Initiate if needed
    if "4b_recall" not in RESULTS:
        initiateParamBeamWidthResults()
    recalls, precisions, f1s = getArrayForParamWithCustomValues(param_name, custom_values_dict)
    
    # 2. Get metadata
    _, param_name_to_values, train_percs, dataset_fullnames, _ = getParamForBeamSearchMetadata()
    
    # 3. Define indices of numpy matrix
    train_idx = train_percs.index(train_perc)
    param_idx = param_name_to_values[param_name].index(param_value)
    data_idx = dataset_fullnames.index(dataset_name)
    
    # 4. Fetch result
    target_idx = (train_idx, param_idx, data_idx)
    target_recalls =    recalls[target_idx]
    target_precisions = precisions[target_idx]
    target_f1s =        f1s[target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_recall = mean_except_minus1(target_recalls)
    non_m1_precision = mean_except_minus1(target_precisions)
    non_m1_f1 = mean_except_minus1(target_f1s)
        
    # 5. Return results
    return non_m1_recall, non_m1_precision, non_m1_f1



def getResultForBWPercParam(param_name, train_perc, param_value, custom_values_dict):
    # param_name : str
    # train_perc : int
    # param_value : int
    
    # 1. Initiate if needed
    if "4b_recall" not in RESULTS:
        initiateParamBeamWidthResults()
    recalls, precisions, f1s = getArrayForParamWithCustomValues(param_name, custom_values_dict)
    
    # 2. Get metadata
    _, param_name_to_values, train_percs, _, _ = getParamForBeamSearchMetadata()
    
    # 3. Define indices of numpy matrix
    train_idx = train_percs.index(train_perc)
    param_idx = param_name_to_values[param_name].index(param_value)
    
    # 4. Fetch result
    target_idx = (train_idx, param_idx)
    target_recalls =    recalls[target_idx]
    target_precisions = precisions[target_idx]
    target_f1s =        f1s[target_idx]
    
    # 5. Calculate non-(-1) mean
    non_m1_recall = mean_except_minus1(target_recalls)
    non_m1_precision = mean_except_minus1(target_precisions)
    non_m1_f1 = mean_except_minus1(target_f1s)
        
    # 5. Return results
    return non_m1_recall, non_m1_precision, non_m1_f1


























##########################################################################################
##########################################################################################
# Weighted MDL                                                                           #
# dataset_fullname, train_perc, src_weight, drc_weight, exp_num, recall, precision, f1
##########################################################################################
##########################################################################################


# def initiateWeightedMDLResults():
    
#     # 1. Define metadata
#     file_path, train_percs, mdl_weights, dataset_ids, exp_nums = getWeightedMDLMdetadata()
    
#     # 2. Initialize results
#     f1_results          = np.full( (len(train_percs), len(mdl_weights), len(dataset_ids), len(exp_nums)), -1, dtype = float)
#     recall_results      = np.full( (len(train_percs), len(mdl_weights), len(dataset_ids), len(exp_nums)), -1, dtype = float)
#     precision_results   = np.full( (len(train_percs), len(mdl_weights), len(dataset_ids), len(exp_nums)), -1, dtype = float)

#     # 3. Read results from file
#     with open(file_path, newline='') as f:
    
#         for s in csv.reader(f):
#             if not s: continue
#             if s[0] == "": continue
            
#             data_name = s[0]
#             train_percent = int(s[1])
#             exp_num = int(s[2])
#             src_weight = float(s[3])
#             drc_weight = float(s[4])
            
            
#             if "nan" in s[5]: recall = 0
#             elif s[5] == "": recall = 0
#             else: recall = float(s[5])
            
#             if "nan" in s[6]: precision = 0
#             elif s[6] == "": precision = 0
#             else: precision = float(s[6])
            
#             if "nan" in s[7]: f1 = 0
#             elif s[7] == "": f1 = 0
#             else: f1 = float(s[7])
            
#             mdlweight_idx = mdl_weights.index((src_weight, drc_weight))
#             train_idx = train_percs.index(train_percent)
#             try: data_idx = dataset_ids.index(data_name)
#             except ValueError: continue
#             try: exp_idx = exp_nums.index(exp_num)
#             except ValueError: continue
            
#             f1_results       [train_idx][mdlweight_idx][data_idx][exp_idx] = f1
#             recall_results   [train_idx][mdlweight_idx][data_idx][exp_idx] = recall
#             precision_results[train_idx][mdlweight_idx][data_idx][exp_idx] = precision
            
#     RESULTS["6_recall"] = recall_results
#     RESULTS["6_precision"] = precision_results
#     RESULTS["6_f1"] = f1_results

    
# def getWeightedMDLMdetadata():
#     return WEIGHTEDMDL_EXP["result_path"], WEIGHTEDMDL_EXP["train_percs"], WEIGHTEDMDL_EXP["mdl_weights"], WEIGHTEDMDL_EXP["dataset_names"], WEIGHTEDMDL_EXP["exp_nums"]



# def getAccForPercWeightDatasetExpnum(train_perc, mdl_weight, dataset_name, exp_num):
#     # algorithm : str
#     # train_perc : int
#     # dataset_id : str
#     # exp_num : int

#     # 1. Initiate if needed
#     if "6_recall" not in RESULTS:
#         initiateWeightedMDLResults()
        
#     # 2. Get metadata
#     _, train_percs, mdl_weights, dataset_ids, exp_nums = getWeightedMDLMdetadata()
    
#     # 3. Define indices of numpy matrix
#     mdlweight_idx = mdl_weights.index(mdl_weight)
#     train_perc_idx = train_percs.index(train_perc)
#     data_idx = dataset_ids.index(dataset_name)
#     exp_idx = exp_nums.index(exp_num)
    
#     # 4. Fetch result
#     recall      = RESULTS["6_recall"][train_perc_idx][mdlweight_idx][data_idx][exp_idx]
#     precision   = RESULTS["6_precision"][train_perc_idx][mdlweight_idx][data_idx][exp_idx]
#     f1          = RESULTS["6_f1"][train_perc_idx][mdlweight_idx][data_idx][exp_idx]
    
#     # 5. Return results
#     return recall, precision, f1


# def getAccForPercWeightDataset(train_perc, mdl_weight, dataset_name):
#     # algorithm : str
#     # train_perc : int
#     # dataset_id : str
    
#     # 1. Initiate if needed
#     if "6_recall" not in RESULTS:
#         initiateWeightedMDLResults()
        
#     # 2. Get metadata
#     _, train_percs, mdl_weights, dataset_ids, _ = getWeightedMDLMdetadata()
    
#     # 3. Define indices of numpy matrix
#     mdlweight_idx = mdl_weights.index(mdl_weight)
#     train_perc_idx = train_percs.index(train_perc)
#     data_idx = dataset_ids.index(dataset_name)
    
#     target_idx = (train_perc_idx, mdlweight_idx, data_idx)
    
#     # 4. Fetch results
#     recalls = RESULTS["6_recall"][target_idx]
#     precisions = RESULTS["6_precision"][target_idx]
#     f1s = RESULTS["6_f1"][target_idx]
    
#     # 5. Calculate non-(-1) mean
#     recall_mean = mean_except_minus1(recalls)
#     precision_mean = mean_except_minus1(precisions)
#     f1_mean = mean_except_minus1(f1s)
    
#     return recall_mean, precision_mean, f1_mean


# def getAccForPercWeight(train_perc, mdl_weight):
#     # algorithm : str
#     # train_perc : int
    
#     # 1. Initiate if needed
#     if "6_recall" not in RESULTS:
#         initiateWeightedMDLResults()
        
#     # 2. Get metadata
#     _, train_percs, mdl_weights, _, _ = getWeightedMDLMdetadata()
    
#     # 3. Define indices of numpy matrix
#     mdlweight_idx = mdl_weights.index(mdl_weight)
#     train_perc_idx = train_percs.index(train_perc)
    
#     target_idx = (train_perc_idx, mdlweight_idx)

#     # 4. Fetch results
#     recalls = RESULTS["6_recall"][target_idx]
#     precisions = RESULTS["6_precision"][target_idx]
#     f1s = RESULTS["6_f1"][target_idx]
    
#     # 5. Calculate non-(-1) mean
#     recall_mean = mean_except_minus1(recalls)
#     precision_mean = mean_except_minus1(precisions)
#     f1_mean = mean_except_minus1(f1s)
    
#     return recall_mean, precision_mean, f1_mean
    

































