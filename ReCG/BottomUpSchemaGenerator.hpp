#ifndef BOTTOMUPSGEN
#define BOTTOMUPSGEN

#include "SchemaNodeDeriver.hpp"
#include "InstanceClusterMerge.hpp"
#include "Clustering.hpp"
#include "Distance.hpp"

#include <thread>

using ClusterId = int;

#define ARRAY_EPSILON 0.5


class StateMaterials
{
    private:

        DerivationResult        result_;
        stateId                 state_id_;
        vector<SchemaNode*>     derived_schemas_;

    public:
        
        StateMaterials()
        {
            derived_schemas_ = vector<SchemaNode*>();
        }
            
        void setDerivationResult(DerivationResult result)
        {
            result_ = result;
        }        

        void setStateId(stateId state_id)
        {
            state_id_ = state_id;
        }
            
        DerivationResult getDerivationResult()
        {
            return result_;
        }

        stateId getStateId()
        {
            return state_id_;
        }
};



class MergeCandidate
{
    private:
    
        MDLCost delta_mdl_;
        
        vectorIdx candidate_1_;
        vectorIdx candidate_2_;

        ClusterType merging_type_;

    public:

        MergeCandidate(
            MDLCost delta_mdl,
            vectorIdx candidate_1,
            vectorIdx candidate_2,
            ClusterType merging_type
        ):
        delta_mdl_(delta_mdl),
        merging_type_(merging_type)
        {
            if(candidate_1 < candidate_2)
            {
                candidate_1_ = candidate_1;
                candidate_2_ = candidate_2;
            }
            else
            {
                candidate_1_ = candidate_2;
                candidate_2_ = candidate_1;
            }
        }

        void resetIndices(vectorIdx merged_1, vectorIdx merged_2, int remained_one)
        {
            int target;
            if(remained_one == 2) target = merged_1;
            else if(remained_one == 1) target = merged_2;

            if(candidate_1_ < target);
            else candidate_1_--;

            if(candidate_2_ < target);
            else candidate_2_--;
        }

        MDLCost getDeltaMDL()
        { return delta_mdl_; }

        vector<vectorIdx> getIndices()
        { return vector<vectorIdx>( {candidate_1_, candidate_2_} ); }

        ClusterType getMergingType()
        { return merging_type_; }

        bool includesMergeTargets(vectorIdx target_1, vectorIdx target_2)
        {
            if(
                candidate_1_ == target_1 ||
                candidate_1_ == target_2 ||
                candidate_2_ == target_1 ||
                candidate_2_ == target_2
            ) return true;
            return false;
        }

        void fillInMergeTargets(vectorIdx& target_1, vectorIdx& target_2, ClusterType& merging_type)
        {
            target_1 = candidate_1_;
            target_2 = candidate_2_;
            merging_type = merging_type_;
        }
};















class BottomUpSchemaGenerator
{
    private:

        static stateId              unique_state_id_;

        stateId                     working_state_id_;

        DerivationPhase             derivation_phase_;

        int                         max_depth_;
        int                         current_depth_;
        GroupedInstances*           grouped_instances_;

        // <\mathcal{I}> ///////////////////////////////////////
        CostParameters              cost_parameters_;
        ////////////////////////////////////////////////////////

        // User input //////////////////////////////////////////
        int                         sample_size_;
        float                       epsilon_;
        ////////////////////////////////////////////////////////

        // Heuristic values ////////////////////////////////////
        int                         generalizing_threshold_;
        int                         min_points_;
        // float                       epsilon_;
        ////////////////////////////////////////////////////////

        // [Clusters]
        vector<InstanceCluster>     object_clusters_;
        vector<InstanceCluster>     array_clusters_;

        vector<vectorIdx>           update_targets_;
        vector<MergeCandidate>      merge_candidates_;

        // [After Derivation]
        vector<SchemaNode*>         derived_schemas_;

    public:
        // BottomUpSchemaGenerator(const BottomUpSchemaGenerator&) = delete;
        // BottomUpSchemaGenerator& operator=(const BottomUpSchemaGenerator&) = delete;
        // BottomUpSchemaGenerator(BottomUpSchemaGenerator&&) = delete;
        // BottomUpSchemaGenerator& operator=(BottomUpSchemaGenerator&&) = delete;

