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

        bool        viable_;

        MDLCost     delta_mdl_;

        ClusterType to_merge_type_;

    public:
        
        mergeInfo()
        {}

        void setViableBit(bool bit)
        { viable_ = bit; }

        void setDeltaMdl(MDLCost delta_mdl)
        { delta_mdl_ = delta_mdl; }

        void setMergeClusterType(ClusterType cluster_type)
        { to_merge_type_ = cluster_type; }

        bool getViableBit()
        { return viable_; }

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



mergeInfo KSEDistance(InstanceCluster& cluster_a, InstanceCluster& cluster_b, CostParameters& cost_parameters);
    int homHomKSEClusterDist(InstanceCluster& a_hom, InstanceCluster& b_hom, CostParameters& cost_parameters, mergeInfo& merge_info);
    int homHetKSEClusterDist(InstanceCluster& a_hom, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info);
    int hetHetKSEClusterDist(InstanceCluster& a_het, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info);
    int homComKSEClusterDist(InstanceCluster& a_hom, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info);
    int comComKSEClusterDist(InstanceCluster& a_com, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info);
    int comHetKSEClusterDist(InstanceCluster& a_com, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info);

    MDLCost calculateKSEForTwoClusters(InstanceCluster& a, InstanceCluster& b, CostParameters& cost_parameters);


#endif