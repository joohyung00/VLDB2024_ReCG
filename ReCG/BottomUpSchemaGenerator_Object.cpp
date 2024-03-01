#include "BottomUpSchemaGenerator.hpp"



void BottomUpSchemaGenerator::clusterAndGeneralizeObjects()
{
    InstanceForest& object_forest = grouped_instances_->getInstanceForestByType(kObject);
    vector<bool> mask(object_forest.size(), true);
    int unmasked_num = mask.size();

    // 1. First filter out empty objects / het objects(using outliers)
    preprocessInstances(mask, unmasked_num);

    // 2. Cluster hom/com/het
    clusterCDObjects(mask, unmasked_num);
    
    // 3. Generlize CD-instances, then cluster again
    generalizeOutlierObjects(mask, unmasked_num);
    clusterGeneralizedOutlierObjects(mask, unmasked_num);
    if(unmasked_num > 0)
    { treatEdgeCases(mask, unmasked_num); }
    

    // 4. Update metadata
    updateClustersMetadata();

    // 5. Filter out false(?) homogeneous clusters using metadata
    // cout << "HERE" << endl;
    // filterHeterogeneousClusters();
    // cout << "HERE2" << endl;
}






////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////// Cluster & Generalize /////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void BottomUpSchemaGenerator::preprocessInstances(vector<bool>& mask, int& instance_num)
{
    InstanceForest& object_forest = grouped_instances_->getInstanceForestByType(kObject);

    // 1. Update instances + 
    object_clusters_.push_back(InstanceCluster(kEmptyObjC));
    for(int i = 0; i < mask.size(); i++)
    {
        object_forest[i]->updateBitmaps();
        
        if(!object_forest[i]->getChildrenNum())
        {
            object_clusters_.back().addInstance(object_forest[i]);
            mask[i] = false;
            instance_num--;
        }
    }
    if(!object_clusters_.back().getForestSize())
    { object_clusters_.clear(); }

    // 2. Filter out heterogeneous objects
    filterHeterogeneousObjects(mask, instance_num);
}

void BottomUpSchemaGenerator::filterHeterogeneousObjects(vector<bool>& mask, int& instance_num)
{
    // Get object instances
    // printHeader();
    // cout << "   [Filtering Hetero Objects]" << endl;

    InstanceForest& object_forest = grouped_instances_->getInstanceForestByType(kObject);

    unordered_map<hash32, roaring_bitmap_t*> children_hash_to_set_bitmap;

    for(int i = 0; i < mask.size(); i++)
    {
        if(!mask[i]) continue;
        // 1. Find an instance with only `*`
        if( roaring_bitmap_get_cardinality(object_forest[i]->getUnkleenedLabelBitmap()) == 0 )
        {
                // Heuristic!
                // There might be homogeneous objects that only have primitive schemas that are existent in heterogeneous objects!
            // + check if there is at least one or more non-primitive schemas
            vector<Node*>& children = object_forest[i]->getChildren();
            bool all_primitives = true;
            hash32 hash_val = 0;
            SchemaSet children_set;
            for(int i = 0; i < children.size(); i++)
            {
                SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema());
                children_set.insert(derived_schema);

                if(!isPrimitive(derived_schema->getType()))
                { 
                    all_primitives = false;
                    break;
                }
            }

            // If not all_primitives, then add it to the map
                // TOCHECK: May have error here
            if(!all_primitives)
            {
                // CAN BE IMPROVED: direct hashing from roaring_bitmap_t
                for(auto schema_ptr : children_set)
                { 
                    hash_val ^= schema_ptr->getId(); 
                }

                auto it = children_hash_to_set_bitmap.find(hash_val);
                if(it == children_hash_to_set_bitmap.end())
                {
                    children_hash_to_set_bitmap.insert( {hash_val, object_forest[i]->getChildrenSchemasBitmap()} ); 
                }
            }
        }
    }
    // 1.1. Return if none exists
    if(children_hash_to_set_bitmap.size() == 0) 
    {
        // printHeader();
        // cout << "   [None were found]" << endl;
        return;
    }

    // for(auto hash_bitmap_pair : children_hash_to_set_bitmap)
    // {
    //     cout << hash_bitmap_pair.first << ": " << endl;
    //     roaring_bitmap_printf(hash_bitmap_pair.second);
    //     cout << endl << endl;
    // }

    while(children_hash_to_set_bitmap.size())
    {
        // 2. Pick the one with the least number of distinct children schemas
        Count min_sch_num = 10000;
        hash32 target_hash;
        roaring_bitmap_t* target_bitmap;
        for(auto it = children_hash_to_set_bitmap.begin(); it != children_hash_to_set_bitmap.end(); it++)
        {
            if(roaring_bitmap_get_cardinality(it->second) < min_sch_num) 
            {
                min_sch_num = roaring_bitmap_get_cardinality(it->second);
                target_hash = it->first;
                target_bitmap = it->second;
            }
        }
        children_hash_to_set_bitmap.erase(target_hash);
        // 3. Filter each out as a cluster

        // 3.1. Generate a heterogeneous object cluster
        object_clusters_.push_back(InstanceCluster(kHetObjC));

        // 3.2. Check whether another instance can be expressed with that pattern        
        for(int i = 0; i < object_forest.size(); i++)
        {
            if(!mask[i]) continue; 

            roaring_bitmap_t* children_schema_ids = object_forest[i]->getChildrenSchemasBitmap();

            if( roaring_bitmap_equals(target_bitmap, children_schema_ids) )
            {
                object_clusters_.back().addInstance(object_forest[i]);
                mask[i] = false;
                instance_num--;
            }
        }
            // 
            // 
        if(object_clusters_.back().getForestSize() == 0)
        { object_clusters_.pop_back(); }
        // cout << roaring_bitmap_get_cardinality(target_bitmap) << endl;
        // cout << instance_num << endl << endl;
        // roaring_bitmap_printf(target_bitmap);
        // cout << endl;
    }
    // printHeader();
    // cout << "[Some found]" << endl;
    return;
}














    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////// 2. Cluster Hom/Com/Het /////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


