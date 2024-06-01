#ifndef RECG
#define RECG

#include <string>
#include <fstream>
#include <chrono>


// [ReCG.hpp]
#include "Search.hpp"
#include "StateNode.hpp"
// TopDownSchemaGenerator.hpp
// SchemaNodeDeriver.hpp
#include "Initiator.hpp"
// Clustering.hpp
// Distance.hpp
// InstanceCluster.hpp
#include "Schema.hpp"
// Instance.hpp
// EdgeLabelledTree.hpp
// utils.hpp
// simdjson.h

class Klettke
{
    private:
        Parameters* recg_parameters_;
        string input_filepath_;
        string output_filepath_;
        parameters_ search_alg_;
        int beam_width_;

        Initiator initiator_;
        
        std::string* discovered_schema_;


    public:
        Klettke(Parameters* parameters)
        : recg_parameters_(parameters)

        { 
            discovered_schema_ = new string(); 
            input_filepath_ = recg_parameters_->getInPath();
            output_filepath_ = recg_parameters_->getOutPath();
            search_alg_ = recg_parameters_->getSearchMode();
            beam_width_ = recg_parameters_->getBeamWidth();
        }

        void run();

    private:

        void printParameters();

        void runInitiator();

        void discoverSchema();
            void searchKBeam();
            void searchBranchAndBound();
            void searchGreedy();

            StateNode* setInitialState();
            

        void printSchema() const;
};

#endif