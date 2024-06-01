import os

negative_schema_paths = ["negative_schema_" + str(i) + ".json" for i in range(1, 11)]
temp_file_paths = ["temp_" + str(i) + ".txt" for i in range(1, 11)]


for negative_schema_path in negative_schema_paths:
    if os.path.exists(negative_schema_path):  os.remove(negative_schema_path)
for temp_file_path in temp_file_paths:
    if os.path.exists(temp_file_path):  os.remove(temp_file_path)