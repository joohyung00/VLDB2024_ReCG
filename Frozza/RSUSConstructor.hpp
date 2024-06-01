#ifndef RSUSCONSTR
#define RSUSCONSTR


#include "Instance.hpp"


class RSUSConstructor
{
    private:

        // Input
        SchemaForest* unique_raw_schemas_;
        vector<Count>* count_per_raw_schema_;

        // Output
        SchemaNode* rsus_;
    
    public:
        RSUSConstructor()
        {}

        // RSUSConstructor(InstanceForest& instance_forest)
        // : instance_forest_(instance_forest)
        // {}

        ~RSUSConstructor()
        {}

        void setUniqueRawSchemas(SchemaForest* unique_raw_schemas)
        { unique_raw_schemas_ = unique_raw_schemas; }

        void setCountPerRawSchema(vector<Count>* count_per_raw_schema)
        { count_per_raw_schema_ = count_per_raw_schema; }

        SchemaNode* getRSUS()
        { return rsus_; }

        void constructRSUS();

    private:

        SchemaNode* constructRSUSRecursive(SchemaNode* raw_schema_node, Count occur_count, SchemaNode* rsus_node);

        void boldifyLabelsRecursive(SchemaNode* schema_node);

};





#endif