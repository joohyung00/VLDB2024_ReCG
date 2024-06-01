import sys
import argparse
import re


RUNTIME_PRINT_PATH = "../exp3_runtime.txt"
MEMORY_PRINT_PATH  = "../exp3_memory.txt"
RUNTIME_STRING_PER_ALGORITHM = {
    "ReCG": "TOTAL ELAPSED TIME",
    "jxplain": "Total Time: ",
    "kreduce": "Total Time: ",
    "lreduce": "Total Time: ",
    "klettke": "TOTAL ELAPSED TIME",
    "frozza": "TOTAL ELAPSED TIME"
}
MEMORY_STRING = "Maximum resident set size (kbytes)"


JXPLAIN_RUNTIME_ANALYSIS_PRINT_PATH = "../exp4_jxplain_runtime_analysis.txt"
JXPLAIN_RUNTIME_ANALYSIS_TARGET_STRINGS = [
    "1. Extract Complex Schemas: ",
    "2. Generate Feature Vectors: ",
    "3. Bimax: ",
    "4. Merge Schemas: ",
    "5. Variable Objs With Mult: ",
    "6. Variable Objs With Mult: "
]



def parseArguments(argv):
    parser = argparse.ArgumentParser(description = "Splits the positive samples into train and test set")
    
    parser.add_argument('--mode', choices = ["Runtime", "Memory", "Both"])
    parser.add_argument('--algorithm')
    parser.add_argument('--dataset_name')
    parser.add_argument('--train_perc')
    parser.add_argument('--experiment_num')
    parser.add_argument('--temp_file_path')
    
    args = parser.parse_args(argv)  
    print(args)
    
    return args



def main(argv):
    args = parseArguments(argv)

    if args.mode in ["Runtime", "Both"]:
        parseRuntime(args)
        if args.algorithm == "jxplain":
            parseJxplainRuntimeAnalysis(args)
    
    if args.mode in ["Memory", "Both"]:
        parseMemory(args)



def parseJxplainRuntimeAnalysis(args):
    with open(args.temp_file_path, "r") as f:
        lines = f.readlines()
        
        times = [-1 for _ in JXPLAIN_RUNTIME_ANALYSIS_TARGET_STRINGS]
        for line in lines:
            for i, target_string in enumerate(JXPLAIN_RUNTIME_ANALYSIS_TARGET_STRINGS):
                if target_string in line:
                    runtime_val_in_list = [int(s) for s in line.split() if s.isdigit()]
                    # print(runtime_val_in_list)
                    if len(runtime_val_in_list) != 1:
                        print("SOMETHING WRONG")
                        exit()
                    times[i] = runtime_val_in_list[0]
                    break
        
    with open(JXPLAIN_RUNTIME_ANALYSIS_PRINT_PATH, "a") as outfile:
        outstring = args.dataset_name + "," + args.train_perc + "," + args.experiment_num + ","
        for time in times:
            outstring += str(time) + ","
        outstring = outstring[:-1]
        outstring += "\n"
        outfile.write(outstring)
        
    return

def parseRuntime(args):
    with open(args.temp_file_path, "r") as f:
        lines = f.readlines()
        
        for line in lines:

            if RUNTIME_STRING_PER_ALGORITHM[args.algorithm] in line:
                runtime_val_in_list = [int(s) for s in line.split() if s.isdigit()]
                if len(runtime_val_in_list) != 1:
                    print("SOMETHING WRONG")
                    exit()
                break
            
        
    with open(RUNTIME_PRINT_PATH, "a") as outfile:
        outstring = args.algorithm + "," + args.dataset_name + "," + args.train_perc + "," + args.experiment_num + "," + str(runtime_val_in_list[0]) + "\n"
        outfile.write(outstring)
        
    return



def parseMemory(args):
    with open(args.temp_file_path, "r") as f:
        lines = f.readlines()
        
        for line in lines:
            if MEMORY_STRING in line:
                memory_val_in_list = [int(s) for s in line.split() if s.isdigit()]
                if len(memory_val_in_list) != 1:
                    print("SOMETHING WRONG")
                    exit()
                break
        
    with open(MEMORY_PRINT_PATH, "a") as outfile:
        outstring = args.algorithm + "," + args.dataset_name + "," + args.train_perc + "," + args.experiment_num + "," + str(memory_val_in_list[0]) + "\n"
        outfile.write(outstring)
        
    return




if __name__ == "__main__":
    main((sys.argv)[1:])