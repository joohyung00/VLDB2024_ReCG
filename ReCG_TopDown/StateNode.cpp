#include "StateNode.hpp"

vector<StateNode*> StateNode::transitions()
{
    if(is_leaf_) 
    {
        return vector<StateNode*>();
    }

    // 1. Update CD-instances to this state
    // updateCDInstances();
    
    // 2. Derive possible schemas
    printHeaderTab();
    cout << "[Derived Schemas]" << endl;

    while(true)
    {
        // 2.1. Derive schema (receive as `stateMaterials`)
        StateMaterials state_materials = top_down_schema_generator_.deriveNextSchema();

        // 2.2. If a schema is successfully derived
        if(state_materials.getDerivationResult() == kDerived)
        {
            // 2.2.1. Make a new state with derived schemas
            StateNode* new_state = new StateNode(
                state_materials.getStateId(),
                current_depth_ + 1,
                max_depth_,
                cost_parameters_,
                instance_manager_,
                recg_parameters_
            );
            new_state->setParentState(this);

            if(current_depth_ == 0)
            {
                // 2.2.2. If `new_state` is actually a leaf state
                    // Set the final schema - Maybe `anyOf` node should be derived
                new_state->setFinalSchema(top_down_schema_generator_.getCompleteSchema());
            }

            // 2.2.3. Calculate Cost
            new_state->setWeightedMDLCost(
                getWeightedMDLCost() +
                src_weight_ * top_down_schema_generator_.getSRC() +
                drc_weight_ * top_down_schema_generator_.getDRC()
            );
            printHeaderTab();
            cout << "## " << 
                "SRC: " << (int)(src_weight_ * top_down_schema_generator_.getSRC()) << ", " << 
                "DRC: " << (int)(drc_weight_ * top_down_schema_generator_.getDRC()) << endl;

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


SchemaNode* StateNode::getFinalSchema()
{
    // 1. Update the instances' derived schemas as the schemas of the optimal path
    updateInstancesDerivedSchemas();

    // 2. Connect the unconnected schemas
    for(int i = max_depth_; i > -1; i--)
    { connectSchemasAtDepth(i); }

    return aggregateFinalSchema();
}

SchemaNode* StateNode::aggregateFinalSchema()
{
    // 1. Get the instances with object or array type at depth
    GroupedInstances* grouped_instances = instance_manager_.getGroupedInstancesPtrByDepth(0);

    SchemaSet depth0_schemas;

    // 2. Aggregate derived schema for instances
    if(grouped_instances->getInstanceForestByType(kObject).size() > 0)
    {
        for(auto& obj_instance : grouped_instances->getInstanceForestByType(kObject))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(obj_instance->getDerivedSchema());
            depth0_schemas.insert(derived_schema);
        }
    }
    if(grouped_instances->getInstanceForestByType(kArray).size() > 0)
    {
        for(auto& arr_instance : grouped_instances->getInstanceForestByType(kArray))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(arr_instance->getDerivedSchema());
            depth0_schemas.insert(derived_schema);
        }
    }
    if(grouped_instances->getInstanceForestByType(kNumber).size() > 0)
    {
        for(auto& num_instance : grouped_instances->getInstanceForestByType(kNumber))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(num_instance->getDerivedSchema());
            depth0_schemas.insert(derived_schema);
        }
    }
    if(grouped_instances->getInstanceForestByType(kString).size() > 0)
    {
        for(auto& str_instance : grouped_instances->getInstanceForestByType(kString))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(str_instance->getDerivedSchema());
            depth0_schemas.insert(derived_schema);
        }
    }
    if(grouped_instances->getInstanceForestByType(kBoolean).size() > 0)
    {
        for(auto& bool_instance : grouped_instances->getInstanceForestByType(kBoolean))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(bool_instance->getDerivedSchema());
            depth0_schemas.insert(derived_schema);
        }
    }
    if(grouped_instances->getInstanceForestByType(kNull_).size() > 0)
    {
        for(auto& null_instance : grouped_instances->getInstanceForestByType(kNull_))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(null_instance->getDerivedSchema());
            depth0_schemas.insert(derived_schema);
        }
    }

    // 3. Connect the unconnected schemas
    if(depth0_schemas.size() == 1)
    {
        SchemaNode* final_schema = *depth0_schemas.begin();
        return final_schema;
    }
    else
    {
        SchemaNode* final_schema = new SchemaNode(kAnyOf);
        for(auto& schema : depth0_schemas)
        { final_schema->addChild(schema); }
        return final_schema;
    }
}

