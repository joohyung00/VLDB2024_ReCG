
from __future__ import print_function

import matplotlib.pyplot as plt
from cycler import cycler
import csv

import sys

import json
import argparse

import statistics 
from copy import deepcopy


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

dataset_to_name = {
    "1": "NYT",
    "3": "Twitter",
    "4": "Github",
    "5": "Pharmaceutical",
    "6": "Wikidata",
    "7": "Yelp",
    "8": "VK",
    "9": "OpenWeather",
    "12": "Iceberg",
    "13": "Ember",
    "21": "ETH",
    "22": "GeoJSON", 
    "23": "ThaiMovies",
    "31": "RBD",
    "32": "AdonisRC", 
    "33": "HelmChart",
    "34": "Dolittle",
    "35": "Drupal",
    "41": "DeinConfig",
    "43": "Ecosystem",
    "44": "Plagiarize"
}



def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode')
    parser.add_argument('--num')

    args = parser.parse_args(argv)  
    print(args)

    if(args.mode == "dataset"):
        datasetInfo(args.num)
    elif(args.mode == "all"):
        for num in ["1", "3", "4", "5", "6", "7", "8", "9", "12", "13", "21"
                    "22", "23",
                    "31", "32", "33", "34", "35",
                    "41", "43", "44"]:
            datasetInfo(num)
    
    return


    
    
def datasetInfo(num):
    schema_path, dataset_path = datasets[num]
    # print(dataset_path)
    directory = "/mnt/SchemaDataset/"
    schema_path = directory + schema_path
    dataset_path = directory + dataset_path
    
    to_print = ""
    to_print += " & " + dataset_to_name[num] + " & "
    
    with open(schema_path, "r") as file:
        schema = json.load(file)
    agg = getSchemaMetadata(schema)

    # str(agg["MaxLevel"]) + " & " + \
    to_print += str(checkSchemaLevel(schema)) + " & " + \
                str(schemaSize(schema)) + " & " + \
                str(agg["HomObj Nodes"]) + " & " + \
                str(agg["HetObj Nodes"]) + " & " + \
                str(agg["ComObj Nodes"]) + " & " + \
                str(agg["HomArr Nodes"]) + " & " + \
                str(agg["HetArr Nodes"]) + " & " + \
                str(agg["AnyOf Nodes"]) + " & "
    
    # Instances Num
    agg = checkInstances(dataset_path)
    to_print += str(agg["Instance Num"]) + " & " + \
                ('%.2f' % agg["Average Nodes"]) + " \\\\ \\cline{2-12}"
                
    print(to_print)
    
    
    
    


#####################################################
# checkSchemaLevel                                  #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def getSchemaMetadata(schema):
    agg = {
        "Max Level": 0,
        "Schema Nodes": 0,
        "HomObj Nodes": 0,
        "HetObj Nodes": 0,
        "ComObj Nodes": 0,
        "HomArr Nodes": 0,
        "HetArr Nodes": 0,
        "AnyOf Nodes": 0
    }
    
    if "definitions" in schema:
        for key in schema["definitions"]:
            getSchemaMetadataRecursive(schema["definitions"][key], agg)
    getSchemaMetadataRecursive(schema, agg)
            
    return agg