void BottomUpSchemaGenerator::clusterCDObjects(vector<bool>& mask, int& instance_num)
{
    InstanceForest& object_forest = grouped_instances_->getInstanceForestByType(kObject);

    // 1. Random sample + Linear Filtering via Clustering Result of DBSCAN
    bool repeat = true;
    int sample_num = sample_size_;
    while(instance_num > sample_num && repeat)
    {
        // 1.1. Sample 1000 instances
        InstanceForest samples;
        int to_sample_more = sample_num;
        for(int i = 0; i < mask.size(); i++)
        {
            if(mask[i])
            {
                samples.push_back(object_forest[i]);
                if(to_sample_more-- < 0) break;
            }
        }

        // 1.2. Perform clustering
        InstanceForest biggest_cluster;

        Dbscan dbscan(samples, epsilon_, min_points_, "l");
        dbscan.cluster();
        dbscan.getBiggestCluster(biggest_cluster);

        // cout << "Biggest Cluster #: " << biggest_cluster.size() << endl;

        if(biggest_cluster.size() == 0)
        { 
            repeat = false; 
            continue; 
        }

        // 1.3. Keys + parameterized types of the cluster
        // 1.4. Linearly check the containment of the cluster
        linearlyFilterObjects(object_forest, mask, instance_num, biggest_cluster);

    }


    // 2. Leftover samples < `sample_num`
    if(repeat)
    {
        // 2.1. Gather Leftover Instances
        InstanceForest leftovers;
        vector<int> mask_map;
        for(int i = 0; i < mask.size(); i++)
        { 
            if(mask[i])
            { 
                leftovers.push_back(object_forest[i]); 
                mask_map.push_back(i);
            }
        }

        // 2.2. Perform DBSCAN
        Dbscan dbscan(leftovers, epsilon_, min_points_, "l");
        dbscan.cluster();
        int max_label;
        vector<int> labels = dbscan.getLabels(max_label);

        // 2.3. Make Instance Cluster with them
        for(int i = 0; i <= max_label; i++)
        {
            object_clusters_.push_back(InstanceCluster(kHomObjC));
            object_clusters_.back().getInstanceForest()->reserve(leftovers.size());
        }
        for(int i = 0; i < labels.size(); i++)
        {
            int cluster_num = labels[i];
            if(cluster_num != -1)
            { 
                object_clusters_[object_clusters_.size() - 1 - cluster_num].addInstance(leftovers[i]); 
                mask[mask_map[i]] = false;
                instance_num--;
            }
        }

        // 2.4. Update Instance Cluster Type according to Instances 
        for(int i = 0; i <= max_label; i++)
        { object_clusters_[object_clusters_.size() - 1 - i].updateClusterType(); }
    }
}












    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////// 3. Generlize-Cluster /////////////////////////////////////////////////
    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



