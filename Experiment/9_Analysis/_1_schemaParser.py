import csv
import json
import os
from copy import deepcopy

import jsonschema
import requests
from jsonschema import Draft7Validator
# from tqdm import tqdm




class Logger:
    def __init__(self) -> None:
        self.f = open("schema_parser_errors.log", "w")

    def info(self, msg):
        pass
        # self.f.write(msg + "\n")

    def exception(self, exc):
        self.f.write(str(exc) + "\n")

    def close(self):
        self.f.close()
logging = Logger()

import time


# def run_with_timeout__(func, timeout, *args, **kwargs):
#     start_time = time.time()
#     result = None
    
#     try:
#         while True:
#             result = func(*args, **kwargs)
#             if result is not None:
#                 break
            
#             elapsed_time = time.time() - start_time
#             if elapsed_time >= timeout:
#                 raise TimeOutError("Function execution time exceeded the timeout.")
            
#             time.sleep(0.1)  # Adjust the sleep duration as needed
#     except KeyboardInterrupt:
#         raise TimeOutError("TimeOUT!")
    
#     return result


def run_with_timeout(func, timeout, *args, **kwargs):
    import signal

    # Register an handler for the timeout
    def handler(signum, frame):
        print("Forever is over!")
        raise TimeOutError("end of time")

    # This function *may* run for an indetermined time...
    def loop_forever():
        import time
        while 1:
            time.sleep(1)
            
    # Register the signal function handler
    signal.signal(signal.SIGALRM, handler)

    # Define a timeout for your function
    signal.alarm(timeout)

    try:
        return_value = func(*args, **kwargs)
    except KeyboardInterrupt:
        raise TimeOutError("TimeOUT!")
    except TimeOutError:
        raise TimeOutError("TimeOUT!")
    except Exception as exc:
        raise exc

    # Cancel the timer if the function returned before timeout
    # (ok, mine won't but yours maybe will :)
    signal.alarm(0)

    return return_value        




class InvalidArrayItemException(Exception):
    def __init__(self):
        super().__init__("Undefined schema: array - non-object/list items")


class InvalidSchemaTypeException(Exception):
    def __init__(self, msg):
        super().__init__(f"Undefined schema: schema with undefined type {msg}!")

class RequestError(Exception):
    def __init__(self, msg):
        super().__init__(f"Request Error: bad request of {msg}!")


class InvalidConstTypeException(Exception):
    def __init__(self):
        super().__init__("Undefined schema: const")


class KnownKeywordNotFoundException(Exception):
    def __init__(self):
        super().__init__(
            "Undefined schema: no type, not enum/const, not one/any/allOf!")


class OverlappingAdditionalPropertiesException(Exception):
    def __init__(self):
        super().__init__("Unimplemented schema: overlapping additionals...!")


class UndefinedReferenceException(Exception):
    def __init__(self, msg="UNDEFINED REFERENCE"):
        super().__init__(msg)

class TimeOutError(Exception):
    def __init__(self, msg="TIMTEOUT"):
        super().__init__(msg)




