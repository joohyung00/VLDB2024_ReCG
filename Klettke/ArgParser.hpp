#ifndef ARGPARSE
#define ARGPARSE

#include "utils.hpp"




void printUsage()
{
    cout << "Usage: " 
        << "Klettke" << endl
        << "\t--in_path" <<       " \t: " << "str (pathToInputFile)" << endl
        << "\t--out_path" <<      " \t: " << "str (pathToSchemaFile)" << endl;
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
    parameters->setInPath( input.getCmdOption("--in_path") );
    parameters->setOutPath(input.getCmdOption("--out_path"));

    return 1;
}


#endif