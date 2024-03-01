


import os
import sys
import json
import argparse
from multiprocessing import Pool
from time import sleep

from jsonschema import validate
import jsonschema
from jsonschema.exceptions import ValidationError

sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema

from sklearn.metrics import recall_score, precision_score, f1_score
import statistics

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
from copy import deepcopy


# TODO: Checking if all instances were labelled


out_path = "../exp_mdl.txt"

datasets = \
{
    "1":  ("1_NewYorkTimes/new_york_times.json",     "1_NewYorkTimes/new_york_times_positive.jsonl"         ),
    "3":  ("3_Twitter/twitter_old.json",             "3_Twitter/twitter_positive_10000.jsonl"               ),
    "4":  ("4_Github/merged.json",                   "4_Github/merged_positive.jsonl"                       ),
    "5":  ("5_Pharmaceutical/pharmaceutical.json",   "5_Pharmaceutical/pharmaceutical_positive.jsonl"       ),
    "6":  ("6_Wikidata/wikidata.json",               "6_Wikidata/wikidata_positive.jsonl"                   ),
    "7":  ("7_Yelp/merged.json",                     "7_Yelp/merged_positive.jsonl"                         ),
    "8":  ("8_VK/vk.json",                           "8_VK/vk_positive.jsonl"                               ),
    "9":  ("9_OpenWeather/open_weather.json",        "9_OpenWeather/open_weather_positive.jsonl"            ),
    "12": ("12_Iceberg/iceberg.json",                "12_Iceberg/iceberg_positive.jsonl"                    ),
    "13": ("13_Ember/ember.json",                    "13_Ember/ember_positive.jsonl"                        ),
    "21": ("21_ETH/merged.json",                     "21_ETH/merged_positive.jsonl"                         ),
    "22": ("22_GeoJSON/merged.json",                 "22_GeoJSON/merged_positive.jsonl"                     ),
    "23": ("23_MoviesInThailand/merged.json",        "23_MoviesInThailand/merged_positive.jsonl"            ),
    "31": ("31_RedDiscordBot/red_discordbot.json",   "31_RedDiscordBot/red_discordbot_positive____.jsonl"   ),
    "32": ("32_Adonisrc/adonisrc.json",              "32_Adonisrc/adonisrc_positive____.jsonl"              ),
    "33": ("33_HelmChart/helmchart.json",            "33_HelmChart/helmchart_positive____.jsonl"            ),
    "34": ("34_Dolittle/merged.json",                "34_Dolittle/merged_positive.jsonl"                    ),
    "35": ("35_Drupal/merged.json",                  "35_Drupal/merged_positive.jsonl"                      ),
    "41": ("41_DeinConfig/deinconfig_tree.json",     "41_DeinConfig/deinconfig_positive.jsonl"              ),
    "43": ("43_Ecosystem/ecosystem_tree.json",       "43_Ecosystem/ecosystem_positive.jsonl"                ),
    "44": ("44_Plagiarize/plagiarize.json",          "44_Plagiarize/plagiarize_positive.jsonl"              )
}

dataset_to_name = \
{
    "1": "1_NewYorkTimes",
    "3": "3_Twitter",
    "4": "4_Github",
    "5": "5_Pharmaceutical",
    "6": "6_Wikidata",
    "7": "7_Yelp",
    "8": "8_VK",
    "9": "9_OpenWeather",
    "12": "12_Iceberg",
    "13": "13_Ember",
    "21": "21_ETH",
    "22": "22_GeoJSON",
    "23": "23_MoviesInThailand",
    "31": "31_RedDiscordBot",
    "32": "32_Adonisrc",
    "33": "33_HelmChart",
    "34": "34_Dolittle",
    "35": "35_Drupal",
    "41": "41_DeinConfig",
    "43": "43_Ecosystem",
    "44": "44_Plagiarize"
}


