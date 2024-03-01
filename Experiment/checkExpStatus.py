
import csv
import sys
import argparse
from colorama import Fore, Style

sys.path.insert(1, "/root/jsdReCG/Experiment/utils")
from dataset_metadata import num_to_name
sys.path.insert(2, "/root/jsdReCG/ExperimentVisualization")
from aggregateExpResults import *



algorithms = ["ReCG", "kreduce", "jxplain", "groundtruth"]
train_percents = ["1", "10", "50", "90"]

line_separator = """ % --------------------------------------------------------------------------------------------------------- % \n"""




def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', choices = ["f1", "mdl", "perf", "ALL"])
    args = parser.parse_args(argv)  
    print(args)
    

    if(args.exp == "f1" or args.exp == "ALL"):
        checkF1Experiment("exp_f1.txt")
        
    if(args.exp == "mdl" or args.exp == "ALL"):
        checkMDLExperiment("exp_mdl.txt")
        
    if(args.exp == "perf" or args.exp == "ALL"):
        checkPerfExperiment("exp_perf.txt")

    


def checkF1Experiment(file_path):
    algorithms = ["ReCG", "jxplain", "kreduce"]
    train_percents = [1, 10, 50, 90]
    exp_nums = [1, 2, 3, 4, 5]
    
    for algorithm in algorithms:
        print()
        print("[[ ", algorithm, " ]]")
        print()
        for train_percent in train_percents:
            print("\t<< Percent: ", train_percent, "% >>" "\t", end = "")
        print()
        for num in num_to_name:
            
            for train_percent in train_percents:
            
                dataset_name = num_to_name[num][0][:2]
                data_name = num_to_name[num][0]
                print("\t", dataset_name, "\t", end = "")
                
                for exp_num in exp_nums:    
                
                    if getAccForAlgPercDatasetExpnum(algorithm, train_percent, data_name, exp_num) != (-1, -1, -1):
                        print(Fore.GREEN + 'O ', end = "")
                    else:
                        if algorithm == "jxplain" and dataset_name in ["1_", "6_", "31", "43", "44"]:
                            print(Fore.BLUE + "X ", end = "")
                        else:
                            print(Fore.RED + "X ", end = "")
                                
                print(Style.RESET_ALL, end = "")
                print("\t", end = "")
                    
            print()
        
        
        
def checkMDLExperiment(file_path):
    algorithms = ["groundtruth", "ReCG", "jxplain", "kreduce"]
    train_percents = [10]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    for algorithm in algorithms:
        print()
        print("[[ ", algorithm, " ]]")
        print()
        for train_percent in train_percents:
            print("\t<< Percent: ", train_percent, "% >>" "\t\t", end = "")
        print()
        for num in num_to_name:
            
            for train_percent in train_percents:
            
                dataset_name = num_to_name[num][0][:2]
                data_name = num_to_name[num][0]
                print("\t", dataset_name, "\t", end = "")
                
                for exp_num in exp_nums:    
                
                    if getMDLForAlgPercDatasetExpnum(algorithm, train_percent, data_name,   exp_num) != (-1, -1, -1):
                        print(Fore.GREEN + 'O ', end = "")
                    else:
                        if algorithm == "jxplain" and dataset_name in ["1_", "6_", "31", "43", "44"]:
                            print(Fore.BLUE + "X ", end = "")
                        else:
                            print(Fore.RED + "X ", end = "")
                                
                print(Style.RESET_ALL, end = "")
                print("\t", end = "")
                    
            print()

    

def checkPerfExperiment(file_path):
    
    algorithms = ["ReCG", "jxplain", "kreduce"]
    train_percents_1 = [10, 20, 30, 40, 50]
    train_percents_2 = [60, 70, 80, 90, 100]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    
    def printHorizontallyForTrainPercs(train_percs):
        for train_percent in train_percs:
            print("\t<< Percent: ", train_percent, "% >>" "\t\t", end = "")
        print()
        for num in num_to_name:
            
            for train_percent in train_percs:
                dataset_name = num_to_name[num][0][:2]
                data_name = num_to_name[num][0]
                print("\t", dataset_name, "\t", end = "")
                for exp_num in exp_nums:    
                    if getRuntimeForAlgPercDatasetExpnum(algorithm, train_percent, data_name, exp_num) != -1:
                        print(Fore.GREEN + 'O ', end = "")
                    else:
                        if algorithm == "jxplain" and dataset_name in ["1_", "6_", "31", "43", "44"]:
                            print(Fore.BLUE + "X ", end = "")
                        else:
                            print(Fore.RED + "X ", end = "")
                print(Style.RESET_ALL, end = "")
                print("\t", end = "")
            print()
    
    
    for algorithm in algorithms:
        print()
        print("[[ ", algorithm, " ]]")
        print()
        printHorizontallyForTrainPercs(train_percents_1)
        print()
        printHorizontallyForTrainPercs(train_percents_2)
        print()

    return 






if __name__ == "__main__":
    main((sys.argv)[1:])
    
    
    
    