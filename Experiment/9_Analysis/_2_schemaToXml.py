
import os
import sys
import traceback
import xml.dom.minidom
import xml.etree.ElementTree as ET
import xml.parsers.expat
from xml.etree.ElementTree import Element, ElementTree, SubElement

sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_schema


def main():

    schema_paths = [
        "/mnt/nvme1n1p2/jhyun/SchemaDataset/1_NewYorkTimes/new_york_times_formalized.json"
    ]
    
    failed_names = []
    for schema_path in schema_paths:
        print()
        print(schema_path)
        if "_formalized" not in schema_path:
            continue
        try:
            schema = load_schema(schema_path)

            tree = schema_to_xml(schema)
            tree = tree.getroot()
            xml_string = ET.tostring(tree, encoding="utf-8")
            parsed_xml = xml.dom.minidom.parseString(xml_string)
            pretty_xml_string = parsed_xml.toprettyxml(indent="  ")

            # Write file in the same directory

            name, extension = os.path.splitext(schema_path)
            # Add "_formalized" before the extension
            modified_filename = name[:-11] + ".xml"

            with open(modified_filename, "w") as file:
                file.write(pretty_xml_string)
            print(f"!!!!!!!!! Successfully XML-ified {schema_path} !!!!!!!!!")
        except xml.parsers.expat.ExpatError as e:
            print(xml_string)
            failed += 1
        except TypeError as e:
            print(f"++++ TypeError {schema_path}: {e}")
            traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"++++ Failed to XML-ify {schema_path}: {e}")
            traceback.print_exc()
            failed_names.append(schema_path)
            failed += 1
        except:
            failed += 1

    print()
    for name in failed_names:
        print(name)
    print(f"[FAILED] : {len(failed_names)}")


# The schema is given in python data structure format (dictionary, list)
def schema_to_xml(normalized_schema):
    root = Element("schema")
    schema_to_xml_recursive(normalized_schema, root)
    tree = ElementTree(root)

    return tree

from copy import deepcopy