void BottomUpSchemaGenerator::generalizeOutlierObjects(vector<bool>& mask, int& unmasked_num)
{
    InstanceForest& object_forest = grouped_instances_->getInstanceForestByType(kObject);
    
    #if VERBOSE2
      printHeader();
      cout << "Generalizing Outliers #: " << unmasked_num << endl;
    #endif

    for(int i = 0; i < object_forest.size(); i++)
    {
        if(mask[i]) 
        { object_forest[i]->generalizeOutlier(); }
    }
}


void BottomUpSchemaGenerator::clusterGeneralizedOutlierObjects(vector<bool>& mask, int& instance_num)
{
    #if VERBOSE2
      printHeader();
      cout << "Reclustering Generalized Outliers..." << endl;
    #endif 

    InstanceForest& object_forest = grouped_instances_->getInstanceForestByType(kObject);

    // 1. Random sample + Linear Filtering
    bool repeat = true;
    int sample_num = sample_size_;
    
    while(instance_num > sample_num && repeat)
    {
        // 1.1. Sample Instances
        InstanceForest samples;
        int to_sample_more = sample_num;
        for(int i = 0; i < mask.size(); i++)
        {
            if(mask[i])
            {
                samples.push_back(object_forest[i]);
                if(to_sample_more-- < 0) break;
            }
        }

        // 1.2. Perform clustering with Sampled Instances
        InstanceForest biggest_cluster;

        Dbscan dbscan(samples, epsilon_, min_points_, "leq");
        dbscan.cluster();
        dbscan.getBiggestCluster(biggest_cluster);

        if(biggest_cluster.size() == 0)
        { repeat = false; continue; }

        // 1.3. Linearly Filter Instances 
        //      that match the pattern of the biggest cluster
        linearlyFilterObjects(object_forest, mask, instance_num, biggest_cluster);
    }

    // if(instance_num == 0) return;
    
}