        BottomUpSchemaGenerator()
        {}

        BottomUpSchemaGenerator(
            stateId state_id,
            GroupedInstances* grouped_instances, 
            int current_depth, 
            int max_depth, 
            CostParameters cost_parameters,
            int sample_size,
            float epsilon
        )
        : working_state_id_(state_id),
        current_depth_(current_depth), 
        max_depth_(max_depth), 
        grouped_instances_(grouped_instances), 
        cost_parameters_(cost_parameters),
        sample_size_(sample_size),
        epsilon_(epsilon)
        {
            derivation_phase_ = kClusteringPhase;

            epsilon_ = 0.5;
            min_points_ = 10;

            generalizing_threshold_ = 5;
        }

        ~BottomUpSchemaGenerator()
        { }

        StateMaterials deriveNextSchema();



        void addDerivedSchema(SchemaNode* derived_schema)
        {
            derived_schemas_.push_back(derived_schema);
        }

        vector<SchemaNode*>& getDerivedSchemas()
        {
            return derived_schemas_;
        }

        void cleanSchemas()
        { 
            for(auto schema_node : derived_schemas_)
            { delete schema_node; }
        }

        // [Get Set]
        SchemaNode* getCompleteSchema()
        { 
            int total_num = 0;
            total_num += grouped_instances_->getInstanceForestByType(kObject).size();
            total_num += grouped_instances_->getInstanceForestByType(kArray).size();
            total_num += grouped_instances_->getInstanceForestByType(kNumber).size();
            total_num += grouped_instances_->getInstanceForestByType(kString).size();
            total_num += grouped_instances_->getInstanceForestByType(kBoolean).size();
            total_num += grouped_instances_->getInstanceForestByType(kNull_).size();

            return deriveAnyOfNode(derived_schemas_, cost_parameters_, total_num);
        }

        MDLCost getSRC()
        {
            MDLCost schema_cost = 0;
            for(auto& derived_schema : derived_schemas_)
            { schema_cost += derived_schema->getSRC(); }

            schema_cost += grouped_instances_->getInstanceForestByType(kObject).size() * derived_schemas_.size();

            return schema_cost;
        }

        MDLCost getDRC()
        {
            MDLCost data_cost = 0;
            for(auto& derived_schema : derived_schemas_)
            { data_cost += derived_schema->getDRC(); }

            return data_cost;
        }

    private:

        // [Object-Related Functions]
        // 1. Clustering Phase
        void clusterAndGeneralizeObjects();
            void preprocessInstances(vector<bool>& mask, int& instance_num);
            void clusterCDObjects(vector<bool>& mask, int& instance_num);
                void filterHeterogeneousObjects(vector<bool>& mask, int& instance_num);
                void linearlyFilterObjects(
                    InstanceForest& object_forest,
                    vector<bool>& mask,
                    int& unmasked_num,
                    InstanceForest& biggest_cluster
                );
            void generalizeOutlierObjects(vector<bool>& mask, int& instance_num);
            void clusterGeneralizedOutlierObjects(vector<bool>& mask, int& instance_num);
            void treatEdgeCases(vector<bool>& mask, int& instance_num);
            void filterHeterogeneousClusters();

        // 2. Merging Phase
        bool mergeToGeneralize();
        void setInitialDistanceCalculationTargets();
        void setNextMergeParams();


        // [Array-Related Functions]
        // Clustering Instances
        void clusterAllGenericTypes();
        void generalizeAndClusterArrays();
            void clusterCDArrays(vector<bool>& mask, int& instance_num);
                void linearlyFilterArrays(
                    InstanceForest& array_forest,
                    vector<bool>& mask,
                    int& unmasked_num,
                    InstanceForest& biggest_cluster
                );
        void findHomArrayCluster();

        void updateClustersMetadata();

        // Deriving Schema Nodes from Clusters
        void deriveSchemasFromClusters();

        // Utils
        void printHeader();
};

void mapInstancesForState(stateId state_id, InstanceForest& instance_forest, SchemaNode* derived_schema);
void mapInstancesForState(stateId state_id, InstanceForest* instance_forest, SchemaNode* derived_schema);

#endif