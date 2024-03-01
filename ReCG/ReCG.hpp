#ifndef RECG
#define RECG

#include <string>
#include <fstream>
#include <chrono>


// [ReCG.hpp]
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

class ReCG
{
    private:
        string input_filepath_;
        string output_filepath_;
        SearchMode search_mode_;
        int beam_size_;
        int sample_size_;
        float epsilon_;

        Initiator initiator_;
        
        std::string* discovered_schema_;


    public:
        ReCG(
            string input_filepath, 
            string output_filepath, 
            SearchMode search_mode, 
            int beam_size, 
            int sample_size, 
            float epsilon
        )
        : input_filepath_(input_filepath), 
        output_filepath_(output_filepath), 
        search_mode_(search_mode),
        beam_size_(beam_size),
        sample_size_(sample_size),
        epsilon_(epsilon)
        { discovered_schema_ = new string(); }

        void run();

    private:

        void runInitiator();

        void discoverSchema();
            void searchKBeam();
            void searchBranchAndBound();
            void searchGreedy();
            

        void printSchema() const;
};

#endif