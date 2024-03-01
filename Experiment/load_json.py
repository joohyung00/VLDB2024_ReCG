import json
from copy import deepcopy

global orig_schema
global ref_key



def count_lines(file_path):
    line_count = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            line_count += 1
    
    return line_count

def load_dataset(path, data_list):
    # premise: json documents are distinguished in different lines
    with open(path, "r") as json_file:
        for line in json_file:
            try:
                data_list.append(json.loads(line))
            except:
                pass

def load_schema(path):
    # Case 1 is met
    # if false, it is not
    case_1 = True

    # Case 1: file itself is json schema
    try:
        with open(path, "r") as schema_file:
            schema = json.load(schema_file)
    except:
        case_1 = False

    # Case 2: schema is in the last line of the given json file
    if not case_1:
        with open(path, "r") as schema_file:
            for line in schema_file:
                try:
                    new_line = ""
                    for i, char in enumerate(line):
                        if char.encode() == b"\\":
                            if line[i - 1].encode() != b"\\" and line[i + 1].encode() != b"\\":
                                new_line += char
                                new_line += char
                        else:
                            new_line += char
                    schema = json.loads(new_line)
                except:
                    pass

    return schema



def unreference_schema(original_schema_):

    original_schema = deepcopy(original_schema_)

    to_return = unreference(original_schema, original_schema_)

    return to_return


def unreference(original_schema, schema):
    if type(schema) is list:
        for i, subschema in enumerate(schema):
            # print(i)
            schema[i] = unreference(original_schema, subschema)
        return schema

    elif type(schema) is dict:
        keys = schema.keys()

        if "$ref" in keys:
            tgt = schema["$ref"]
            unreferenced_schema = deepcopy(reference_to_tree(original_schema, tgt))
            return unreference(original_schema, unreferenced_schema)
        else:
            for key in keys:
                schema[key] = unreference(original_schema, schema[key])
            return schema

    return schema


def reference_to_tree(original_schema, ref_path):
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
    res = resolve_key(key_, original_schema)

    return res

def resolve_key(key_, tree_):
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