def getSchemaMetadataRecursive(schema, metadata):

    if "type" in schema and schema["type"] == "object":
        
        if isEmptyObjectSchema(schema):
            metadata["HomObj Nodes"] += 1
            
            return
        
        elif isHomObjectSchema(schema):

            metadata["HomObj Nodes"] += 1
            
            for key in schema["properties"]:
                getSchemaMetadataRecursive(schema["properties"][key], metadata)

            return

        elif isComObjectSchema(schema):
            
            metadata["ComObj Nodes"] += 1

            for key in schema["properties"]:
                getSchemaMetadataRecursive(schema["properties"][key], metadata)
            getSchemaMetadataRecursive(schema["additionalProperties"], metadata)

            return

        elif isHetObjectSchema(schema):
            metadata["HetObj Nodes"] += 1
            
            getSchemaMetadataRecursive(schema["additionalProperties"], metadata)
    
            return

        else:
            print(json.dumps(schema))
            print("Undefined type of schema 1")

    elif "type" in schema and schema["type"] == "array":
        
        if isEmptyArraySchema(schema):
            metadata["HomArr Nodes"] += 1
            
            return
        
        elif isHomArraySchema(schema):
            metadata["HomArr Nodes"] += 1
            
            if "items" in schema:
                schema["prefixItems"] = schema["items"]
                del schema["items"]

            for subschema in schema["prefixItems"]:
                getSchemaMetadataRecursive(subschema, metadata)
                
            return 

        elif isHetArraySchema(schema):
            metadata["HetArr Nodes"] += 1
            
            getSchemaMetadataRecursive(schema["items"], metadata)
            
            return

        else:
            print(json.dumps(schema))
            print("Undefined type of schema 2")

    elif "anyOf" in schema or "oneOf" in schema:
        metadata["AnyOf Nodes"] += 1
        if "oneOf" in schema:
            schema["anyOf"] = schema["oneOf"]
            del schema["oneOf"]
                    
        for subschema in schema["anyOf"]:
            getSchemaMetadataRecursive(subschema, metadata)
        
        return
    
    elif "$ref" in schema:
        return
    
    elif "type" in schema and schema["type"] == "string":
        return
    elif "type" in schema and schema["type"] == "integer":
        return 
    elif "type" in schema and schema["type"] == "number":
        return 
    elif "type" in schema and schema["type"] == "boolean":
        return 
    elif "type" in schema and schema["type"] == "null":
        return 
    
    else:
        print(json.dumps(schema))
        raise Exception("Error 999: Unexpected schema in SRC")









#####################################################
# checkSchemaLevel                                  #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################

def checkSchemaLevel(schema):
    agg = {}
    try:
        schema = unreference_schema(schema)
    except:
        return "\\infty"
    return recursiveCheckSchemaLevel(schema)
            