schemaname_to_gtpath = \
{
    "1_NewYorkTimes"        : "/mnt/SchemaDataset/1_NewYorkTimes/new_york_times.json",
    "3_Twitter"             : "/mnt/SchemaDataset/3_Twitter/twitter_old.json",
    "4_Github"              : "/mnt/SchemaDataset/4_Github/merged.json",
    "5_Pharmaceutical"      : "/mnt/SchemaDataset/5_Pharmaceutical/pharmaceutical.json",
    "6_Wikidata"            : "/mnt/SchemaDataset/6_Wikidata/wikidata.json",
    "7_Yelp"                : "/mnt/SchemaDataset/7_Yelp/merged.json",
    "8_VK"                  : "/mnt/SchemaDataset/8_VK/vk.json",
    "9_OpenWeather"         : "/mnt/SchemaDataset/9_OpenWeather/open_weather.json",
    "12_Iceberg"            : "/mnt/SchemaDataset/12_Iceberg/iceberg.json",
    "13_Ember"              : "/mnt/SchemaDataset/13_Ember/ember.json",
    "21_ETH"                : "/mnt/SchemaDataset/21_ETH/merged.json",
    "22_GeoJSON"            : "/mnt/SchemaDataset/22_GeoJSON/merged.json",
    "23_MoviesInThailand"   : "/mnt/SchemaDataset/23_MoviesInThailand/merged.json",
    "31_RedDiscordBot"      : "/mnt/SchemaDataset/31_RedDiscordBot/red_discordbot.json",
    "32_Adonisrc"           : "/mnt/SchemaDataset/32_Adonisrc/adonisrc.json",
    "33_HelmChart"          : "/mnt/SchemaDataset/33_HelmChart/helmchart_.json",
    "34_Dolittle"           : "/mnt/SchemaDataset/34_Dolittle/merged.json",
    "35_Drupal"             : "/mnt/SchemaDataset/35_Drupal/merged.json",
    "41_DeinConfig"         : "/mnt/SchemaDataset/41_DeinConfig/deinconfig_tree.json",
    "43_Ecosystem"          : "/mnt/SchemaDataset/43_Ecosystem/ecosystem_tree.json",
    "44_Plagiarize"         : "/mnt/SchemaDataset/44_Plagiarize/plagiarize.json"
}








#####################################################
# main                                              #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def main(argv):
    parser = argparse.ArgumentParser(description = "prototype experiment program of JSD")
    parser.add_argument("--algo")
    parser.add_argument("--dataset")
    parser.add_argument("--train_perc")
    parser.add_argument("--exp_num")
    parser.add_argument("--schema_path")
    parser.add_argument("--instance_path")

    args = parser.parse_args(argv)
    print(args)

    schema_path = ""
    if args.algo == "groundtruth":
        schema_path = schemaname_to_gtpath[args.dataset]
    else:
        schema_path = args.schema_path
        
    src, drc, accepted_num = MDLExperiment(schema_path, args.instance_path)

    out_str = args.algo + "," + \
                args.dataset + "," + \
                args.train_perc + "," + \
                args.exp_num + "," + \
                str(src) + "," + \
                str(drc) + "," + \
                str(accepted_num) + "\n"

    print("[RESULT]")
    print("SRC: ", src, "\tDRC: ", drc)
    with open(out_path, "a") as file:
        file.write(out_str)



#####################################################
# MDLExperiment                                     #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

METACHAR_NUM = 12

