from contextlib import nullcontext
import numpy as np
import csv
import statistics

import sys
sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames, possible_algorithms_list

from itertools import product

F1IDX = 0
RECALLIDX = 1
PRECISIONIDX = 2
SRCIDX = 0
DRCIDX = 1
MDLIDX = 2


RESULTS = {}

ACC_EXP = {
    "result_path": "../Experiment/exp_f1.txt",
    "algorithms": ["ReCG", "jxplain", "kreduce"],
    "train_percs" : [1, 10, 50, 90],
    "dataset_names" : dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5],
}
MDL_EXP = {
    "exp_type": "MDL",
    "result_path": "../Experiment/exp_mdl.txt",
    "algorithms": ["ReCG", "jxplain", "kreduce", "groundtruth"],
    "train_percs" : [10],
    "dataset_names" : dataset_fullnames,
    "exp_nums" : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}
PERF_EXP = {
    "exp_type": "Performance",
    "result_path": "../Experiment/exp_perf.txt",
    "algorithms": ["ReCG", "jxplain", "kreduce"],
    "train_percs" : [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
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
    _, algorithms, train_percs, dataset_names, exp_nums = getF1Metadata()
    
    # 3. Define indices of numpy matrix
    alg_idx = algorithms.index(algorithm)
    train_perc_idx = train_percs.index(train_perc)
    data_idx = dataset_names.index(dataset_name)
    
    # 4. Calculate results
    f1_mean = non_m1_mean(RESULTS["1_f1"][alg_idx][train_perc_idx][data_idx])
    # if f1_mean == -1: f1_mean = 0
    f1_stdev = non_m1_stdev(RESULTS["1_f1"][alg_idx][train_perc_idx][data_idx])
    recall_mean = non_m1_mean(RESULTS["1_recall"][alg_idx][train_perc_idx][data_idx])
    # if recall_mean == -1: recall_mean = 0
    recall_stdev = non_m1_stdev(RESULTS["1_recall"][alg_idx][train_perc_idx][data_idx])
    precision_mean = non_m1_mean(RESULTS["1_precision"][alg_idx][train_perc_idx][data_idx])
    # if precision_mean == -1: precision_mean = 0
    precision_stdev = non_m1_stdev(RESULTS["1_precision"][alg_idx][train_perc_idx][data_idx])
        
    # 5. Return results
    return f1_mean, f1_stdev, recall_mean, recall_stdev, precision_mean, precision_stdev


def non_m1_mean(array):
    """ mean of elements not -1. if all is -1, return -1 """
    non_m1 = array[array != -1]
    if len(non_m1) == 0: return -1
    return np.mean(non_m1)

def non_m1_stdev(array):
    """ stdev of elements not -1. if all is -1, return -1 """
    non_m1 = array[array != -1]
    if len(non_m1) == 0: return -1
    return np.std(non_m1)


def getAccForAlgPerc(algorithm, train_perc):
    # algorithm : str
    # train_perc : int
    
    # 1. Initiate if needed
    if "1_f1" not in RESULTS:
        initiateAccResults()
        
    # 2. Get metadata
    _, _, _, dataset_names, exp_nums = getF1Metadata()
    
    # 3. Calculate results buy marginalization
    f1s = []
    recalls = []
    precisions = []
    
    for i, dataset_name in enumerate(dataset_names):
        f1, _, recall, _, precision, _ = getAccForAlgPercDataset(algorithm, train_perc, dataset_name)
        if f1 == -1: continue
        f1s.append(f1)
        recalls.append(recall)
        precisions.append(precision)
    
    return np.mean(np.array(f1s)), np.mean(np.array(recalls)), np.mean(np.array(precisions))

def getAccForAlg(algorithm):
    # algorithm : str
    
    # 1. Initiate if needed
    if "1_f1" not in RESULTS:
        initiateAccResults()
        
    # 2. Get metadata
    _, algorithms, train_percs, _, _ = getF1Metadata()
        
    # 3. Calculate results buy marginalization
    f1s = np.zeros(len(train_percs))
    recalls = np.zeros(len(train_percs))
    precisions = np.zeros(len(train_percs))
    
    for i, train_perc in enumerate(train_percs):
        f1, recall, precision = getAccForAlgPerc(algorithm, train_perc)
        f1s[i] = f1
        recalls[i] = recall
        precisions[i] = precision
    
    return np.mean(f1s), np.mean(recalls), np.mean(precisions)
    


def initiateAccResults():
    
    # 1. Define metadata
    file_path, algorithms, train_percs, dataset_ids, exp_nums = getF1Metadata()
    
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
            
    RESULTS["1_recall"] = recall_results
    RESULTS["1_precision"] = precision_results
    RESULTS["1_f1"] = f1_results



def getF1Metadata():
    return ACC_EXP["result_path"], ACC_EXP["algorithms"], ACC_EXP["train_percs"], ACC_EXP["dataset_names"], ACC_EXP["exp_nums"]









##########################################################################################
##########################################################################################
# MDL                                                                                    #
##########################################################################################
##########################################################################################
# src : [algorithms (with groundtruth), [10], dataset_ids, exp_nums]
# drc : [algorithms (with groundtruth), [10], dataset_ids, exp_nums]


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
    if mdl == -2: mdl = -1
    
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
    
    # 4. Calculate results
    src_mean = np.mean(RESULTS["2_src"][alg_idx][train_perc_idx][data_idx])
    drc_mean = np.mean(RESULTS["2_drc"][alg_idx][train_perc_idx][data_idx])
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
    
    # 4. Calculate results
        # ndim = 2
        # axis 0 = dataset_name
        # axis 1 = exp_num
    # runtime_mean = np.mean(np.mean(RESULTS["3_runtime"][alg_idx][train_perc_idx], axis = 1))
    # runtime_stdev = np.mean(np.std(RESULTS["3_runtime"][alg_idx][train_perc_idx], axis = 1))
    data_expnums__src = RESULTS["2_src"][alg_idx][train_perc_idx]
    data_expnums__drc = RESULTS["2_drc"][alg_idx][train_perc_idx]    
        
    data__src_mean = np.mean(data_expnums__src, axis = 1)
    data__drc_mean = np.mean(data_expnums__drc, axis = 1)
        
    filtered_data__src_mean = np.array([x for x in data__src_mean if x != -1])
    filtered_data__drc_mean = np.array([x for x in data__drc_mean if x != -1])
        
    src_mean = np.mean(filtered_data__src_mean)
    drc_mean = np.mean(filtered_data__drc_mean)
    mdl_mean = src_mean + drc_mean
    
    return src_mean, drc_mean, mdl_mean


# def getMDLForAlg(algorithm):
#     # algorithm : str
    
#     # 1. Initiate if needed
#     if "2_src" not in RESULTS:
#         initiateMDLResults()
        
#     # 2. Get metadata
#     file_path, algorithms, train_percs, dataset_names, exp_nums = getMDLMetadata()
    
#     # 3. Define indices of numpy matrix
#     alg_idx = algorithms.index(algorithm)
    
#     # 4. Calculate results
#     # axis alg
#     # axis 0 = train_perc
#     # axis 1 = dataset_name
#     # axis 2 = exp_num 
#     perc_name__mean_src = np.mean(RESULTS["2_src"][alg_idx], axis = 2)
#     perc_name__mean_drc = np.mean(RESULTS["2_drc"][alg_idx], axis = 2)
    
    
#     src_mean = np.mean(np.mean(np.mean(RESULTS["2_src"][alg_idx], axis = 2), axis = 1))
#     drc_mean = np.mean(np.mean(np.mean(RESULTS["2_drc"][alg_idx], axis = 2), axis = 1))
#     mdl_mean = src_mean + drc_mean
    
#     return src_mean, drc_mean, mdl_mean
    


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
























##########################################################################################
##########################################################################################
# Performance                                                                            #
##########################################################################################
##########################################################################################
# runtime : [algorithms, [10, 20, ..., 100], dataset_ids, exp_nums]




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
    
    # 4. Calculate results
    runtime_mean = np.mean(RESULTS["3_runtime"][alg_idx][train_perc_idx][data_idx])
    
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
    
    # 4. Calculate results
        # ndim = 2
        # axis 0 = dataset_name
        # axis 1 = exp_num
    
    
    # runtime_mean = np.mean(np.mean(RESULTS["3_runtime"][alg_idx][train_perc_idx], axis = 1))
    # runtime_stdev = np.mean(np.std(RESULTS["3_runtime"][alg_idx][train_perc_idx], axis = 1))
    data_expnums = RESULTS["3_runtime"][alg_idx][train_perc_idx]
    data_means = np.mean(data_expnums, axis = 1)
    data_stdevs = np.std(data_expnums, axis = 1)
    
    filtered_data_means = np.array([x for x in data_means if x != -1])
    filtered_data_stdevs = np.array([x for x in data_stdevs if x != -1])
    
    runtime_mean = np.mean(filtered_data_means)
    runtime_stdev = np.mean(filtered_data_stdevs)
    
    return runtime_mean, runtime_stdev


# def getRuntimeForAlg(algorithm):
#     # algorithm : str
    
#     # 1. Initiate if needed
#     if "3_runtime" not in RESULTS:
#         initiateRuntimeResults()
        
#     # 2. Get metadata
#     file_path, algorithms, train_percs, dataset_names, exp_nums = getPerfMetadata()
    
#     # 3. Define indices of numpy matrix
#     alg_idx = algorithms.index(algorithm)
    
#     # 4. Calculate results
#     # axis alg
#     # axis 0 = train_perc
#     # axis 1 = dataset_name
#     # axis 2 = exp_num 
#     runtime_mean = np.mean(np.mean(np.mean(RESULTS["3_runtime"][alg_idx], axis = 2), axis = 1))
#     runtime_stdev = np.mean(np.std(np.mean(RESULTS["3_runtime"][alg_idx], axis = 2), axis = 1))
    
#     return runtime_mean, runtime_stdev
    


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
            exp_num = int(s[1])
            data_name = s[2]
            train_percent = int(s[5])
            runtime = float(s[7])
            
            alg_idx = algorithms.index(algo_name)
            train_idx = train_percs.index(train_percent)
            data_idx = dataset_ids.index(data_name)
            exp_idx = exp_nums.index(exp_num)
            
            runtime_results[alg_idx][train_idx][data_idx][exp_idx] = runtime
            
    RESULTS["3_runtime"] = runtime_results

    
def getPerfMetadata():
    return PERF_EXP["result_path"], PERF_EXP["algorithms"], PERF_EXP["train_percs"], PERF_EXP["dataset_names"], PERF_EXP["exp_nums"]