void StateNode::updateInstancesDerivedSchemas()
{
    // cout << " CURRENT DEPTH: " << current_depth_ << endl;
    // cout << " |||||| " << getStateId() << endl;
    // setDerivedSchemaAsThisState();
    StateNode* parent_state = parent_state_;
    
    while(parent_state != nullptr)
    {
        // cout << " |||||| " << parent_state->getStateId() << endl;
        parent_state->setDerivedSchemaAsThisState();
        parent_state = parent_state->getParentState();
    }
    
    return;
}



void StateNode::connectSchemasAtDepth(int depth)
{
    SchemaToInstanceForest objsch_to_instanceforest;
    SchemaToInstanceForest arrsch_to_instanceforest;

    // 1. Get the instances with object or array type at depth
    GroupedInstances* grouped_instances = instance_manager_.getGroupedInstancesPtrByDepth(depth);

    // 2. Connect the unconnected schemas
    if(grouped_instances->getInstanceForestByType(kObject).size() > 0)
    {
        for(auto& obj_instance : grouped_instances->getInstanceForestByType(kObject))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(obj_instance->getDerivedSchema());

            auto schema_to_forest_it = objsch_to_instanceforest.find(derived_schema);
            if(schema_to_forest_it == objsch_to_instanceforest.end())
            { objsch_to_instanceforest.insert( {derived_schema, InstanceForest( {obj_instance} )} ); }
            else
            { schema_to_forest_it->second.push_back(obj_instance); }
        }
    }

    // FOR DEBUG ///////////////////////////////////////////////////////////////
    // cout << "[CONNECTING NODES AT DEPTH: " << depth << "]" << endl;
    // cout << "OBJECT TOTAL: \t" << grouped_instances->getInstanceForestByType(kObject).size() << endl;
    // Count obj_count = 0;
    // for(auto& objsch_instanceforest_pair : objsch_to_instanceforest)
    // {
    //     SchemaNode* objsch = objsch_instanceforest_pair.first;
    //     InstanceForest& objforest = objsch_instanceforest_pair.second;
    //     obj_count += objforest.size();
    // }
    // cout << "OBJECT MAP: \t" << obj_count << endl;
    ////////////////////////////////////////////////////////////////////////////

    if(grouped_instances->getInstanceForestByType(kArray).size() > 0)
    {
        for(auto& arr_instance : grouped_instances->getInstanceForestByType(kArray))
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(arr_instance->getDerivedSchema());

            auto schema_to_forest_it = arrsch_to_instanceforest.find(derived_schema);
            if(schema_to_forest_it == arrsch_to_instanceforest.end())
            { arrsch_to_instanceforest.insert( {derived_schema, InstanceForest( {arr_instance} )} ); }
            else
            { schema_to_forest_it->second.push_back(arr_instance); }
        }
    }

    // FOR DEBUG ///////////////////////////////////////////////////////////////
    // cout << "ARRAY TOTAL: \t" << grouped_instances->getInstanceForestByType(kArray).size() << endl;
    // Count arr_count = 0;
    // for(auto& arrsch_instanceforest_pair : arrsch_to_instanceforest)
    // {
    //     SchemaNode* arrsch = arrsch_instanceforest_pair.first;
    //     InstanceForest& arrforest = arrsch_instanceforest_pair.second;
    //     arr_count += arrforest.size();
    // }
    // cout << "ARRAY MAP: \t" << arr_count << endl << endl; 
    ////////////////////////////////////////////////////////////////////////////

    for(auto& objsch_forest_pair : objsch_to_instanceforest)
    {
        SchemaNode* objsch = objsch_forest_pair.first;
        InstanceForest& objforest = objsch_forest_pair.second;
        connectObjSchemaUsingInstances(objsch, objforest);
    }

    for(auto& arrsch_forest_pair : arrsch_to_instanceforest)
    {
        SchemaNode* arrsch = arrsch_forest_pair.first;
        InstanceForest& arrforest = arrsch_forest_pair.second;
        connectArrSchemaUsingInstances(arrsch, arrforest);
    }
}



