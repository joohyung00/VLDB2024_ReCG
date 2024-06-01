import sys
sys.path.insert(1, '/root/JsonExplorerSpark/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_id_to_fullname, dataset_id_to_positive_dataset_path, dataset_id_to_negative_dataset_path, possible_algorithms
sys.path.insert(3, "/root/JsonExplorerSpark/ExperimentVisualization")
from aggregateExpResults import getResultForPercParamDatasetExpnum

from itertools import product
import subprocess
import yaml


CONFIG_FILE_PATH = "param_exp_config.yaml"

CONFIG_PARAM_SET = {
    "exp_types", 
    "target_dataset_ids", 
    "target_percents", 
    "exp_nums", 
    "beam_widths", 
    "epsilons", 
    "min_pts_percs", 
    "sample_sizes",
    "mdl_weights"
    }
TOTAL_ELEMENTS = len(CONFIG_PARAM_SET)


def main():

    # 1. Parse config file
    parsed_exp_configs = readConfigFile()
    
    # 2. Run experiments according to configurations
    for exp_config in parsed_exp_configs:
        runSingleExperimentSet(exp_config)








#################################################
# runSingleExperimentSet                        #
#   input: config object                        #
#                                               #
#                                               #
# - Run experiment according to config          #
#################################################

def runSingleExperimentSet(exp_config):
    
    # 1. Name each parameter set
    exp_types = exp_config["exp_types"]
    target_dataset_ids = exp_config["target_dataset_ids"]
    target_percents = exp_config["target_percents"]
    exp_nums = exp_config["exp_nums"]
    beam_widths = exp_config["beam_widths"]
    epsilons = exp_config["epsilons"]
    min_pts_percs = exp_config["min_pts_percs"]
    sample_sizes = exp_config["sample_sizes"]
    mdl_weights = exp_config["mdl_weights"]
    iteration_order = exp_config["iteration_order"]
    
    
    # 2. Determine the iteration order
    iterating_order = []
    interpretation_order = []
    if iteration_order == None:
        iterating_order =       [ exp_nums,  exp_types,  target_percents, mdl_weights,  sample_sizes,  epsilons,  min_pts_percs,  beam_widths,  target_dataset_ids] 
        interpretation_order =  ["exp_num", "exp_type", "target_percent", "mdl_weight", "sample_size", "epsilon", "min_pts_perc", "beam_width", "target_dataset_id"]
    else:
        if len(iteration_order) != TOTAL_ELEMENTS:
            print(f"Error: iteration_order must contain all {TOTAL_ELEMENTS} elements")
            return None
        for iteration_target in iteration_order:
            if iteration_target == "exp_nums": 
                iterating_order.append(exp_nums)
                interpretation_order.append("exp_num")
            elif iteration_target == "exp_types": 
                iterating_order.append(exp_types)
                interpretation_order.append("exp_type")
            elif iteration_target == "target_percents": 
                iterating_order.append(target_percents)
                interpretation_order.append("target_percent")
            elif iteration_target == "beam_widths": 
                iterating_order.append(beam_widths)
                interpretation_order.append("beam_width")
            elif iteration_target == "min_pts_percs":
                iterating_order.append(min_pts_percs)
                interpretation_order.append("min_pts_perc")
            elif iteration_target == "epsilons": 
                iterating_order.append(epsilons)
                interpretation_order.append("epsilon")
            elif iteration_target == "sample_sizes": 
                iterating_order.append(sample_sizes)
                interpretation_order.append("sample_size")
            elif iteration_target == "mdl_weights":
                iterating_order.append(mdl_weights)
                interpretation_order.append("mdl_weight")
            elif iteration_target == "target_dataset_ids": 
                iterating_order.append(target_dataset_ids)
                interpretation_order.append("target_dataset_id")
            
            else:
                print(f"Error: iteration_order must contain all {TOTAL_ELEMENTS} elements")
                return None
        
    # 3. Generate all combinations of the parameters
    all_combinations = list(product(*iterating_order))
    
    # 4. Run the experiments
    for param_list in all_combinations:
        
        # 4.1. Get the parameters and generate argument list for bash file
        exp_type = param_list[interpretation_order.index("exp_type")]
        target_dataset_id = param_list[interpretation_order.index("target_dataset_id")]
        target_percent = param_list[interpretation_order.index("target_percent")]
        exp_num = param_list[interpretation_order.index("exp_num")]
        beam_width = param_list[interpretation_order.index("beam_width")]
        min_pts_perc = param_list[interpretation_order.index("min_pts_perc")]
        sample_size = param_list[interpretation_order.index("sample_size")]
        epsilon = param_list[interpretation_order.index("epsilon")]
        mdl_weight = param_list[interpretation_order.index("mdl_weight")]
        
        dataset_name =          dataset_id_to_fullname[target_dataset_id]
        positive_dataset_path = dataset_id_to_positive_dataset_path[target_dataset_id]
        negative_dataset_path = dataset_id_to_negative_dataset_path[target_dataset_id]
        
        # exp_type
        # dataset_name
        # target_percent
        # beam_width
        # epsilon
        # min_pts_perc
        # sample_size
        # mdl_weights
        # exp_num

        cvd = {
            "epsilon": float(epsilon),
            "min_pts_perc": int(min_pts_perc),
            "sample_size": int(sample_size),
            "mdl_weights": (float(mdl_weight.split(",")[0]), float(mdl_weight.split(",")[1]))
        }
        recall, precision, f1, runtime, src, drc, accepted = getResultForPercParamDatasetExpnum("beam_width", int(target_percent), int(beam_width), dataset_name, int(exp_num), cvd)
        
        cont = False
        if exp_type == "Accuracy" and (recall != -1 and precision != -1 and f1 != -1): cont = True
        if exp_type == "Performance" and runtime != -1: cont = True
        if exp_type == "MDL" and (src != -1 and drc != -1 and accepted != -1): cont = True
        if cont:
            print("ALREADY HERE")
            continue
        
        
        arglist = [
            "bash", 
            "experiment_param.sh",
            exp_type,
            dataset_name,
            positive_dataset_path,
            negative_dataset_path,
            target_percent,
            "10",           # Test percent
            exp_num,
            beam_width,
            epsilon,
            min_pts_perc,
            sample_size,
            mdl_weight.split(",")[0],
            mdl_weight.split(",")[1]
        ]

        try:
            subprocess.run(arglist, timeout = 7200)
        except subprocess.TimeoutExpired:
            print("Timeout: ", arglist)




#################################################
# readConfigFile                                #
#   input: None                                 #
#   output: list of config objects              #
#                                               #
# - Read the config file written in YAML        #
#################################################


def readConfigFile():
    
    def parseSingleConfigObject(config_obj):
    
        parsed_config = {}
        
        # 1. Check if exp_types are comprised of valid types
        if "exp_types" not in config_obj:
            print("Error: exp_types not found in config")
            return None
        if not set(stringifyElements(config_obj["exp_types"])).issubset(set(["Accuracy", "Performance", "MDL"])):
            print("Error: exp_types must be valid")
            return None
        parsed_config["exp_types"] = stringifyElements(config_obj["exp_types"])
        
        # 2. Check if target_dataset_ids are comprised of valid dataset_ids
        if "target_dataset_ids" not in config_obj:
            print("Error: target_dataset_ids not found in config")
            return None
        if not set(stringifyElements(config_obj["target_dataset_ids"])).issubset(set(dataset_ids)):
            print("Error: target_dataset_ids must be a subset of dataset_ids")
            return None
        parsed_config["target_dataset_ids"] = stringifyElements(config_obj["target_dataset_ids"])
        
        # 3. Check if target_percents are comprised of valid train percents
        if "target_percents" not in config_obj:
            print("Error: target_percents not found in config")
            return None
        parsed_config["target_percents"] = stringifyElements(config_obj["target_percents"])
        
        # 4. Check if beam_widths are comprised of valid beam_width
        if "beam_widths" not in config_obj:
            print("Error: beam_widths not found in config")
            return None
        for beam_width_str in config_obj["beam_widths"]:
            try:
                _ = int(beam_width_str)
            except:
                print("Error: illegal value of k found in config")
                return None
        parsed_config["beam_widths"] = stringifyElements(config_obj["beam_widths"])
        
        # 5. Check if epsilons are comprised of valid sample sizes
        if "epsilons" not in config_obj:
            print("Error: epsilons not found in config")
            return None
        for epsilon_str in config_obj["epsilons"]:
            try:
                epsilon = int(epsilon_str)
                if epsilon < 0 or 1 < epsilon:
                    print("Error: illegal value (out-of-range) of sample_size found in config")
                    return None
            except:
                print("Error: illegal value (non-float) of sample_size found in config")
                return None
        parsed_config["epsilons"] = stringifyElements(config_obj["epsilons"])
        
        
        if "min_pts_percs" not in config_obj:
            print("Error: min_pts_percs not found in config")
            return None
        for min_pts_perc_str in config_obj["min_pts_percs"]:
            try:
                min_pts_perc = float(min_pts_perc_str)
                if min_pts_perc < 0 or 100 < min_pts_perc:
                    print("Error: illegal value (out-of-range) of min_pts_perc found in config")
                    return None
            except:
                print("Error: illegal value (non-float) of min_pts_perc found in config")
                return None
        parsed_config["min_pts_percs"] = stringifyElements(config_obj["min_pts_percs"])
        
        # 7. Check if sample_sizes are comprised of valid sample sizes
        if "sample_sizes" not in config_obj:
            print("Error: sample_sizes not found in config")
            return None
        for sample_size_str in config_obj["sample_sizes"]:
            try:
                _ = int(sample_size_str)
            except:
                print("Error: illegal value of sample_size found in config")
                return None
        parsed_config["sample_sizes"] = stringifyElements(config_obj["sample_sizes"])
        
        
        # 8. Check if exp_nums are comprised of valid experiment numbers
        if "exp_nums" not in config_obj:
            print("Error: exp_nums not found in config")
            return None
        parsed_config["exp_nums"] = stringifyElements(config_obj["exp_nums"])
        
        # 9. Check MDL weights
        if "mdl_weights" not in config_obj:
            print("Error: mdl_weights not found in config")
            return None
        for sample_size_str in config_obj["mdl_weights"]:
            try:
                src_weight_str, drc_weight_str = sample_size_str.split(",")
                src_weight = float(src_weight_str)
                drc_weight = float(drc_weight_str)
                if src_weight + drc_weight != 1.0:
                    print("Error: mdl_weights must sum up to 1")
                    return None
            except:
                print("Error: illegal value of sample_size found in config")
                return None
        parsed_config["mdl_weights"] = stringifyElements(config_obj["mdl_weights"])
        
        # 10. Check if iteration_order is valid
        if "iteration_order" in config_obj:
            iteration_order = config_obj["iteration_order"]
            
            if len(iteration_order) != TOTAL_ELEMENTS:
                print(f"Error: iteration_order must be a list of {TOTAL_ELEMENTS} elements")
                return None
            
            config_param_set = CONFIG_PARAM_SET
            if set(iteration_order) != config_param_set:
                print(f"Error: iteration_order must contain all {TOTAL_ELEMENTS} elements")
                return None    
                    
            parsed_config["iteration_order"] = stringifyElements(config_obj["iteration_order"])
        else:
            parsed_config["iteration_order"] = None

        print(parsed_config)

        return parsed_config
    
    # 1. Read the config file written in JSON or YAML
    config_file_path = CONFIG_FILE_PATH
    with open(config_file_path, "r") as file:
        config_lists = yaml.safe_load(file)

    # 2. Parse the configs
    parsed_configs = []
    for config_obj in config_lists:
        parsed_config_obj = parseSingleConfigObject(config_obj)
        if parsed_config_obj != None:
            parsed_configs.append(parsed_config_obj)
        else:
            print("Error: Invalid config object")
            exit()
        
    return parsed_configs




#################################################
# stringifyElements                             #
#   input: list                                 #
#   output: list with stringified elements      #
#                                               #
# - Read a list and return a list with the      #
#    elements stringified                       #
#################################################

def stringifyElements(list):
    return [str(x) for x in list]


if __name__ == "__main__":
    main()



# #  #Script                 #Exp_type   #Dataset name          #Positive path                                                           #Negative path                                                             #Train% #Test%  #Beamsize #Samplesize  #Epsilon   #ExpNum
# ./experiment_param.sh     Accuracy     1_NewYorkTimes          /mnt/SchemaDataset/1_NewYorkTimes/new_york_times_positive.jsonl          /mnt/SchemaDataset/1_NewYorkTimes/new_york_times_negative.jsonl            10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     3_Twitter               /mnt/SchemaDataset/3_Twitter/twitter_positive_10000.jsonl                /mnt/SchemaDataset/3_Twitter/twitter_negative_10000.jsonl                  10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     4_Github                /mnt/SchemaDataset/4_Github/merged_positive.jsonl                        /mnt/SchemaDataset/4_Github/merged_negative.jsonl                          10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     5_Pharmaceutical        /mnt/SchemaDataset/5_Pharmaceutical/pharmaceutical_positive.jsonl        /mnt/SchemaDataset/5_Pharmaceutical/pharmaceutical_negative.jsonl          10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     6_Wikidata              /mnt/SchemaDataset/6_Wikidata/wikidata_positive.jsonl                    /mnt/SchemaDataset/6_Wikidata/wikidata_negative.jsonl                      10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     7_Yelp                  /mnt/SchemaDataset/7_Yelp/merged_positive.jsonl                          /mnt/SchemaDataset/7_Yelp/merged_negative.jsonl                            10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     8_VK                    /mnt/SchemaDataset/8_VK/vk_positive.jsonl                                /mnt/SchemaDataset/8_VK/vk_negative.jsonl                                  10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     12_Iceberg              /mnt/SchemaDataset/12_Iceberg/iceberg_positive.jsonl                     /mnt/SchemaDataset/12_Iceberg/iceberg_negative.jsonl                       10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     13_Ember                /mnt/SchemaDataset/13_Ember/ember_positive.jsonl                         /mnt/SchemaDataset/13_Ember/ember_negative.jsonl                           10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     21_ETH                  /mnt/SchemaDataset/21_ETH/merged_positive.jsonl                          /mnt/SchemaDataset/21_ETH/merged_negative.jsonl                            10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     22_GeoJSON              /mnt/SchemaDataset/22_GeoJSON/merged_positive.jsonl                      /mnt/SchemaDataset/22_GeoJSON/merged_negative.jsonl                        10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     23_MoviesInThailand     /mnt/SchemaDataset/23_MoviesInThailand/merged_positive.jsonl             /mnt/SchemaDataset/23_MoviesInThailand/merged_negative.jsonl               10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     31_RedDiscordBot        /mnt/SchemaDataset/31_RedDiscordBot/red_discordbot_positive____.jsonl    /mnt/SchemaDataset/31_RedDiscordBot/red_discordbot_negative____.jsonl      10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     32_Adonisrc             /mnt/SchemaDataset/32_Adonisrc/adonisrc_positive____.jsonl               /mnt/SchemaDataset/32_Adonisrc/adonisrc_negative____.jsonl                 10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     33_HelmChart            /mnt/SchemaDataset/33_HelmChart/helmchart_positive____.jsonl             /mnt/SchemaDataset/33_HelmChart/helmchart_negative____.jsonl               10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     34_Dolittle             /mnt/SchemaDataset/34_Dolittle/merged_positive.jsonl                     /mnt/SchemaDataset/34_Dolittle/merged_negative.jsonl                       10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     35_Drupal               /mnt/SchemaDataset/35_Drupal/merged_positive.jsonl                       /mnt/SchemaDataset/35_Drupal/merged_negative.jsonl                         10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     41_DeinConfig           /mnt/SchemaDataset/41_DeinConfig/deinconfig_positive.jsonl               /mnt/SchemaDataset/41_DeinConfig/deinconfig_negative.jsonl                 10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     43_Ecosystem            /mnt/SchemaDataset/43_Ecosystem/ecosystem_positive.jsonl                 /mnt/SchemaDataset/43_Ecosystem/ecosystem_negative.jsonl                   10      10      1         12           0.5       1
# ./experiment_param.sh     Accuracy     44_Plagiarize           /mnt/SchemaDataset/44_Plagiarize/plagiarize_positive.jsonl               /mnt/SchemaDataset/44_Plagiarize/plagiarize_negative.jsonl                 10      10      1         12           0.5       1