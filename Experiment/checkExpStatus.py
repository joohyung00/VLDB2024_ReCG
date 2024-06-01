
import csv
import sys
import argparse
from colorama import Fore, Style
from art import tprint

sys.path.insert(1, "/root/JsonExplorerSpark/Experiment/utils")
from dataset_metadata import num_to_name, isRunnableExperiment
sys.path.insert(2, "/root/JsonExplorerSpark/ExperimentVisualization")
from aggregateExpResults import getAccForAlgPercDatasetExpnum, \
                                getMDLForAlgPercDatasetExpnum, \
                                getRuntimeForAlgPercDatasetExpnum, \
                                getResultForPercParamDatasetExpnum, \
                                getMemoryForAlgPercDatasetExpnum
                                # getAccForPercWeightDatasetExpnum



algorithms = ["ReCG", "kreduce", "jxplain", "lreduce", "klettke", "frozza", "groundtruth"]
train_percents = ["1", "10", "50", "90"]

line_separator = """ % --------------------------------------------------------------------------------------------------------- % \n"""




def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', choices = ["acc", "mdl", "runtime", "memory", "param", "wmdl", "ALL"])
    parser.add_argument('--subexp', choices = ["beam_width", "epsilon", "min_pts_perc", "sample_size", "mdl_weights"], default = "ALL")
    ######
    # parser.add_argument('--k')
    # parser.add_argument('--sample_size')
    # parser.add_argument("--epsilon")
    # parser.add_argument('--mode', choices = ["allAccuracy", "allPerformance"])

    args = parser.parse_args(argv)  
    print(args)

    if(args.exp == "acc" or args.exp == "ALL"):
        checkF1Experiment()
        
    if(args.exp == "mdl" or args.exp == "ALL"):
        checkMDLExperiment()
        
    if(args.exp == "runtime" or args.exp == "ALL"):
        checkPerfExperiment()

    if(args.exp == "memory" or args.exp == "ALL"):
        checkMemoryExperiment()
        
    if(args.exp == "param" or args.exp == "ALL"):
        checkParamExperiment(args.subexp)
        
    if(args.exp == "wmdl" or args.exp == "ALL"):
        checkWeightedMDLExperiment()
    
    return
    
    


def checkF1Experiment():
    algorithms = ["ReCG", "ReCG(TopDown)", "ReCG(KSE)", "jxplain", "kreduce", "lreduce", "klettke", "frozza"]
    train_percents = [1, 10, 50, 90]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    tprint("EXP: ACCURACY")
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
                
                    if getAccForAlgPercDatasetExpnum(algorithm, train_percent, data_name, exp_num) != (-1, -1, -1):
                        print(Fore.GREEN + 'O ', end = "")
                    else:
                        if isFailingExperiment(algorithm, dataset_name, train_percent):
                            print(Fore.BLUE + "X ", end = "")
                        else:
                            print(Fore.RED + "X ", end = "")
                                
                print(Style.RESET_ALL, end = "")
                print("\t", end = "")
                    
            print()
        
        
        
def checkMDLExperiment():
    algorithms = ["groundtruth", "ReCG", "jxplain", "kreduce", "lreduce", "klettke", "frozza"]
    train_percents = [10]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    tprint("EXP: MDL")
    for train_percent in train_percents:
        print()
        print("\t<< Percent: ", train_percent, "% >>")
        print()
        print("\t", end = "")
        for algorithm in algorithms:
            if algorithm in ["ReCG"]:
                print("[[ ", algorithm, " ]] \t\t\t\t", end = "")
            else:
                print("[[ ", algorithm, " ]] \t\t\t", end = "")
        
        print()
        for num in num_to_name:
            for algorithm in algorithms:
            
                
                for train_percent in train_percents:
                
                    dataset_name = num_to_name[num][0][:2]
                    data_name = num_to_name[num][0]
                    print("\t", dataset_name, "\t", end = "")
                    
                    for exp_num in exp_nums:    
                    
                        if getMDLForAlgPercDatasetExpnum(algorithm, train_percent, data_name, exp_num)[0] != -1:
                            print(Fore.GREEN + 'O ', end = "")
                        else:
                            if  isFailingExperiment(algorithm, dataset_name, train_percent):
                                print(Fore.BLUE + "X ", end = "")
                            else:
                                print(Fore.RED + "X ", end = "")
                                    
                    print(Style.RESET_ALL, end = "")
                    print("\t", end = "")
                        
                # print()
            print()
    print()
            

    