void StateNode::connectObjSchemaUsingInstances(SchemaNode* schema, InstanceForest& instance_forest)
{
    // Case 1) Hom
    if(schema->getType() == kHomObj)
    {

        // 1. Initiate data structures
        LabelToSchemaSet label_to_schema_set;
        for(auto& label : schema->getStringLabels())
        { label_to_schema_set.insert( {label, SchemaSet()} ); }


        // 2. Aggregate derived schema for instances
        for(auto& instance : instance_forest)
        {
            for(auto& label : instance->getStringLabels())
            {
                SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(instance->getChild(label))->getDerivedSchema());
                if(derived_schema == nullptr) cout << schema << "\t";
                label_to_schema_set[label].insert(derived_schema);
            }
        }

        // FOR DEBUG ////////////////////////////////////////////////////////
        // printLabelToSchemaSet(label_to_schema_set);
        /////////////////////////////////////////////////////////////////////

        // printLabelToSchemaSet(label_to_schema_set);

        // 3. Connect the unconnected schemas
        for(auto& label_to_schema_set_pair : label_to_schema_set)
        {
            strInt label = label_to_schema_set_pair.first;
            SchemaSet& schema_set = label_to_schema_set_pair.second;

            if(schema_set.size() == 1)
            {
                SchemaNode* derived_schema = *schema_set.begin();
                if(derived_schema == nullptr) cout << schema << "\t";
                schema->replaceChild(label, derived_schema);
            }
            else if (schema_set.size() == 0)
            {
                cout << "ERROR: StateNode::connectObjSchemaUsingInstances" << endl;
                cout << "    - No derived schema for the label" << endl;
            }
            else
            {
                SchemaNode* anyof_schema = new SchemaNode(kAnyOf);
                for(auto& schema : schema_set)
                { anyof_schema->addChild(schema); }
                schema->replaceChild(label, anyof_schema);
            }
        }
    }
    
    // Case 2) Het
    else if(schema->getType() == kHetObj)
    { 
        // 1. Initiate data structures
        SchemaSet kleene_schema_set;

        // 2. Aggregate derived schema for instances
        for(auto& instance: instance_forest)
        {
            for(auto& label : instance->getStringLabels())
            {
                SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(instance->getChild(label))->getDerivedSchema());
                if(derived_schema == nullptr) cout << schema << "\t";
                kleene_schema_set.insert(derived_schema);
            }
        }

        // 3. Connect the unconnected schemas
        if(kleene_schema_set.size() == 1)
        {
            SchemaNode* derived_schema = *kleene_schema_set.begin();
            schema->setKleeneChild(derived_schema);
        }
        else
        {
            SchemaNode* anyof_schema = new SchemaNode(kAnyOf);
            for(auto& schema : kleene_schema_set)
            { anyof_schema->addChild(schema); }
            schema->setKleeneChild(anyof_schema);
        }
    }



    // Case 3) Com
    else if(schema->getType() == kComObj)
    {
        // 1. Initiate data structures
        SchemaSet kleene_schema_set;
        LabelToSchemaSet label_to_schema_set;
        for(auto& label : schema->getStringLabels())
        { label_to_schema_set.insert( {label, SchemaSet()} ); }

        // 2. Aggregate derived schema for instances
        for(auto& instance : instance_forest)
        {
            for(auto& label : instance->getStringLabels())
            {
                SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(instance->getChild(label))->getDerivedSchema());

                auto label_to_schema_set_it = label_to_schema_set.find(label);
                if(label_to_schema_set_it == label_to_schema_set.end())
                { kleene_schema_set.insert(derived_schema); }
                else
                { label_to_schema_set[label].insert(derived_schema); }
            }
        }

        // 3. Connect the unconnected schemas
        for(auto& label_to_schema_set_pair : label_to_schema_set)
        {
            strInt label = label_to_schema_set_pair.first;
            SchemaSet& schema_set = label_to_schema_set_pair.second;

            if(schema_set.size() == 1)
            {
                SchemaNode* derived_schema = *schema_set.begin();
                schema->replaceChild(label, derived_schema);
            }
            else if (schema_set.size() == 0)
            {
                cout << "ERROR: StateNode::connectObjSchemaUsingInstances" << endl;
                cout << "    - No derived schema for the label" << endl;
            }
            else
            {
                SchemaNode* anyof_schema = new SchemaNode(kAnyOf);
                for(auto& schema : schema_set)
                { anyof_schema->addChild(schema); }
                schema->replaceChild(label, anyof_schema);
            }
        }

        if(kleene_schema_set.size() == 1)
        {
            SchemaNode* derived_schema = *kleene_schema_set.begin();
            schema->setKleeneChild(derived_schema);
        }
        else
        {
            SchemaNode* anyof_schema = new SchemaNode(kAnyOf);
            for(auto& schema : kleene_schema_set)
            { anyof_schema->addChild(schema); }
            schema->setKleeneChild(anyof_schema);
        }
    }

    else
    {
        cout << "ERROR: StateNode::connectObjSchemaUsingInstances" << endl;
        cout << "    - Invalid Schema Type" << endl;
    }
    return;
}

