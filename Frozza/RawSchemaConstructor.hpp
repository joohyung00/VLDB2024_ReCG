#ifndef RSCHCONSTR
#define RSCHCONSTR


#include "Instance.hpp"


class RawSchemaConstructor
{
    private:

        InstanceForest* instance_forest_;

        SchemaForest* raw_schemas_;
    
    public:

        RawSchemaConstructor()
        {}

        ~RawSchemaConstructor()
        {}

        // Get set
        void setInstanceForest(InstanceForest* instance_forest)
        { instance_forest_ = instance_forest; }

        void setRawSchemas(SchemaForest* raw_schemas)
        { raw_schemas_ = raw_schemas; }

        void constructRawSchemas();

    private:

        SchemaNode* constructSingleRawSchemaRecursive(InstanceNode* instance_node);


};





#endif