from copy import deepcopy
import json

import random
import sys
sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_dataset, load_schema

from pprint import pprint



global goal_schema
global candidate_dict
global definition_path



def initiate_schema_candiates(schema):
    global goal_schema
    global candidate_dict
    global definition_path

    definition_path = None

    # Initialize
    candidate_dict = {}
    goal_schema = schema

    # Unreference
    try:
        goal_schema = unreference(schema)
        
        if definition_path:
            try:
                del goal_schema[definition_path]
            except:
                pass
    except:
        pass
    
    

    # Correct, mainly default value of additionalProperties
    addAdditionalPropertiesFalse(goal_schema)

    #################################################
    ######## Fileprint corrected goal schema ########
    #################################################

    # Mark
    probe_to_mark(goal_schema, [], 0)
    if "definitions" in goal_schema:
        for ref in goal_schema["definitions"]:
            probe_to_mark(goal_schema["definitions"][ref], ["definitions", ref], 0)

    print(json.dumps(candidate_dict))

    return candidate_dict


def probe_to_mark(schema, path, nesting_level):

    # Marking if it is a candidate
    mark_target(schema, path, nesting_level)

    # Keep probing
    if type(schema) is list:
        for i, subschema in enumerate(schema):
            copied_path = deepcopy(path)
            copied_path.append(i)
            probe_to_mark(subschema, copied_path, nesting_level)
        return

    elif type(schema) is dict:
        keys = schema.keys()
        
        if "type" in keys:
            if schema["type"] == "object" or schema["type"] == "array":
                nesting_level += 1

        for key in keys:
            copied_path = deepcopy(path)
            copied_path.append(key)
            probe_to_mark(schema[key], copied_path, nesting_level)
        return
    


    return


def mark_target(schema, path, nesting_level):

    if not (type(schema) is dict):
        return

    if "type" in schema:
        
        if schema["type"] == "number":
            add_candidate_dict("change_type", nesting_level, path)
        #    mark_number(schema, path, nesting_level)

        elif schema["type"] == "string":
            add_candidate_dict("change_type", nesting_level, path)
        #    mark_string(schema, path, nesting_level)

        elif schema["type"] == "boolean":
            add_candidate_dict("change_type", nesting_level, path)

        elif schema["type"] == "integer":
            add_candidate_dict("change_type", nesting_level, path)
        #    mark_number(schema, path, nesting_level)

        elif schema["type"] == "object":
            add_candidate_dict("change_type", nesting_level, path)
            mark_object(schema, path, nesting_level)

        elif schema["type"] == "array":
            add_candidate_dict("change_type", nesting_level, path)
            mark_array(schema, path, nesting_level)
        return 

    else:
        # enum
        # if "enum" in schema:
        #     add_candidate_dict("enum", nesting_level, path)
        # # const
        # if "const" in schema:
        #     add_candidate_dict("const", nesting_level, path)

        # composition
        
        if "anyOf" in schema:
            mark_anyOf(schema, path, nesting_level)
            return
        elif "oneOf" in schema:
            mark_anyOf(schema, path, nesting_level)
            return
        # elif "allOf" in schema:
        #     mark_allOf(schema, path, nesting_level)

    return


###############################################################################
################################### NUMBER ####################################
###############################################################################

def mark_number(schema, path, nesting_level):

    global candidate_dict
    keys = schema.keys()

    if "minimum" in keys:
        add_candidate_dict("number_minimum", nesting_level, path)
    if "maximum" in keys:
        add_candidate_dict("number_maximum", nesting_level, path)

    if "enum" in keys:
        add_candidate_dict("enum_number", nesting_level, path)

    if "multipleOf" in keys:
        add_candidate_dict("number_multipleOf", nesting_level, path)

    return


###############################################################################
################################### STRING ####################################
###############################################################################

def mark_string(schema, path, nesting_level):

    global candidate_dict
    keys = schema.keys()

    if "minLength" in keys and schema["minLength"] != 0:
        add_candidate_dict("string_minLength", nesting_level, path)
    if "maxLength" in keys:
        add_candidate_dict("string_maxLength", nesting_level, path)

    if "enum" in keys:
        add_candidate_dict("enum_string", nesting_level, path)

    if "pattern" in keys:
        add_candidate_dict("string_pattern", nesting_level, path)

    if "format" in keys:
        add_candidate_dict("string_format", nesting_level, path)
    
    return


##############################################################################
################################### ARRAY ####################################
##############################################################################


def mark_array(schema, path, nesting_level):
    keys = schema.keys()

    # if "minItems" in keys and schema["minItems"] != 0:
    #     add_candidate_dict("array_minItems", nesting_level, path)
    # if "maxItems" in keys:
    #     add_candidate_dict("array_maxItems", nesting_level, path)

    # if "uniqueItems" in keys and schema["uniqueItems"] == True:
    #     add_candidate_dict("array_uniqueItems", nesting_level, path)

    if "items" in keys:
        if type(schema["items"]) is list:
            add_candidate_dict("array_tuple_add", nesting_level, path)
            add_candidate_dict("array_tuple_delete", nesting_level, path)

        if type(schema["items"]) is dict and "anyOf" in schema["items"].keys():
            add_candidate_dict("array_collection_anyOf", nesting_level, path)

            # Add new schema under anyOf
            # Edit Add contains to mandate the added schema
        else:
            add_candidate_dict("array_collection_single", nesting_level, path)
    elif "prefixItems" in keys:
        add_candidate_dict("array_tuple_add", nesting_level, path)
        add_candidate_dict("array_tuple_delete", nesting_level, path)



