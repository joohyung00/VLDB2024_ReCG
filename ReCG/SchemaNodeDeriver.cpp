#include "SchemaNodeDeriver.hpp"



SchemaNode* deriveSchemaFromCluster(InstanceCluster& instance_cluster, CostParameters& cost_parameters)
{
    SchemaNode* derived_schema = nullptr;

    switch(instance_cluster.getClusterType())
    {
        case kHomObjC:
            derived_schema = deriveHomObjNode(instance_cluster, cost_parameters);
            break;
        case kHetObjC:
            derived_schema = deriveHetObjNode(instance_cluster, cost_parameters);
            break;
        case kComObjC:
            derived_schema = deriveComObjNode(instance_cluster, cost_parameters);
            break;
        case kEmptyObjC:
            derived_schema = deriveHomObjNode(instance_cluster, cost_parameters);
            break;
        case kHomArrC:
            derived_schema = deriveHomArrNode(instance_cluster, cost_parameters);
            break;
        case kHetArrC:
            derived_schema = deriveHetArrNode(instance_cluster, cost_parameters);
            break;
        case kEmptyArrC:
            derived_schema = deriveHomArrNode(instance_cluster, cost_parameters);
            break;
        default:
            IllegalBehaviorError("deriveSchemaFromCluster - unexpected cluster type");
    }

    if(derived_schema == nullptr)
    { cout << "STILL NULLPTR!" << endl; }
    return derived_schema;
}













//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Hom Obj Node ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

SchemaNode* deriveHomObjNode(InstanceCluster& hom_obj_cluster, CostParameters& cost_parameters)
{
    if(!hom_obj_cluster.getUpToDateBit())
    {
        // 1. Fill in Metadata for cluster
        hom_obj_cluster.updateHomObjCMetadata(cost_parameters);
    }

    // 2. Derive Homobgeneous Object Node
    SchemaNode* hom_obj_node = new SchemaNode(kHomObj);

        // REQ
        // labels -> schemaSet
        // required labels
        // + distinct_labels
            // -> optional_labels

        // + children_schemas

    int forest_size = hom_obj_cluster.getForestSize();
    int optional_labels_num = 0;

    unordered_map<strInt, int>* label_count = hom_obj_cluster.getLabelCount();
    unordered_map<strInt,unordered_set<SchemaNode*>>* labels_to_schemas = hom_obj_cluster.getLabelsToSchemas();

    for(auto& key_schemas_pair : *labels_to_schemas)
    {
        strInt key = key_schemas_pair.first;
        SchemaNode* child_schema = deriveAnyOfNode(key_schemas_pair.second, cost_parameters, label_count->at(key));

        hom_obj_node->addChild(key, child_schema);
        if(label_count->at(key) == forest_size) 
        {
            hom_obj_node->boldifyLabel(key);
        }
        else
        {
            optional_labels_num++;
        }
    }

    // 3. Calculate MDL Cost
        // n
        // optional_num
    hom_obj_node->setSRC( homObjSRC(hom_obj_cluster, cost_parameters) );
    hom_obj_node->setDRC( homObjDRC(hom_obj_cluster, cost_parameters) );
    hom_obj_node->aggregateAnyOfChildrenCost();

    // 4. Set derived schema as Cluster's schema
    hom_obj_cluster.setDerivedSchema(hom_obj_node);

    return hom_obj_node;
}


//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Het Obj Node ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

SchemaNode* deriveHetObjNode(InstanceCluster& het_obj_cluster, CostParameters& cost_parameters)
{
    if(!het_obj_cluster.getUpToDateBit())
    {
        // 1. Fill in Metadata for cluster
        het_obj_cluster.updateHetObjCMetadata(cost_parameters);
    }
    
    
    // 2. Derive Heterogeneous Object Node

        // REQ
        // children_schemas

        // + distinct_labels

    SchemaNode* het_obj_node = new SchemaNode(kHetObj);

    int m = het_obj_cluster.getChildrenNum();

    het_obj_node->setKleeneChild( deriveAnyOfNode(het_obj_cluster.getChildrenSchemaSet(), cost_parameters, m) );

    // 3. Calculate MDL Cost
        // n
        // m
    het_obj_node->setSRC( hetObjSRC(het_obj_cluster, cost_parameters) );
    het_obj_node->setDRC( hetObjDRC(het_obj_cluster, cost_parameters) );
    het_obj_node->aggregateAnyOfChildrenCost();

    // 4. Set derived schema as Cluster's schema
    het_obj_cluster.setDerivedSchema(het_obj_node);

    return het_obj_node;
}


//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Com Obj Node ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

