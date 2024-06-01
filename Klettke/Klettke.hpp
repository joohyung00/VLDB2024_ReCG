#ifndef KLETTKE
#define KLETTKE

#include <string>
#include <fstream>
#include <chrono>


// [Klettke.hpp]
#include "Initiator.hpp"
#include "ReducedSGConstructor.hpp"
#include "Schema.hpp"
// Instance.hpp
// EdgeLabelledTree.hpp
#include "utils.hpp"
// simdjson.h

class Klettke
{
    private:
        string input_filepath_;
        string output_filepath_;

        Initiator initiator_;
        
        SchemaNode* rg_tree_;

        string* discovered_schema_;


    public:
        Klettke(Parameters* parameters)
        {
            discovered_schema_ = new string(); 
            input_filepath_ = parameters->getInPath();
            output_filepath_ = parameters->getOutPath();
        }

        void run();

    private:

        void runInitiator();

        void constructRG();

        void printSchema();
};

#endif