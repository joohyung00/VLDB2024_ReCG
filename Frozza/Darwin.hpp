#ifndef DARWIN
#define DARWIN

#include <string>
#include <fstream>
#include <chrono>


// [Darwin.hpp]
#include "Initiator.hpp"
#include "RSUSConstructor.hpp"
#include "RawSchemaAggregator.hpp"
#include "RawSchemaConstructor.hpp"
#include "Instance.hpp"
// Schema.hpp
// EdgeLabelledTree.hpp
#include "utils.hpp"
// simdjson.h


class Darwin
{
    private:
        // Input of Darwin
        string input_filepath_;
        
        // Output of Drawin
        string* discovered_schema_;
        string output_filepath_;

        // 1. Initiation
        Initiator initiator_;
        
        // 2. Raw Schema Construction
        SchemaForest raw_schemas_;
        RawSchemaConstructor raw_schema_constructor_;

        // 3. Unique Raw Schemas
        SchemaForest unique_raw_schemas_;
        vector<Count> count_per_raw_schema_;
        RawSchemaAggregator raw_schema_aggregator_;

        // 4. RSUS Construction
        SchemaNode* rsus_;
        RSUSConstructor rsus_constructor_;


    public:
        Darwin(Parameters* parameters)
        {
            discovered_schema_ = new string(); 
            input_filepath_    = parameters->getInPath();
            output_filepath_   = parameters->getOutPath();

            InstanceForest temp({});
        }

        void run();

    private:

        void runInitiator();

        void constructRawSchemas();
        void aggregateRawSchemas();
        void unionIntoRSUS();

        void printSchema();
};

#endif