void BottomUpSchemaGenerator::treatEdgeCases(vector<bool>& mask, int& instance_num)
{
    InstanceForest& object_forest = grouped_instances_->getInstanceForestByType(kObject);
    
    // 1. Gather Leftover Instances
    InstanceForest leftovers;
    vector<int> mask_map;
    for(int i = 0; i < mask.size(); i++)
    { 
        if(mask[i])
        {
            leftovers.push_back(object_forest[i]); 
            mask_map.push_back(i);
        }
    }
    #if VERBOSE2
      cout << "Object leftovers: " << leftovers.size() << endl;
    #endif

    if(leftovers.size() < sample_size_)
    {
        // (a).1. Perform Naive DBSCAN
        int max_label;
        Dbscan dbscan(leftovers, epsilon_, min_points_, "leq");
        dbscan.cluster();
        vector<int> labels = dbscan.getLabels(max_label);

        // (a).2. Put Clusters as InstanceCluster
        for(int i = 0; i <= max_label; i++)
        {
            object_clusters_.push_back(InstanceCluster(kHetObjC));
            object_clusters_.back().getInstanceForest()->reserve(leftovers.size());
        }
        for(int i = 0; i < labels.size(); i++)
        {
            int cluster_num = labels[i];
            if(cluster_num != -1)
            { 
                object_clusters_[object_clusters_.size() - 1 - cluster_num].addInstance(leftovers[i]); 
                mask[mask_map[i]] = false;
                instance_num--;
            }
        }

        // (a).3. Gather leftovers that weren't clustered
        leftovers.clear();
        mask_map.clear();
        for(int i = 0; i < mask.size(); i++)
        {
            if(mask[i])
            {
                leftovers.push_back(object_forest[i]);
                mask_map.push_back(i);
            }
        }

        // (a).4. Ungeneralize Instances
        for(auto& leftover_instance : leftovers)
        {
            // Turn the instance back to ungeneralized form
            leftover_instance->updateBitmaps();
        }

        // (a).5. DBSCAN Outliers with `min_points` = 1 (1 neighbor in epsilon range)
        max_label = -1;
        Dbscan dbscan_outliers(leftovers, epsilon_, 1, "leq");
        dbscan_outliers.cluster();
        labels = dbscan_outliers.getLabels(max_label);

        // (a).6. Make them into clusters
        for(int i = 0; i <= max_label; i++)
        {
            object_clusters_.push_back(InstanceCluster(kHomObjC));
            object_clusters_.back().getInstanceForest()->reserve(leftovers.size());
        }
        for(int i = 0; i < labels.size(); i++)
        {
            int cluster_num = labels[i];
            if(cluster_num != -1)
            { 
                object_clusters_[object_clusters_.size() - 1 - cluster_num].addInstance(leftovers[i]); 
                mask[mask_map[i]] = false;
                instance_num--;
            }
            // else
            //   cluster_num == -1
            //   Leave outlier's mask as true
        }

        // (a).7. Update Instance Cluster Type
        for(int i = 0; i <= max_label; i++)
        { object_clusters_[object_clusters_.size() - 1 - i].updateClusterType(); }

        // (a).8. The last outliers are clusters as their own
        for(int i = 0; i < labels.size(); i++)
        {
            if(labels[i] == -1)
            {
                object_clusters_.push_back(InstanceCluster(kHomObjC));
                object_clusters_.back().getInstanceForest()->push_back(leftovers[i]);
                object_clusters_.back().updateClusterType();
                mask[mask_map[i]] = false;
                instance_num--;
            }
        }

        if(instance_num > 0) cout << "Impossible case: edge case 1" << endl;
    }
    else
    {
        // (b). Random sample + Linear Filter with smaller number of min_pts
        bool repeat = true;
        int sample_num = sample_size_;
        
        while(instance_num > sample_num && repeat)
        {
            // (b).1. Sample Instances
            InstanceForest samples;
            int to_sample_more = sample_num;
            for(int i = 0; i < mask.size(); i++)
            {
                if(mask[i])
                {
                    samples.push_back(object_forest[i]);
                    if(to_sample_more-- < 0) break;
                }
            }

            // (b).2. Perform clustering with Sampled Instances
            InstanceForest biggest_cluster;

            Dbscan dbscan(samples, epsilon_, 1, "leq");
            dbscan.cluster();
            dbscan.getBiggestCluster(biggest_cluster);

            if(biggest_cluster.size() == 0)
            { repeat = false; continue; }

            // 1.3. Linearly Filter Instances 
            //      that match the pattern of the biggest cluster
            linearlyFilterObjects(object_forest, mask, instance_num, biggest_cluster);
        }

        while(instance_num > 0)
        {
            // Sample instances
            InstanceForest biggest_cluster;
            for(int i = 0; i < mask.size(); i++)
            {
                if(mask[i])
                {
                    biggest_cluster.push_back(object_forest[i]);
                    break;
                }
            }

            // cout << "Biggest Cluster #: " << biggest_cluster.size() << endl;

            // 3. Keys + parameterized types of the cluster
            // 4. Linearly check the containment of the cluster
            linearlyFilterObjects(object_forest, mask, instance_num, biggest_cluster);
        }
        if(instance_num > 0)
        {
            cout << "Object leftover instances: " << instance_num << endl;
            cout << "Impssible case: edge case 2" << endl;
        }

        // if(instance_num == 0) return;
    }
    

    
}








        ////////////////////////////////////////////////////////////////////
        /////////////////////////// Subfunctions ///////////////////////////
        ////////////////////////////////////////////////////////////////////


void BottomUpSchemaGenerator::linearlyFilterObjects(
    InstanceForest& object_forest, 
    std::vector<bool>& mask,
    int& unmasked_num,
    InstanceForest& biggest_cluster
)
{
    // 1. Put the most general pattern within one instance
    roaring_bitmap_t* general_key       =       roaring_bitmap_create();
    roaring_bitmap_t* general_key_schema =      roaring_bitmap_create();
    roaring_bitmap_t* general_kleene_schema =   roaring_bitmap_create();

    for(auto& cluster_object : biggest_cluster)
    {
        roaring_bitmap_t* key =        cluster_object->getUnkleenedLabelBitmap();
        roaring_bitmap_t* key_schema = cluster_object->getLabelSchemaBitmap();
        roaring_bitmap_t* kleene_schema = cluster_object->getKleenedSchemas();
         
        roaring_bitmap_or_inplace(general_key, key);
        roaring_bitmap_or_inplace(general_key_schema, key_schema);
        roaring_bitmap_or_inplace(general_kleene_schema, kleene_schema);
    }

    // 2. Check whether another instance can be expressed with that pattern
    // If yes, then put it in.

    /**
     * Return true if all the elements of r1 are also in r2.
     * 
     * bool roaring_bitmap_is_subset(const roaring_bitmap_t *r1,
                                const roaring_bitmap_t *r2);
     */
    
    if(roaring_bitmap_get_cardinality(general_key_schema) > 0)
    {
        if(roaring_bitmap_get_cardinality(general_kleene_schema) > 0)
            object_clusters_.push_back(InstanceCluster(kComObjC));
        else
            object_clusters_.push_back(InstanceCluster(kHomObjC));
    }
    else
        object_clusters_.push_back(InstanceCluster(kHetObjC));
    
    for(int i = 0; i < object_forest.size(); i++)
    {
        if(mask[i] == false) continue; 

        roaring_bitmap_t* key = object_forest[i]->getUnkleenedLabelBitmap();
        roaring_bitmap_t* key_schema = object_forest[i]->getLabelSchemaBitmap();
        roaring_bitmap_t* kleene_schema = object_forest[i]->getKleenedSchemas();

        if( roaring_bitmap_is_subset(key, general_key) &&
            roaring_bitmap_is_subset(key_schema, general_key_schema) &&
            roaring_bitmap_is_subset(kleene_schema, general_kleene_schema) )
        {
            object_clusters_.back().addInstance(object_forest[i]);
            mask[i] = false;
            unmasked_num--;
        }
    }

    roaring_bitmap_free(general_key);
    roaring_bitmap_free(general_key_schema);
    roaring_bitmap_free(general_kleene_schema);
}





