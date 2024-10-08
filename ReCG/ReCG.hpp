#ifndef RECG
#define RECG

#include <string>
#include <fstream>
#include <chrono>


// [Klettke.hpp]
#include "Search.hpp"
#include "StateNode.hpp"
// BottomUpSchemaGenerator.hpp
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
        string input_filepath_;
        string output_filepath_;
        parameters_ search_alg_;
        int beam_width_;
        // int sample_size_;
        // float epsilon_;
        // int min_pts_perc_;
        // float src_weight_;
        // float drc_weight_;
        Parameters* recg_parameters_;

        Initiator initiator_;
        
        std::string* discovered_schema_;


    public:
        Klettke(Parameters* parameters)
        : recg_parameters_(parameters)
        // : input_filepath_(input_filepath), 
        // output_filepath_(output_filepath), 
        // search_alg_(search_mode),
        // beam_width_(beam_width),
        // sample_size_(sample_size),
        // epsilon_(epsilon),
        // min_pts_perc_(min_pts_perc),
        // src_weight_(src_weight),
        // drc_weight_(drc_weight)
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