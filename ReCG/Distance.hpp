#ifndef DISTANCE
#define DISTANCE

// [Distance]
#include "InstanceCluster.hpp"
#include "Cost.hpp"
// Schema.hpp
// Instance.hpp
// EdgeLabelledTree.hpp
// utils.hpp
// simdjson.h


// Instance Distance
float jaccardDistance(InstanceNode* inode_a, InstanceNode* inode_b);
float weightedJaccardDistance(InstanceNode* inode_a, InstanceNode* inode_b);
// hash32 hashCDInstance(InstanceNode* instance_node);



// Cluster Distance
class mergeInfo
{
    private:

        bool        meaningful_merge_;

        MDLCost     delta_mdl_;

        ClusterType to_merge_type_;

    public:
        
        mergeInfo()
        {}

        void setMeaningfulBit(bool bit)
        { meaningful_merge_ = bit; }

        void setDeltaMdl(MDLCost delta_mdl)
        { delta_mdl_ = delta_mdl; }

        void setMergeClusterType(ClusterType cluster_type)
        { to_merge_type_ = cluster_type; }

        bool getMeaningfulBit()
        { return meaningful_merge_; }

        MDLCost getDeltaMdl()
        { return delta_mdl_; }

        ClusterType getClusterType()
        { return to_merge_type_; }
};


mergeInfo clusterDistance(InstanceCluster& cluster_a, InstanceCluster& cluster_b, CostParameters& cost_parameters);
    int homHomClusterDist(InstanceCluster& a_hom, InstanceCluster& b_hom, CostParameters& cost_parameters, mergeInfo& merge_info);
    int homHetClusterDist(InstanceCluster& a_hom, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info);
    int hetHetClusterDist(InstanceCluster& a_het, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info);
    int homComClusterDist(InstanceCluster& a_hom, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info);
    int comComClusterDist(InstanceCluster& a_com, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info);
    int comHetClusterDist(InstanceCluster& a_com, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info);



#endif