def normalize_object_schema(schema):
    if "allOf" in schema:
        schemas_to_be_merged = []

        for sub_anyof in schema["allOf"]:
            properties = {}
            required = []
            additionalProperties = {}

            if "properties" in sub_anyof:
                properties = {}
                for key in sub_anyof["properties"].keys():
                    properties[key] = normalize_schema(
                        sub_anyof["properties"][key])

            if "required" in sub_anyof:
                required = sub_anyof["required"]

            if "additionalProperties" in sub_anyof:
                if type(sub_anyof["additionalProperties"]) is bool:
                    additionalProperties = sub_anyof["additionalProperties"]
                else:
                    additionalProperties = normalize_schema(sub_anyof["additionalProperties"])

            if "patternProperties" in sub_anyof:
                subschemas = []
                for key in sub_anyof["patternProperties"]:
                    subschemas.append(normalize_schema(sub_anyof["patternProperties"][key]))
                
                if type(additionalProperties) is dict and additionalProperties != {}:
                    if "anyOf" in additionalProperties:
                        if len(subschemas) == 0:
                            pass
                        elif len(subschemas) == 1:
                            additionalProperties["anyOf"].append(subschemas[0])
                        elif len(subschemas) > 1:
                            additionalProperties["anyOf"].extend(subschemas)
                    else:
                        if len(subschemas) == 0:
                            pass
                        elif len(subschemas) == 1:
                            additionalProperties = {"anyOf": [additionalProperties, subschemas[0]]}
                        elif len(subschemas) > 1:
                            additionalProperties = {"anyOf": [additionalProperties]}
                            additionalProperties["anyOf"].extend(subschemas)
                else:
                    if len(subschemas) > 1:
                        additionalProperties = {"anyOf": subschemas}
                    else:
                        additionalProperties = subschemas[0]

            schemas_to_be_merged.append(
                {"properties": properties, "required": required,
                 "additionalProperties": additionalProperties})
            
        copied_schema = deepcopy(schema)
        del copied_schema["allOf"]
        copied_schema = normalize_schema(copied_schema)

        schemas_to_be_merged[0] = andmerge_object_schemas(copied_schema, schemas_to_be_merged[0])

        from functools import reduce
        reduced_schema = reduce(andmerge_object_schemas, schemas_to_be_merged)

        #######
        ####### this part might be problematic!!
        return normalize_schema(reduced_schema)


    elif "anyOf" in schema:
        children = []
        

        for sub_anyof in schema["anyOf"]:
            # Normalize sub_anyof
            
            properties = {}
            required = []
            additionalProperties = {}
            if "properties" in sub_anyof:
                properties = {}
                for key in sub_anyof["properties"].keys():
                    properties[key] = normalize_schema(
                        sub_anyof["properties"][key])

            if "required" in sub_anyof:
                required = sub_anyof["required"]

            if "additionalProperties" in sub_anyof:
                if type(sub_anyof["additionalProperties"]) is bool:
                    additionalProperties = sub_anyof["additionalProperties"]
                else:
                    additionalProperties = normalize_schema(
                        sub_anyof["additionalProperties"])
                    
            if "patternProperties" in sub_anyof:
                subschemas = []
                for key in sub_anyof["patternProperties"]:
                    subschemas.append(normalize_schema(sub_anyof["patternProperties"][key]))
                
                if type(additionalProperties) is dict and additionalProperties != {}:
                    if "anyOf" in additionalProperties:
                        if len(subschemas) == 0:
                            pass
                        elif len(subschemas) == 1:
                            additionalProperties["anyOf"].append(subschemas[0])
                        elif len(subschemas) > 1:
                            additionalProperties["anyOf"].extend(subschemas)
                    else:
                        if len(subschemas) == 0:
                            pass
                        elif len(subschemas) == 1:
                            additionalProperties = {"anyOf": [additionalProperties, subschemas[0]]}
                        elif len(subschemas) > 1:
                            additionalProperties = {"anyOf": [additionalProperties]}
                            additionalProperties["anyOf"].extend(subschemas)
                else:
                    if len(subschemas) > 1:
                        additionalProperties = {"anyOf": subschemas}
                    else:
                        additionalProperties = subschemas[0]

                    
            copied_schema = deepcopy(schema)
            del copied_schema["anyOf"]
            # Normalize copied schema
            copied_schema = normalize_schema(copied_schema)

            # Merge two schemas with AND operation
            children.append(andmerge_object_schemas(copied_schema,
                                                    {"properties": properties,
                                                     "required": required,
                                                     "additionalProperties": additionalProperties}))

        #######
        ####### this part might be problematic!!
        return normalize_schema({"anyOf": children})

    elif "oneOf" in schema:
        children = []

        for sub_anyof in schema["oneOf"]:
            # Normalize sub_anyof
            properties = {}
            required = []
            additionalProperties = {}
            if "properties" in sub_anyof:
                properties = {}
                for key in sub_anyof["properties"].keys():
                    properties[key] = normalize_schema(
                        sub_anyof["properties"][key])

            if "required" in sub_anyof:
                required = sub_anyof["required"]

            if "additionalProperties" in sub_anyof:
                if type(sub_anyof["additionalProperties"]) is bool:
                    additionalProperties = sub_anyof["additionalProperties"]
                else:
                    additionalProperties = normalize_schema(
                        sub_anyof["additionalProperties"])
                    
            if "patternProperties" in sub_anyof:
                subschemas = []
                for key in sub_anyof["patternProperties"]:
                    subschemas.append(normalize_schema(sub_anyof["patternProperties"][key]))
                
                if type(additionalProperties) is dict and additionalProperties != {}:
                    if "anyOf" in additionalProperties:
                        if len(subschemas) == 0:
                            pass
                        elif len(subschemas) == 1:
                            additionalProperties["anyOf"].append(subschemas[0])
                        elif len(subschemas) > 1:
                            additionalProperties["anyOf"].extend(subschemas)
                    else:
                        if len(subschemas) == 0:
                            pass
                        elif len(subschemas) == 1:
                            additionalProperties = {"anyOf": [additionalProperties, subschemas[0]]}
                        elif len(subschemas) > 1:
                            additionalProperties = {"anyOf": [additionalProperties]}
                            additionalProperties["anyOf"].extend(subschemas)
                else:
                    if len(subschemas) > 1:
                        additionalProperties = {"anyOf": subschemas}
                    else:
                        additionalProperties = subschemas[0]

            copied_schema = deepcopy(schema)
            del copied_schema["oneOf"]
            # Normalize copied schema
            copied_schema = normalize_schema(copied_schema)

            # Merge two schemas with AND operation
            children.append(andmerge_object_schemas(copied_schema,
                                                    {"properties": properties,
                                                     "required": required,
                                                     "additionalProperties": additionalProperties}))

        #######
        ####### this part might be problematic!!
        return normalize_schema({"oneOf": children})

    # Clear from now on
    properties = {}
    required = []
    additionalProperties = {}

    if "properties" in schema:
        try:
            schema_keys_ = schema["properties"].keys()
        except AttributeError:
            print("no property")
            raise UndefinedReferenceException()
        for key in schema_keys_:
            properties[key] = normalize_schema(schema["properties"][key])

    if "required" in schema:
        required = schema["required"]

    if "additionalProperties" in schema:
        if type(schema["additionalProperties"]) is bool:
            additionalProperties = schema["additionalProperties"]
        else:
            additionalProperties = normalize_schema(schema["additionalProperties"])

    if "patternProperties" in schema:
        subschemas = []
        for key in schema["patternProperties"]:
            subschemas.append(normalize_schema(schema["patternProperties"][key]))
        
        if type(additionalProperties) is dict and additionalProperties != {}:
            if "anyOf" in additionalProperties:
                if len(subschemas) == 0:
                    pass
                elif len(subschemas) == 1:
                    additionalProperties["anyOf"].append(subschemas[0])
                elif len(subschemas) > 1:
                    additionalProperties["anyOf"].extend(subschemas)
            else:
                if len(subschemas) == 0:
                    pass
                elif len(subschemas) == 1:
                    additionalProperties = {"anyOf": [additionalProperties, subschemas[0]]}
                elif len(subschemas) > 1:
                    additionalProperties = {"anyOf": [additionalProperties]}
                    additionalProperties["anyOf"].extend(subschemas)
        else:
            if len(subschemas) > 1:
                additionalProperties = {"anyOf": subschemas}
            elif len(subschemas) == 1:
                additionalProperties = subschemas[0]

    # Build schema
    if properties:
        properties = {"properties": properties}
    if required:
        required = {"required": required}
    else:
        required = {}
    if additionalProperties != {}:
        additionalProperties = {"additionalProperties": additionalProperties}

    return {"type": "object", **properties, **required, **additionalProperties}


