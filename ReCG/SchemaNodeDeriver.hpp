#ifndef SCHNODEGEN
#define SCHNODEGEN


// StateNode.hpp
// BottomUpSchemaGenerator.hpp
// Clustering.hpp
// SchemaGeneration.hpp
#include "Cost.hpp"
// #include "InstanceCluster.hpp"
// Initiator.hpp
// Distance.hpp
// Schema.hpp
// Instance.hpp
// EdgeLabelledTree.hpp
// utils.hpp




SchemaNode* deriveSchemaFromCluster(InstanceCluster& instance_cluster, CostParameters& cost_parameters);


SchemaNode* deriveObjectNode(InstanceCluster& object_cluster,       CostParameters& cost_parameters);
    SchemaNode* deriveHomObjNode(InstanceCluster& hom_obj_cluster,  CostParameters& cost_parameters);
    SchemaNode* deriveHetObjNode(InstanceCluster& het_obj_cluster,  CostParameters& cost_parameters);
    SchemaNode* deriveComObjNode(InstanceCluster& com_obj_cluster,  CostParameters& cost_parameters);

SchemaNode* deriveHomArrNode(InstanceCluster& hom_arr_cluster,      CostParameters& cost_parameters);

SchemaNode* deriveHetArrNode(InstanceCluster& het_arr_cluster,      CostParameters& cost_parameters);

SchemaNode* deriveAnyOfNode(SchemaSet& children_set,    CostParameters& cost_parameters, int data_num);
SchemaNode* deriveAnyOfNode(SchemaSet* children_set,    CostParameters& cost_parameters, int data_num);
SchemaNode* deriveAnyOfNode(SchemaVec& children_forest, CostParameters& cost_parameters, int data_num);

void mdlCostOptimizationAtAnyOf(SchemaNode* any_of_node);
void schemaConsicificationAtAnyOf(SchemaNode* any_of_node);

#endif