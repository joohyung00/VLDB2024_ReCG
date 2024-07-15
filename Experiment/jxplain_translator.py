import sys
import argparse

import json

sys.path.insert(1, '/root/VLDB2024_ReCG/Experiment')
from load_json import load_dataset, load_schema

def translate_jxplain__(filepath, output_path):
    schema = load_schema(filepath)

    translated_jxplain = translate_jxplain(schema)

    with open(output_path, "w") as outfile:
        json.dump(translated_jxplain, outfile)


def translate_jxplain(schema):
    
    if "type" in schema:
        if schema["type"] == "object":
            to_return = {"type": "object"}

            if "maxItems" in schema and schema["maxItems"] == 0.0:
                to_return["maxProperties"] = 0
                return to_return

            if "additionalProperties" in schema:
                if schema["additionalProperties"] == True:
                    
                    children_schemas = set()
                    properties = schema["properties"]
                    
                    for key in properties.keys():
                        subschema_in_string = json.dumps(properties[key])
                        children_schemas.add(subschema_in_string)
                        
                    if len(children_schemas) == 1:
                        to_return["additionalProperties"] = (json.loads(list(children_schemas)[0]))
                        
                    else:
                        loaded_subschemas = []
                        for child_schema in children_schemas:
                            loaded_subschemas.append(json.loads(child_schema))
                            
                        subschemas = {"oneOf": loaded_subschemas}
                        to_return["additionalProperties"] = translate_jxplain(subschemas)
                    
                    return to_return

            if "properties" in schema:
                all_keys = sorted(list(schema["properties"].keys()))
 
                if all_keys:
                    to_return["properties"] = {}
                    for key in all_keys:
                        to_return["properties"][key] = translate_jxplain(schema["properties"][key])

            if "additionalProperties" in schema:
                if schema["additionalProperties"] == False:
                    to_return["additionalProperties"] = False

            if "properties" in schema and "additionalProperties" not in schema:
                to_return["additionalProperties"] = False
                
            if "required" in schema:
                if schema["required"] != []:
                    to_return["required"] = schema["required"]        

            return to_return

        elif schema["type"] == "array":

            to_return = {"type": "array"}

            if "prefixItems" in schema:

                if schema["prefixItems"]:
                    to_return["prefixItems"] = []
                    for i, subschema in enumerate(schema["prefixItems"]):
                        to_return["prefixItems"].append(subschema)

            elif "items" in schema:
                if type(schema["items"]) == list:
                    if schema["items"]:
                        to_return["items"] = []
                        for i, subschema in enumerate(schema["items"]):
                            to_return["items"].append(translate_jxplain(subschema))

                if type(schema["items"]) == dict:

                    to_return["items"] = translate_jxplain(schema["items"])
                
            elif "maxItems" in schema and schema["maxItems"] == 0.0:
                to_return["maxItems"] = 0

            return to_return

        elif schema["type"] == "integer": 
            return {"type": "number"}
        elif schema["type"] == "string":
            return {"type": "string"}
        elif schema["type"] == "number":
            return {"type": "number"}
        elif schema["type"] == "boolean":
            return {"type": "boolean"}
        elif schema["type"] == "null":
            return {"type": "null"}
        else:
            print(schema)
            raise Exception("Undefined schema!")
        

    elif "oneOf" in schema:
        to_return = {"anyOf": []}
        
        for subschema in schema["oneOf"]:
            if "type" in subschema and subschema["type"] == "array" and "maxItems" in subschema and subschema["maxItems"] == 0.0:
                continue
            
            if "type" in subschema and subschema["type"] == "object" and "maxItems" in subschema and subschema["maxItems"] == 0.0:
                continue
            
            to_return["anyOf"].append(translate_jxplain(subschema))
        
        if len(to_return["anyOf"]) == 1:
            return to_return["anyOf"][0]
        
        return to_return

    elif "anyOf" in schema:
        to_return = {"anyOf": []}
        for subschema in schema["anyOf"]:
            to_return["anyOf"].append(translate_jxplain(subschema))
        return to_return

    else:
        print(json.dumps(schema))
        raise Exception("Undefined schema 2!")
    
    
    
def main(argv):
    parser = argparse.ArgumentParser(description = "prototype experiment program of JSD")
    parser.add_argument('--in_path')
    parser.add_argument('--out_path')

    args = parser.parse_args(argv)  
    print(args)

    translate_jxplain__(args.in_path, args.out_path)
    
if __name__ == "__main__":
    main((sys.argv)[1:])
    
    
    
    
    
    