def normalize_array_schema(schema):
    items = {}
    prefixItems = []

    if "items" in schema:
        if type(schema["items"]) == dict:
            items = normalize_schema(schema["items"])
        elif type(schema["items"]) == list:
            for subschema in schema["items"]:
                prefixItems.append(normalize_schema(subschema))
        else:
            raise InvalidArrayItemException()

    if "prefixItems" in schema:
        for subschema in schema["prefixItems"]:
            prefixItems.append(normalize_schema(subschema))

    # Build schema
    if items:
        items = {"items": items}
    if prefixItems:
        prefixItems = {"prefixItems": prefixItems}
    else:
        prefixItems = {}
    return {"type": "array", **items, **prefixItems}

def normalize_schema(schema):
    if type(schema) is bool:
        return schema
    if "type" in schema:
        if type(schema["type"]) is list:
            subschemas = []
            for subschema in schema["type"]:
                if subschema == "string":
                    subschemas.append({"type": "string"})
                elif subschema == "number" or subschema == "integer":
                    subschemas.append({"type": "number"})
                elif subschema == "boolean":
                    subschemas.append({"type": "boolean"})
                elif subschema == "null":
                    subschemas.append({"type": "null"})
                elif subschema == "object":
                    properties = {}
                    required = []
                    additionalProperties = {}
                    # Check if there are keywords to parse
                    if "properties" in schema:
                        properties = {}
                        for key in schema["properties"].keys():
                            properties[key] = normalize_schema(
                                schema["properties"][key])
                    if "required" in schema:
                        required = schema["required"]
                    if "additionalProperties" in schema:
                        if type(schema["additionalProperties"]) is bool:
                            additionalProperties = schema["additionalProperties"]
                        else:
                            additionalProperties = normalize_schema(schema)
                    # Build schema
                    if properties:
                        properties = {"properties": properties}
                    if required:
                        required = {"required": required}
                    else:
                        required = {}
                    if additionalProperties != {}:
                        additionalProperties = {"additionalProperties": additionalProperties}

                    subschemas.append({"type": "object", **properties, **required, **additionalProperties})

                elif subschema == "array":
                    items = {}
                    prefixItems = []
                    if "items" in schema:
                        if type(schema["items"]) == dict:
                            items = normalize_schema(schema["items"])
                        elif type(schema["items"]) == list:
                            for subschema in schema["items"]:
                                prefixItems.append(normalize_schema(subschema))
                        else:
                            raise InvalidArrayItemException()

                    if "prefixItems" in schema:
                        for subschema in schema["prefixItems"]:
                            prefixItems.append(normalize_schema(subschema))
                    # Build schema
                    if items:
                        items = {"items": items}
                    if prefixItems:
                        prefixItems = {"prefixItems": prefixItems}
                    else:
                        prefixItems = {}
                    subschemas.append({"type": "array", **items, **prefixItems})

            return {"anyOf": subschemas}

        elif schema["type"] == "object":
            # Compositional schema in object schema
            return normalize_object_schema(schema)

        elif schema["type"] == "array":
            return normalize_array_schema(schema)

        elif schema["type"] == "number":
            return {"type": "number"}
        elif schema["type"] == "integer":
            return {"type": "number"}
        elif schema["type"] == "string":
            return {"type": "string"}
        elif schema["type"] == "boolean":
            return {"type": "boolean"}
        elif schema["type"] == "null":
            return {"type": "null"}
        else:
            print(schema)
            raise InvalidSchemaTypeException(schema["type"])

    elif "const" in schema:
        if type(schema["const"]) == str:
            return {"type": "string"}
        elif type(schema["const"]) == float or type(schema["const"]) == int:
            return {"type": "number"}
        elif type(schema["const"]) == bool:
            return {"type": "boolean"}
        elif schema["const"] is None:
            return {"type": "null"}
        else:
            raise InvalidConstTypeException()

    elif "enum" in schema:
        generic_types = set()
        for value in schema["enum"]:
            if type(value) == str:
                generic_types.add("string")
            elif type(value) == float or type(value) == int:
                generic_types.add("number")
            elif type(value) == bool:
                generic_types.add("boolean")
            elif value == None:
                generic_types.add("null")

        subschemas = []
        for generic_type in generic_types:
            subschemas.append({"type": generic_type})

        if len(subschemas) > 1:
            return {"anyOf": subschemas}
        elif len(subschemas) == 0:
            return False
        else:
            return subschemas[0]

    elif "oneOf" in schema:
        subschemas = []
        for subschema in schema["oneOf"]:
            subschemas.append(normalize_schema(subschema))
        return {"oneOf": subschemas}

    elif "anyOf" in schema:
        subschemas = []
        for subschema in schema["anyOf"]:
            subschemas.append(normalize_schema(subschema))
        return {"anyOf": subschemas}

    elif "allOf" in schema:
        subschemas = []
        for subschema in schema["allOf"]:
            subschemas.append(normalize_schema(subschema))
        return {"allOf": subschemas}

    # Special case! keywords without its type
    elif "properties" in schema or "required" in schema or "additionalProperties" in schema:
        return normalize_object_schema(schema)

    elif "pattern" in schema or "minLength" in schema or "maxLength" in schema or "format" in schema:
        return {"type": "string"}

    elif "multipleOf" in schema or "minimum" in schema or "maximum" in schema or "exclusiveMinimum" in schema or "exclusiveMaximum" in schema:
        return {"type": "number"}

    elif "items" in schema or "prefixItems" in schema:
        return normalize_array_schema(schema)

    else:
        if "description" in schema or "title" in schema:
            return {}
        elif "default" in schema:
            if type(schema["default"]) == str:
                return {"type": "string"}
            elif type(schema["default"]) == float or type(schema["default"]) == int:
                return {"type": "number"}
            elif type(schema["default"]) == bool:
                return {"type": "boolean"}
            elif schema["default"] is None:
                return {"type": "null"}
            else:
                raise InvalidConstTypeException()
        elif schema == {}:
            return True

        print(schema)
        raise KnownKeywordNotFoundException()


