import os
import sys

import json
import argparse
from copy import deepcopy
import random

sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_dataset, load_schema

from negative_schema_candidates import *
from negative_schema_gen_ops import *

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed, TimeoutError

import subprocess


# global candidate_dict
# candidate_dict := {
#   "operation_1": [ (path to target schema, nesting_level), (path to target schema, nesting_level), ...,  ].
#   ...,
#   "operation_n": [ (path to target schema, nesting_level), (path to target schema, nesting_level), ...,  ] 
# }

def main(argv):
    parser = argparse.ArgumentParser(description = "")
    parser.add_argument('--Sg')
    parser.add_argument('--num')
    parser.add_argument('--out_path')
    parser.add_argument('--newS')
    parser.add_argument('--newK')

    args = parser.parse_args(argv)
    print(args)

    generate_negative_samples(args.Sg, args.num, args.out_path, args.newS, args.newK)



def generate_negative_samples(goal_schema_path, generating_num, out_path, new_schema, new_key):

    # 1. Load goal schema
    loaded_goal_schema = load_schema(goal_schema_path)
    
    def change_to_jsf_compatible(schema):
        if type(schema) is dict:
            new_schema = {}
            
            for key in schema:
                if key == "prefixItems" and type(schema["prefixItems"]) is list:
                    new_schema["items"] = change_to_jsf_compatible(schema["prefixItems"])
                else:
                    new_schema[key] = change_to_jsf_compatible(schema[key])

            return new_schema
        
        elif type(schema) is list:
            
            for i, subschema in enumerate(schema):
                schema[i] = change_to_jsf_compatible(subschema)
            
            return schema
            
        else:
            return schema
        
    loaded_goal_schema = change_to_jsf_compatible(loaded_goal_schema)

    # 2. Initiate candidates
    candidate_dict = initiate_schema_candiates(loaded_goal_schema)

    candidate_space = []
    weight = []
    for operation in candidate_dict.keys():
        for path_level in candidate_dict[operation]:
            candidate_space.append((operation, path_level[0], path_level[1]))
            # Maybe give some weights?
            # But not yet...! 근거가 없음
            # 그냥 일대일로 하는 게 당연히 말이 되긴 하지
    

    print()
    print(candidate_space)
    # 3. Create negative samples
    #   3.1 Pick candidate
    #   3.2 Create negative schema
    #   3.3 Create negative sample

    NUM_PROCS = 10
    TIME_OUT = 3000000
    WAITING_TIME = TIME_OUT * 60

    generating_num = int(generating_num)
    if generating_num <= NUM_PROCS:
        NUM_PROCS = generating_num

    with ProcessPoolExecutor(NUM_PROCS) as executor:
        
        indices_per_process = list(split(range(generating_num), NUM_PROCS))

        num_per_process = [len(x) for x in indices_per_process]

        print(num_per_process)
        futures = []
        for i, num_for_a_process in enumerate(num_per_process):
            print("[Process " + str(i + 1) + "] Starting...")
            future = executor.submit(multi_js, goal_schema_path, loaded_goal_schema, candidate_space, num_for_a_process, i + 1, new_schema, new_key)
            futures.append(future)

        try:
            for i, future in enumerate(as_completed(futures, timeout = WAITING_TIME)):
                future.result()
                print("[" + str(i + 1) + "th Process] Ended!")
        except TimeoutError:
            print("this took too long...")
            stop_process_pool(executor)


    # temp 파일들을 하나의 파일로 모아준다
    tempfile_names = ["temp_" + str(temp_num) + ".txt" for temp_num in [i + 1 for i in range(NUM_PROCS)]]
    merge_files(tempfile_names, out_path)
    
    # temp 파일들 지우기
    delete_files(tempfile_names)

    return













def multi_js(goal_schema_path, goal_schema, candidate_space, generating_num, process_num, new_schema, new_key):

    SHOW_BY = generating_num // 20

    num_generated = 0

    temp_file_name = "temp_" + str(process_num) + ".txt"
    with open(temp_file_name, "w") as tmp_file:
        print("FAILED", file = tmp_file)
    print(len(candidate_space))

    while (num_generated < generating_num):

        try:
            # 1. Fairly random pick a candidate -> operation and path
            operation_path_level = random.choice(candidate_space)


            negative_schema = {}
            # if "anyOf" in operation_path_level[0]:
            #     print(operation_path_level[0])

            # 2. Generate Negative schema from candidate
            negative_schema = generate_negative_schema(goal_schema, operation_path_level[0], operation_path_level[1], new_schema, new_key)

            # Write negative schema to the file
            with open("negative_schema_" + str(process_num) + ".json", "w") as file:
                json.dump(negative_schema, file)

            # 3. Generate negative JSON document from negative schema
            result = subprocess.run(
                # [
                #     "node", "negative_generator.js", 
                #     "--goal_schema_path", goal_schema_path, 
                #     "--negative_schema_path", "negative_schema_" + str(process_num) + ".json", 
                #     "--temp", temp_file_name,
                #     "--operation", operation_path_level[0],
                #     "--path", str(operation_path_level[1]),
                #     "--nesting_level", str(operation_path_level[2])
                # ]
                [
                    "node", "/root/jsdReCG/DataGen/routes/json_schemas.js", 
                    "--mode", "negative",
                    "--goal_schema_path", goal_schema_path, 
                    "--negative_schema_path", "negative_schema_" + str(process_num) + ".json", 
                    "--temp", temp_file_name,
                    "--operation", operation_path_level[0],
                    "--path", str(operation_path_level[1]),
                    "--nesting_level", str(operation_path_level[2])
                ]
            )
            result.check_returncode()
            # Check if the recent file is not 'FAILED'
            # If not failed, num_generated += 1
            # If failed, pass

            last_line = read_last_line(temp_file_name)

            if "FAILED" in last_line:
                continue
            else:
                num_generated += 1

            if (num_generated) % SHOW_BY == 0:
                print("[Process " + str(process_num) + "]: " + str(num_generated) + "/" + str(generating_num) + " (" + str(int(100 * num_generated / generating_num)) + "%)")
        except Exception as e:
            pass



def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def stop_process_pool(executor):
    for pid, process in executor._processes.items():
        process.terminate()
    executor.shutdown()


def read_last_line(file_path):

    with open(file_path, 'rb+') as f:

        f.seek(0, 2)
        end = f.tell()

        if end == 0:
            return None

        elif end == 1:
            f.seek(0)
            last_line = f.readline().decode().strip()
            return last_line

        else:
            f.seek(-1, 2)
            while f.read(1) != b'\n' and f.tell() > 0:
                f.seek(-2, 1)
            last_line = f.readline().decode().strip()

            return last_line


def merge_files(input_files, output_file):
    with open(output_file, 'a') as out_file:
        for input_file in input_files:
            with open(input_file, 'r') as in_file:
                for line in in_file:
                    if "FAILED" not in line and line != "\n":
                        if line[-1] != '\n':
                            out_file.write(line + '\n')
                        else:
                            out_file.write(line)

    return

def delete_files(filenames):
    for filename in filenames:
        try:
            os.remove(filename)
        except OSError:
            print(f"Error: Could not delete file {filename}")
    return



if __name__ == "__main__":
    main((sys.argv)[1:])