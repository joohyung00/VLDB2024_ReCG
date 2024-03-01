# [GENERATION]


# [POSITIVE SAMPLES] (Synthetic Dataset)

# (O) node json_generator.js      --num 100000                                     --in_path /mnt/SchemaDataset/31_RedDiscordBot/red_discordbot.json   --out_path /mnt/SchemaDataset/31_RedDiscordBot/red_discordbot_positive.jsonl 
# (O) node json_generator.js      --num 100000                                     --in_path /mnt/SchemaDataset/32_Adonisrc/adonisrc.json              --out_path /mnt/SchemaDataset/32_Adonisrc/adonisrc_positive.jsonl    
# (O) node json_generator.js      --num 100000                                     --in_path /mnt/SchemaDataset/33_HelmChart/helmchart.json            --out_path /mnt/SchemaDataset/33_HelmChart/helmchart_positive.jsonl  
# (O) node json_generator.js      --num 100000                                     --in_path /mnt/SchemaDataset/34_Dolittle/merged.json                --out_path /mnt/SchemaDataset/34_Dolittle/merged_positive.jsonl      
# (O) node json_generator.js      --num 100000                                     --in_path /mnt/SchemaDataset/35_Drupal/merged.json                  --out_path /mnt/SchemaDataset/35_Drupal/merged_positive.jsonl        

# [NEGATIVE SAMPLES]



# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/1_NewYorkTimes/new_york_times.json      --out_path /mnt/SchemaDataset/1_NewYorkTimes/new_york_times_negative.jsonl 
# python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/3_Twitter/twitter_old.json              --out_path /mnt/SchemaDataset/3_twitter_negative.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/4_Github/merged.json                    --out_path /mnt/SchemaDataset/4_Github/merged_negative.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/5_Pharmaceutical/pharmaceutical.json    --out_path /mnt/SchemaDataset/5_Pharmaceutical/pharmaceutical_negative.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/6_Wikidata/wikidata.json                --out_path /mnt/SchemaDataset/6_Wikidata/wikidata_negative.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/7_Yelp/merged.json                      --out_path /mnt/SchemaDataset/7_Yelp/merged_negative.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/8_VK/vk.json                            --out_path /mnt/SchemaDataset/8_VK/vk_negative.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/9_OpenWeather/open_weather.json         --out_path /mnt/SchemaDataset/9_OpenWeather/open_weather_negative.jsonl
# (X) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/11_MedicalStudies/medical_studies.json  --out_path /mnt/SchemaDataset/11_MedicalStudies/???
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/12_Iceberg/iceberg.json                 --out_path /mnt/SchemaDataset/12_Iceberg/iceberg_negative.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/13_Ember/ember.json                     --out_path /mnt/SchemaDataset/13_Ember/ember_negative.jsonl

python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/21_ETH/merged.json                      --out_path /mnt/SchemaDataset/21_ETH/merged_negative.jsonl
python3 negative_sample_generator.py --newS schema --newK schema --num 100000 --Sg /mnt/SchemaDataset/22_GeoJSON/merged.json                  --out_path /mnt/SchemaDataset/22_GeoJSON/merged_negative.jsonl
python3 negative_sample_generator.py --newS schema --newK schema --num 1400 --Sg /mnt/SchemaDataset/23_MoviesInThailand/merged.json         --out_path /mnt/SchemaDataset/23_MoviesInThailand/merged_negative.jsonl

# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 10000 --Sg /mnt/SchemaDataset/31_RedDiscordBot/red_discordbot.json       --out_path /mnt/SchemaDataset/31_RedDiscordBot/red_discordbot_negative____.jsonl
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 10000 --Sg /mnt/SchemaDataset/32_Adonisrc/adonisrc.json                  --out_path /mnt/SchemaDataset/32_Adonisrc/adonisrc_negative____.jsonl           
# (O) python3 negative_sample_generator.py --newS schema --newK schema --num 10000 --Sg /mnt/SchemaDataset/33_HelmChart/helmchart.json                --out_path /mnt/SchemaDataset/33_HelmChart/helmchart_negative____.jsonl         




# node json_generator.js --num 10000 --in_path /mnt/SchemaDataset/34_Dolittle/merged.json   --out_path /mnt/SchemaDataset/34_Dolittle/merged_positive.jsonl
# python3 negative_sample_generator.py --newS schema --newK schema --num 9500 --Sg /mnt/SchemaDataset/34_Dolittle/merged.json                    --out_path /mnt/SchemaDataset/34_Dolittle/merged_negative.jsonl    
# python3 negative_sample_generaotor.py --newS schema --newK schema --num 3333 --Sg /mnt/SchemaDataset/34_Dolittle/dolittle_artifacts.json                    --out_path /mnt/SchemaDataset/34_Dolittle/dolittle_artifacts_negative.jsonl    
# python3 negative_sample_generator.py --newS schema --newK schema --num 333 --Sg /mnt/SchemaDataset/34_Dolittle/dolittle_context.json                    --out_path /mnt/SchemaDataset/34_Dolittle/dolittle_context_negative.jsonl    
# python3 negative_sample_generatr.py --newS schema --newK schema --num 334 --Sg /mnt/SchemaDataset/34_Dolittle/dolittle_event.json                    --out_path /mnt/SchemaDataset/34_Dolittle/dolittle_event_negative.jsonl    


# node json_generator.js --num 10000 --in_path /mnt/SchemaDataset/35_Drupal/merged.json   --out_path /mnt/SchemaDataset/35_Drupal/merged_positive.jsonl
# python3 negative_sample_generator.py --newS schema --newK schema --num 9500 --Sg /mnt/SchemaDataset/35_Drupal/merged.json                      --out_path /mnt/SchemaDataset/35_Drupal/merged_negative.jsonl                 
# python3 negative_sample_generator.py --newS schema --newK schema --num 2000 --Sg /mnt/SchemaDataset/35_Drupal/drupal_breakpoints.json                  --out_path /mnt/SchemaDataset/35_Drupal/drupal_breakpoints_negative.jsonl
# python3 negative_sample_generator.py --newS schema --newK schema --num 2000 --Sg /mnt/SchemaDataset/35_Drupal/drupal_layouts.json                      --out_path /mnt/SchemaDataset/35_Drupal/drupal_layouts_negative.jsonl
# python3 negative_sample_generator.py --newS schema --newK schema --num 2000 --Sg /mnt/SchemaDataset/35_Drupal/drupal_linksmenu.json                    --out_path /mnt/SchemaDataset/35_Drupal/drupal_linksmenu_negative.jsonl
# python3 negative_sample_generator.py --newS schema --newK schema --num 2000 --Sg /mnt/SchemaDataset/35_Drupal/drupal_migration.json                    --out_path /mnt/SchemaDataset/35_Drupal/drupal_migration_negative.jsonl

# (X) python3 negative_sample_generator.py --newS schema --newK schema --num 10000 --Sg /mnt/SchemaDataset/36_GraphQL/graphql.json                  --out_path /mnt/SchemaDataset/36_GraphQL/graphql.jsonl



