#ifndef STATENODE
#define STATENODE


#include "BottomUpSchemaGenerator.hpp"
#include "utils.hpp"

class StateNode
{
    private:

        // State-related
        vector<StateNode*> children_states_;

        stateId state_id_;

        int current_depth_;

        int max_depth_; 

        bool is_leaf_;

        MDLCost cost_; 

        SchemaNode*                 final_schema_;
        

        BottomUpSchemaGenerator     bottomUpSchemaGenerator;
            // Parameters for bottom-up schema generator
        DepthToGroupedInstances&    instance_manager_;
        Parameters*                 recg_parameters_;
        CostParameters              cost_parameters_;


        int                         sample_size_;
        float                       epsilon_;
        int                         min_pts_perc_;
        float                       src_weight_;
        float                       drc_weight_;


    public:

        StateNode(
            stateId state_id,
            int current_depth, 
            int max_depth,
            CostParameters cost_parameters,
            DepthToGroupedInstances& instance_manager,

            Parameters* recg_parameters
        )
        : state_id_(state_id),
        current_depth_(current_depth), 
        max_depth_(max_depth), 
        cost_parameters_(cost_parameters),
        instance_manager_(instance_manager),
        recg_parameters_(recg_parameters)

        {
            is_leaf_ = (current_depth_ == -1);

            sample_size_ = recg_parameters_->getSampleSize();
            epsilon_ = recg_parameters_->getEpsilon();
            min_pts_perc_ = recg_parameters_->getMinPtsPerc();
            src_weight_ = recg_parameters_->getSrcWeight();
            drc_weight_ = recg_parameters_->getDrcWeight();


            if(!is_leaf_)
            {
                bottomUpSchemaGenerator = BottomUpSchemaGenerator(
                    state_id_,
                    instance_manager.getGroupedInstancesPtrByDepth(current_depth_),
                    current_depth_,
                    max_depth_,
                    cost_parameters_,
                    recg_parameters_
                );
            }
        }

        ~StateNode()
        { }

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


        // Called only in final state
        SchemaNode* getDerivedSchema()
        { return bottomUpSchemaGenerator.getCompleteSchema(); }

        void setFinalSchema(SchemaNode* final_schema)
        { final_schema_ = final_schema; }

        SchemaNode* getFinalSchema()
        { return final_schema_; }

        void printInfo();


    private:

        void printHeader();

        void printHeaderTab();
};


#endif