def andmerge_object_schemas(obj1, obj2):
    properties1 = {}
    properties2 = {}
    if "properties" in obj1:
        properties1 = obj1["properties"]
    if "properties" in obj2:
        properties2 = obj2["properties"]
    properties = {**properties1, **properties2}

    required1 = []
    required2 = []
    if "required" in obj1:
        required1 = obj1["required"]
    if "required" in obj2:
        required2 = obj2["required"]
    required = list(set(required1 + required2))

    # AND of two additionals
    additional1 = {}
    additional2 = {}
    if "additionalProperties" in obj1:
        additional1 = obj1["additionalProperties"]
    if "additionalProperties" in obj2:
        additional2 = obj2["additionalProperties"]
    if additional1 != {} and additional2 != {}:
        if additional1 == False:
            additionalProperties = additional2
        elif additional2 == False:
            additionalProperties = additional1
        else:
            raise OverlappingAdditionalPropertiesException()
    elif additional1:
        additionalProperties = additional1
    elif additional2:
        additionalProperties = additional2
    else:
        additionalProperties = False

    schema = {"type": "object"}
    if properties:
        schema["properties"] = properties
    if required:
        schema["required"] = required
    if additionalProperties != {}:
        schema["additionalProperties"] = additionalProperties

    return schema



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
                    schema = json.loads(line)
                except:
                    pass
    
    try:
        return schema
    except UnboundLocalError:
        raise UndefinedReferenceException(f"No file {path} found")
 

