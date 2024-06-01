#ifndef COST
#define COST


// StateNode.hpp
// BottomUpSchemaGenerator.hpp
// Clustering.hpp
// SchemaGeneration.hpp
// Distance.hpp

// Cost.hpp

#include "InstanceCluster.hpp"
// Initiator.hpp
// Schema.hpp
// Instance.hpp
// EdgeLabelledTree.hpp
// utils.hpp


MDLCost homObjSRC(InstanceCluster& hom_obj_cluster, CostParameters& cost_parameters);
MDLCost homObjDRC(InstanceCluster& hom_obj_cluster, CostParameters& cost_parameters);

MDLCost hetObjSRC(InstanceCluster& het_obj_cluster, CostParameters& cost_parameters);
MDLCost hetObjDRC(InstanceCluster& het_obj_cluster, CostParameters& cost_parameters);

MDLCost comObjSRC(InstanceCluster& com_obj_cluster, CostParameters& cost_parameters);
MDLCost comObjDRC(InstanceCluster& com_obj_cluster, CostParameters& cost_parameters);

MDLCost homArrSRC(InstanceCluster& hom_arr_cluster, CostParameters& cost_parameters);
MDLCost homArrDRC(InstanceCluster& hom_arr_cluster, CostParameters& cost_parameters);

MDLCost hetArrSRC(InstanceCluster& het_arr_cluster, CostParameters& cost_parameters);
MDLCost hetArrDRC(InstanceCluster& het_arr_cluster, CostParameters& cost_parameters);

MDLCost anyOfSRC(SchemaNode* any_of,                CostParameters& cost_parameters, int instance_num);
MDLCost anyOfDRC(SchemaNode* any_of,                CostParameters& cost_parameters, int instance_num);


MDLCost homObjKSE(SchemaNode* schema, InstanceCluster& hom_obj_cluster, CostParameters& cost_parameters);
MDLCost hetObjKSE(SchemaNode* schema, InstanceCluster& het_obj_cluster, CostParameters& cost_parameters);
MDLCost comObjKSE(SchemaNode* schema, InstanceCluster& com_obj_cluster, CostParameters& cost_parameters);
MDLCost homArrKSE(SchemaNode* schema, InstanceCluster& hom_arr_cluster, CostParameters& cost_parameters);
MDLCost hetArrKSE(SchemaNode* schema, InstanceCluster& het_arr_cluster, CostParameters& cost_parameters);
MDLCost anyOfKSE(SchemaNode* any_of, int instance_num);

#endif