import os
import sys
import argparse
import json
import random
import shutil

sys.path.insert(1, '/root/JsonExplorerSpark/Experiment')
from load_json import load_schema, unreference_schema
from _1_schemaParser import normalize_schema
from _2_schemaToXml import schema_to_xml
from _3_xmlToGraph import graphvizify_xml

import xml.dom.minidom
import xml.etree.ElementTree as ET
import xml.parsers.expat
from xml.etree.ElementTree import Element, ElementTree, SubElement
import pygraphviz as pgv




def remove_file(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
        print("File Removed")
    else:
        print("No such file")
        
        
        
def main(argv):
    
    # 0. Args
    parser = argparse.ArgumentParser(description = "Splits the positive samples into train and test set")
    
    parser.add_argument('--schema_path')
    
    args = parser.parse_args(argv)  
    print(args)
    
    if args.schema_path == None:
        directory = ""
        schema_path = "target_schema.json"
    else:
        directory = "inputs/"
        schema_path = args.schema_path

    
    # 1. Read and normalize schema
    schema = load_schema(directory + schema_path)
    unreferenced_schema = unreference_schema(schema)
    formalized_schema = normalize_schema(unreferenced_schema)
    
    # 2. Normalized schema to XML
    tree = schema_to_xml(schema)
    tree = tree.getroot()
    # xml_string = ET.tostring(tree, encoding="utf-8")
    # parsed_xml = xml.dom.minidom.parseString(xml_string)
    # pretty_xml_string = parsed_xml.toprettyxml(indent="  ")
    # with open("target_schema.json", "w") as file:
    #     file.write(pretty_xml_string)
    
    # 3. XML to graph
    # tree = ET.parse(schema_path)
    graph = graphvizify_xml(tree)

    # Write file in the same directory
    if graph.number_of_nodes() > 5000:
        # source_file = "node_shapes/Crying Sad Emoji.png"
        # destination_file = modified_filename
        # shutil.copy2(source_file, destination_file)
        print("Graph too big! Crying Emoji called")
    else:
        name, extension = os.path.splitext(schema_path)
        modified_filename = name + ".pdf"
        # Write the file as PNG
        graph.draw("outputs/" + modified_filename, prog="dot", format="pdf")
    
    
    
    


if __name__ == "__main__":
    main((sys.argv)[1:])