# def unreference_schema(original_schema_, schema_path):

#     original_schema = deepcopy(original_schema_)

#     to_return = unreference(original_schema, original_schema_, schema_path)

#     return to_return


# def unreference(original_schema, schema, schema_path):
#     if type(schema) is list:
#         for i, subschema in enumerate(schema):
#             # print(i)
#             schema[i] = unreference(original_schema, subschema, schema_path)
#         return schema

#     elif type(schema) is dict:
#         keys = schema.keys()

#         if "$ref" in keys:
#             try:
#                 tgt = schema["$ref"]
#                 unreferenced_schema = deepcopy(reference_to_tree(original_schema, tgt, schema_path))
#             except RequestError as e:
#                 logging.exception(f"RequestError while unreferencing {tgt}")
#                 raise e
#             except UndefinedReferenceException as e:
#                 logging.exception(f"UndefinedReferenceException while unreferencing {tgt}")
#                 raise e
#             all_unreferenced = unreference(original_schema, unreferenced_schema, schema_path)
#             return all_unreferenced
#         else:
#             for key in keys:
#                 schema[key] = unreference(original_schema, schema[key], schema_path)
#             return schema

#     return schema


# def reference_to_tree(original_schema, ref_path, directory, file_name):
#     # Currently only treats references starting with "#"!
#     # Others have to be implemented additionaly if needed
#     # As I've seen to this date, haven't seen any uses different from "#..."
#     logging.info(f"resolving reference : {ref_path} in {directory}/{file_name}")

#     if type(ref_path) is not str:
#         exc = UndefinedReferenceException(f"Ref path {ref_path} is type {type(ref_path)}")
#         logging.exception(exc)
#         raise exc

#     if ref_path == '#':
#         exc = RecursionError("Ref to self")
#         logging.exception(exc)
#         raise exc

