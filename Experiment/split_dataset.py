import argparse
import json
import os
import random
import sys

sys.path.insert(1, '/root/JsonExplorerSpark/Experiment')
from load_json import load_dataset, load_schema, count_lines



def remove_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        print("File Removed")
    else:
        print("No such file")
        
        
        
def main(argv):
    parser = argparse.ArgumentParser(description = "Splits the positive samples into train and test set")
    
    parser.add_argument('--positive')
    parser.add_argument('--negative')
    parser.add_argument('--test_num')
    parser.add_argument('--train_perc')
    parser.add_argument('--test_perc')
    parser.add_argument('--train_out')
    parser.add_argument('--test_out')
    parser.add_argument('--meta')
    parser.add_argument('--mode')
    
    args = parser.parse_args(argv)  
    print(args)
    
    generate_dataset(
        args.mode,
        args.test_num, 
        args.positive, 
        args.negative, 
        args.train_perc, 
        args.test_perc,
        args.train_out, 
        args.test_out, 
        args.meta
    )

    


def generate_dataset(mode, test_iter, positive_path, negative_path, train_percent, test_percent, train_out, test_out, meta_out):
    test_iter = int(test_iter)
    POS_NEG_RATIO = 9
    
    print(positive_path)
    print(negative_path)

    num_pos_sample = count_lines(positive_path)
    num_pos_sample = min(10000, num_pos_sample)
    print(f"num_pos_sample={num_pos_sample}")

    # Negative sample
    # { 
    #   "operation": ..., 
    #   "nesting level": ...,
    #   "data": (data)
    # }
    num_neg_sample = count_lines(negative_path)
    num_neg_sample = min(10000, num_neg_sample)
    print(f"num_neg_sample={num_neg_sample}")
    
    # Split positive data into train and test dataset
    
    num_train_pos = int(num_pos_sample * float(train_percent) / 100)
    
    
    num_test_pos = min(num_pos_sample - num_train_pos, int(num_pos_sample * float(test_percent) / 100))
    print("Train Num: ", num_train_pos)
    
    # HERE 0
        # phase -> seed value
    random.seed(test_iter)
    # HERE 0

    # HERE 1
        # train_indices -> train_positive_indices
    train_pos_ind = random.sample(range(num_pos_sample), k = num_train_pos)
    train_pos_ind.sort()
    # print(train_pos_ind)
    # HERE 1
    
    print("Train Dataset Indices: [", train_pos_ind[0], train_pos_ind[-1], "]")

    
    print("Test Positive Num: ", num_test_pos)
    
    # HERE 2
        # positive_indices -> test_positive_indices
    pool = list(set(range(num_pos_sample)) - set(train_pos_ind))
    test_pos_ind = random.sample(pool, k=num_test_pos)
    test_pos_ind.sort()
    # print(test_pos_ind)
    # HERE 2
    

    num_test_neg = num_test_pos * POS_NEG_RATIO
    
    print(f"num_test_neg={num_test_neg}")
    
    # HERE 3
        # negative_indices -> test_negative_indices
    test_neg_ind = random.sample(range(num_neg_sample), k=num_test_neg)
    test_neg_ind.sort()
    # print(test_neg_ind)
    # HERE 3

    print("[Train Samples : Sampling...]")
    
    with open(train_out, "w") as trainout:
        with open(positive_path, "r") as positive_in:
            line_num = 0
            cursor = 0
            
            for line in positive_in:
                if(line_num < train_pos_ind[cursor]):
                    line_num += 1
                elif(line_num == train_pos_ind[cursor]):
                    trainout.write(line)
                    cursor += 1
                    line_num += 1
                else:
                    pass
                
                if(cursor == len(train_pos_ind)): break
                
    with open(train_out, "r") as file:
        count = 0
        for line in file:
            count += 1
        print("[Train Samples : Complete]")
        print("[Actual Train Samples:", count, " ]")
    
    
    with open(train_out, "r") as trainout:
        count = 0
        for line in trainout:
            count += 1
        print("[Train Samples : ", count, "]")
    
      
    with open(test_out, "w") as testout:
        print("[Test(Positive) Samples: Sampling...]")
        
        with open(positive_path, "r") as positive_in:
            line_num = 0
            cursor = 0
            
            if not len(test_pos_ind) == 0:
                for line in positive_in:
                    if(line_num < test_pos_ind[cursor]):
                        line_num += 1
                    elif(line_num == test_pos_ind[cursor]):
                        json_ = json.loads(line)
                        testout.write(json.dumps(
                            {"index": line_num + 1, 
                            "data": json_, 
                            "label": "positive"
                            }) + "\n")
                        line_num += 1
                        cursor += 1
                    
                    if(cursor == len(test_pos_ind)): break
        
        print("[Test(Positive) Samples: Complete]")
        print()

        if mode == "recall_precision":
            print("[Test(Negative) Samples: Sampling...]")
            
            if not len(test_neg_ind) == 0:
                with open(negative_path, "r") as negative_in:
                    line_num = 1
                    cursor = 1
                    
                    for line in negative_in:
                        if(line_num < test_neg_ind[cursor]):
                            line_num += 1
                        elif(line_num == test_neg_ind[cursor]):
                            json_ = json.loads(line)
                            json_["index"] = line_num + 1
                            json_["label"] = "negative"
                            testout.write(json.dumps(json_) + "\n")
                            line_num += 1
                            cursor += 1
                        
                        if(cursor == len(test_neg_ind)): 
                            break
                    
            print("[Test(Negative) Samples: Complete]")

    with open(test_out, "r") as testout:
        count = 0
        for line in testout:
            count += 1
        print("[Actual Test Samples : ", count, "]")
    
                    

    # Write it down in metadata path
    train_positive_indices = [x + 1 for x in train_pos_ind]
    test_positive_indices = [x + 1 for x in test_pos_ind]
    test_negative_indices = [x + 1 for x in test_neg_ind]

    meta_info = {}
    meta_info["train percent"] = train_percent
    meta_info["test percent"] = test_percent
    meta_info["TRAIN INDICES (positive)"] = train_positive_indices
    meta_info["positive test indices"] = test_positive_indices
    meta_info["negative test indices"] = test_negative_indices

    with open(meta_out, "w") as metafile:
        json.dump(meta_info, metafile)

    



if __name__ == "__main__":
    main((sys.argv)[1:])