def recursiveCheckSchemaLevel(schema):
    if "type" in schema and schema["type"] == "object":
        levels = []
        if  ("properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] == False) or \
            ("properties" in schema and "additionalProperties" not in schema):
            if schema["properties"] == {}:
                return 1
            for key in schema["properties"]:
                levels.append(recursiveCheckSchemaLevel(schema["properties"][key]))
        elif "properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] != False:
            for key in schema["properties"]:
                levels.append(recursiveCheckSchemaLevel(schema["properties"][key]))
            levels.append(recursiveCheckSchemaLevel(schema["additionalProperties"]))
        elif "additionalProperties" in schema and schema["additionalProperties"] != False:
            levels.append(recursiveCheckSchemaLevel(schema["additionalProperties"]))
        else:
            print("Undefined type of schema")
        return max(levels) + 1
    
    elif "type" in schema and schema["type"] == "array":
        levels = []
        if "items" in schema and type(schema["items"]) is list:
            for subschema in schema["items"]:
                levels.append(recursiveCheckSchemaLevel(subschema))
        elif "prefixItems" in schema:
            for subschema in schema["prefixItems"]:
                levels.append(recursiveCheckSchemaLevel(subschema))
        elif "items" in schema and type(schema["items"]) is dict:
            levels.append(recursiveCheckSchemaLevel(schema["items"]))
        else:
            print("Undefined type of schema")
        return max(levels) + 1
    
    elif "anyOf" in schema:
        levels = []
        for subschema in schema["anyOf"]:
            levels.append(recursiveCheckSchemaLevel(subschema))
        return max(levels) + 1
            
    else:
        return 1
    
    
    
#####################################################
# checkSchemaLevel                                  #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################


def schemaSize(schema):
    try:
        schema = unreference_schema(schema)
    except:
        return "\\infty"
    return schemaSizeRecursive(schema)

    
def schemaSizeRecursive(schema):
    if "type" in schema and schema["type"] == "object":
        size = 0
        if  ("properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] == False) or \
            ("properties" in schema and "additionalProperties" not in schema):
            for key in schema["properties"]:
                size += schemaSizeRecursive(schema["properties"][key])
                
        elif "properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] != False:
            for key in schema["properties"]:
                size += schemaSizeRecursive(schema["properties"][key])
            size += schemaSizeRecursive(schema["additionalProperties"])
            
        elif "additionalProperties" in schema and schema["additionalProperties"] != False:
            size += schemaSizeRecursive(schema["additionalProperties"])
            
        else:
            print("Undefined type of schema")
        return size + 1
    
    elif "type" in schema and schema["type"] == "array":
        size = 0
        if "items" in schema and type(schema["items"]) is list:
            for subschema in schema["items"]:
                size += schemaSizeRecursive(subschema)
                
        elif "prefixItems" in schema:
            for subschema in schema["prefixItems"]:
                size += schemaSizeRecursive(subschema)
                
        elif "items" in schema and type(schema["items"]) is dict:
            size += schemaSizeRecursive(schema["items"])
            
        else:
            print("Undefined type of schema")
            
        return size + 1
    
    elif "anyOf" in schema:
        size = 0
        for subschema in schema["anyOf"]:
            size += schemaSizeRecursive(subschema)
        return size + 1
            
    else:
        return 1


#####################################################
# checkSchemaLevel                                  #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#                                                   #
#####################################################



def recursiveCheckSchema(schema, agg):
    if "type" in schema and schema["type"] == "object":
        # Homogeneous
        if  ("properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] == False) or \
            ("properties" in schema and "additionalProperties" not in schema):
            agg["HomObj Nodes"] += 1
            for key in schema["properties"]:
                recursiveCheckSchema(schema["properties"][key], agg)
        elif "properties" in schema and "additionalProperties" in schema and schema["additionalProperties"] != False:
            agg["ComObj Nodes"] += 1
            for key in schema["properties"]:
                recursiveCheckSchema(schema["properties"][key], agg)
            recursiveCheckSchema(schema["additionalProperties"], agg)
        elif "additionalProperties" in schema and schema["additionalProperties"] != False:
            agg["HetObj Nodes"] += 1
            recursiveCheckSchema(schema["additionalProperties"], agg)
        else:
            print("Undefined type of schema")
    
    elif "type" in schema and schema["type"] == "array":
        if "items" in schema and type(schema["items"]) is list:
            agg["HomArr Nodes"] += 1
            for subschema in schema["items"]:
                recursiveCheckSchema(subschema, agg)
        elif "prefixItems" in schema:
            agg["HomArr Nodes"] += 1
            for subschema in schema["prefixItems"]:
                recursiveCheckSchema(subschema, agg)
        elif "items" in schema and type(schema["items"]) is dict:
            agg["HetArr Nodes"] += 1
            recursiveCheckSchema(schema["items"], agg)
        else:
            print("Undefined type of schema")
    
    elif "anyOf" in schema:
        agg["AnyOf Nodes"] += 1
        for subschema in schema["anyOf"]:
            recursiveCheckSchema(subschema, agg)
    else:
        pass
        

def checkInstances(instance_path):
    agg = {}
    with open(instance_path, 'r') as fp:
        for count, line in enumerate(fp):
            pass
    count += 1
    if count > 10000:
        count = 10000
    agg["Instance Num"] = count
    
    count_copied = count
    size_agg = 0
    with open(instance_path, "r") as file:
        for line in file:
            if count_copied < 1:
                break
            count_copied -= 1
            json_ = json.loads(line)
            size_agg += getInstanceSize(json_)
            
    agg["Average Nodes"] = size_agg / count
    
    return agg



def getInstanceSize(instance):
    size = 0
    if type(instance) is dict:
        size = 1
        for key in instance:
            size += getInstanceSize(instance[key])
        return size
    elif type(instance) is list:
        size = 1
        for subinstance in instance:
            size += getInstanceSize(subinstance)
        return size
    else:
        return 1













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



def unreference_schema(original_schema_):
    global orig_schema
    global ref_key

    orig_schema = original_schema_
    
    to_return = unreference(orig_schema)

    try:
        del to_return[ref_key]
    except:
        a = 1

    return to_return

def unreference(schema):
    if type(schema) is list:
        for i, subschema in enumerate(schema):
            # print(i)
            schema[i] = unreference(subschema)
        return schema

    elif type(schema) is dict:
        keys = schema.keys()

        if "$ref" in keys:
            unreferenced_schema = deepcopy(reference_to_tree(schema["$ref"]))
            all_unreferenced = unreference(unreferenced_schema)
            return all_unreferenced
        else:
            for key in keys:
                schema[key] = unreference(schema[key])            
            return schema

    return schema


def reference_to_tree(ref_path):
    # Currently only treats references starting with "#"!
    # Others have to be implemented additionaly if needed
    # As I've seen to this date, haven't seen any uses different from "#..."

    path_list = ref_path.split('/')

    global orig_schema
    global ref_key
    schema = orig_schema

    if path_list[0] == "#":
        ref_key = path_list[1]
        for step in path_list[1:]:
            schema = schema[step]
        return schema

    # print(ref_path)
    raise Exception("UNDEFINED REFERENCE")

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








if __name__=="__main__":
    main((sys.argv)[1:])