void BottomUpSchemaGenerator::updateClustersMetadata()
{
    for(auto& cluster : object_clusters_)
    { 
        cluster.updateClusterMetadata(cost_parameters_); 
    }
    for(auto& cluster : array_clusters_)
    { 
        cluster.updateClusterMetadata(cost_parameters_); 
    }
}














// void BottomUpSchemaGenerator::filterHeterogeneousClusters()
// {
//     vector<vectorIdx> already_merged;

//     while(true)
//     {
//         // 1. Find a heterogeneous cluster
//         bool target_found = false;
//         vectorIdx target_idx = -1;
//         for(int i = 0; i < object_clusters_.size(); i++)
//         {
//             if(contains(already_merged, i)) continue;
//             // 1.1. Heterogeneous object cluster
//             if(object_clusters_[i].getClusterType() == kHetObjC)
//             { 
//                 // 1.2. + Not all primitives
//                 SchemaSet* children_schemas = object_clusters_[i].getChildrenSchemaSet();
//                 bool all_primitives = true;
//                 for(auto schema_node : *children_schemas)
//                 {
//                     if(!isPrimitive(schema_node->getType())) 
//                     {
//                         all_primitives = false; break;
//                     }
//                 }
//                 if(!all_primitives)
//                 {
//                     target_found = true;
//                     target_idx = i;
//                     break;
//                 }
//             }
//         }
//         if(!target_found) return;

//         // 2. Check each clusters and check if equals to the children schemas
//         already_merged.push_back(target_idx);
//         vector<vectorIdx> merging_indices;
//         for(int i = 0; i < object_clusters_.size(); i++)
//         {
//             if(i == target_idx) continue;

//             // for(auto& element : *object_clusters_[i].getChildrenSchemaSet())
//             // {
//             //     cout << element << " ";
//             // }
//             // cout << endl;
//             // for(auto& element : *object_clusters_[target_idx].getChildrenSchemaSet())
//             // {
//             //     cout << element << " ";
//             // }
//             // cout << endl;

//             if(isEqual(object_clusters_[i].getChildrenSchemaSet(), object_clusters_[target_idx].getChildrenSchemaSet()))
//             { 
//                 // cout << "EQUALED" << endl;
//                 merging_indices.push_back(i); 
//             }
//         }
//         if(merging_indices.size() == 0)
//         { continue; }

//         // 3. Perform actual merging
//         for (vectorIdx merging_index : merging_indices) 
//         {
//             mergeInstanceClusters(
//                 object_clusters_[target_idx],
//                 object_clusters_[merging_index],
//                 kHetObjC,
//                 cost_parameters_
//             );
//         }

//         // 4. Erase merged clusters.
//         sort(merging_indices.rbegin(), merging_indices.rend());
//         for (vectorIdx index : merging_indices)
//         { object_clusters_.erase(object_clusters_.begin() + index); }

//         // 5. Update already_merged
//         for(auto it = already_merged.begin(); it != already_merged.end(); )
//         {
//             bool is_merged_and_deleted = false;
//             Count smaller_merged_indices = 0;

//             for(auto merged_index : merging_indices)
//             {
//                 if(merged_index < *it)
//                 { smaller_merged_indices++; }
//                 else if(merged_index == *it)
//                 {
//                     is_merged_and_deleted = true;
//                 }
//             }
//             *it -= smaller_merged_indices;

//             if(is_merged_and_deleted) it = already_merged.erase(it); 
//             else it++;
//         }
//     }
// }