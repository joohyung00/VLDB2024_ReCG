import os
import sys
import json
import argparse

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from copy import deepcopy
from art import *
import statistics

sys.path.insert(1, '/root/VLDB2024_ReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema

from concurrent.futures import ProcessPoolExecutor
import functools
import logging
import threading
import traceback
from typing import Callable


out_path = "../exp4_param.txt"




def main(argv):
    # filepath = filepath to json schema
    
    parser = argparse.ArgumentParser(description = "prototype experiment program of JSD")
    parser.add_argument("--dataset")
    parser.add_argument("--train_perc")
    parser.add_argument("--exp_num")
    parser.add_argument("--schema_path")
    parser.add_argument("--test_path")
    parser.add_argument("--beam_width")
    parser.add_argument("--sample_size")
    parser.add_argument("--min_pts_perc")
    parser.add_argument("--epsilon")
    parser.add_argument("--src_weight")
    parser.add_argument("--drc_weight")
    
    

    args = parser.parse_args(argv)
    print(args)


    recall, precision, f1_score = accuracyExperiment(args.schema_path, args.test_path)

    out_str =   "Accuracy" + "," + \
                args.dataset + "," + \
                args.train_perc + "," + \
                args.exp_num + "," + \
                args.beam_width + "," + \
                args.epsilon + "," + \
                args.min_pts_perc + "," + \
                args.sample_size + "," + \
                args.src_weight + "," + \
                args.drc_weight + "," + \
                str(recall) + "," + \
                str(precision) + "," + \
                str(f1_score) + "\n"

    print("[RESULT]")
    print("Recall: ", recall, "\tPrecision: ", precision, "\tF1: ", f1_score)
    with open(out_path, "a") as file:
        file.write(out_str)



###################################################################################################################
#################################################### CALCULATE ####################################################
###################################################################################################################

def accuracyExperiment(schema_path, instance_path):
    # algorithm, dataset, exp_num, train_perc

    # 1. Get schema and dataset
    print("[1. Loading Test Dataset and Schemas...]")
    
    schema = load_schema(schema_path)
    original_schema = deepcopy(schema)
    labelled_test_dataset = []
    load_dataset(instance_path, labelled_test_dataset)
    
    print("[1. Loaded Test Dataset, #: ", len(labelled_test_dataset), "]\n")


    # 3. Calculate DRC
    print("[2. Validating Instances against Schema...]\n")

    argments = [(labeled_test_data, schema) for labeled_test_data in labelled_test_dataset]

    outer = process_map(runner, argments, max_workers = 50)
    tp_bits, fn_bits, tn_bits, fp_bits = zip(*outer)
    
    tp = tp_bits.count(True)
    fn = fn_bits.count(True)
    tn = tn_bits.count(True)
    fp = fp_bits.count(True)

    
    print("[2. Validating Instances Complete]\n")

    # 4. For each schema node, calculate SRC and DRC
    print("[3. Aggregating Results...]")

        # 4.1. Calculate ordinary SRC, DRC
    # Recall
    recall = tp / (tp + fn)
    try:
        precision = tp / (tp + fp)
    except ZeroDivisionError:
        precision = float('nan')
    f1_score = statistics.harmonic_mean([recall, precision])
    
    print("[3. Aggregating Results Complete]")
    
    return recall, precision, f1_score






def runner(inp):
    
    labeled_test_data, schema = inp
    
    instance = labeled_test_data["data"]
    index = labeled_test_data["index"]
    label = labeled_test_data["label"]
    
    copied_schema = deepcopy(schema)

    tp = False
    tn = False
    fp = False
    fn = False

    if label == "negative":
        if(validateCustom(instance, schema, copied_schema)):
            fp = True
        else:
            tn = True

    elif label == "positive":
        if(validateCustom(instance, schema, copied_schema)):
            tp = True
        else:
            fn = True
            
    return tp, fn, tn, fp




#####################################################
# validateCustom                                    #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def validateCustom(instance, schema, original_schema):
    
    # Case A. $ref -> unref
    if "$ref" in schema:
        schema, _ = getReferencingNode(original_schema, schema["$ref"])
        
    # Case B. AnyOf
    if "anyOf" in schema:
        for subschema in schema["anyOf"]:
            if(validateCustom(instance, subschema, original_schema)):
                return True
            
        return False
    
    # Case C. oneOf
    if "oneOf" in schema:
        success_num = 0
        for subschema in schema["oneOf"]:
            if(validateCustom(instance, subschema, original_schema)):
                success_num += 1
        
        if success_num == 1:
            return True
        return False
    
    # Now look at instance
    if type(instance) is int or type(instance) is float:
        if "type" in schema and (schema["type"] == "number" or schema["type"] is "integer"):
            return True
        else:
            return False
    
    elif type(instance) is str:
        if "type" in schema and schema["type"] == "string":
            return True
        else:
            return False
    
    elif type(instance) is bool:
        if "type" in schema and schema["type"] == "boolean":
            return True
        else:
            return False
        
    elif instance == None:
        if "type" in schema and schema["type"] == "null":
            return True
        else:
            return False
        
    elif type(instance) is dict:
        
        # 0. Check type
        if "type" in schema and schema["type"] != "object":
            return False

        # Case 1. Empty Object Schema
        if isEmptyObjectSchema(schema):
            if len(instance) == 0:
                return True
            else:
                return False

        # Case 1. Hom Object Schema
        if isHomObjectSchema(schema):
            
            instance_keys = set(instance.keys())
            schema_all_keys = set(schema["properties"].keys())
            
            if "required" in schema:
                schema_required_keys = set(schema["required"])
            else:
                schema_required_keys = set()
            schema_optional_keys = schema_all_keys - schema_required_keys

            # Check if keys are defined within `properties`
            if not (instance_keys <= schema_all_keys):
                return False

            # Check if all required keys appeared
            if not (schema_required_keys <= instance_keys):
                return False
                        
            for key in instance.keys():
                if not validateCustom(instance[key], schema["properties"][key], original_schema):
                    return False
            
            return True
        
        # Case 2. Com Object Schema
        elif isComObjectSchema(schema):
            
            instance_keys = set(instance.keys())
            schema_all_keys = set(schema["properties"].keys())
            if "required" in schema:
                schema_required_keys = set(schema["required"])
            else:
                schema_required_keys = set()
            schema_optional_keys = schema_all_keys - schema_required_keys

            # Check if all required keys appeared
            if not (schema_required_keys <= instance_keys):
                return False
            
            kleene_keys = instance_keys - schema_all_keys
            
            for key in instance.keys():
                if key in kleene_keys:
                    if not validateCustom(instance[key], schema["additionalProperties"], original_schema):
                        return False
                else:
                    if not validateCustom(instance[key], schema["properties"][key], original_schema):
                        return False
            
            return True
        
        # Case 3. Het Object Schema
        elif isHetObjectSchema(schema):

            for key in instance:
                if not validateCustom(instance[key], schema["additionalProperties"], original_schema):
                    return False
                
            return True
            
        else:
            print(json.dumps(schema))
            print(json.dumps(instance))
            raise Exception("Error 3")
    
    
    elif type(instance) is list:
        # 0. Check type
        if "type" in schema and schema["type"] != "array":
            return False
        
        # Case 1. Empty Array Schema
        if isEmptyArraySchema(schema):
            if len(instance) == 0:
                return True
            else:
                return False
        
        # Case 2. Hom Array Schema
        elif isHomArraySchema(schema):
            
            if "items" in schema:
                schema["prefixItems"] = schema["items"]
            
            if len(instance) != len(schema["prefixItems"]):
                return False
            

            for i, _ in enumerate(instance):
                if not validateCustom(instance[i], schema["prefixItems"][i], original_schema):
                    return False
        
            return True
        
        # Case 3. Het Array Schema
        elif isHetArraySchema(schema):
            
            for subinstance in instance:
                if not validateCustom(subinstance, schema["items"], original_schema):
                    return False
            
            return True
        
        else:
            print(json.dumps(schema))
            print(json.dumps(instance))
            raise Exception("Error 4")
    
    else:
        print(json.dumps(schema))
        print(json.dumps(instance))
        raise Exception("Error 1")
    
    

#####################################################
# schemaClassification                              #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def isHomObjectSchema(schema):
    if "type" in schema and schema["type"] == "object":
        if  ("properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] == False) or \
            ("properties" in schema and "additionalProperties" not in schema):
                return True
    return False

def isComObjectSchema(schema):
    if "type" in schema and schema["type"] == "object":
        if "properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] != False:
            return True
    return False

def isHetObjectSchema(schema):
    if "type" in schema and schema["type"] == "object":
        if "properties" not in schema and "additionalProperties" in schema and schema["additionalProperties"] != False:
            return True
    return False

def isEmptyObjectSchema(schema):
    if "type" in schema and schema["type"] == "object":
        if "maxProperties" in schema and schema["maxProperties"] == 0:
            return True
        if "properties" in schema and schema["properties"] == {} and ("additionalProperties" not in schema or ("additionalProperties" in schema and schema["additionalProperties"] == False)):
            return True
    return False

def isHomArraySchema(schema):
    if "type" in schema and schema["type"] == "array":
        if "items" in schema and type(schema["items"]) is list:
            return True
        elif "prefixItems" in schema:
            return True
    return False

def isHetArraySchema(schema):
    if "type" in schema and schema["type"] == "array":
        if "items" in schema and type(schema["items"]) is dict:
            return True
    return False

def isEmptyArraySchema(schema):
    if "maxItems" in schema and schema["maxItems"] == 0:
        return True
    return False



#####################################################
# Schema UTILS                                      #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def getReferencingNode(original_schema, ref_path):
    # Currently only treats references starting with "#"!
    # Others have to be implemented additionaly if needed
    # As I've seen to this date, haven't seen any uses different from "#..."

    # if ref_path == '#':
    #     exc = RecursionError("Ref to self")
    #     logging.exception(exc)
    #     raise exc

    split_res = ref_path.split('#')
    split_res.append('')
    root_, key_ = split_res[0], split_res[1]
    res = resolveKey(key_, original_schema)

    return res, tuple(key_.split('/')[1:])

def resolveKey(key_, tree_):
    while key_.startswith('/'):
        key_ = key_[1:]
    ref_key = key_.split('/')
    for step in ref_key:
        if not step:
            continue
        try:
            tree_ = tree_[step]
        except KeyError:
            print("WRONG")
    return tree_

def getToPath(schema, path):
    for step in path:
        schema = schema[step]
    return schema


if __name__ == "__main__":
    main((sys.argv)[1:])
