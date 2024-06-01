import sys
import argparse

import json

def main(argv):
    parser = argparse.ArgumentParser(description = "prototype experiment program of JSD")
    parser.add_argument('--in_path')
    parser.add_argument('--out_path')

    args = parser.parse_args(argv)  
    print(args)

    with open(args.in_path, "r") as infile:
        schema = json.load(infile)

    translted_schema = translateKlettke(schema)
    
    with open(args.out_path, "w") as outfile:
        json.dump(translted_schema, outfile, indent = 4)


    

def translateKlettke(schema):
    
    if "type" in schema and type(schema["type"]) == str:
        if schema["type"] == "object":
            return translateObject(schema)
        elif schema["type"] == "array":
            return translateArray(schema)
        elif schema["type"] in ["integer", "string", "number", "boolean", "null"]:
            return translatePrimitives(schema)
        else:
            print(schema)
            raise Exception("translateKlettke: Undefined schema in single type!")
        
        
    elif "type" in schema and type(schema["type"]) == list:
        return translateListOfSchemas(schema)
    
    elif "anyOf" in schema:
        return translateAnyOfSchema(schema)
    
    else:
        print(json.dumps(schema))
        raise Exception("translateKlettke: Undefined schema! Does not have type")




def translateObject(schema):
    to_return = {"type": "object"}

    if "properties" in schema:
        all_keys = sorted(list(schema["properties"].keys()))

        if all_keys:
            to_return["properties"] = {}
            for key in all_keys:
                to_return["properties"][key] = translateKlettke(schema["properties"][key])
        
    if "required" in schema:
        to_return["required"] = schema["required"]        

    return to_return

def translateArray(schema):
    to_return = {"type": "array"}

    if "items" in schema:
        if type(schema["items"]) == list:
            if schema["items"]:
                to_return["items"] = []
                for i, subschema in enumerate(schema["items"]):
                    to_return["items"].append(translateKlettke(subschema))

        if type(schema["items"]) == dict:

            to_return["items"] = translateKlettke(schema["items"])

    return to_return

def translatePrimitives(schema):
    if schema["type"] == "integer": 
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
        raise Exception("translatePrimitives: Undefined schema!")


def translateAnyOfSchema(schema):
    to_return = {"anyOf": []}
    
    for subschema in schema["anyOf"]:
        to_return["anyOf"].append(translateKlettke(subschema))
    
    return to_return
    
    

def translateListOfSchemas(schema):
    to_return = {"anyOf": []}
    used_count = 0
    
    if "integer" in schema["type"] or "number" in schema["type"]:
        to_return["anyOf"].append({"type": "number"})
        used_count += 1
    if "string" in schema["type"]:
        to_return["anyOf"].append({"type": "string"})
        used_count += 1
    if "boolean" in schema["type"]:
        to_return["anyOf"].append({"type": "boolean"})
        used_count += 1
    if "null" in schema["type"]:
        to_return["anyOf"].append({"type": "null"})
        used_count += 1
    
    if "object" in schema["type"]:
        to_return["anyOf"].append(translateObject(schema))
        used_count += 1
    if "array" in schema["type"]:
        to_return["anyOf"].append(translateArray(schema))
        used_count += 1
        
    num_subschemas = len(schema["type"])
    if "integer" in schema["type"] and "number" in schema["type"]: num_subschemas -= 1
    
    if used_count != num_subschemas:
        print()
        print(schema)
        print()
        raise Exception("translateListOfSchemas: Something wrong!")
        
    return to_return

    

if __name__ == "__main__":
    main((sys.argv)[1:])