#     split_res = ref_path.split('#')
#     split_res.append('')
#     root_, key_ = split_res[0], split_res[1]
#     tree_ = deepcopy(resolve_root(root_, original_schema, directory, file_name))
#     res = resolve_key(key_, tree_)
#     logging.info("refernce resolved.\n---")
#     return res


# def resolve_root(root_, original_schema, directory, file_name):
#     global unref_map

#     logging.info(f"resolving root : {root_}")
#     try:
#         res = deepcopy(unref_map[root_])
#         logging.info("root cache HIT.")
#     except KeyError:
#         def is_website(string):
#             return string.startswith("http:") or string.startswith("https:")
        
#         if root_ == '':
#             logging.info("root is an original schema")
#             res = original_schema
#         elif is_website(root_):
#             res = resolve_website_root(root_, directory, file_name)
#             unref_map[root_] = deepcopy(res)
#         else:
#             res = resolve_filename_root(root_, directory, file_name)
#             unref_map[root_] = deepcopy(res)
#         logging.info("root resolved.")
#     return res
    

# def resolve_website_root(root_, directory, file_name):
#     global url_map

#     logging.info("root is an url")

#     def get_json_from_url(url):
#         try:
#             response = requests.get(url, timeout = 3)
#         except requests.exceptions.Timeout:
#             exc = RequestError(f"Timeout: {url}")
#             logging.exception(exc)
#             raise exc
#         except requests.exceptions.RequestException:
#             exc = RequestError(f"RequestException: {url}")
#             logging.exception(exc)
#             raise exc

#         if response.status_code == 200:
#             try:
#                 response_data = response.json()
#             except requests.exceptions.JSONDecodeError:
#                 raise RequestError(f"Invalid JSON {url}")
#             return response_data
#         else:
#             exc = RequestError(f"Status code {response.status_code}: {url}")
#             logging.exception(exc)
#             raise exc

#     try:
#         refed_schema = deepcopy(url_map[root_])
#         logging.info("root url cache HIT.")
#     except KeyError:
#         refed_schema = get_json_from_url(root_)
#         logging.info("successful GET")
#         url_map[root_] = deepcopy(refed_schema)

#     return unreference_schema(refed_schema, directory, file_name)

# def resolve_filename_root(root_, directory, file_name):
#     global bd_map

#     logging.info("root is a rel-path file")

#     try:
#         this_file = bd_map[file_name]
#     except KeyError:
#         exc = UndefinedReferenceException(f"file path {file_name} not found.")
#         logging.exception(exc)
#         raise exc
    
#     rel_file = os.path.normpath(os.path.join(os.path.dirname(this_file), root_))
#     if ':/' in rel_file and '://' not in rel_file:
#         # change :/ to ://
#         rel_file = rel_file.replace(":/", "://", 1)

#     rel_file += '?raw=true'
#     try:
#         rel_filename = bd_map[rel_file]
#     except KeyError:
#         exc = UndefinedReferenceException(f"file path {rel_file} not found.")
#         logging.exception(exc)
#         raise exc

#     # directory up one level
#     directory = os.path.dirname(directory)
#     directory = directory + '/' + rel_filename.split('.')[0]

#     try:
#         refed_schema = load_schema(directory + "/" + rel_filename)
#     except FileNotFoundError:
#         raise RequestError(directory + '/' + rel_filename + " not found")
#     logging.info(f"root file {rel_filename} loaded")
#     refed_schema = run_with_timeout(unreference_schema, 20, refed_schema, directory, file_name)
#     return refed_schema
    
# def resolve_key(key_, tree_):
#     logging.info(f"resolving key : {key_}")
#     while key_.startswith('/'):
#         key_ = key_[1:]
#     ref_key = key_.split('/')
#     for step in ref_key:
#         if not step:
#             continue
#         try:
#             tree_ = tree_[step]
#         except KeyError:
#             exc = UndefinedReferenceException(f"Ref path not found: tree_[{step}] while following step {key_}")
#             logging.exception(exc)
#             raise exc
#     logging.info("key resolved.")
#     return tree_

def create_bidirectional_map():
    bidirectional_map = {}
    with open('out.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            key, value = row
            bidirectional_map[key] = value
            bidirectional_map[value] = key
    return bidirectional_map


if __name__ == "__main__":
    main()
    logging.close()
