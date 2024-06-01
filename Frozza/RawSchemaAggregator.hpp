#ifndef RSCHAGGR
#define RSCHAGGR


#include "Instance.hpp"


class RawSchemaAggregator
{
    private:

        // Input
        SchemaForest* raw_schemas_;

        // Output
        SchemaForest* unique_raw_schemas_;
        vector<Count>* count_per_raw_schema_;

    
    public:
        RawSchemaAggregator()
        {}

        ~RawSchemaAggregator()
        {}

        void setRawSchemas(SchemaForest* raw_schemas)
        { raw_schemas_ = raw_schemas; }

        void setCountPerRawSchema(vector<Count>* count_per_raw_schema)
        { count_per_raw_schema_ = count_per_raw_schema; }

        void setUniqueRawSchemas(SchemaForest* unique_raw_schemas)
        { unique_raw_schemas_ = unique_raw_schemas; }

        void aggregateRawSchemas();

    private:

};





#endif