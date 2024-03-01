import sys
import argparse

import json


def translate_kreduce(filepath, output_path):
    with open(filepath, "r") as kreduce_file:
       for line in kreduce_file:
            schema = json.loads(line)
            break

    data = schema["schema"]

    with open(output_path, "w") as outfile:
        json.dump(probe_kreduce(data), outfile)


def probe_kreduce(data):
    kind = data["__Kind"]
    if kind == "NumType":
        return {"type": "number"}
    elif kind == "StrType":
        return {"type": "string"}
    elif kind == "NullType":
        return {"type": "null"}
    elif kind == "BoolType":
        return {"type": "boolean"}

    elif kind == "Union":
        return translate_union(data)
    elif kind == "Record":
        return translate_object(data)
    elif kind == "Array":
        return translate_array(data)
    else:
        return {}


def translate_union(data):
    oneOf = []

    for subschema in data["__Content"]:
        oneOf.append(probe_kreduce(subschema))

    return {"anyOf": oneOf}

def translate_object(data):
    field_dict = data["__Content"]

    schema = {}
    schema["type"] = "object"
    properties_dict = {}

    all_keys = field_dict.keys()
    required_keys = []

    for key in all_keys:
        
        property_dict = field_dict[key]

        optional = False
        optional_route = None

        for nested_key in property_dict.keys():
            if "__Optional_" in nested_key:
                optional = True
                optional_route = nested_key

        if optional:
            properties_dict[key] = probe_kreduce(field_dict[key][optional_route])
        elif not optional:
            required_keys.append(key)
            properties_dict[key] = probe_kreduce(field_dict[key])

    if properties_dict != {}:
        schema["properties"] = properties_dict
    else:
        schema["maxProperties"] = 0
    
    if required_keys:
        schema["required"] = required_keys

    schema["additionalProperties"] = False

    return schema


def translate_array(data):
    schema = {}

    schema["type"] = "array"
    return_value = probe_kreduce(data["__Content"])
    if return_value == {}:
        schema["maxItems"] = 0
    else:
        schema["items"] = return_value

    return schema



def main(argv):
    parser = argparse.ArgumentParser(description = "prototype experiment program of JSD")
    parser.add_argument('--in_path')
    parser.add_argument('--out_path')

    args = parser.parse_args(argv)  
    print(args)

    translate_kreduce(args.in_path, args.out_path)

    

if __name__ == "__main__":
    main((sys.argv)[1:])