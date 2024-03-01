#include "BottomUpSchemaGenerator.hpp"



void BottomUpSchemaGenerator::generalizeAndClusterArrays()
{
    InstanceForest& array_forest = grouped_instances_->getInstanceForestByType(kArray);
    vector<bool> mask(array_forest.size(), true);
    int unmasked_num = mask.size();

    clusterCDArrays(mask, unmasked_num);
    findHomArrayCluster();
    
    // generalizeOutlierObjects(mask, unmasked_num);
    // clusterGeneralizedOutlierObjects(mask, unmasked_num);
}


void BottomUpSchemaGenerator::clusterCDArrays(vector<bool>& mask, int& instance_num)
{
    InstanceForest& array_forest = grouped_instances_->getInstanceForestByType(kArray);

    // 1. Update instances
    array_clusters_.push_back(InstanceCluster(kEmptyArrC));
    for(int i = 0; i < mask.size(); i++)
    {
        array_forest[i]->updateBitmaps();
        
        if(!array_forest[i]->getChildrenNum())
        {
            array_clusters_.back().addInstance(array_forest[i]);
            mask[i] = false;
            instance_num--;
        }
    }
    if(!array_clusters_.back().getForestSize())
    { array_clusters_.clear(); }


    // 2. Random sample + Linear Filtering
    bool repeat = true;
    int sample_num = sample_size_;
    while(instance_num > sample_num && repeat)
    {
        // Sample 1000 instances
        InstanceForest samples;
        int to_sample_more = sample_num;
        for(int i = 0; i < mask.size(); i++)
        {
            if(mask[i])
            {
                samples.push_back(array_forest[i]);
                if(to_sample_more-- < 0) break;
            }
        }

        // Perform clustering
        InstanceForest biggest_cluster;

        Dbscan dbscan(samples, ARRAY_EPSILON, min_points_, "leq");
        dbscan.cluster();
        dbscan.getBiggestCluster(biggest_cluster);

        // cout << "Biggest Cluster #: " << biggest_cluster.size() << endl;

        if(biggest_cluster.size() == 0)
        {
            repeat = false;
            continue; 
        }

        // 3. Keys + parameterized types of the cluster
        // 4. Linearly check the containment of the cluster
        linearlyFilterArrays(array_forest, mask, instance_num, biggest_cluster);
    }


    // 3. Leftover samples < `sample_num`
    InstanceForest outliers;
    if(repeat)
    {
        // 3.1. Gather Leftover Instances
        InstanceForest leftovers;
        vector<int> mask_map;
        for(int i = 0; i < mask.size(); i++)
        { 
            if(mask[i])
            { 
                leftovers.push_back(array_forest[i]); 
                mask_map.push_back(i);
            }
        }

        // 3.2. Perform DBSCAN
        Dbscan dbscan(leftovers, ARRAY_EPSILON, min_points_, "leq");
        dbscan.cluster();
        int max_label;
        vector<int> labels = dbscan.getLabels(max_label);

        // 3.3. Make Instance Cluster with them
        for(int i = 0; i <= max_label; i++)
        {
            array_clusters_.push_back(InstanceCluster(kHetArrC));
            array_clusters_.back().getInstanceForest()->reserve(leftovers.size());
        }
        for(int i = 0; i < labels.size(); i++)
        {
            int cluster_num = labels[i];
            if(cluster_num != -1)
            { 
                array_clusters_[array_clusters_.size() - 1 - cluster_num].addInstance(leftovers[i]); 
                mask[mask_map[i]] = false;
                instance_num--;
            }
            else
            {
                outliers.push_back(leftovers[i]);
            }
        }
    }
    // 4. Treat outliers
    if(outliers.size())
    {
        Dbscan dbscan(outliers, ARRAY_EPSILON, 1, "leq");
        dbscan.cluster();
        int max_label;
        vector<int> labels = dbscan.getLabels(max_label);

        for(int i = 0; i <= max_label; i++)
        {
            array_clusters_.push_back(InstanceCluster(kHetArrC));
            array_clusters_.back().getInstanceForest()->reserve(outliers.size());
        }
        for(int i = 0; i < labels.size(); i++)
        {
            int cluster_num = labels[i];
            if(cluster_num != -1)
            {
                array_clusters_[array_clusters_.size() - 1 - cluster_num].addInstance(outliers[i]); 
            }
        }

        for(int i = 0; i < labels.size(); i++)
        {
            if(labels[i] == -1)
            {
                array_clusters_.push_back(InstanceCluster(kHetArrC));
                array_clusters_.back().getInstanceForest()->push_back(outliers[i]);
            }
        }
    }

    // 3.(b) Still left here
    repeat = true;
    sample_num = sample_size_;
    while(instance_num > 0 && repeat)
    {
        // Sample instances
        InstanceForest samples;
        int to_sample_more = sample_num;
        for(int i = 0; i < mask.size(); i++)
        {
            if(mask[i])
            {
                samples.push_back(array_forest[i]);
                if(to_sample_more-- < 0) break;
            }
        }

        // Perform clustering
        InstanceForest biggest_cluster;

        Dbscan dbscan(samples, ARRAY_EPSILON, 1, "leq");
        dbscan.cluster();
        dbscan.getBiggestCluster(biggest_cluster);

        // cout << "Biggest Cluster #: " << biggest_cluster.size() << endl;

        if(biggest_cluster.size() == 0)
        {
            repeat = false;
            continue; 
        }

        // 3. Keys + parameterized types of the cluster
        // 4. Linearly check the containment of the cluster
        linearlyFilterArrays(array_forest, mask, instance_num, biggest_cluster);
    }
    while(instance_num > 0)
    {
        // Sample instances
        InstanceForest biggest_cluster;
        for(int i = 0; i < mask.size(); i++)
        {
            if(mask[i])
            {
                biggest_cluster.push_back(array_forest[i]);
                break;
            }
        }

        // cout << "Biggest Cluster #: " << biggest_cluster.size() << endl;

        // 3. Keys + parameterized types of the cluster
        // 4. Linearly check the containment of the cluster
        linearlyFilterArrays(array_forest, mask, instance_num, biggest_cluster);
    }
    if(instance_num > 0)
    {
        cout << "Array leftover instances: " << instance_num << endl;
        cout << "Something wrong" << endl;
    }
}