def checkPerfExperiment():
    
    algorithms = ["ReCG", "jxplain", "kreduce", "lreduce", "klettke", "frozza"]
    train_percents_1 = [10, 20, 30, 40, 50]
    train_percents_2 = [60, 70, 80, 90, 100]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    tprint("EXP: RUNTIME")
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
                        if isFailingExperiment(algorithm, dataset_name, train_percent):
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
        



def checkParamExperiment(target_subexp):
    
    RUNTIME_IDX = 3
    
    param_name_to_values = {
        "beam_width": [1, 2, 3, 4, 5],
        "epsilon": [0.1, 0.3, 0.5, 0.7, 0.9],
        "min_pts_perc": [1, 3, 5, 10, 20, 30],
        "sample_size": [25, 50, 100, 250, 500, 1000],
        "mdl_weights": [(0.01, 0.99), (0.1, 0.9), (0.3, 0.7), (0.5, 0.5), (0.7, 0.3), (0.9, 0.1), (0.99, 0.01)]
    }
    beam_width_cvd = {
        "epsilon": 0.1,
        "min_pts_perc": 1,
        "sample_size": 500,
        # "mdl_weights": (0.01, 0.99)
        # "mdl_weights": (0.1, 0.9)
        # "mdl_weights": (0.3, 0.7)
        # "mdl_weights": (0.5, 0.5)
    }
    beam_width_cvd = {
        "epsilon": 0.3,
        "min_pts_perc": 3,
        "sample_size": 500,
        "mdl_weights": (0.5, 0.5)
    }

    acc_target_percents = [10]
    runtime_target_percents = [40, 60, 80, 100]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    
    
    def visualizeSingleParamExp(param_name, param_value, acc_target_percents, runtime_target_percents, exp_nums, cvd):
        print()
        print("[[ " + paramNameToPrintName(param_name) + ": " + str(param_value) + " ]]")
        print()
        
        print("\t{{ Accuracy }} \t\t\t\t {{ MDL }} \t\t\t\t {{ Performance  }}")
        
        for train_percent in acc_target_percents:
            print("\t<< Percent: ", train_percent, "% >>" "\t\t", end = "")
        for train_percent in acc_target_percents:
            print("\t<< Percent: ", train_percent, "% >>" "\t\t", end = "")
        for train_percent in runtime_target_percents:
            print("\t<< Percent: ", train_percent, "% >>" "\t\t", end = "")
            
        print()
        
        for num in num_to_name:
            for train_percent in acc_target_percents:
            
                dataset_name = num_to_name[num][0][:2]
                data_name = num_to_name[num][0]
                print("\t", dataset_name, "\t", end = "")
                
                for exp_num in exp_nums:    
                    if getResultForPercParamDatasetExpnum(param_name, train_percent, param_value ,data_name, exp_num, cvd)[:RUNTIME_IDX] != (-1, -1, -1):
                        print(Fore.GREEN + 'O ', end = "")
                    else:
                        print(Fore.RED + "X ", end = "")
                print(Style.RESET_ALL, end = "")
                print("\t", end = "")
                
            for train_percent in acc_target_percents:
                
                    dataset_name = num_to_name[num][0][:2]
                    data_name = num_to_name[num][0]
                    print("\t", dataset_name, "\t", end = "")
                    
                    for exp_num in exp_nums:    
                        if getResultForPercParamDatasetExpnum(param_name, train_percent, param_value ,data_name, exp_num, cvd)[RUNTIME_IDX + 1:] != (-1, -1, -1):
                            print(Fore.GREEN + 'O ', end = "")
                        else:
                            print(Fore.RED + "X ", end = "")
                    print(Style.RESET_ALL, end = "")
                    print("\t", end = "")
            
            for train_percent in runtime_target_percents:
            
                dataset_name = num_to_name[num][0][:2]
                data_name = num_to_name[num][0]
                print("\t", dataset_name, "\t", end = "")
                
                for exp_num in exp_nums:    
                    if getResultForPercParamDatasetExpnum(param_name, train_percent, param_value ,data_name, exp_num, cvd)[RUNTIME_IDX] != -1:
                        print(Fore.GREEN + 'O ', end = "")
                    else:
                        print(Fore.RED + "X ", end = "")
                print(Style.RESET_ALL, end = "")
                print("\t", end = "")
            
            print()
        print()
    
    
    # for param_name in param_name_to_values:
    

    if target_subexp == "ALL":
        for param_name in param_name_to_values:
            if param_name == "beam_width":
                cvd = beam_width_cvd
                cvd["mdl_weights"] = (0.5, 0.5)
            elif param_name == "mdl_weights":
                cvd = mdl_weight_cvd
            else:
                cvd = None
            
            tprint("EXP: PARAM - " + paramNameToPrintName(param_name))
            for param_value in param_name_to_values[param_name]:
                visualizeSingleParamExp(param_name, param_value, acc_target_percents, runtime_target_percents, exp_nums, cvd)
                
    else:
        tprint("EXP: PARAM - " + paramNameToPrintName(target_subexp))
        
        if target_subexp == "beam_width":
            for mdl_weight in [(0.01, 0.99), (0.1, 0.9), (0.3, 0.7), (0.5, 0.5)]:
                beam_width_cvd["mdl_weights"] = mdl_weight
                for param_value in param_name_to_values[target_subexp]:
                    visualizeSingleParamExp(target_subexp, param_value, acc_target_percents, runtime_target_percents, exp_nums, beam_width_cvd)
                
        else:
            if target_subexp == "mdl_weights": cvd = mdl_weight_cvd
            else:                              cvd = None
            for param_value in param_name_to_values[target_subexp]:
                visualizeSingleParamExp(target_subexp, param_value, acc_target_percents, runtime_target_percents, exp_nums, cvd)
    
    
            
        
        
        
    
    
