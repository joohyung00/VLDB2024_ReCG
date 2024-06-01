#include "StateNode.hpp"

vector<StateNode*> StateNode::transitions()
{
    if(is_leaf_) 
    {
        return vector<StateNode*>();
    }

    // 1. Update CD-instances to this state
    updateCDInstances();
    
    // 2. Derive possible schemas
    printHeaderTab();
    cout << "[Derived Schemas]" << endl;

    while(true)
    {
        // 2.1. Derive schema (receive as `stateMaterials`)
        StateMaterials state_materials = bottomUpSchemaGenerator.deriveNextSchema();

        // 2.2. If a schema is successfully derived
        if(state_materials.getDerivationResult() == kDerived)
        {
            // 2.2.1. Make a new state with derived schemas
            StateNode* new_state = new StateNode(
                state_materials.getStateId(),
                current_depth_ - 1, 
                max_depth_,
                cost_parameters_,
                instance_manager_,
                recg_parameters_
            );

            if(current_depth_ == 0)
            {
                // 2.2.2. If `new_state` is actually a leaf state
                    // Set the final schema - Maybe `anyOf` node should be derived
                new_state->setFinalSchema(bottomUpSchemaGenerator.getCompleteSchema());
            }

            // 2.2.3. Calculate Cost
            new_state->setWeightedMDLCost(
                getWeightedMDLCost() +
                src_weight_ * bottomUpSchemaGenerator.getSRC() +
                drc_weight_ * bottomUpSchemaGenerator.getDRC()
            );
            printHeaderTab();
            if(recg_parameters_->getCostModel() == kMDL)
                cout << "## " << 
                "SRC: " << (int)(src_weight_ * bottomUpSchemaGenerator.getSRC()) << ", " << 
                "DRC: " << (int)(drc_weight_ * bottomUpSchemaGenerator.getDRC()) << " || " << "TOTAL: " << new_state->getWeightedMDLCost() << endl;
            else if(recg_parameters_->getCostModel() == kKeySpaceEntropy)
                cout << "## " << "KSE: " << src_weight_ * bottomUpSchemaGenerator.getSRC() << 
                " || " << "TOTAL: " << new_state->getWeightedMDLCost() << endl;

            // 2.2.4. Append to `children_states`
            children_states_.push_back(new_state);
        }
        else break;
    }
    cout << endl;

    return children_states_;
}



void StateNode::printInfo()
{
    // Printing Costs...
    printHeader();
    cout << "------------------------" << endl;
    printHeader();
    cout << "<< Depth : " << current_depth_ << " | State #" << state_id_ << " >>" << endl;
    printHeader();
    if(recg_parameters_->getCostModel() == kMDL)
        cout << "[Entire Cost] " << (int)getWeightedMDLCost() << endl;
    else if(recg_parameters_->getCostModel() == kKeySpaceEntropy)
        cout << "[Entire Cost] " << getWeightedMDLCost() << endl;
}



void StateNode::printHeader()
{
    int times = max_depth_ - current_depth_;

    cout << "-"; 
    for(int i = 0; i < times; i++)
    {
        cout << "----";
    }
    cout << "| "; 
}

void StateNode::printHeaderTab()
{
    int times = max_depth_ - current_depth_;

    cout << "-"; 
    for(int i = 0; i < times; i++)
    {
        cout << "----";
    }
    cout << "|->| "; 
}



void StateNode::updateCDInstances()
{
    // We're interested in children's depth -> Change children to their derived schemas
    int children_depth = current_depth_ + 1;

    if(children_depth > max_depth_)
        return;
        
    GroupedInstances* children_grouped_instances = instance_manager_.getGroupedInstancesPtrByDepth(children_depth);

    if(children_grouped_instances->getInstanceForestByType(kObject).size() > 0)
    {
        for(auto& obj_instance : children_grouped_instances->getInstanceForestByType(kObject))
            obj_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kArray).size() > 0)
    {
        for(auto& arr_instance : children_grouped_instances->getInstanceForestByType(kArray))
            arr_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kNumber).size() > 0)
    {
        for(auto& num_instance : children_grouped_instances->getInstanceForestByType(kNumber))
            num_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kString).size() > 0)
    {
        for(auto& str_instance : children_grouped_instances->getInstanceForestByType(kString))
            str_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kBoolean).size() > 0)
    {
        for(auto& bool_instance : children_grouped_instances->getInstanceForestByType(kBoolean))
            bool_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kNull_).size() > 0)
    {
        for(auto& null_instance : children_grouped_instances->getInstanceForestByType(kNull_))
            null_instance->setNodeAsState(state_id_);
    }
}
