#include "BottomUpSchemaGenerator.hpp"

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////// Merge to Generalize /////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

bool BottomUpSchemaGenerator::mergeToGeneralize()
{
    // 1. Update distances between clusters
    for(auto target_idx : update_targets_)
    {
        for(int i = 0; i < object_clusters_.size(); i++)
        {
            if(i == target_idx) continue;

            mergeInfo merge_info = clusterDistance(object_clusters_[i], object_clusters_[target_idx], cost_parameters_);

            if(merge_info.getMeaningfulBit())
            {
                merge_candidates_.push_back(
                    MergeCandidate(
                        merge_info.getDeltaMdl(),
                        i,
                        target_idx,
                        merge_info.getClusterType()
                    )
                );
            }
        }
    }
    update_targets_.clear();

    // 2. Pick the best pair
        // 2.1. If none exists, then return false
            // Semantic) none is merged: this state's transition is over
    if(!merge_candidates_.size()) return false;

        // 2.2. Pick the smallest of them all
    MDLCost smallest_delta_mdl = 100000000000;
    vectorIdx optimal_merge_candidate_idx = -1;
    vectorIdx merge_target_1;
    vectorIdx merge_target_2;
    ClusterType merging_type;

    for(int i = 0; i < merge_candidates_.size(); i++)
    {
        if(merge_candidates_[i].getDeltaMDL() < smallest_delta_mdl)
        {
            smallest_delta_mdl = merge_candidates_[i].getDeltaMDL();
            optimal_merge_candidate_idx = i;
        }
    }
    merge_candidates_[optimal_merge_candidate_idx].fillInMergeTargets(
        merge_target_1, 
        merge_target_2,
        merging_type
    );

    // cout << "Merging... " << object_clusters_[merge_target_1].getTypeInString() << ", " 
    //     << object_clusters_[merge_target_2].getTypeInString() << " -> ";
    
        // 2.3. Remove every merge candidates that include the two target indices
    // 3. Actual merging
    int to_leave = mergeInstanceClusters(
        object_clusters_[merge_target_1], 
        object_clusters_[merge_target_2], 
        merging_type,
        cost_parameters_
    );
    
    vector<MergeCandidate>::iterator candidates_iter;
    for (candidates_iter = merge_candidates_.begin(); candidates_iter != merge_candidates_.end(); ) 
    {
        if (candidates_iter->includesMergeTargets(merge_target_1, merge_target_2))
        {
            candidates_iter = merge_candidates_.erase(candidates_iter);
        }
        else
        {
            candidates_iter->resetIndices(merge_target_1, merge_target_2, to_leave);
            candidates_iter++;
        }
    }


    if(to_leave == 1) 
    {
        object_clusters_.erase(object_clusters_.begin() + merge_target_2);
        update_targets_.push_back(merge_target_1);
    }
    else if(to_leave == 2) 
    {
        object_clusters_.erase(object_clusters_.begin() + merge_target_1);
        update_targets_.push_back(merge_target_2 - 1);
    }
    else throw IllegalBehaviorError("BottomUpSchemaGenerator::mergeToGeneralize - `-1` returned from `mergeInstanceClusters`");
    // cout << object_clusters_[merge_target_1].getTypeInString() << endl;

    return true;
}


void BottomUpSchemaGenerator::setInitialDistanceCalculationTargets()
{
    for(vectorIdx i = 0; i < object_clusters_.size(); i++)
    { update_targets_.push_back(i); }
}