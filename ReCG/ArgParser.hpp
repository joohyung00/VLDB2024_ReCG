#ifndef ARGPARSE
#define ARGPARSE

#include "utils.hpp"


#define ARG(x) argv[x * 2 - 1]
#define PARAM(x) argv[x * 2]


#define DEFAULT_SEARCH_MODE kKBeam
#define DEFAULT_BEAM_WIDTH 3
#define DEFAULT_SAMPLE_SIZE 500
#define DEFAULT_EPSILON 0.5
#define DEFAULT_MIN_PTS_PERC 5
#define DEFAULT_SRC_WEIGHT 1
#define DEFAULT_DRC_WEIGHT 1






void printUsage()
{
    cout << "Usage: " 
        << "ReCG" << endl
        << "\t--in_path" <<       " \t: " << "str (pathToInputFile)" << endl
        << "\t--out_path" <<      " \t: " << "str (pathToSchemaFile)" << endl
        << "\t--search_alg" <<    " \t: " << "str {greedy, bnb, kbeam}" << endl
        << "\t--beam_width" <<    " \t\t: " << "int (0 < beam)" << endl
        << "\t--epsilon" <<       " \t: " << "float (0.0 < epsilon && epsilon <= 1.0)" << endl
        << "\t--min_pts_perc" <<  " \t: " << "int (0 < minPtsPerc && minPtsPerc <= 100)" << endl
        << "\t--sample_size" <<   " \t: " << "int (10 <= sample_size)" << endl
        << "\t--src_weight" <<    " \t: " << "float (0.0 <= src_weight && src_weight <= 1.0 && src_weight + drc_weight == 1)" << endl
        << "\t--drc_weight" <<    " \t: " << "float (0.0 <= drc_weight && drc_weight <= 1.0 && src_weight + drc_weight == 1)" << endl
        << "\t--cost_model" <<    " \t: " << "str {mdl, kse}" << endl;
    return;
}


class InputParser{
    private:
        vector <string> tokens;

    public:
        InputParser (int& argc, char** argv)
        {
            for (int i = 1; i < argc; i++)
            { this->tokens.push_back(string(argv[i])); }
        }
        
        /// @author iain
        const string& getCmdOption(const string &option) const
        {
            vector<string>::const_iterator itr;

            itr =  find(this->tokens.begin(), this->tokens.end(), option);
            if (itr != this->tokens.end() && ++itr != this->tokens.end())
            { return *itr; }

            static const string empty_string("");
            return empty_string;
        }

        /// @author iain
        bool cmdOptionExists(const string &option) const
        { return find(this->tokens.begin(), this->tokens.end(), option) != this->tokens.end(); }
};




class ValidValues{
    private:
        vector<string> valid_search_modes = {"greedy", "bnb", "kbeam"};

    public:
        ValidValues(int a)
        {}

        bool isValidSearchMode(string mode)
        { return find(valid_search_modes.begin(), valid_search_modes.end(), mode) != valid_search_modes.end(); }
};