def MDLExperiment(schema_path, instance_path):
    # algorithm, dataset, exp_num, train_perc

    # 1. Get schema and dataset
    print("[1. Loading Instances and Schemas...]")
    
    schema = load_schema(schema_path)
    original_schema = deepcopy(schema)
    instances = []
    load_dataset(instance_path, instances)
    
    print("[1. Loaded Instances, #: ", len(instances), "]\n")

    print("[1.1. Get number of distinct labels]")
    
    distinct_labels = set()
    metadata = {
        "max_obj_len": 0,
        "max_arr_len": 0
    }
    
    for instance in instances:
        getMetadataRecursive(instance, distinct_labels, metadata)
    distinct_labels_num = len(distinct_labels)
        
    print("[1.1. Getting number of distinct labels complete]")

    

    # 2. Calculate SRC
    print("[2. Calculating SRC...]")
    src = 0
    print("  [2. Calculating SRC $ref ]")
    
    for_ref = deepcopy(original_schema)
    if "definitions" in schema:
        for ref_name in for_ref["definitions"]:
            src += calculateSRCRecursive(for_ref["definitions"][ref_name], distinct_labels_num)
    
    print("  [2. Calculating SRC]")    
    for_src = deepcopy(original_schema)
    src += calculateSRCRecursive(for_src, distinct_labels_num)
    
    print("[2. Calculating SRC Complete]")


    # 3. Calculate DRC
    print("[3. Calculating DRC...]\n")

    argments = [(instance, schema, original_schema, distinct_labels_num, metadata["max_obj_len"], metadata["max_arr_len"]) for instance in instances]
    
    total_drc = 0
    successes = 0
    
    outer = process_map(runner, argments)
    success_bits, drc_values = zip(*outer)
    
    # outer = process_map(runner, argments)
    
    print("[3. DRC Calculation Complete]\n")

    # 4. For each schema node, calculate SRC and DRC
    print("[4. Aggregating Results...]")

        # 4.1. Calculate ordinary SRC, DRC
    for success_bit in success_bits:
        if success_bit:
            successes += 1
    for drc_value in drc_values:
        total_drc += drc_value
    drc = total_drc
    
    print("[4. Aggregating Results Complete]")
    
    return src, drc, successes






def runner(inp):
    instance, schema, original_schema, distinct_labels_num, max_obj_len, max_array_len = inp

    success, drc = calculateDRCRecursive(instance, schema, original_schema, bitSize(distinct_labels_num), bitSize(max_obj_len), bitSize(max_array_len))

    if success:
        return success, drc
    else:
        return success, calculateUnacceptedInstanceDRC(instance, distinct_labels_num)







#####################################################
# calculateSRCRecursive                             #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################


def calculateSRCRecursive(schema, distinct_labels_num):

    bit_size = bitSize(distinct_labels_num + METACHAR_NUM)

    if "type" in schema and schema["type"] == "object":
        
        if isEmptyObjectSchema(schema):
            symbol_num = 3
            src = bit_size * symbol_num
            return src
        
        elif isHomObjectSchema(schema):

            labels_num = len(list(schema["properties"].keys()))
            symbol_num = 3 + 4 * labels_num
            src = bit_size * symbol_num
            
            for key in schema["properties"]:
                src += calculateSRCRecursive(schema["properties"][key], distinct_labels_num)

            return src

        elif isComObjectSchema(schema):
            
            sch_labels = set(schema["properties"].keys())
            symbol_num = 3 + 4 * len(sch_labels) + 3
            src = bit_size * symbol_num

            for key in schema["properties"]:
                src += calculateSRCRecursive(schema["properties"][key], distinct_labels_num)
            src += calculateSRCRecursive(schema["additionalProperties"], distinct_labels_num)

            return src

        elif isHetObjectSchema(schema):

            symbol_num = 3
            src = bit_size * symbol_num
            
            src += calculateSRCRecursive(schema["additionalProperties"], distinct_labels_num)
    
            return src

        else:
            print(json.dumps(schema))
            print("Undefined type of schema 1")

    elif "type" in schema and schema["type"] == "array":
        
        if isEmptyArraySchema(schema):
            src = 3 * bit_size

            return src
        
        elif isHomArraySchema(schema):
            if "items" in schema:
                schema["prefixItems"] = schema["items"]
                del schema["items"]
                
            subschema_num = len(schema["prefixItems"])
            src = bit_size * (3 + 3 * subschema_num)

            for subschema in schema["prefixItems"]:
                src += calculateSRCRecursive(subschema, distinct_labels_num)

            return src

        elif isHetArraySchema(schema):
            src = 3 * bit_size
            
            src += calculateSRCRecursive(schema["items"], distinct_labels_num)
            
            return src

        

        else:
            print(json.dumps(schema))
            print("Undefined type of schema 2")

    elif "anyOf" in schema or "oneOf" in schema:
        if "oneOf" in schema:
            schema["anyOf"] = schema["oneOf"]
            del schema["oneOf"]
            
        subschema_len = len(schema["anyOf"])
        src = (subschema_len - 1) * bit_size    
        
        for subschema in schema["anyOf"]:
            src += calculateSRCRecursive(subschema, distinct_labels_num)
        
        return src
    
    elif "$ref" in schema:
        return 0
    
    elif "type" in schema and schema["type"] == "string":
        return 0
    elif "type" in schema and schema["type"] == "integer":
        return 0
    elif "type" in schema and schema["type"] == "number":
        return 0
    elif "type" in schema and schema["type"] == "boolean":
        return 0
    elif "type" in schema and schema["type"] == "null":
        return 0
    
    else:
        print(json.dumps(schema))
        raise Exception("Error 999: Unexpected schema in SRC")




