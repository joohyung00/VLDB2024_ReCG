import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
import os

import xml.dom.minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree, SubElement

import pygraphviz as pgv


counter = 1

def main_finegrained():
    global xml_string

    tree = ET.fromstring(xml_string)
    root = tree

    graphvizify_xml(root)




def main():

    schema_paths = [
        "/mnt/nvme1n1p2/jhyun/SchemaDataset/1_NewYorkTimes.xml"
    ]

    success = 0
    failed = 0

    failed_names = []

    for schema_path in schema_paths:

        # if any(filename == f"{file_name[:-4]}.png" for filename in os.listdir(directory)):
        #     # If a .png file exists, skip the processing for this file
        #     print("Already exists!")
        #     continue

        try:
            name, extension = os.path.splitext(schema_path)
            modified_filename = name + ".png"

            tree = ET.parse(schema_path)
            graph = graphvizify_xml(tree)

            # Write file in the same directory

            if graph.number_of_nodes() > 5000:
                import shutil
                source_file = "node_shapes/Crying Sad Emoji.png"
                destination_file = modified_filename
                shutil.copy2(source_file, destination_file)
                print("Graph too big! Crying Emoji called")

            else:
                # Write the file as PNG
                graph.draw(modified_filename, prog="dot", format="png")
                print(f"!!!!!!!!! Successfully grahvizified {schema_path} !!!!!!!!!")
        
        except AttributeError as e:
            failed += 1
        except Exception as e:
            print(f"++++ Failed to XML-ify {schema_path}: {e}")
            failed_names.append(schema_path)

            import shutil
            source_file = "node_shapes/Crying Sad Emoji.png"
            destination_file = modified_filename
            shutil.copy2(source_file, destination_file)
            print("Graph too big! Crying Emoji called")
            failed += 1
        except:
            failed += 1

    print()
    for name in failed_names:
        print(name)
    print(f"[FAILED] : {len(failed_names)}")


TIME_OUT_IN_MINUTES = 2
TIMEOUT = TIME_OUT_IN_MINUTES * 60

def main2():
    root_directory = '../json_schema_corpus'

    # Initialize an empty list to store the pairs
    schema_pairs = []

    # Traverse the directory structure
    for root, directories, files in os.walk(root_directory):
        for filename in files:
            # Check if the file is an XML file
            if filename.endswith('.xml'):
                # Append the pair of directory path and filename to the list
                schema_pairs.append((root, filename))

    # Specify the number of processes
    num_processes = 50

    # Split the schema pairs into chunks for each process
    chunk_size = len(schema_pairs) // num_processes
    data_for_processes = [schema_pairs[x: x + chunk_size] for x in range(0, len(schema_pairs), chunk_size)]

    # Create a ProcessPoolExecutor
    with ProcessPoolExecutor(num_processes) as executor:
        futures = []
        for i, data_chunk in enumerate(data_for_processes):
            future = executor.submit(process_chunk, data_chunk)
            print(f"[Process {i + 1}] Started")
            futures.append(future)

        try:
            for future in as_completed(futures, timeout = TIMEOUT):
                result = future.result()

        except TimeoutError:
            print("Processing took too long...")
            # stop_process_pool(executor)


def process_chunk(data_chunk):
    # Perform the processing for each data chunk
    results = []
    for directory, file_name in data_chunk:
        # Check if a .png file already exists in the directory
        if any(filename.endswith('.png') for filename in os.listdir(directory)):
            # If a .png file exists, skip the processing for this file
            results.append((file_name, True))
            continue

        try:
            print(file_name)
            tree = ET.parse(os.path.join(directory, file_name))
            graph = graphvizify_xml(tree)

            # Modify the filename
            name, extension = os.path.splitext(file_name)
            modified_filename = name + ".png"

            if graph.number_of_nodes > 5000:
                import shutil
                source_file = "node_shapes/Crying Sad Emoji.png"
                destination_file = os.path.join(directory, modified_filename)
                shutil.copy2(source_file, destination_file)
                print("Graph too big! Crying Emoji called")

            else:
                # Write the file as PNG
                graph.draw(os.path.join(directory, modified_filename), prog="dot", format="png")

            results.append((file_name, True))
        except Exception as e:
            results.append((file_name, False))

    return results







# The schema is given in python data structure format (dictionary, list)
def graphvizify_xml(xml_tree):
    graph = pgv.AGraph(directed=True)
    schema = get_only_child(xml_tree)
    graphvizify_xml_recursive(graph, None, schema)  # Pass None instead of ""
    
    return graph



