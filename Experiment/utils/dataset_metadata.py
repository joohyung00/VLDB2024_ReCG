
def isRunnableExperiment(target_algorithm, dataset_name, train_percent):
    return  not (target_algorithm in ["jxplain"] and dataset_name in ["1_NewYorkTimes", "6_Wikidata", "31_RedDiscordBot", "43_Ecosystem", "44_Plagiarize"])
            
            
possible_algorithms = set( ["ReCG", "ReCG(TopDown)", "ReCG(KSE)", "jxplain", "kreduce", "lreduce", "klettke", "frozza", "groundtruth"] )
possible_algorithms_list = ["ReCG", "ReCG(TopDown)", "ReCG(KSE)", "jxplain", "kreduce", "lreduce", "klettke", "frozza", "groundtruth"]

dataset_ids = [
    "1",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "12",
    "13",
    "21",
    "22",
    "23",
    "31",
    "32",
    "33",
    "34",
    "35",
    "41",
    "43",
    "44"
]

dataset_fullnames = [
    "1_NewYorkTimes",
    "3_Twitter",
    "4_Github",
    "5_Pharmaceutical",
    "6_Wikidata",
    "7_Yelp",
    "8_VK",
    "12_Iceberg",
    "13_Ember",
    "21_ETH",
    "22_GeoJSON",
    "23_MoviesInThailand",
    "31_RedDiscordBot",
    "32_Adonisrc",
    "33_HelmChart",
    "34_Dolittle",
    "35_Drupal",
    "41_DeinConfig",
    "43_Ecosystem",
    "44_Plagiarize"
]


num_to_name = {
    "1":  ('1_NewYorkTimes', "NYT"),
    "3":  ('3_Twitter', "Twitter"),
    "4":  ('4_Github', "Github" ),
    "5":  ('5_Pharmaceutical', "Pharmaceutical"),
    "6":  ('6_Wikidata', "Wikidata"),
    "7":  ('7_Yelp', "Yelp"),
    "8":  ('8_VK',  "VK"),
    "12": ('12_Iceberg',  "Iceberg"),
    "13": ('13_Ember',  "Ember"),
    "21": ('21_ETH', "ETH"),
    "22": ('22_GeoJSON', "GeoJSON" ),
    "23": ('23_MoviesInThailand', "ThaiMovies" ),
    "31": ('31_RedDiscordBot', "RDB" ),
    "32": ('32_Adonisrc', "AdonisRC" ),
    "33": ('33_HelmChart', "HelmChart" ),
    "34": ('34_Dolittle', "Dolittle"),
    "35": ('35_Drupal', "Drupal"),
    "41": ('41_DeinConfig', 'DeinConfig'),
    "43": ('43_Ecosystem', 'Ecosystem'),
    "44": ('44_Plagiarize', 'Plagiarize')
}

dataset_id_to_fullname = {
    "1": "1_NewYorkTimes",
    "3": "3_Twitter",
    "4": "4_Github",
    "5": "5_Pharmaceutical",
    "6": "6_Wikidata",
    "7": "7_Yelp",
    "8": "8_VK",
    "9": "9_OpenWeather",
    "12": "12_Iceberg",
    "13": "13_Ember",
    "21": "21_ETH",
    "22": "22_GeoJSON",
    "23": "23_MoviesInThailand",
    "31": "31_RedDiscordBot",
    "32": "32_Adonisrc",
    "33": "33_HelmChart",
    "34": "34_Dolittle",
    "35": "35_Drupal",
    "41": "41_DeinConfig",
    "43": "43_Ecosystem",
    "44": "44_Plagiarize"
}

dataset_id_to_positive_dataset_path = {
    "1":  "/root/VLDB2024_ReCG/Dataset/1_NewYorkTimes/new_york_times_positive.jsonl",
    "3":  "/root/VLDB2024_ReCG/Dataset/3_Twitter/twitter_positive.jsonl",
    "4":  "/root/VLDB2024_ReCG/Dataset/4_Github/merged_positive.jsonl",
    "5":  "/root/VLDB2024_ReCG/Dataset/5_Pharmaceutical/pharmaceutical_positive.jsonl",
    "6":  "/root/VLDB2024_ReCG/Dataset/6_Wikidata/wikidata_positive.jsonl",
    "7":  "/root/VLDB2024_ReCG/Dataset/7_Yelp/merged_positive.jsonl",
    "8":  "/root/VLDB2024_ReCG/Dataset/8_VK/vk_positive.jsonl",
    "12": "/root/VLDB2024_ReCG/Dataset/12_Iceberg/iceberg_positive.jsonl",
    "13": "/root/VLDB2024_ReCG/Dataset/13_Ember/ember_positive.jsonl",
    "21": "/root/VLDB2024_ReCG/Dataset/21_ETH/merged_positive.jsonl",
    "22": "/root/VLDB2024_ReCG/Dataset/22_GeoJSON/merged_positive.jsonl",
    "23": "/root/VLDB2024_ReCG/Dataset/23_MoviesInThailand/merged_positive.jsonl",
    "31": "/root/VLDB2024_ReCG/Dataset/31_RedDiscordBot/red_discordbot_positive____.jsonl",
    "32": "/root/VLDB2024_ReCG/Dataset/32_Adonisrc/adonisrc_positive____.jsonl",
    "33": "/root/VLDB2024_ReCG/Dataset/33_HelmChart/helmchart_positive____.jsonl",
    "34": "/root/VLDB2024_ReCG/Dataset/34_Dolittle/merged_positive.jsonl",
    "35": "/root/VLDB2024_ReCG/Dataset/35_Drupal/merged_positive.jsonl",
    "41": "/root/VLDB2024_ReCG/Dataset/41_DeinConfig/deinconfig_positive.jsonl",              
    "43": "/root/VLDB2024_ReCG/Dataset/43_Ecosystem/ecosystem_positive.jsonl",                
    "44": "/root/VLDB2024_ReCG/Dataset/44_Plagiarize/plagiarize_positive.jsonl"
}