def paramNameToPrintName(param_name):
    if param_name == "beam_width":
        return "Beam Width"
    elif param_name == "epsilon":
        return "Epsilon"
    elif param_name == "min_pts_perc":
        return "MinPts Percentage"
    elif param_name == "sample_size":
        return "Sample Size"
    elif param_name == "mdl_weights":
        return "MDL Weights"
    else:
        print("Something went wrong in paramNameToPrintName")
        print()
    
    
    

def checkMemoryExperiment():
    algorithms = ["ReCG", "jxplain", "kreduce", "lreduce", "klettke"]
    train_percents_1 = [10, 20, 30, 40, 50]
    train_percents_2 = [60, 70, 80, 90, 100]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    tprint("EXP: MEMORY")
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
                    if getMemoryForAlgPercDatasetExpnum(algorithm, train_percent, data_name, exp_num) != -1:
                        print(Fore.GREEN + 'O ', end = "")
                    else:
                        if isFailingExperiment(algorithm, dataset_name, train_percent):
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





def checkWeightedMDLExperiment():
    train_percents = [10, 50, 90]
    mdl_weights = [(0.01, 0.99), (0.1, 0.9), (0.3, 0.7), (0.5, 0.5), (0.7, 0.3), (0.9, 0.1), (0.99, 0.01)]
    exp_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    tprint("EXP: WEIGHTED MDL")
    # for train_percent in train_percents:
    #     print()
    #     print("[[ Train Percent: ", train_percent, " % ]]")
    #     print()
    #     for mdl_weight in mdl_weights:
    #         print("\t<< ",  mdl_weight, " >>" "\t\t", end = "")
    #     print()
    #     for num in num_to_name:
            
    #         for mdl_weight in mdl_weights:
            
    #             dataset_name = num_to_name[num][0][:2]
    #             data_name = num_to_name[num][0]
    #             print("\t", dataset_name, "\t", end = "")
                
    #             for exp_num in exp_nums:    
    #                 if getAccForPercWeightDatasetExpnum(train_percent, mdl_weight, data_name, exp_num) != (-1, -1, -1):
    #                     print(Fore.GREEN + 'O ', end = "")
    #                 else:
    #                     print(Fore.RED + "X ", end = "")
                                
    #             print(Style.RESET_ALL, end = "")
    #             print("\t", end = "")
                    
    #         print()

    
    
    
def isFailingExperiment(algorithm, dataset_name, train_percent):
    return (algorithm == "jxplain" and dataset_name in ["1_", "6_", "31", "43", "44"]) or \
           (algorithm == "klettke" and dataset_name in ["6_"]) or \
           (algorithm == "klettke" and dataset_name in ["12"] and train_percent in [50, 60, 70, 80, 90, 100]) or \
           (algorithm == "klettke" and dataset_name in ["35"] and train_percent in [50, 60, 70, 80, 90, 100])
    

   
    












if __name__ == "__main__":
    main((sys.argv)[1:])