#ifndef DBSCAN
#define DBSCAN


// Clustering.hpp
#include "InstanceCluster.hpp"
#include "Distance.hpp"
#include "Schema.hpp"
#include "utils.hpp"

#define OUTLIER -1
// #define CORE_POINT 1
// #define BORDER_POINT 2
// #define NOISE -2
// #define SUCCESS 0
// #define FAILURE -3


class Dbscan
{
    private:
        InstanceForest& instance_forest_;
        int n_;

        float epsilon_;
        int min_points_;

        int cluster_label_;
        vector<int> labels_;
        vector<bool> visited_;
        vector<float> distance_matrix_;

        string mode_;

        // Neighbors of the core point
        vector<int> neighbors_;
        // Incrementally found neighbors of core points
        vector<int> new_neighbors_;

        // Debugging purpose
        Count distance_call_count_;
        

    public:
        Dbscan(
            InstanceForest& instance_forest, 
            float epsilon, 
            int min_points,
            string mode
        )
        : instance_forest_(instance_forest),
        epsilon_(epsilon),
        min_points_(min_points),
        mode_(mode)
        {
            cluster_label_ = -1;
            
            labels_     = vector<int> (instance_forest_.size(), -1);
            visited_    = vector<bool>(instance_forest_.size(), false);

            neighbors_.reserve((int)(labels_.size() * labels_.size()));
            new_neighbors_.reserve(labels_.size());

            distance_call_count_ = 0;

            n_ = instance_forest_.size(); 
            distance_matrix_.resize(n_ * n_);
            
        }

        void cluster();

        void getBiggestCluster(InstanceForest& to_write);

        vector<int>& getLabels(int &max_label)
        { 
            max_label = cluster_label_;
            return labels_; 
        }

    private:

        void initiateDistanceMatrix();
        float getDistance(int a, int b);
        void regionQuery(int instance_index);
        void newRegionQuery(int instance_index);
};


using SchemaForest = SchemaVec;


#endif