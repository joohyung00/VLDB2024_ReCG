import os
import sys

import json
import argparse
from copy import deepcopy
import random

sys.path.insert(1, '/root/VLDB2024_ReCG/Experiment')
from load_json import load_dataset, load_schema

from negative_schema_candidates import *
from negative_schema_gen_ops import *

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed, TimeoutError

import subprocess


NUM_PROCS = 10
TIME_OUT_IN_MINUTES = 10000
TIME_OUT_IN_SECONDS = TIME_OUT_IN_MINUTES * 60


def parseArguments(argv):

    parser = argparse.ArgumentParser(description = "")
    parser.add_argument("--Sg")
    parser.add_argument("--num_to_generate", type = int)
    parser.add_argument("--out_path")
    parser.add_argument("--newS")
    parser.add_argument("--newK")
    parser.add_argument("--neg_generator")
    parser.add_argument("--num_operations", type = int)

    args = parser.parse_args(argv)
    print(args)
    
    return args



def main(argv):
    
    args = parseArguments(argv)
    
    generateNegativeSamples(
        args.Sg, 
        args.num_to_generate, 
        args.out_path, 
        args.neg_generator,
        args.num_operations,
        args.newS, 
        args.newK
    )



def generateNegativeSamples(
    goal_schema_path, 
    generating_num, 
    out_path, 
    negative_schema_generator, 
    num_operations, 
    new_schema, 
    new_key
):
    global NUM_PROCS

    # 1. Load goal schema
    loaded_goal_schema = load_schema(goal_schema_path)
    loaded_goal_schema = changeToJSFCompatible(loaded_goal_schema)

    # 2. Initiate candidates
    candidate_dict = initiateSchemaCandidates(loaded_goal_schema)
    candidate_space = []

    for operation in candidate_dict.keys():
        for path_level in candidate_dict[operation]:
            candidate_space.append((operation, path_level[0], path_level[1]))
    

    if generating_num <= NUM_PROCS:
        NUM_PROCS = generating_num

    with ProcessPoolExecutor(NUM_PROCS) as executor:
        
        indices_per_process = list(split(range(generating_num), NUM_PROCS))
        num_per_process = [len(x) for x in indices_per_process]
        
        futures = []
        for i, num_to_generate in enumerate(num_per_process):
            
            print("[Process " + str(i + 1) + "] Starting...")
            future = executor.submit(
                generateNegativeSamplesOneProcess, 
                negative_schema_generator,
                num_operations,
                goal_schema_path,
                loaded_goal_schema,
                candidate_space,
                num_to_generate, 
                i + 1,
                new_schema,
                new_key
            )
            futures.append(future)

        try:
            for i, future in enumerate(as_completed(futures, timeout = TIME_OUT_IN_SECONDS)):
                future.result()
                print("[" + str(i + 1) + "th Process] Ended!")
        except TimeoutError:
            print("this took too long...")
            stopProcessPool(executor)


    # temp 파일들을 하나의 파일로 모아준다
    tempfile_names = ["temp_" + str(temp_num) + ".txt" for temp_num in [i + 1 for i in range(NUM_PROCS)]]
    mergeFiles(tempfile_names, out_path)
    deleteFiles(tempfile_names)

    return