void StateNode::connectArrSchemaUsingInstances(SchemaNode* schema, InstanceForest& instance_forest)
{
    if(schema->getType() == kHomArr)
    {
        // 1. Initiate data structures
        vector<SchemaSet> index_to_schema_set;
        for(int i = 0; i < schema->getChildrenNum(); i++)
        { index_to_schema_set.push_back(SchemaSet()); }

        // 2. Aggregate derived schema for instances
        for(auto& instance : instance_forest)
        {
            for(int i = 0; i < instance->getChildrenNum(); i++)
            {
                SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(instance->getChildWithIndex(i))->getDerivedSchema());
                index_to_schema_set[i].insert(derived_schema);
            }
        }

        // FOR DEBUG //
        int count = 1;
        for(auto& schema_set : index_to_schema_set)
        {
            cout << "INDEX: " << count++ << endl;
            for(auto& schema : schema_set)
            { cout << schema << " "  << endl; }
        }
        ///////////////

        // 3. Connect the unconnected schemas
        for(int i = 0; i < schema->getChildrenNum(); i++)
        {
            SchemaSet& schema_set = index_to_schema_set[i];

            if(schema_set.size() == 1)
            {
                SchemaNode* derived_schema = *schema_set.begin();
                schema->replaceChildWithIndex(i, derived_schema);
            }
            else
            {
                SchemaNode* anyof_schema = new SchemaNode(kAnyOf);
                for(auto& schema : schema_set)
                { anyof_schema->addChild(schema); }
                schema->replaceChildWithIndex(i, anyof_schema);
            }
        }
    }

    else if(schema->getType() == kHetArr)
    {
        // 1. Initiate data structures
        SchemaSet kleene_schema_set;

        // 2. Aggregate derived schema for instances
        for(auto& instance: instance_forest)
        {
            for(int i = 0; i < instance->getChildrenNum(); i++)
            {
                SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(instance->getChildWithIndex(i))->getDerivedSchema());
                kleene_schema_set.insert(derived_schema);
            }
        }

        // 3. Connect the unconnected schemas
        if(kleene_schema_set.size() == 1)
        {
            SchemaNode* derived_schema = *kleene_schema_set.begin();
            schema->setKleeneChild(derived_schema);
        }
        else
        {
            SchemaNode* anyof_schema = new SchemaNode(kAnyOf);
            for(auto& schema : kleene_schema_set)
            { anyof_schema->addChild(schema); }
            schema->setKleeneChild(anyof_schema);
        }
    }

    else
    {
        cout << "ERROR: StateNode::connectArrSchemaUsingInstances" << endl;
        cout << "    - Invalid Schema Type" << endl;
    }

    return;
}





void StateNode::checkAllInstancesHaveDerivedSchema()
{
    for(int check_depth = max_depth_; check_depth > -1; check_depth--)
    {
        GroupedInstances* children_grouped_instances = instance_manager_.getGroupedInstancesPtrByDepth(check_depth);

        if(children_grouped_instances->getInstanceForestByType(kObject).size() > 0)
        {
            for(auto& obj_instance : children_grouped_instances->getInstanceForestByType(kObject))
                if(obj_instance->getDerivedSchema() == nullptr)
                    cout << "ERROR: StateNode::checkAllInstancesHaveDerivedSchema" << endl;
        }

        if(children_grouped_instances->getInstanceForestByType(kArray).size() > 0)
        {
            for(auto& arr_instance : children_grouped_instances->getInstanceForestByType(kArray))
                if(arr_instance->getDerivedSchema() == nullptr)
                    cout << "ERROR: StateNode::checkAllInstancesHaveDerivedSchema" << endl;
        }

        if(children_grouped_instances->getInstanceForestByType(kNumber).size() > 0)
        {
            for(auto& num_instance : children_grouped_instances->getInstanceForestByType(kNumber))
                if(num_instance->getDerivedSchema() == nullptr)
                    cout << "ERROR: StateNode::checkAllInstancesHaveDerivedSchema" << endl;
        }

        if(children_grouped_instances->getInstanceForestByType(kString).size() > 0)
        {
            for(auto& str_instance : children_grouped_instances->getInstanceForestByType(kString))
                if(str_instance->getDerivedSchema() == nullptr)
                    cout << "ERROR: StateNode::checkAllInstancesHaveDerivedSchema" << endl;
        }

        if(children_grouped_instances->getInstanceForestByType(kBoolean).size() > 0)
        {
            for(auto& bool_instance : children_grouped_instances->getInstanceForestByType(kBoolean))
                if(bool_instance->getDerivedSchema() == nullptr)
                    cout << "ERROR: StateNode::checkAllInstancesHaveDerivedSchema" << endl;
        }

        if(children_grouped_instances->getInstanceForestByType(kNull_).size() > 0)
        {
            for(auto& null_instance : children_grouped_instances->getInstanceForestByType(kNull_))
                if(null_instance->getDerivedSchema() == nullptr)
                    cout << "ERROR: StateNode::checkAllInstancesHaveDerivedSchema" << endl;
        }
    }
}