int parseArguments(
    int argc, 
    char** argv,
    Parameters* parameters
)
{
    InputParser input(argc, argv);
    ValidValues value_validator(0);

    // if(input.cmdOptionExists("-h")){
    // }
    // const string &filename = input.getCmdOption("-f");
    // if (!filename.empty()){
    // }

    // #1. Check if all necessary arguments are given
    bool valid = true;
    if(!input.cmdOptionExists("--in_path"))
    {
        cout << "No input file is given" << endl;
        valid = false;
    }
    if(!input.cmdOptionExists("--out_path"))
    {
        cout << "No output file is given" << endl;
        valid = false;
    }
    if(!valid)
    {
        cout << endl;
        printUsage();
        return -1;
    }

    
    // #2. Check if each value for arguments are valid and assign them
    valid = true;

        // Input and output paths
    parameters->setInPath(input.getCmdOption("--in_path"));
    parameters->setOutPath(input.getCmdOption("--out_path"));

        // Search mode
    if(!input.cmdOptionExists("--search_alg"))
    { parameters->setSearchMode( DEFAULT_SEARCH_MODE ); }
    else
    {
        string mode = input.getCmdOption("--search_alg");
        if(value_validator.isValidSearchMode(mode))
        {
            if(mode == "greedy")
            { parameters->setSearchMode(kGreedy); }
            else if(mode == "bnb")
            { parameters->setSearchMode(kBranchAndBound); }
            else if(mode == "kbeam")
            { parameters->setSearchMode(kKBeam); }
        }
        else
        {
            cout << "Valid search modes: { greedy | bnb | kbeam }" << endl;
            valid = false;
        }
    }
    
        // Beam width
    if(input.cmdOptionExists("--beam_width"))
    {
        string beam_str = input.getCmdOption("--beam_width");

        try
        { parameters->setBeamWidth(stoi(beam_str)); }
        catch(invalid_argument& e)
        {
            cout << "Invalid beam width input. Must be int-convertible." << endl;
            valid = false;
        }
        catch(out_of_range& e)
        {
            cout << "Invalid beam width input. Out of int range." << endl;
            valid = false;
        }

        if( parameters->getBeamWidth() < 1)
        {
            cout << "Invalid beam width: Must be greater than or equal to 1." << endl;
            valid = false;
        }
    }
    else
    { parameters->setBeamWidth( DEFAULT_BEAM_WIDTH ); }


        // Epsilon
    if(input.cmdOptionExists("--epsilon"))
    {
        string epsilon_str = input.getCmdOption("--epsilon");

        try
        { parameters->setEpsilon( stof(epsilon_str) ); }
        catch(invalid_argument& e)
        {
            cout << "Invalid epsilon input. Must be float-convertible." << endl;
            valid = false;
        }
        catch(out_of_range& e)
        {
            cout << "Invalid epsilon input. Out of float range." << endl;
            valid = false;
        }

        if( parameters->getEpsilon() <= 0 || 1 < parameters->getEpsilon() )
        {
            cout << "Invalid epsilon: must be (0 < epsilon && epsilon <= 1)" << endl;
            valid = false;
        }
    }
    else
    { parameters->setEpsilon( DEFAULT_EPSILON); }


        // MinPts percentage
    if(input.cmdOptionExists("--min_pts_perc"))
    {
        string min_pts_perc_str = input.getCmdOption("--min_pts_perc");

        try
        { parameters->setMinPtsPerc( stoi(min_pts_perc_str) ); }
        catch(invalid_argument& e)
        {
            cout << "Invalid min_pts_perc input. Must be int-convertible." << endl;
            valid = false;
        }
        catch(out_of_range& e)
        {
            cout << "Invalid min_pts_perc input. Out of int range." << endl;
            valid = false;
        }

        if( parameters->getMinPtsPerc() < 1 || 100 < parameters->getMinPtsPerc() )
        {
            cout << "Invalid min_pts_perc: Must be between 1 and 100." << endl;
            valid = false;
        }
    }
    else
    { parameters->setMinPtsPerc( DEFAULT_MIN_PTS_PERC ); }



        // Sample size
    if(input.cmdOptionExists("--sample_size"))
    {
        string sample_size_str = input.getCmdOption("--sample_size");

        try
        { parameters->setSampleSize( stoi(sample_size_str) ); }
        catch(invalid_argument& e)
        {
            cout << "Invalid sample_size input. Must be int-convertible." << endl;
            valid = false;
        }
        catch(out_of_range& e)
        {
            cout << "Invalid sample_size input. Out of int range." << endl;
            valid = false;
        }

        if(parameters->getSampleSize() < 10)
        {
            cout << "Invalid sample_size: Must be greater than or equal to 10." << endl;
            valid = false;
        }
    }
    else
    { parameters->setSampleSize(DEFAULT_SAMPLE_SIZE); }




        // SRC weight, DRC weight
    if(input.cmdOptionExists("--src_weight") && input.cmdOptionExists("--drc_weight"))
    {
        string src_weight_str = input.getCmdOption("--src_weight");
        string drc_weight_str = input.getCmdOption("--drc_weight");

        try
        { 
            parameters->setSrcWeight( stof(src_weight_str) ); 
            parameters->setDrcWeight( stof(drc_weight_str) );
        }
        catch(invalid_argument& e)
        {
            cout << "Invalid src_weight or drc_weight input. Must be float-convertible." << endl;
            valid = false;
        }
        catch(out_of_range& e)
        {
            cout << "Invalid src_weight or drc_weight input. Out of float range." << endl;
            valid = false;
        }

        if( parameters->getSrcWeight() + parameters->getDrcWeight() != 1)
        {
            cout << "Invalid src_weight and drc_weight: must be (src_weight + drc_weight == 1)" << endl;
            valid = false;
        }
    }
    else if(!input.cmdOptionExists("--src_weight") && !input.cmdOptionExists("--drc_weight"))
    { 
        parameters->setSrcWeight( DEFAULT_SRC_WEIGHT );
        parameters->setDrcWeight( DEFAULT_DRC_WEIGHT );
    }
    else
    {
        cout << "Both src_weight and drc_weight must be given." << endl;
        valid = false;
    }


    

        // Cost model
    if(input.cmdOptionExists("--cost_model"))
    {
        string cost_model = input.getCmdOption("--cost_model");
        if(cost_model == "mdl")
        { parameters->setCostModel(kMDL); }
        else if(cost_model == "kse")
        { parameters->setCostModel(kKeySpaceEntropy); }
        else
        {
            cout << "Valid cost models: { mdl | kse }" << endl;
            valid = false;
        }
    }
    else
    {
        parameters->setCostModel(kMDL);
    }
    




    if(!valid)
    {
        cout << endl;
        printUsage();
        return -1;
    }
    return 1;
}


#endif