def generateNegativeSamplesOneProcess(
    negative_generator,
    num_operations,
    goal_schema_path, 
    goal_schema,
    original_candidate_space, 
    num_to_generate, 
    process_id, 
    new_schema_from, 
    new_key_from
):

    # 3. Create negative samples
    #   3.1 Pick candidate
    #   3.2 Create negative schema
    #   3.3 Create negative sample
    if num_to_generate // 20 == 0:  SHOW_BY = 1
    else:                           SHOW_BY = num_to_generate // 20

    num_generated = 0

    temp_file_name = "temp_" + str(process_id) + ".txt"
    with open(temp_file_name, "a") as tmp_file:
        print("FAILED", file = tmp_file)
    print(len(original_candidate_space))


    while num_generated < num_to_generate:

        try:
      
            # 1. Fairly random pick a candidate -> operation and path
            operation_path_level = random.choice(original_candidate_space)
            operations = [operation_path_level[0]]
            paths = [operation_path_level[1]]
            levels = [operation_path_level[2]]


            # 2. Generate Negative schema from candidate
            negative_schema = generate_negative_schema(goal_schema, operation_path_level[0], operation_path_level[1], new_schema_from, new_key_from)
            currently_operated = 1
                        
            if currently_operated < num_operations:
                # 0.2. Initiate candidates
                candidate_dict = initiateSchemaCandidates(negative_schema)
                candidate_space = []

                for operation in candidate_dict.keys():
                    for path_level in candidate_dict[operation]:
                        candidate_space.append( (operation, path_level[0], path_level[1]) )
                                            
                # 1. Fairly random pick a candidate -> operation and path
                operation_path_level = random.choice(candidate_space)
                                
                # 2. Generate Negative schema from candidate
                negative_schema = generate_negative_schema(negative_schema, operation_path_level[0], operation_path_level[1], new_schema_from, new_key_from)
        
                operations.append(operation_path_level[0])
                paths.append(operation_path_level[1])
                levels.append(operation_path_level[2])
                          
                currently_operated += 1
            
            

            # Write negative schema to the file
            negative_schema_path = "negative_schema_" + str(process_id) + ".json"
            with open(negative_schema_path, "w") as file:
                json.dump(negative_schema, file, indent = 4)

            # 3. Generate negative JSON document from negative schema
            
            if negative_generator == "jsf":
                arguments = [
                    "node", "negative_generator.js", 
                    "--goal_schema_path", goal_schema_path, 
                    "--negative_schema_path", negative_schema_path, 
                    "--temp", temp_file_name,
                    "--operation", json.dumps(operations),
                    "--path", json.dumps(paths),
                    "--nesting_level", json.dumps(levels)
                ]
            elif negative_generator == "dataGen":
                arguments = [
                    "node", "/root/VLDB2024_ReCG/DataGen/routes/json_schemas.js", 
                    "--mode", "negative",
                    "--goal_schema_path", goal_schema_path, 
                    "--negative_schema_path", negative_schema_path, 
                    "--temp", temp_file_name,
                    "--operation", json.dumps(operations),
                    "--path", json.dumps(paths),
                    "--nesting_level", json.dumps(levels)
                ]
            else:
                raise Exception("generateNegativeSamplesWithMultipleProcesses: Unprecedented negative schema generator")
            
            result = subprocess.run(arguments)
            result.check_returncode()
            last_line = readLastLine(temp_file_name)
            if "FAILED" in last_line: continue
            else: num_generated += 1

            if os.path.exists(negative_schema_path):  os.remove(negative_schema_path)
            if (num_generated) % SHOW_BY == 0: 
                print("[Process " + str(process_id) + "]: " + str(num_generated) + "/" + str(num_to_generate) + " (" + str(int(100 * num_generated / num_to_generate)) + "%)")
                
        except Exception as e:
            pass




def changeToJSFCompatible(schema):
    if type(schema) is dict:
        new_schema = {}
        for key in schema:
            if key == "prefixItems" and type(schema["prefixItems"]) is list:
                new_schema["items"] = changeToJSFCompatible(schema["prefixItems"])
            else:
                new_schema[key] = changeToJSFCompatible(schema[key])

        return new_schema
    
    elif type(schema) is list:
        for i, subschema in enumerate(schema):
            schema[i] = changeToJSFCompatible(subschema)
        
        return schema
        
    else:
        return schema













def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))


def stopProcessPool(executor):
    for pid, process in executor._processes.items():
        process.terminate()
    executor.shutdown()


def readLastLine(file_path):

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


def mergeFiles(input_files, output_file):
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


def deleteFiles(filenames):
    for filename in filenames:
        try:
            os.remove(filename)
        except OSError:
            print(f"Error: Could not delete file {filename}")
    return


if __name__ == "__main__":
    main((sys.argv)[1:])