void StateNode::setDerivedSchemaAsThisState()
{
    GroupedInstances* children_grouped_instances = instance_manager_.getGroupedInstancesPtrByDepth(current_depth_);

    // cout << "DEPTH: " << current_depth_ << endl;
    if(children_grouped_instances->getInstanceForestByType(kObject).size() > 0)
    {
        // cout << "(OBJ) " << children_grouped_instances->getInstanceForestByType(kObject).size() << endl;
        for(auto& obj_instance : children_grouped_instances->getInstanceForestByType(kObject))
            obj_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kArray).size() > 0)
    {
        // cout << "(ARR) " << children_grouped_instances->getInstanceForestByType(kArray).size() << endl;
        for(auto& arr_instance : children_grouped_instances->getInstanceForestByType(kArray))
            arr_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kNumber).size() > 0)
    {
        // cout << "(NUM) " << children_grouped_instances->getInstanceForestByType(kNumber).size() << endl;
        for(auto& num_instance : children_grouped_instances->getInstanceForestByType(kNumber))
            num_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kString).size() > 0)
    {
        // cout << "(STR) " << children_grouped_instances->getInstanceForestByType(kString).size() << endl;
        for(auto& str_instance : children_grouped_instances->getInstanceForestByType(kString))
            str_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kBoolean).size() > 0)
    {
        // cout << "(BOOL) " << children_grouped_instances->getInstanceForestByType(kBoolean).size() << endl;
        for(auto& bool_instance : children_grouped_instances->getInstanceForestByType(kBoolean))
            bool_instance->setNodeAsState(state_id_);
    }

    if(children_grouped_instances->getInstanceForestByType(kNull_).size() > 0)
    {
        // cout << "(NULL) " << children_grouped_instances->getInstanceForestByType(kNull_).size() << endl;
        for(auto& null_instance : children_grouped_instances->getInstanceForestByType(kNull_))
            null_instance->setNodeAsState(state_id_);
    }

    // cout << endl;
}


// void StateNode::updateCDInstances()
// {
//     // We're interested in children's depth -> Change children to their derived schemas
//     int children_depth = current_depth_ + 1;

//     if(children_depth > max_depth_)
//         return;
        
//     GroupedInstances* children_grouped_instances = instance_manager_.getGroupedInstancesPtrByDepth(children_depth);

//     if(children_grouped_instances->getInstanceForestByType(kObject).size() > 0)
//     {
//         for(auto& obj_instance : children_grouped_instances->getInstanceForestByType(kObject))
//             obj_instance->setNodeAsState(state_id_);
//     }

//     if(children_grouped_instances->getInstanceForestByType(kArray).size() > 0)
//     {
//         for(auto& arr_instance : children_grouped_instances->getInstanceForestByType(kArray))
//             arr_instance->setNodeAsState(state_id_);
//     }

//     if(children_grouped_instances->getInstanceForestByType(kNumber).size() > 0)
//     {
//         for(auto& num_instance : children_grouped_instances->getInstanceForestByType(kNumber))
//             num_instance->setNodeAsState(state_id_);
//     }

//     if(children_grouped_instances->getInstanceForestByType(kString).size() > 0)
//     {
//         for(auto& str_instance : children_grouped_instances->getInstanceForestByType(kString))
//             str_instance->setNodeAsState(state_id_);
//     }

//     if(children_grouped_instances->getInstanceForestByType(kBoolean).size() > 0)
//     {
//         for(auto& bool_instance : children_grouped_instances->getInstanceForestByType(kBoolean))
//             bool_instance->setNodeAsState(state_id_);
//     }

//     if(children_grouped_instances->getInstanceForestByType(kNull_).size() > 0)
//     {
//         for(auto& null_instance : children_grouped_instances->getInstanceForestByType(kNull_))
//             null_instance->setNodeAsState(state_id_);
//     }
// }