SchemaNode* deriveComObjNode(InstanceCluster& com_obj_cluster, CostParameters& cost_parameters)
{
    if(!com_obj_cluster.getUpToDateBit())
    {
        // 1. Fill in Metadata for cluster
        com_obj_cluster.updateComObjCMetadata(cost_parameters);
    }

    // 2. Derive Homo-Hetero Object Node
        // 2.1. Derive Homo-Part

        // REQ
        // labels -> schemaSet
        // required labels
        // children_schemas(*-part)
            // label_count
        
        // + distinct_labels

    SchemaNode* com_obj_node = new SchemaNode(kComObj);

    int optional_labels_num = 0;
    int forest_size = com_obj_cluster.getForestSize();

    unordered_map<strInt, int>* label_count = com_obj_cluster.getLabelCount();
    for(auto& key_schemas_pair : *(com_obj_cluster.getLabelsToSchemas()))
    {
        strInt key = key_schemas_pair.first;
        SchemaNode* child_schema = deriveAnyOfNode(key_schemas_pair.second, cost_parameters, label_count->at(key));

        com_obj_node->addChild(key, child_schema);
        if(label_count->at(key) == forest_size) 
        {
            com_obj_node->boldifyLabel(key);
        }
        else
        {
            optional_labels_num++;
        }
    }

    int m = com_obj_cluster.getChildrenNumForCom();

        // 2.2. Derive Hetero Part
    com_obj_node->setKleeneChild( deriveAnyOfNode(com_obj_cluster.getChildrenSchemaForCom(), cost_parameters, m) );

    // 3. Calculate MDL Cost
        // n
        // m
        // label_count
    com_obj_node->setSRC( comObjSRC(com_obj_cluster, cost_parameters) );
    com_obj_node->setDRC( comObjDRC(com_obj_cluster, cost_parameters) );
    com_obj_node->aggregateAnyOfChildrenCost();

    // 4. Set derived schema as Cluster's schema
    com_obj_cluster.setDerivedSchema(com_obj_node);

    return com_obj_node;
}





////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Hom Arr Derivation ////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

SchemaNode* deriveHomArrNode(InstanceCluster& hom_arr_cluster, CostParameters& cost_parameters)
{
    if(!hom_arr_cluster.getUpToDateBit())
    {
        // 1. Fill in Metadata for cluster
        hom_arr_cluster.updateHomArrCMetadata(cost_parameters);
    }

    // 2. Derive HomArr Schema Node
    vector<SchemaNode*> schema_seq;

    for(auto& child : hom_arr_cluster.getInstanceForest()->at(0)->getChildren())
    { schema_seq.push_back(TO_SCHEMA_NODE(TO_INSTANCE_NODE(child)->getDerivedSchema())); }

    SchemaNode* hom_arr_node = new SchemaNode(kHomArr);
    for(auto child_schema : schema_seq)
    { hom_arr_node->addChild(child_schema); }

    // 3. Calculate MDL Cost
    hom_arr_node->setSRC( homArrSRC(hom_arr_cluster, cost_parameters) );
    hom_arr_node->setDRC( homArrDRC(hom_arr_cluster, cost_parameters) );
    hom_arr_node->aggregateAnyOfChildrenCost();

    // 4. Set derived schema as Cluster's schema
    hom_arr_cluster.setDerivedSchema(hom_arr_node);

    return hom_arr_node;
}


////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Het Arr Derivation ////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

SchemaNode* deriveHetArrNode(InstanceCluster& het_arr_cluster, CostParameters& cost_parameters)
{
    if(!het_arr_cluster.getUpToDateBit())
    {
        // 1. Fill in Metadata for cluster
        het_arr_cluster.updateHetArrCMetadata(cost_parameters);
    }

    // 2. Derive HetArr Schema Node
    SchemaNode* het_arr_node = new SchemaNode(kHetArr);
    int m = het_arr_cluster.getChildrenNum();

    het_arr_node->setKleeneChild( deriveAnyOfNode(het_arr_cluster.getChildrenSchemaSet(), cost_parameters, m) );

    // 3. Calculate MDL Cost
        // n
    het_arr_node->setSRC( hetArrSRC(het_arr_cluster, cost_parameters) );
    het_arr_node->setDRC( hetArrDRC(het_arr_cluster, cost_parameters) );
    het_arr_node->aggregateAnyOfChildrenCost();

    // 4. Set derived schema as Cluster's schema
    het_arr_cluster.setDerivedSchema(het_arr_node);

    return het_arr_node;
}


















//////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// AnyOf Derivation ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////

