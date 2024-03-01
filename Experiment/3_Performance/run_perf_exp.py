import sys
sys.path.insert(1, '/root/jsdReCG/Experiment')
from load_json import load_dataset, load_schema, count_lines, unreference_schema
sys.path.insert(2, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import dataset_ids, dataset_id_to_fullname, dataset_id_to_positive_dataset_path, dataset_id_to_negative_dataset_path, possible_algorithms

from itertools import product
import subprocess
import yaml



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
    target_algorithms = exp_config["target_algorithms"]
    target_dataset_ids = exp_config["target_dataset_ids"]
    train_percents = exp_config["target_percents"]
    exp_nums = exp_config["exp_nums"]
    iteration_order = exp_config["iteration_order"]
    
    # 2. Determine the iteration order
    iterating_order = []
    interpretation_order = []
    if iteration_order == None:
        iterating_order = [exp_nums, train_percents, target_algorithms, target_dataset_ids]
        interpretation_order = ["exp_num", "train_percent", "target_algorithm", "target_dataset_id"]
    else:
        for iteration_target in iteration_order:
            if   iteration_target == "target_algorithms": 
                iterating_order.append(target_algorithms)
                interpretation_order.append("target_algorithm")
            elif iteration_target == "target_dataset_ids": 
                iterating_order.append(target_dataset_ids)
                interpretation_order.append("target_dataset_id")
            elif iteration_target == "target_percents": 
                iterating_order.append(train_percents)
                interpretation_order.append("train_percent")
            elif iteration_target == "exp_nums": 
                iterating_order.append(exp_nums)
                interpretation_order.append("exp_num")
            else:
                print("Error: iteration_order must contain all 4 elements")
                return None
        
    # 3. Generate all combinations of the parameters
    all_combinations = list(product(*iterating_order))
    
    # 4. Run the experiments
    for param_list in all_combinations:
        
        # 4.1. Get the parameters and generate argument list for bash file
        target_algorithm = param_list[interpretation_order.index("target_algorithm")]
        target_dataset_id = param_list[interpretation_order.index("target_dataset_id")]
        train_percent = param_list[interpretation_order.index("train_percent")]
        exp_num = param_list[interpretation_order.index("exp_num")]
        
        dataset_name = dataset_id_to_fullname[target_dataset_id]
        positive_dataset_path = dataset_id_to_positive_dataset_path[target_dataset_id]
        negative_dataset_path = dataset_id_to_negative_dataset_path[target_dataset_id]
        
        arglist = [
            "bash", 
            "experiment_performance.sh",
            target_algorithm,
            dataset_name,
            positive_dataset_path,
            negative_dataset_path,
            train_percent,
            "10",
            exp_num
        ]
        # ./experiment_performance.sh ReCG 7_Yelp /mnt/SchemaDataset/7_Yelp/merged_positive.jsonl  /mnt/SchemaDataset/7_Yelp/merged_negative.jsonl 10 10 1
        
        if not (target_algorithm in ["jxplain"] and dataset_name in ["1_NewYorkTimes", "6_Wikidata", "31_RedDiscordBot", "43_Ecosystem", "44_Plagiarize"]):
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
        
        # 1. Check if target_algorithms are comprised of valid algorithms
        if "target_algorithms" not in config_obj:
            print("Error: target_algorithms not found in config")
            return None
        if not set(config_obj["target_algorithms"]).issubset(possible_algorithms):
            print("Error: target_algorithms must be a subset of possible_algorithms")
            return None
        parsed_config["target_algorithms"] = stringifyElements(config_obj["target_algorithms"])
        
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
        
        # 4. Check if exp_nums are comprised of valid experiment numbers
        if "exp_nums" not in config_obj:
            print("Error: exp_nums not found in config")
            return None
        parsed_config["exp_nums"] = stringifyElements(config_obj["exp_nums"])
        
        # 5. Check if iteration_order is valid
        if "iteration_order" in config_obj:
            iteration_order = config_obj["iteration_order"]
            if len(iteration_order) != 4:
                print("Error: iteration_order must be a list of 4 elements")
                return None
            config_param_set = {"target_algorithms", "target_dataset_ids", "target_percents", "exp_nums"}
            if set(iteration_order) != config_param_set:
                print("Error: iteration_order must contain all 4 elements")
                return None            
            parsed_config["iteration_order"] = stringifyElements(config_obj["iteration_order"])
        else:
            parsed_config["iteration_order"] = None

        print(parsed_config)

        return parsed_config
    
    # 1. Read the config file written in JSON or YAML
    config_file_path = "perf_exp_config.yaml"
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



# import subprocess
# from itertools import product

# out_path = "/root/jsdReCG/Experiment/exp_perf.txt"

# algo_name = [
#     "ReCG", 
#     # "kreduce", 
#     # "jxplain"
# ]

# name_pos_neg = \
# [
#     ('1_NewYorkTimes',      '/mnt/SchemaDataset/1_NewYorkTimes/new_york_times_positive.jsonl',          '/mnt/SchemaDataset/1_NewYorkTimes/new_york_times_negative.jsonl'),
#     ('3_Twitter',           '/mnt/SchemaDataset/3_Twitter/twitter_positive.jsonl',                      '/mnt/SchemaDataset/3_Twitter/twitter_negative.jsonl'),
#     ('4_Github',            '/mnt/SchemaDataset/4_Github/merged_positive.jsonl',                        '/mnt/SchemaDataset/4_Github/merged_negative.jsonl'),
#     ('5_Pharmaceutical',    '/mnt/SchemaDataset/5_Pharmaceutical/pharmaceutical_positive.jsonl',        '/mnt/SchemaDataset/5_Pharmaceutical/pharmaceutical_negative.jsonl'),
#     ('6_Wikidata',          '/mnt/SchemaDataset/6_Wikidata/wikidata_positive.jsonl',                    '/mnt/SchemaDataset/6_Wikidata/wikidata_negative.jsonl'),
#     ('7_Yelp',              '/mnt/SchemaDataset/7_Yelp/merged_positive.jsonl',                          '/mnt/SchemaDataset/7_Yelp/merged_negative.jsonl'),
#     ('8_VK',                '/mnt/SchemaDataset/8_VK/vk_positive.jsonl',                                '/mnt/SchemaDataset/8_VK/vk_negative.jsonl'),
#     ('12_Iceberg',          '/mnt/SchemaDataset/12_Iceberg/iceberg_positive.jsonl',                     '/mnt/SchemaDataset/12_Iceberg/iceberg_negative.jsonl'),
#     ('13_Ember',            '/mnt/SchemaDataset/13_Ember/ember_positive.jsonl',                         '/mnt/SchemaDataset/13_Ember/ember_negative.jsonl'),
#     ('21_ETH',              '/mnt/SchemaDataset/21_ETH/merged_positive.jsonl',                          '/mnt/SchemaDataset/21_ETH/merged_negative.jsonl'),
#     ('22_GeoJSON',          '/mnt/SchemaDataset/22_GeoJSON/merged_positive.jsonl',                      '/mnt/SchemaDataset/22_GeoJSON/merged_negative.jsonl'),
#     ('23_MoviesInThailand', '/mnt/SchemaDataset/23_MoviesInThailand/merged_positive.jsonl',             '/mnt/SchemaDataset/23_MoviesInThailand/merged_negative.jsonl'),
#     ('31_RedDiscordBot',    '/mnt/SchemaDataset/31_RedDiscordBot/red_discordbot_positive____.jsonl',    '/mnt/SchemaDataset/31_RedDiscordBot/red_discordbot_negative____.jsonl'),
#     ('32_Adonisrc',         '/mnt/SchemaDataset/32_Adonisrc/adonisrc_positive____.jsonl',               '/mnt/SchemaDataset/32_Adonisrc/adonisrc_negative____.jsonl'),
#     ('33_HelmChart',        '/mnt/SchemaDataset/33_HelmChart/helmchart_positive____.jsonl',             '/mnt/SchemaDataset/33_HelmChart/helmchart_negative____.jsonl'),
#     ('34_Dolittle',         '/mnt/SchemaDataset/34_Dolittle/merged_positive.jsonl',                     '/mnt/SchemaDataset/34_Dolittle/merged_negative.jsonl'),
#     ('35_Drupal',           '/mnt/SchemaDataset/35_Drupal/merged_positive.jsonl',                       '/mnt/SchemaDataset/35_Drupal/merged_negative.jsonl'),
#     ('41_DeinConfig',       '/mnt/SchemaDataset/41_DeinConfig/deinconfig_positive.jsonl',               '/mnt/SchemaDataset/41_DeinConfig/deinconfig_negative.jsonl'),              
#     ('43_Ecosystem',        '/mnt/SchemaDataset/43_Ecosystem/ecosystem_positive.jsonl',                 '/mnt/SchemaDataset/43_Ecosystem/ecosystem_negative.jsonl'),                
#     ('44_Plagiarize',       '/mnt/SchemaDataset/44_Plagiarize/plagiarize_positive.jsonl',               '/mnt/SchemaDataset/44_Plagiarize/plagiarize_negative.jsonl'),              
# ]

# train=[
#     '10',
#     '20',
#     '30',
#     '40',
#     '50',
#     '60',
#     '70',
#     '80',
#     '90',
#     '100'
#     ]

# start_end = ( "1", "10" )

# test = ['1']

# def main():
#     for exp_num in range(1, 11):
#         for algo_name_, train_, test_, name_pos_neg_ in product(algo_name, train, test, name_pos_neg):
#             arglist = ["bash", "experiment_performance.sh", algo_name_, str(exp_num), str(exp_num), *name_pos_neg_, train_, test_, "3", "1000", "0.5"]
#             print(arglist)
            
#             if not (algo_name_ == "jxplain" and 
#                     (
#                         name_pos_neg_[0] == "1_NewYorkTimes" or
#                         name_pos_neg_[0] == "6_Wikidata" or
#                         name_pos_neg_[0] == "31_RedDiscordBot" or
#                         name_pos_neg_[0] == "43_Ecosystem" or
#                         name_pos_neg_[0] == "44_Plagiarize"
#                     )):
#                 try:
#                     subprocess.run(arglist, timeout = 7200)
                    
#                 except subprocess.TimeoutExpired:
#                     with open(out_path, "a") as f:
#                         f.write(",".join(arglist) + ",timeout\n")
                        
#             else:
#                 with open(out_path, "a") as f:
#                     f.write(",".join(arglist) + ",timeout\n")
    


# if __name__ == "__main__":
#     main()


