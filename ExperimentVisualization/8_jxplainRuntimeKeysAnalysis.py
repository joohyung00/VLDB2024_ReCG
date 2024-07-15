import sys

sys.path.insert(1, "/root/VLDB2024_ReCG/Experiment")
from utils.dataset_metadata import dataset_ids, dataset_id_to_fullname, dataset_id_to_positive_dataset_path
from load_json import load_dataset
import json
from tqdm import tqdm
import numpy as np

sys.path.insert(1, "/root/VLDB2024_ReCG/ExperimentVisualization")
from aggregateExpResults import getRuntimeForAlgPercDataset, getMemoryForAlgPercDataset



KEYNUM_FILE                         = "Performance/JxplainAnalysis/1_distinctKeyNum_per_dataset.json"
RELATIVE_PERFORMANCE_PER_DATASET    = "Performance/JxplainAnalysis/1_relativePerformance_per_dataset.json"
KEYNUM_N_RELRUNTIME_PER_DATASET     = "Performance/JxplainAnalysis/1_relativePerformanceAndKeyNum_per_dataset.json"
KEYNUM_N_PERFORMANCE_PER_DATASET    = "Performance/JxplainAnalysis/1_PerformanceAndKeyNum_per_dataset.json"

def main():
    
    # 1.1.
    num_of_keys_per_dataset = {}

    for dataset_id in dataset_ids:
        dataset = []
        load_dataset(dataset_id_to_positive_dataset_path[dataset_id], dataset)
        num_of_keys = checkNumOfKeys(dataset)
        
        num_of_keys_per_dataset[dataset_id] = num_of_keys
    
    print(json.dumps(num_of_keys_per_dataset, indent = 4))
    with open(KEYNUM_FILE, "w") as file:
        json.dump(num_of_keys_per_dataset, file, indent = 4)
    
    # 1.2. Calculate relative performance per dataset
    getRelativePerformancePerDataset(RELATIVE_PERFORMANCE_PER_DATASET)
    
    # 1.3. Match results
    aggregateRelativityAndKeyNum(KEYNUM_FILE, RELATIVE_PERFORMANCE_PER_DATASET, KEYNUM_N_RELRUNTIME_PER_DATASET)
    aggregatePerformanceAndKeyNum(KEYNUM_FILE, KEYNUM_N_PERFORMANCE_PER_DATASET)
    
    # 1.4. Analyze results
    file_names = [KEYNUM_N_RELRUNTIME_PER_DATASET, KEYNUM_N_PERFORMANCE_PER_DATASET]
    for file_name in file_names:
        getCorrelationBetweenKeyNumAndRuntime(file_name)
    
    
    
def aggregateRelativityAndKeyNum(keynum_file, relativity_file, out_file):
    with open(keynum_file, "r") as file:
        keynum_per_dataset = json.load(file)
    
    with open(relativity_file, "r") as file:
        relativity_per_dataset = json.load(file)
    
    relativity_and_keynum_per_dataset = {}
    
    for data_name in keynum_per_dataset:
        data_fullname = dataset_id_to_fullname[data_name]
        
        if data_fullname not in relativity_per_dataset: continue
        
        relativity_and_keynum_per_dataset[data_name] = {
            "relative performance": relativity_per_dataset[data_fullname],
            "num of distinct keys": keynum_per_dataset[data_name]
        }
    
    with open(out_file, "w") as file:
        json.dump(relativity_and_keynum_per_dataset, file, indent = 4)
        
        
def aggregatePerformanceAndKeyNum(keynum_file, out_file):
    with open(keynum_file, "r") as file:
        keynum_per_dataset = json.load(file)    
    
    performance_and_keynum_per_dataset = {}
    
    for data_name in keynum_per_dataset:
        if data_name in ["1", "31", "6", "43", "44"]:
            continue
        
        data_fullname = dataset_id_to_fullname[data_name]
        
        performance_and_keynum_per_dataset[data_name] = {
            "num of distinct keys": keynum_per_dataset[data_name],
            "relative performance": getRuntimeForAlgPercDataset("jxplain", 100, data_fullname)
        }
        
        print(getRuntimeForAlgPercDataset("ReCG", 100, data_fullname))
        
    with open(out_file, "w") as file:
        json.dump(performance_and_keynum_per_dataset, file, indent = 4)

    
    
    
    
def getCorrelationBetweenKeyNumAndRuntime(file_name):
    relative_runtimes = []
    distinct_key_nums = []
    
    with open(file_name, "r") as file:
        relativeperformance_and_keynum_per_datasetfullname = json.load(file)
    
    for dataset_fullname in relativeperformance_and_keynum_per_datasetfullname:
        relative_runtime = relativeperformance_and_keynum_per_datasetfullname[dataset_fullname]["relative performance"]
        distinct_key_num = relativeperformance_and_keynum_per_datasetfullname[dataset_fullname]["num of distinct keys"]
        
        relative_runtimes.append(relative_runtime)
        distinct_key_nums.append(distinct_key_num)
    
    print(np.corrcoef(relative_runtimes, distinct_key_nums))
    
    
    
    
    
def getRelativePerformancePerDataset(out_file):
    algorithm1 = "ReCG"
    algorithm2 = "jxplain"
    target_dataset_ids = dataset_ids
    
    relative_performance_per_dataset = {}
    relative_memory_per_dataset = {}
    
    for dataset_id in target_dataset_ids:
        if dataset_id in ["1", "6", "31", "43", "44"]: continue
        
        runtime_acc_1 = 0
        runtime_acc_2 = 0
        memory_acc_1 = 0
        memory_acc_2 = 0
        for perc in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            runtime_acc_1 += getRuntimeForAlgPercDataset(algorithm1, perc, dataset_id_to_fullname[dataset_id])
            runtime_acc_2 += getRuntimeForAlgPercDataset(algorithm2, perc, dataset_id_to_fullname[dataset_id])
            
            memory_acc_1 += getMemoryForAlgPercDataset(algorithm1, perc, dataset_id_to_fullname[dataset_id])
            memory_acc_2 += getMemoryForAlgPercDataset(algorithm2, perc, dataset_id_to_fullname[dataset_id])
        
        relative_performance_per_dataset[dataset_id_to_fullname[dataset_id]] = runtime_acc_2 / runtime_acc_1
        relative_memory_per_dataset[dataset_id_to_fullname[dataset_id]] = memory_acc_2 / memory_acc_1
        
    with open(out_file, "w") as file:
        json.dump(relative_performance_per_dataset, file, indent = 4)
        
    # with open("1_relativeMemory_per_dataset.json", "w") as file:
    #     json.dump(relative_memory_per_dataset, file, indent = 4)
    
    
    
    
def checkNumOfKeys(json_list):
    key_set = set()
    for json_obj in tqdm(json_list):
        incrementKeySetRecursive(json_obj, key_set)
    
    return len(key_set)
    

def incrementKeySetRecursive(json_obj, key_set : set):
    
    if type(json_obj) == dict:
        for key in json_obj:
            key_set.add(key)
            incrementKeySetRecursive(json_obj[key], key_set)
    
    elif type(json_obj) == list:
        for item in json_obj:
            incrementKeySetRecursive(item, key_set)
    
    return



if __name__ == "__main__": 
    main()