def schema_to_xml_recursive(schema, node):
    if type(schema) is bool:
        if schema == True:
            subnode = SubElement(node, "ANY")
            subnode.set("component", "node")
            return
    if "type" in schema:
        if schema["type"] == "object":
            object_schema_node = SubElement(node, "object")

            class_attribute = ""

            if "properties" in schema:
                object_schema_node.set("heterogeneous", "true")

                all_keys = schema["properties"].keys()
                required_keys = []

                if "required" in schema:
                    required_keys = schema["required"]
                if type(required_keys) is bool:
                    if required_keys == False:
                        required_keys = []
                    else:
                        required_keys = deepcopy(all_keys)

                required_keys = list(set(required_keys) - (set(required_keys) - set(all_keys)))
                optional_keys = list(set(all_keys) - set(required_keys))
                # print("<<<<>>>>")
                # print(required_keys)
                # print(optional_keys)
            
                for key in required_keys:
                    escaped_key = escape_xml(key)
                    subnode = SubElement(object_schema_node, escaped_key)
                    subnode.set("component", "edge")
                    subnode.set("required", "true")
                    schema_to_xml_recursive(schema["properties"][key], subnode)

                for key in optional_keys:
                    escaped_key = escape_xml(key)
                    subnode = SubElement(object_schema_node, escaped_key)
                    subnode.set("component", "edge")
                    subnode.set("required", "false")
                    schema_to_xml_recursive(schema["properties"][key], subnode)


            if "additionalProperties" in schema:
                if schema["additionalProperties"] == False:
                    pass
                else:
                    object_schema_node.set("homogeneous", "true")

                    subnode = SubElement(object_schema_node, "all")
                    subnode.set("component", "edge")
                    subnode.set("any", "true")
                    schema_to_xml_recursive(schema["additionalProperties"], subnode)
            
            object_schema_node.set("component", "node")
            object_schema_node.set("class", class_attribute)

            return

        elif schema["type"] == "array":
            array_schema_node = SubElement(node, "array")
            
            class_attribute = "" 

            if "prefixItems" in schema:
                array_schema_node.set("heterogeneous", "true")

                for i, subschema in enumerate(schema["prefixItems"]):
                    subnode = SubElement(array_schema_node, "subschema")
                    subnode.set("component", "edge")
                    subnode.set("index", str(i + 1))
                    schema_to_xml_recursive(schema["prefixItems"][i], subnode)

            if "items" in schema:
                array_schema_node.set("homogeneous", "true")

                subnode = SubElement(array_schema_node, "all")
                subnode.set("component", "edge")
                subnode.set("any", "true")
                schema_to_xml_recursive(schema["items"], subnode)

            array_schema_node.set("component", "node")
            array_schema_node.set("class", class_attribute)

            return
                
        elif schema["type"] == "number":
            subnode = SubElement(node, "number")
            subnode.set("component", "node")
            return
        elif schema["type"] == "integer":
            subnode = SubElement(node, "number")
            subnode.set("component", "node")
            return
        elif schema["type"] == "string":
            subnode = SubElement(node, "string")
            subnode.set("component", "node")
            return
        elif schema["type"] == "boolean":
            subnode = SubElement(node, "boolean")
            subnode.set("component", "node")
            return
        elif schema["type"] == "null":
            subnode = SubElement(node, "null")
            subnode.set("component", "node")
            return
        else:
            print(schema)
            return

    elif "oneOf" in schema:
        subel = SubElement(node, "oneof")
        subel.set("composition", "true")
        subel.set("component", "node")
        for i, subschema in enumerate(schema["oneOf"]):
            subsubel = SubElement(subel, "empty_edge")
            subsubel.set("component", "edge")
            schema_to_xml_recursive(subschema, subsubel)
        return 

    elif "anyOf" in schema:
        subel = SubElement(node, "anyof")
        subel.set("composition", "true")
        subel.set("component", "node")
        for i, subschema in enumerate(schema["anyOf"]):
            subsubel = SubElement(subel, "empty_edge")
            subsubel.set("component", "edge")
            schema_to_xml_recursive(subschema, subsubel)
        return 

    elif "allOf" in schema:
        subel = SubElement(node, "allof")
        subel.set("composition", "true")
        subel.set("component", "node")
        for i, subschema in enumerate(schema["allOf"]):
            subsubel = SubElement(subel, "empty_edge")
            subsubel.set("component", "edge")
            schema_to_xml_recursive(subschema, subsubel)
        return 
    
    print("None")
    return

# convert string to XML node name (escape special characters)
def escape_xml(string):
    string = string.replace(" ", "_").replace("-", "_").replace(".", "_").replace(":", "_").replace("/", "_")
    string = string.replace("\\", "_").replace("?", "_").replace("*", "_").replace("<", "_").replace(">", "_")
    string = string.replace("|", "_").replace("!", "_").replace("@", "_").replace("#", "_").replace("$", "_")
    string = string.replace("%", "_").replace("^", "_").replace("&", "_").replace("(", "_").replace(")", "_")
    string = string.replace("+", "_").replace("=", "_").replace("`", "_").replace("~", "_").replace("{", "_")
    string = string.replace("}", "_").replace("[", "_").replace("]", "_").replace("'", "_").replace('"', "_")
    string = string.replace(",", "_").replace(";", "_").replace(" ", "_").replace("\n", "_").replace("\t", "_")
    string = string.replace("\r", "_").replace("\f", "_").replace("\v", "_").replace("\b", "_").replace("\a", "_")
    string = string.replace("\0", "_").replace("\1", "_").replace("\2", "_").replace("\3", "_").replace("\4", "_")
    string = string.replace("\5", "_").replace("\6", "_").replace("\7", "_").replace("\8", "_").replace("\9", "_")
    if string[0].isdigit():
        string = "_" + string
    return string

if __name__=="__main__":
    main()