#####################################################
# calculateDRCRecursive                             #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def calculateDRCRecursive(instance, schema, original_schema, kleene_bits, obj_length_bits, arr_length_bits):
    
    # Case A. $ref -> unref
    if "$ref" in schema:
        schema, _ = getReferencingNode(original_schema, schema["$ref"])
        
    # Case B. AnyOf
    if "anyOf" in schema:
        drc = bitSize(len(schema["anyOf"]))
        
        smallest_drc = 100000000000000000
        success = False
        
        for subschema in schema["anyOf"]:
            subschema_success, subschema_drc = calculateDRCRecursive(instance, subschema, original_schema, kleene_bits, obj_length_bits, arr_length_bits)
            success |= subschema_success
            
            if subschema_success and subschema_drc < smallest_drc:
                smallest_drc = subschema_drc
        
        if success:
            return success, drc + smallest_drc
        else:
            return False, 0
    
    # Now look at instance
    if (type(instance) is int) or (type(instance) is float):
        if "type" in schema and (schema["type"] == "number" or schema["type"] == "integer"):
            return True, 0
        else:
            return False, 0
    
    elif type(instance) is str:
        if "type" in schema and schema["type"] == "string":
            return True, 0
        else:
            return False, 0
    
    elif type(instance) is bool:
        if "type" in schema and schema["type"] == "boolean":
            return True, 0
        else:
            return False, 0
        
    elif instance == None:
        if "type" in schema and schema["type"] == "null":
            return True, 0
        else:
            return False, 0
        
    elif type(instance) is dict:
        # Check type
        if "type" in schema and schema["type"] != "object":
            return False, 0

        if isEmptyObjectSchema(schema):
            if len(instance) == 0:
                return True, 0
            else:
                return False, 0


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
                return False, 0

            # Check if all required keys appeared
            if not (schema_required_keys <= instance_keys):
                return False, 0
            
            drc = len(schema_optional_keys)
            success = True
            for key in instance.keys():
                sub_success, sub_drc = calculateDRCRecursive(instance[key], schema["properties"][key], original_schema, kleene_bits, obj_length_bits, arr_length_bits)
                success &= sub_success
                drc += sub_drc
            
            return success, drc
            
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
                return False, 0
            
            
            kleene_keys = instance_keys - schema_all_keys
            
            drc = len(schema_optional_keys) + obj_length_bits + len(kleene_keys) * kleene_bits
            success = True
            for key in instance.keys():
                if key in kleene_keys:
                    sub_success, sub_drc = calculateDRCRecursive(instance[key], schema["additionalProperties"], original_schema, kleene_bits, obj_length_bits, arr_length_bits)
                    success &= sub_success
                    drc += sub_drc
                else:
                    sub_success, sub_drc = calculateDRCRecursive(instance[key], schema["properties"][key], original_schema, kleene_bits, obj_length_bits, arr_length_bits)
                    success &= sub_success
                    drc += sub_drc
            
            return success, drc
        
        elif isHetObjectSchema(schema):
            success = True
            drc = obj_length_bits + len(instance) * kleene_bits
            
            for key in instance:
                sub_success, sub_drc = calculateDRCRecursive(instance[key], schema["additionalProperties"], original_schema, kleene_bits, obj_length_bits, arr_length_bits)
                success &= sub_success
                drc += sub_drc
                
            return success, drc
            
        else:
            print(json.dumps(schema))
            print(json.dumps(instance))
            raise Exception("Error 3")
    
    
    elif type(instance) is list:
        # Check type
        if "type" in schema and schema["type"] != "array":
            return False, 0
        
        if isHomArraySchema(schema):
            if "items" in schema:
                schema["prefixItems"] = schema["items"]
            
            if len(instance) != len(schema["prefixItems"]):
                return False, 0
            
            success = True
            drc = 0
            for i, _ in enumerate(instance):
                sub_success, sub_drc = calculateDRCRecursive(instance[i], schema["prefixItems"][i], original_schema, kleene_bits, obj_length_bits, arr_length_bits)
                success &= sub_success
                drc += sub_drc
        
            return success, drc
        
        elif isHetArraySchema(schema):
            success = True
            drc = arr_length_bits
            for subinstance in instance:
                sub_success, sub_drc = calculateDRCRecursive(subinstance, schema["items"], original_schema, kleene_bits, obj_length_bits, arr_length_bits)
                success &= sub_success
                drc += sub_drc
                
            return success, drc
        
        elif isEmptyArraySchema(schema):
            if len(instance) == 0:
                return True, 0
            else:
                return False, 0
        
        else:
            print(json.dumps(schema))
            print(json.dumps(instance))
            raise Exception("Error 4")
    
    else:
        print(json.dumps(schema))
        print(json.dumps(instance))
        raise Exception("Error 1")
        
    
    
    