###############################################################################
################################### OBJECT ####################################
###############################################################################

def mark_object(schema, path, nesting_level):
    keys = schema.keys()

    # if "minProperties" in keys:
    #     add_candidate_dict("object_minProperties", nesting_level, path)
    # if "maxProperties" in keys:
    #     add_candidate_dict("object_maxProperties", nesting_level, path)

    # Property를 제거
    if "required" in keys and len(schema["required"]) >= 1:
        add_candidate_dict("object_delete_required_property", nesting_level, path)

    # Property를 추가
    if not ("additionalProperties" not in schema) and not ("additionalProperties" in schema and schema["additionalProperties"] == True): 
        add_candidate_dict("object_add_property", nesting_level, path)


    # ##### if-then, allOf
    # if "if" in keys and "then" in keys:
    #     copied_path = deepcopy(path)
    #     copied_path.append("then")
    # 
    #     subschema = schema["then"]
    # 
    #     if "required" in subschema.keys() and len(subschema["required"]) >= 1:
    #         add_candidate_dict("object_delete_required_property", nesting_level, copied_path)
    # 
    #     if not ("additionalProperties" not in subschema) and not ("additionalProperties" in subschema and subschema["additionalProperties"] == True):
    #         add_candidate_dict("object_add_property", nesting_level, copied_path)


    if "allOf" in keys:
        for i, subschema in enumerate(schema["allOf"]):
            copied_path = deepcopy(path)
            copied_path.append("allOf")
            copied_path.append(i)

            if "required" in subschema.keys() and len(subschema["required"]) >= 1:
                add_candidate_dict("object_delete_required_property", nesting_level, copied_path)

            # Property를 추가
            if not ("additionalProperties" not in subschema) and not ("additionalProperties" in subschema and subschema["additionalProperties"] == True): 
                add_candidate_dict("object_add_property", nesting_level, copied_path)
            
            # if "if" in subschema.keys() and "then" in subschema.keys():
            #     copied_path = deepcopy(path)
            #     copied_path.append("allOf")
            #     copied_path.append(i)
            #     copied_path.append("then")
            # 
            #     subschema = subschema["then"]
            # 
            #     if "required" in subschema.keys() and len(subschema["required"]) >= 1:
            #         add_candidate_dict("object_delete_required_property", nesting_level, copied_path)
            # 
            #     if not ("additionalProperties" not in subschema) and not ("additionalProperties" in subschema and subschema["additionalProperties"] == True):
            #         add_candidate_dict("object_add_property", nesting_level, copied_path)
    
    return

####################################################################################
################################### COMPOSITION ####################################
####################################################################################

def mark_anyOf(schema, path, nesting_level):
    subschemas = schema["anyOf"]

    object_collection = 0
    object_tuple = 0
    array_schema_num = 0

    for subschema in subschemas:
        
        try:
            if subschema["type"] == "object":
                if "additionalProperties" in subschema and subschema["additionalProperties"] != False:
                    object_collection += 1
                else:
                    object_tuple += 1                
            elif subschema["type"] == "array" and "items" in subschema and type(subschema["items"]) is dict:
                array_schema_num += 1
            else:
                pass
        except:
            pass
    
    if object_collection > 1:
        add_candidate_dict("anyOf_object_collection", nesting_level, path)
    if object_tuple > 1:
        add_candidate_dict("anyOf_object_tuple", nesting_level, path)
    if object_collection > 0 and object_tuple > 0:
        add_candidate_dict("anyOf_object_tuple_collection", nesting_level, path)
    if array_schema_num > 1:
        add_candidate_dict("anyOf_array_collection", nesting_level, path)
    


def mark_allOf(schema, path, nesting_level):
    add_candidate_dict("allOf", nesting_level, path)


####################################################################################
################################# subfunctions #####################################
####################################################################################


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

    global definition_path

    path_list = ref_path.split('/')

    global goal_schema
    schema = goal_schema

    if path_list[0] == "#":
        definition_path = path_list[1]
        for step in path_list[1:]:
            schema = schema[step]
        return schema

    # print(ref_path)
    raise Exception("UNDEFINED REFERENCE")

def addAdditionalPropertiesFalse(schema):
    global original_schema

    if type(schema) is list:
        for i, subschema in enumerate(schema):
            addAdditionalPropertiesFalse(subschema)
        return

    elif type(schema) is dict:
        keys = schema.keys()
        
        for key in keys:
            addAdditionalPropertiesFalse(schema[key])

        if "type" in keys and schema["type"] == "object":
            if "additionalProperties" not in schema:
                schema["additionalProperties"] = False

        return

    return

def add_candidate_dict(operation, nesting_level, path):
    global candidate_dict

    if operation not in candidate_dict.keys():
        candidate_dict[operation] = []

    candidate_dict[operation].append( (path, nesting_level) )
