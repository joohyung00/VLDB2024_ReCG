#ifndef RSGCONSTR
#define RSGCONSTR


#include "Instance.hpp"


class ReducedSGConstructor
{
    private:
        SchemaNode* reduced_graph_;

        InstanceForest& instance_forest_;
    
    public:
        ReducedSGConstructor(InstanceForest& instance_forest)
        : instance_forest_(instance_forest)
        {}

        ~ReducedSGConstructor()
        {}

        void constructReducedSG();

        SchemaNode* getReducedSG()
        { return reduced_graph_; }

    private:

        SchemaNode* constructReducedSGRecursive(InstanceNode* instance_node, SchemaNode* rg_node);

        void boldifyLabelsRecursive(SchemaNode* schema_node);
};





#endif