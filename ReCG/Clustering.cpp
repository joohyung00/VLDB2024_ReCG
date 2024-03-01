#include "Clustering.hpp"



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////// DBSCAN for Instances //////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



void Dbscan::cluster()
{
    initiateDistanceMatrix();


    // Iterate over all instances.
    for (int i = 0; i < n_; i++)
    {
        if(visited_[i]) continue;

        // Check for epsilon-neighbors.
        // Start of a new cluster.
        regionQuery(i);
        visited_[i] = true;

        // Check if `i` is a core point.
        if (neighbors_.size() < min_points_)
        {
            labels_[i] = OUTLIER; // Mark point as noise.
            continue;
        }

        // If core point, then now start a cluster.
        // C = nextCluster;
        cluster_label_++;
        
        // expandCluster
        // add P to cluster C
        labels_[i] = cluster_label_;
        // Points that should be checked after on.
        for (int j = 0; j < neighbors_.size(); j++)
        {
            int q = neighbors_[j];
            // First mark point q as label num.
            if(!visited_[q])
            {
                // Research for epsilon-neighborhood.
                newRegionQuery(q);
                visited_[q] = true;

                // If `q` is a core point, add more epsilon-neighborhood.
                if (new_neighbors_.size() >= min_points_)
                { neighbors_.insert(neighbors_.end(), new_neighbors_.begin(), new_neighbors_.end()); }
            }
            if(labels_[q] == -1) labels_[q] = cluster_label_;
        }
    }

    // cout << endl;
    // cout << "[CLUSTERING]" << endl;
    // cout << "Size: " << instance_forest_.size() << "\tDistance Called: " << distance_call_count_ << endl;
    // cout << endl;
}


void Dbscan::regionQuery(int instance_index)
{
    neighbors_.clear();
    
    for (int j = 0; j < n_; j++)
    {
        if (j == instance_index)
        { continue; }


        float distance = getDistance(instance_index, j);

        if(mode_ == "l" && distance < epsilon_)
        {
            neighbors_.push_back(j); 
        }
        else if(mode_ == "leq" && distance <= epsilon_) 
        { 
            neighbors_.push_back(j);
        }
    }
}

void Dbscan::newRegionQuery(int instance_index)
{
    new_neighbors_.clear();

    for (int j = 0; j < n_; j++)
    {
        if(j == instance_index) continue; 

        float distance = getDistance(instance_index, j);

        if(mode_ == "l" && distance < epsilon_)
        {
            neighbors_.push_back(j);
        }
        else if(mode_ == "leq" && distance <= epsilon_) 
        { 
            neighbors_.push_back(j);
        }
    }
}

void Dbscan::initiateDistanceMatrix()
{
    int i;
    int j;

    for(int vector_idx = 0; vector_idx < distance_matrix_.size(); vector_idx++)
    {
        i = vector_idx / n_;
        j = vector_idx % n_;

        if(i < j)
        {
            float wjd = weightedJaccardDistance(instance_forest_[i], instance_forest_[j]);
            distance_matrix_[vector_idx] = wjd;
        }
    }
}


float Dbscan::getDistance(int a, int b)
{
    int i;
    int j;

    if(a < b)
    {
        i = a;
        j = b;
    }
    else if(a == b)
    { return 0; }
    else
    {
        i = b;
        j = a;
    }

    return distance_matrix_[i * n_ + j];
}














void Dbscan::getBiggestCluster(InstanceForest& to_write)
{
    // Special case : no cluster
    if(cluster_label_ < 0)
    { return; }


    vector<InstanceForest> instance_clusters;

    // Initiate instance_clusters to the number of cluster_num
    for(int i = 0; i <= cluster_label_; i++)
    {
        // Each cluster should be resized to `instance_forest_' size.
        instance_clusters.push_back(InstanceForest());
        instance_clusters.back().reserve(instance_forest_.size());
    }

    // Iterate over `labels_`. Put instances of each label in `instance_clusters`.
    // cluster_label_
    std::vector<int> num_per_labels(cluster_label_ + 1, 0);
    for(int i = 0; i < labels_.size(); i++)
    {
        int cluster_num = labels_[i];
        if(cluster_num == -1)
        { ; }
        else
        {
            instance_clusters[cluster_num].push_back(instance_forest_[i]);
            (num_per_labels[cluster_num])++;
        }
    }

    // Iterate over each cluster
    //   - If the cluster is the biggest, downsize it and save it
    //   - If not, delete.    
    auto max_num_iterator = max_element(num_per_labels.begin(), num_per_labels.end());
    int label_num = 0;

    for(auto it = num_per_labels.begin(); it != num_per_labels.end(); it++)
    {
        if(it == max_num_iterator)
        { to_write = instance_clusters[label_num]; }
        label_num++;
    }
}