SchemaNode* deriveAnyOfNode(SchemaSet& children_set, CostParameters& cost_parameters, int data_num)
{
    // [Error check] None to union
    if(children_set.size() == 0)
    { cout << "ANYOF CHILDREN SIZE 0. MUST CHECK" << endl; }

    // 1. Check if only one type exists
    if(children_set.size() == 1)
    { return *children_set.begin(); }

    // 2. Filter empty objects or empty arrays
    SchemaNode* empty_array_schema = nullptr;
    SchemaSet filtered_children_set;
    for(auto schema_node : children_set)
    {
        if(schema_node->getType() == kHomArr && schema_node->getChildrenNum() == 0)
        { empty_array_schema = schema_node; }
        // else if(schema_node->getType() == kHomObj && schema_node->getChildrenNum() == 0)
        // { continue; }
        else
        { filtered_children_set.insert(schema_node); }
    }

    // 3. Check if only one type exists after filtering
    if(filtered_children_set.size() == 1)
    { 
        if((*(filtered_children_set.begin()))->getType() == kHomArr && empty_array_schema != nullptr)
        {
            SchemaNode* union_schema = new SchemaNode(kAnyOf);
            union_schema->addChild(*(filtered_children_set.begin()));
            union_schema->addChild(empty_array_schema);
            union_schema->sortChildren();
            union_schema->setSRC( anyOfSRC(union_schema, cost_parameters, data_num) );
            union_schema->setDRC( anyOfDRC(union_schema, cost_parameters, data_num) );
            return union_schema;
        }
        return *(filtered_children_set.begin()); 
    }

    // 4. Generate anyOf node
    SchemaNode* union_schema = new SchemaNode(kAnyOf);
    for(auto schema_node : filtered_children_set)
    { union_schema->addChild(schema_node); }

    // 5. Sort children schemas physical ID
    //  - For distance calculation optimization
    union_schema->sortChildren();

    // 6. Calculate MDL Cost
    union_schema->setSRC( anyOfSRC(union_schema, cost_parameters, data_num) );
    union_schema->setDRC( anyOfDRC(union_schema, cost_parameters, data_num) );

    // 7. Optimize mdlCost
    // mdlCostOptimizationAtAnyOf(union_schema); 

    return union_schema;
}

SchemaNode* deriveAnyOfNode(SchemaSet* children_set, CostParameters& cost_parameters, int data_num)
{
    SchemaSet children_set_ = *children_set;
    return deriveAnyOfNode(children_set_, cost_parameters, data_num);
}

SchemaNode* deriveAnyOfNode(SchemaVec& children_forest, CostParameters& cost_parameters, int data_num)
{
    SchemaSet children_set_(children_forest.begin(), children_forest.end());
    return deriveAnyOfNode(children_set_, cost_parameters, data_num);
}

















////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// AnyOf MDL Optimization ////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////


void mdlCostOptimizationAtAnyOf(SchemaNode* any_of_node)
{
    
}


void schemaConsicificationAtAnyOf(SchemaNode* any_of_node)
{
    // [Case 1] Het이 존재.
    SchemaVec target_schemas;

    for(auto& child : any_of_node->getChildren())
    {
        if(TO_SCHEMA_NODE(child)->getType() == kHetObj)
        {
            target_schemas.push_back(TO_SCHEMA_NODE(child)->getKleeneChild());
        }
    }

    for(auto& target_schema : target_schemas)
    {
        auto it = any_of_node->getChildren().begin();
        for( ; it != any_of_node->getChildren().end(); )
        {
            bool condition = true;

            if(TO_SCHEMA_NODE(*it)->getType() == kHomObj)
            {
                for(auto& subschema : (*it)->getChildren())
                {
                    if(target_schema == subschema) continue;
                    else condition = false;
                }
            }
            else if(TO_SCHEMA_NODE(*it)->getType() == kComObj)
            {
                for(auto& subschema : (*it)->getChildren())
                {
                    if(target_schema == subschema) continue;
                    else condition = false;
                }
                if(TO_SCHEMA_NODE(*it)->getKleeneChild() != target_schema)
                { condition = false; }
            }
            else condition = false;
            

            if(condition) 
            {
                it = any_of_node->getChildren().erase(it);
            }
            else it++;
        }
    }

    // [Case 2] Com + 다 똑같이 생김 + No required -> Pruning 가능
    target_schemas.clear();
    for(auto& child : any_of_node->getChildren())
    {
        if(TO_SCHEMA_NODE(child)->getType() == kComObj)
        {
            bool condition = true;

            SchemaNode* kleene_child = TO_SCHEMA_NODE(child)->getKleeneChild();
            for(auto& subschema : TO_SCHEMA_NODE(child)->getChildren())
            { if(kleene_child != subschema) condition = false; }

            if(condition) target_schemas.push_back(kleene_child);
        }
    }

    for(auto& target_schema : target_schemas)
    {
        auto it = any_of_node->getChildren().begin();
        for( ; it != any_of_node->getChildren().end(); )
        {
            bool condition = true;

            if(TO_SCHEMA_NODE(*it)->getType() == kHomObj)
            {
                for(auto& subschema : (*it)->getChildren())
                {
                    if(target_schema == subschema) continue;
                    else condition = false;
                }
            }
            else if(TO_SCHEMA_NODE(*it)->getType() == kComObj)
            {
                for(auto& subschema : (*it)->getChildren())
                {
                    if(target_schema == subschema) continue;
                    else condition = false;
                }
                if(TO_SCHEMA_NODE(*it)->getKleeneChild() != target_schema)
                { condition = false; }
            }
            else condition = false;
            

            if(condition) 
            {
                it = any_of_node->getChildren().erase(it);
            }
            else it++;
        }

        SchemaNode* het = new SchemaNode(kHetObj);
        het->setKleeneChild(target_schema);
        any_of_node->addChild(het);
    }
}