def graphvizify_xml_recursive(graph, graph_node, xml_node):
    # Nodes
    attributes = xml_node.attrib

    if attributes["component"] == "node":
        if xml_node.tag == "ANY":
            node = add_node_with_shape_and_label(graph, "object", "house", "")
            return node

        elif xml_node.tag == "object":
            obj_node = add_node_with_shape_and_label(graph, "object", "circle", "")
            for child in xml_node:
                graphvizify_xml_recursive(graph, obj_node, child)
            return obj_node

        elif xml_node.tag == "array":
            arr_node = add_node_with_shape_and_label(graph, "array", "square", "")
            for child in xml_node:
                graphvizify_xml_recursive(graph, arr_node, child)
            return arr_node

        elif xml_node.tag == "anyof":
            anyof_node = add_node_with_shape_and_label(graph, "anyof", "folder", "")
            for child in xml_node:
                graphvizify_xml_recursive(graph, anyof_node, child)
            return anyof_node

        elif xml_node.tag == "oneof":
            oneof_node = add_node_with_shape_and_label(graph, "oneof", "note", "")
            for child in xml_node:
                graphvizify_xml_recursive(graph, oneof_node, child)
            return oneof_node

        elif xml_node.tag == "allof":
            allof_node = add_node_with_shape_and_label(graph, "allof", "tab", "")
            for child in xml_node:
                graphvizify_xml_recursive(graph, allof_node, child)
            return allof_node
            
        elif xml_node.tag == "string":
            string_node = add_node_with_shape_and_label(graph, "string", "triangle", "STR")
            return string_node
        elif xml_node.tag == "number":
            number_node = add_node_with_shape_and_label(graph, "number", "triangle", "NUM")
            return number_node
        elif xml_node.tag == "boolean":
            boolean_node = add_node_with_shape_and_label(graph, "boolean", "triangle", "BOOL")
            return boolean_node
        elif xml_node.tag == "null":
            null_node = add_node_with_shape_and_label(graph, "null", "triangle", "NULL")
            return null_node
        else:
            "UNDEFINED NODE"
            # raise UndefinedNodeError()
            exit()
    

    # Edges
    elif attributes["component"] == "edge":
        if xml_node.tag == "empty_edge":
            child_xml_node = get_only_child(xml_node)
            child_graph_node = graphvizify_xml_recursive(graph, graph_node, child_xml_node)
            add_labeled_edge_and_bold(graph, graph_node, child_graph_node, "", False)

        elif "subschema" == xml_node.tag and "index" in attributes:
            # Change XML generator. Add attribute for the subschema of hetArray.

            index = attributes["index"]
            child_xml_node = get_only_child(xml_node)
            child_graph_node = graphvizify_xml_recursive(graph, graph_node, child_xml_node)
            add_labeled_edge_and_bold(graph, graph_node, child_graph_node, index, False)

        elif xml_node.tag == "all" and "any" in attributes:
            # Check attributes. Find for `any`
            # either homo or hetero

            child_xml_node = get_only_child(xml_node)
            child_graph_node = graphvizify_xml_recursive(graph, graph_node, child_xml_node)
            add_labeled_edge_and_bold(graph, graph_node, child_graph_node, "*", False)
        else:
            # keys
            key = xml_node.tag
            child_xml_node = get_only_child(xml_node)
            child_graph_node = graphvizify_xml_recursive(graph, graph_node, child_xml_node)
            if attributes["required"] == "true":
                add_labeled_edge_and_bold(graph, graph_node, child_graph_node, key, True)
            else:
                add_labeled_edge_and_bold(graph, graph_node, child_graph_node, key, False)


def add_node_with_shape_and_label(graph, node_name, shape, label):
    global counter
    unique_node_name = f'{node_name}_{str(counter)}'
    counter += 1

    graph.add_node(unique_node_name)
    graph.get_node(unique_node_name).attr['shape'] = shape
    graph.get_node(unique_node_name).attr['label'] = label
    return unique_node_name


def add_labeled_edge_and_bold(graph, src, dest, label, bold):
    if bold:
        graph.add_edge(src, dest, label = label, penwidth = 2)
    else:
        graph.add_edge(src, dest, label = label)


def get_only_child(element):
    # Method 1: Using find() method
    only_child = element.find("*")
    if only_child is not None:
        return only_child

    # Method 2: Iterating over children attribute
    for child in element:
        return child

    return None



if __name__=="__main__":
    main()