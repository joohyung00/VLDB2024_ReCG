#ifndef ARGPARSE
#define ARGPARSE

#include "utils.hpp"

#define ARG(x) argv[x * 2 - 1]
#define PARAM(x) argv[x * 2]




void printUsage(const char* argv0)
{
    cout << "Correct Usage: " 
        << argv0 << endl
        << "\t\t--in_path" << " " << "<str::pathToInputFile>" << endl
        << "\t\t--out_path" << " " << "<str::pathToSchemaFile>" << endl
        << "\t\t--mode" << " " << "<greedy|bnb|kbeam>" << endl
        << "\t\t--beam" << " " << "<int (0 < x)>" << endl
        << "\t\t--sample_size" << " " << "<int (10 <= x)>" << endl
        << "\t\t--epsilon" << " " << "<float (0.0 < x || x <= 1.0)>" << endl; 
    return;
}


int parseArguments(
    // In
    const int argc, 
    const char *const *const argv,
    // InOut
    string& in_path, 
    string& out_path, 
    SearchMode& search_mode,
    int& beam_size,
    int& sample_size,
    float& epsilon
)
{   
    cout << "argc: " << argc << endl;
    // 1. Check Argument Numbers;

    int target_args_num = 6;
    int anticipated_argc = 2 * target_args_num + 1;

    if(argc != anticipated_argc)
    {
        printUsage(argv[0]);
        return -1;
    }




    // 2. Check argument sequence (schema)
    if(
        string(ARG(1)) != "--in_path" || 
        string(ARG(2)) != "--out_path" || 
        string(ARG(3)) != "--mode" || 
        string(ARG(4)) != "--beam" ||
        string(ARG(5)) != "--sample_size" ||
        string(ARG(6)) != "--epsilon"
    )
    {
        printUsage(argv[0]);
        return -1;
    }




    // 3. Check each argument's validity
        
        // 3.1 Check if input file exists
    in_path = string(PARAM(1));
    ifstream file;
    file.open(in_path);
    if (!file)
    { 
        cout << "Given file does not exist" << endl;
        return -1;
    }

        // 3.2. No validity check needed for output file path (Maybe writable?)
    out_path = string(PARAM(2));

        // 3.3. About search mode  
    string input_mode = string(PARAM(3));
    if(input_mode == "greedy")
    {
        search_mode = kGreedy;
    }
    else if(input_mode == "bnb")
    {
        search_mode = kBranchAndBound;
    }
    else if(input_mode == "kbeam")
    {
        search_mode = kKBeam;
    }
    else
    {
        cout << "Not a valid search mode: <greedy|bnb>" << endl; 
        return -1;
    }

        // 3.4. About beam size
    string beam_size_str = string(PARAM(4));
    try
    {
        beam_size = stoi(beam_size_str);
    }
    catch(invalid_argument& e)
    {
        cout << "Invalid beam size input. Must be int-convertible." << endl;
        return -1;
    }
    catch(out_of_range& e)
    {
        cout << "Invalid beam size input. Out of int range." << endl;
        return -1;
    }
    if(beam_size < 1)
    {
        cout << "Invalid beam size: Must be greater than or equal to 1." << endl;
        return -1;
    }

        // 3.5. About sample_size
    string sample_size_str = string(PARAM(5));
    try
    {
        sample_size = stoi(sample_size_str);
    }
    catch(invalid_argument& e)
    {
        cout << "Invalid sample_size input. Must be int-convertible." << endl;
        return -1;
    }
    catch(out_of_range& e)
    {
        cout << "Invalid sample_size input. Out of int range." << endl;
        return -1;
    }
    if(sample_size < 10)
    {
        cout << "Invalid sample_size: Must be greater than or equal to 10." << endl;
        return -1;
    }
    

    string epsilon_str = string(PARAM(6));
    try
    {
        epsilon = stof(epsilon_str);
    }
    catch(invalid_argument& e)
    {
        cout << "Invalid sample_size input. Must be float-convertible." << endl;
        return -1;
    }
    catch(out_of_range& e)
    {
        cout << "Invalid sample_size input. Out of float range." << endl;
        return -1;
    }
    if(epsilon <= 0 || 1 < epsilon)
    {
        cout << "Invalid epsilo: must be (0 < epsilon && epsilon <= 1)" << endl;
        return -1;
    }

    
    return 1;
}



#endif