#ifndef INSTCLUSTERMERGE
#define INSTCLUSTERMERGE

#include "InstanceCluster.hpp"

int mergeInstanceClusters(
    InstanceCluster& a, 
    InstanceCluster& b, 
    ClusterType merging_type, 
    CostParameters& cost_parameters
);

void mergeHomHomToHom(InstanceCluster& a_hom, InstanceCluster& b_hom, CostParameters& cost_parameters);
void mergeHetHetToHet(InstanceCluster& a_het, InstanceCluster& b_het, CostParameters& cost_parameters);
void mergeComComToCom(InstanceCluster& a_com, InstanceCluster& b_com, CostParameters& cost_parameters);
void mergeHomHetToHet(InstanceCluster& a_hom, InstanceCluster& b_het, CostParameters& cost_parameters);
void mergeComHetToHet(InstanceCluster& a_com, InstanceCluster& b_het, CostParameters& cost_parameters);
void mergeHomComToCom(InstanceCluster& a_hom, InstanceCluster& b_com, CostParameters& cost_parameters);
void mergeHetComToCom(InstanceCluster& a_het, InstanceCluster& b_com, CostParameters& cost_parameters);

void unionInplace(SchemaSet* from, SchemaSet* to);
void mergeInplace(LabelToSchemaSet* from, LabelToSchemaSet* to);
void mergeInplace(LabelToCount* from, LabelToCount* to);

void unionInplace(InstanceTypeSet* from, InstanceTypeSet* to);
void mergeInplace(LabelToTypeSet* from, LabelToTypeSet* to);


#endif