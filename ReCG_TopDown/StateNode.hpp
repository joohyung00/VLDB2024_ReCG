#ifndef STATENODE
#define STATENODE


#include "TopDownSchemaGenerator.hpp"
#include "utils.hpp"

using SchemaToInstanceForest = unordered_map<SchemaNode*, InstanceForest>;

class StateNode
{
    private:

        // State-related
        StateNode* parent_state_;
        vector<StateNode*> children_states_;

        stateId state_id_;

        // Depth-related
        int current_depth_;
        int max_depth_; 


        bool is_leaf_;
        MDLCost cost_; 

        SchemaNode*                 final_schema_;
        

        TopDownSchemaGenerator      top_down_schema_generator_;
            // Parameters for bottom-up schema generator
        DepthToGroupedInstances&    instance_manager_;
        // DerivationUnitPtrs*         derivation_units_;

        Parameters*                 recg_parameters_;
        CostParameters              cost_parameters_;

        // User-defined inputs
        // int                         sample_size_;
        // float                       epsilon_;
        // int                         min_pts_perc_;
        float                       src_weight_;
        float                       drc_weight_;


    public:

        StateNode(
            stateId state_id,
            int current_depth, 
            int max_depth,
            CostParameters cost_parameters,
            DepthToGroupedInstances& instance_manager,
            // DerivationUnitPtrs* derivation_units,

            Parameters* recg_parameters
        )
        : state_id_(state_id),
        current_depth_(current_depth), 
        max_depth_(max_depth), 
        cost_parameters_(cost_parameters),
        instance_manager_(instance_manager),
        // derivation_units_(derivation_units),
        recg_parameters_(recg_parameters)
        {
            is_leaf_ = (current_depth_ == max_depth_ + 1);

            src_weight_ = recg_parameters_->getSrcWeight();
            drc_weight_ = recg_parameters_->getDrcWeight();

            parent_state_ = nullptr;

            if(!is_leaf_)
            {
                top_down_schema_generator_ = TopDownSchemaGenerator(
                    state_id_,
                    instance_manager.getGroupedInstancesPtrByDepth(current_depth_),
                    // derivation_units_,
                    current_depth_,
                    max_depth_,
                    cost_parameters_,
                    recg_parameters_
                );
            }
        }

        ~StateNode()
        { }

        void setParentState(StateNode* parent_state)
        { parent_state_ = parent_state; }

        StateNode* getParentState()
        { return parent_state_; }

        int getStateId()
        { return state_id_; }

        bool isLeafState()
        { return is_leaf_; }

        void setWeightedMDLCost(MDLCost cost)
        { cost_ = cost; }

        MDLCost getWeightedMDLCost()
        { return cost_; }

        vector<StateNode*> transitions();

        int getDepth()
        { return current_depth_; }


        // CD-instance-related
        void updateCDInstances();

        void setDerivedSchemaAsThisState();

        // Called only in final state
        SchemaNode* getDerivedSchema()
        { return top_down_schema_generator_.getCompleteSchema(); }

        void setFinalSchema(SchemaNode* final_schema)
        { final_schema_ = final_schema; }

        SchemaNode* getFinalSchema();
            void updateInstancesDerivedSchemas();
            void connectSchemasAtDepth(int depth);
            void connectObjSchemaUsingInstances(SchemaNode* schema, InstanceForest& instance_forest);
            void connectArrSchemaUsingInstances(SchemaNode* schema, InstanceForest& instance_forest);
            SchemaNode* aggregateFinalSchema();


        // For debugging
        void checkAllInstancesHaveDerivedSchema();

        void printInfo();


    private:

        void printHeader();

        void printHeaderTab();
};


#endif