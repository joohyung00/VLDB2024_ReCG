import sys
sys.path.insert(1, '/root/JsonExplorerSpark/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_id_to_negative2_dataset_path, dataset_ids, dataset_fullnames

from itertools import product
import subprocess
import yaml




def main():
    for i, dataset_id in enumerate(dataset_ids):
        print(dataset_fullnames[i])
        
        negative2_dataset_path = dataset_id_to_negative2_dataset_path[dataset_id]
        
        # Check if file exists in that path
        try:
            counts = count_lines(negative2_dataset_path)
            print(counts)
            print()
        except:
            print("File not found")
            print()
            continue
        
        


if __name__ == "__main__":
    main()