#########################################################
# calculateUnacceptedInstanceDRC                        #
#                                                       #
# In: instance                                          #
# Out1: Number of bits needed to encode this instance   #
# Out1: Distinct symbols needed to encode this instance #
#                                                       #
#########################################################

def calculateUnacceptedInstanceDRC(instance, distinct_labels_num):
    bits_needed = InstanceDRCRecursive(instance)

    return bits_needed * bitSize(METACHAR_NUM + distinct_labels_num)


def InstanceDRCRecursive(instance):

    bits_needed = 0

    if type(instance) is dict:

        for key in instance:
            bits_needed += 3
            sub_bits_needed = InstanceDRCRecursive(instance[key])
            bits_needed += sub_bits_needed

        return bits_needed

    elif type(instance) is list:

        for subinstance in instance:
            bits_needed += 2
            sub_bits_needed = InstanceDRCRecursive(subinstance)
            bits_needed += sub_bits_needed

        return bits_needed

    else:
        return 0



#####################################################
# getDistinctLabelsRecursive                        #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def getMetadataRecursive(instance, distinct_labels, metadata):
    if type(instance) is dict:
        keys = set(instance.keys())
        distinct_labels.update(keys)
        
        if len(keys) > metadata["max_obj_len"]:
            metadata["max_obj_len"] = len(keys)
        
        for key in keys:
            getMetadataRecursive(instance[key], distinct_labels, metadata)
        
    elif type(instance) is list:
        if len(instance) > metadata["max_arr_len"]:
            metadata["max_arr_len"] = len(instance)
        for subinstance in instance:
            getMetadataRecursive(subinstance, distinct_labels, metadata)
    else:
        return


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


#####################################################
# UTILS                                             #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def clearDict(dict_):
    for key in dict_:
        dict_[key].clear()

def extendDictionaries(to_dict, from_dict):
    for key in to_dict:
        to_dict[key].extend(from_dict[key])

def getSchemaWithPath(schema, path):
    if len(path) == 0:
        return schema
    else:
        return getSchemaWithPath(schema[path[0]], path[1:])

def encodeLength(length):
    return 2 * bitSize(length) + 1

def bitSize(length):
    return (length - 1).bit_length()















if __name__ == "__main__":
    main((sys.argv)[1:])
