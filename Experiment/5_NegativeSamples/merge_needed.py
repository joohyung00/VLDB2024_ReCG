import sys
sys.path.insert(1, '/root/JsonExplorerSpark/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_id_to_negative2_dataset_path, dataset_ids, dataset_fullnames


import random





TO_MERGE = [
    {
        "sources": [
            "/mnt/SchemaDataset/34_Dolittle/dolittle_artifacts_negative_2.jsonl",
            "/mnt/SchemaDataset/34_Dolittle/dolittle_context_negative_2.jsonl",
            "/mnt/SchemaDataset/34_Dolittle/dolittle_event_negative_2.jsonl"
        ],
        "target": "/mnt/SchemaDataset/34_Dolittle/merged_negative_2.jsonl"
    },
    {
        "sources": [
            "/mnt/SchemaDataset/35_Drupal/drupal_breakpoints_negative_2.jsonl",
            "/mnt/SchemaDataset/35_Drupal/drupal_layouts_negative_2.jsonl",
            "/mnt/SchemaDataset/35_Drupal/drupal_linksmenu_negative_2.jsonl",
            "/mnt/SchemaDataset/35_Drupal/drupal_migration_negative_2.jsonl",
            "/mnt/SchemaDataset/35_Drupal/drupal_merged_negative_2.jsonl"
        ],
        "target": "/mnt/SchemaDataset/35_Drupal/merged_negative_2.jsonl"
    }
]




def main():
    
    for merge_info in TO_MERGE:
        mergeSingleDataset(merge_info)
    

    return
    
    
    
def mergeSingleDataset(merge_info):
    sources = merge_info["sources"]
    target = merge_info["target"]
    
    # 1. Read all the lines within `sources` files and save them in a list
    sources_lines = []
    for source in sources:
        with open(source, "r") as f:
            lines = f.readlines()
            sources_lines.extend(lines)
    
    # 2. Shuffle all the lines
    random.shuffle(sources_lines)
    print(len(sources_lines))
    
    # 3. Write them all to the `target` file
    with open(target, "w") as f:
        f.writelines(sources_lines)
        
    print(count_lines(target))



if __name__ == "__main__":
    main()