void BottomUpSchemaGenerator::linearlyFilterArrays(
    InstanceForest& array_forest,
    vector<bool>& mask,
    int& unmasked_num,
    InstanceForest& biggest_cluster
)
{
    // 1. Put the most general pattern within one instance
    roaring_bitmap_t* general_kleene_schema = roaring_bitmap_create();

    for(auto& cluster_object : biggest_cluster)
    {
        roaring_bitmap_t* kleene_schema = cluster_object->getKleenedSchemas();

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
    
    array_clusters_.push_back(InstanceCluster(kHetArrC));
    
    for(int i = 0; i < array_forest.size(); i++)
    {
        if(mask[i] == false) continue; 

        roaring_bitmap_t* kleene_schema = array_forest[i]->getKleenedSchemas();

        if(roaring_bitmap_is_subset(kleene_schema, general_kleene_schema))
        {
            array_clusters_.back().addInstance(array_forest[i]);
            mask[i] = false;
            unmasked_num--;
        }
    }

    roaring_bitmap_free(general_kleene_schema);
}


void BottomUpSchemaGenerator::findHomArrayCluster()
{
    for(auto& cluster : array_clusters_)
    {
        InstanceForest* forest = cluster.getInstanceForest();
        bool is_actually_hom_partition = true;

        // Prepare length
        int length = (*(forest->begin()))->getChildrenNum();
        // Prepare schema sequence
        vector<Node*> schema_sequence;
        for(auto child : (*forest->begin())->getChildren())
        {
            schema_sequence.push_back(TO_INSTANCE_NODE(child)->getDerivedSchema());
        }
        
        for(InstanceNode* instance : *forest)
        {
            if(instance->getChildrenNum() != length)
            { 
                // 1. First check if the lengths are uniform within the partition instances
                is_actually_hom_partition = false; 
                break;
            }

            int i = 0;
            for(auto child : instance->getChildren())
            {
                // 2. If the lengths are all the same, then see the sequence itself.
                if(schema_sequence[i] != TO_INSTANCE_NODE(child)->getDerivedSchema())
                {
                    is_actually_hom_partition = false; 
                    break;
                }
                i++;
            }
            if(!is_actually_hom_partition) break;
        }

        // 
        if(is_actually_hom_partition)
        {
            // Hom 
            cluster.setClusterType(kHomArrC);
        }
    }
}