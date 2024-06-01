

import csv
import sys
sys.path.insert(2, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_fullnames

FILE_PATH = "/root/JsonExplorerSpark/Experiment/exp4_jxplain_runtime_analysis.txt"


JXPLAIN_RUNTIME_ANALYSIS_TARGET_STRINGS = [
    "1. Extract Complex Schemas: ",
    "2. Generate Feature Vectors: ",
    "3. Bimax: ",
    "4. Merge Schemas: ",
    "5. Variable Objs With Mult: ",
    "6. Variable Objs With Mult: "
]

PERF_EXP = {
    "exp_type": "Performance",
    "result_path":  "/root/JsonExplorerSpark/Experiment/exp4_jxplain_runtime_analysis.txt",
    "train_percs" : [10, 50, 100],
    "dataset_names": dataset_fullnames,
    "exp_nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
}    

def main():

    percentages = []
    accumulations = [0, 0]

    with open(FILE_PATH, newline='') as f:
        for s in csv.reader(f):
            if not s:
                continue
            data_name = s[0]
            train_percent = int(s[1])
            exp_num = int(s[2])
            
            extract_complex_schemas = int(s[3])
            generate_feature_vectors = int(s[4])
            bimax = int(s[5])
            merge_schemas = int(s[6])
            variable_objs_with_mult = int(s[7])
            variable_objs_with_mult = int(s[8])
            
            target_times = extract_complex_schemas + generate_feature_vectors + bimax + merge_schemas
            other_times = variable_objs_with_mult + variable_objs_with_mult
            
            percentages.append(target_times / (target_times + other_times))
            accumulations[0] += target_times
            accumulations[1] += other_times
            
    print("Average of heterogeneity determination & clustering time percentages: ", sum(percentages) / len(percentages))
    
    print("Average of total heterogeneity determination & clustering time: ", accumulations[0] / (accumulations[0] + accumulations[1]))
        
    
            



if __name__ == "__main__":
    main()