dataset_id_to_negative_dataset_path = {
    "1":  "/root/VLDB2024_ReCG/Dataset/1_NewYorkTimes/new_york_times_negative.jsonl",
    "3":  "/root/VLDB2024_ReCG/Dataset/3_Twitter/twitter_negative.jsonl",
    "4":  "/root/VLDB2024_ReCG/Dataset/4_Github/merged_negative.jsonl",
    "5":  "/root/VLDB2024_ReCG/Dataset/5_Pharmaceutical/pharmaceutical_negative.jsonl",
    "6":  "/root/VLDB2024_ReCG/Dataset/6_Wikidata/wikidata_negative.jsonl",
    "7":  "/root/VLDB2024_ReCG/Dataset/7_Yelp/merged_negative.jsonl",
    "8":  "/root/VLDB2024_ReCG/Dataset/8_VK/vk_negative.jsonl",
    "12": "/root/VLDB2024_ReCG/Dataset/12_Iceberg/iceberg_negative.jsonl",
    "13": "/root/VLDB2024_ReCG/Dataset/13_Ember/ember_negative.jsonl",
    "21": "/root/VLDB2024_ReCG/Dataset/21_ETH/merged_negative.jsonl",
    "22": "/root/VLDB2024_ReCG/Dataset/22_GeoJSON/merged_negative.jsonl",
    "23": "/root/VLDB2024_ReCG/Dataset/23_MoviesInThailand/merged_negative.jsonl",
    "31": "/root/VLDB2024_ReCG/Dataset/31_RedDiscordBot/red_discordbot_negative____.jsonl",
    "32": "/root/VLDB2024_ReCG/Dataset/32_Adonisrc/adonisrc_negative____.jsonl",
    "33": "/root/VLDB2024_ReCG/Dataset/33_HelmChart/helmchart_negative____.jsonl",
    "34": "/root/VLDB2024_ReCG/Dataset/34_Dolittle/merged_negative.jsonl",
    "35": "/root/VLDB2024_ReCG/Dataset/35_Drupal/merged_negative.jsonl",
    "41": "/root/VLDB2024_ReCG/Dataset/41_DeinConfig/deinconfig_negative.jsonl",              
    "43": "/root/VLDB2024_ReCG/Dataset/43_Ecosystem/ecosystem_negative.jsonl",                
    "44": "/root/VLDB2024_ReCG/Dataset/44_Plagiarize/plagiarize_negative.jsonl"
}

schemaname_to_gtpath = \
{
    "1_NewYorkTimes"        : "/root/VLDB2024_ReCG/Dataset/1_NewYorkTimes/new_york_times.json",
    "3_Twitter"             : "/root/VLDB2024_ReCG/Dataset/3_Twitter/twitter_old.json",
    "4_Github"              : "/root/VLDB2024_ReCG/Dataset/4_Github/merged.json",
    "5_Pharmaceutical"      : "/root/VLDB2024_ReCG/Dataset/5_Pharmaceutical/pharmaceutical.json",
    "6_Wikidata"            : "/root/VLDB2024_ReCG/Dataset/6_Wikidata/wikidata.json",
    "7_Yelp"                : "/root/VLDB2024_ReCG/Dataset/7_Yelp/merged.json",
    "8_VK"                  : "/root/VLDB2024_ReCG/Dataset/8_VK/vk.json",
    "9_OpenWeather"         : "/root/VLDB2024_ReCG/Dataset/9_OpenWeather/open_weather.json",
    "12_Iceberg"            : "/root/VLDB2024_ReCG/Dataset/12_Iceberg/iceberg.json",
    "13_Ember"              : "/root/VLDB2024_ReCG/Dataset/13_Ember/ember.json",
    "21_ETH"                : "/root/VLDB2024_ReCG/Dataset/21_ETH/merged.json",
    "22_GeoJSON"            : "/root/VLDB2024_ReCG/Dataset/22_GeoJSON/merged.json",
    "23_MoviesInThailand"   : "/root/VLDB2024_ReCG/Dataset/23_MoviesInThailand/merged.json",
    "31_RedDiscordBot"      : "/root/VLDB2024_ReCG/Dataset/31_RedDiscordBot/red_discordbot.json",
    "32_Adonisrc"           : "/root/VLDB2024_ReCG/Dataset/32_Adonisrc/adonisrc.json",
    "33_HelmChart"          : "/root/VLDB2024_ReCG/Dataset/33_HelmChart/helmchart_.json",
    "34_Dolittle"           : "/root/VLDB2024_ReCG/Dataset/34_Dolittle/merged.json",
    "35_Drupal"             : "/root/VLDB2024_ReCG/Dataset/35_Drupal/merged.json",
    "41_DeinConfig"         : "/root/VLDB2024_ReCG/Dataset/41_DeinConfig/deinconfig_tree.json",
    "43_Ecosystem"          : "/root/VLDB2024_ReCG/Dataset/43_Ecosystem/ecosystem_tree.json",
    "44_Plagiarize"         : "/root/VLDB2024_ReCG/Dataset/44_Plagiarize/plagiarize.json"
}