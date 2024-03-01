#include "InstanceCluster.hpp"

void InstanceCluster::setInstanceForest(InstanceSet& instance_set)
{
    copy(instance_set.begin(), instance_set.end(), back_inserter(*instance_forest_));
}

void InstanceCluster::setInstanceForest(InstanceForest& instance_forest)
{
    *instance_forest_ = instance_forest;
}

void InstanceCluster::updateClusterType()
{
    bool hom_part = false;
    bool het_part = false;

    for(auto& instance : *instance_forest_)
    {
        if(roaring_bitmap_get_cardinality(instance->getLabelBitmap()) > 0) hom_part = true;
        if(roaring_bitmap_get_cardinality(instance->getKleenedLabels()) > 0) het_part = true;
    }

    if(hom_part && het_part) type_ = kComObjC;
    else if(hom_part && !het_part) type_ = kHomObjC;
    else if(!hom_part && het_part) type_ = kHetObjC;
    else type_ = kEmptyObjC;
}







void InstanceCluster::updateClusterMetadata(CostParameters& cost_parameters)
{
    if(getUpToDateBit())
    { return; }

    switch(getClusterType())
    {
        case kHomObjC:
        case kEmptyObjC:
            updateHomObjCMetadata(cost_parameters);
            break;
        case kHetObjC:
            updateHetObjCMetadata(cost_parameters);
            break;
        case kComObjC:
            updateComObjCMetadata(cost_parameters);
            break;
        case kHomArrC:
        case kEmptyArrC:
            updateHomArrCMetadata(cost_parameters);
            break;
        case kHetArrC:
            updateHetArrCMetadata(cost_parameters);
            break;
        default:
            break;
    }
}



void InstanceCluster::updateHomObjCMetadata(CostParameters& cost_parameters)
{
    // (1). [------- | Cost | -----] Children num
    // (2). [Pattern | ---- | Merge] Distinct labels
    distinct_labels_        = roaring_bitmap_create();
    // (3). [Pattern | Cost | -----] mandatory labels - OPT REQ
    mandatory_labels_       = roaring_bitmap_create();
    // (4). [Pattern | Cost | -----] Labels to schemas - {a{SCH1}, b{SCH2}, ...}
    label_to_schemas_       = new LabelToSchemaSet();
    // (5). [------- | ---- | Merge] Labels counting - OPT REQ
    label_count_            = new LabelToCount();
    // (6). [------- | ---- | Merge] Children-derived schemas
    children_schema_set_    = new SchemaSet();

    for(auto& object : *instance_forest_)
    {
        vector<strInt>& node_labels  = object->getStringLabels();
        vector<Node*>& children      = object->getChildren();
        roaring_bitmap_t* labels     = object->getLabelBitmap();

        // 1. (1) Aggregate children num
        children_num_ += children.size();

        // 2. (2) Update distinct labels
        roaring_bitmap_or_inplace(distinct_labels_, labels);
        // 3. (3) Update mandatory labels
        roaring_bitmap_and_inplace(mandatory_labels_, labels);

        for(int i = 0; i < node_labels.size(); i++)
        {
            strInt label = node_labels[i];
            SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema());

            // 4. (4) Update label -> schemas

                // Check if the key exists in the unordered_map
            auto label_to_schemas_it = label_to_schemas_->find(label);
            if (label_to_schemas_it == label_to_schemas_->end()) 
            {
                // Key doesn't exist, create a new pair with an empty unordered_set
                label_to_schemas_->insert( {label, SchemaSet( {derived_schema} )} );
            }
            else
            { label_to_schemas_it->second.insert(derived_schema); }

            // 5. (5) Update label count
            auto label_count_it = label_count_->find(label);
            if (label_count_it == label_count_->end())
            { label_count_->insert({label, 1}); }
            else 
            { (label_count_it->second)++; }

            // 6. (6) Update children schemas
            children_schema_set_->insert(derived_schema);
        }
    }

    up_to_date_ = true;
    return;
}


void InstanceCluster::updateHetObjCMetadata(CostParameters& cost_parameters)
{
    // (1). [------- | Cost | -----] Children num
    // (2). [Pattern | ---- | Merge] All children schemas - 
        // {SCH1, SCH2, ...}
    children_schema_set_ = new SchemaSet();

    for(auto& object : *instance_forest_)
    {
        // 1. Derived Schemas
        vector<Node*>& children = object->getChildren();

        // 1. (1) Aggregate children num
        children_num_ += children.size();

        // 2. (2) Update children schemas
        for(int i = 0; i < children.size(); i++)
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema());

            children_schema_set_->insert(derived_schema);
        }
    }

    up_to_date_ = true;
    return;
}


void InstanceCluster::updateComObjCMetadata(CostParameters& cost_parameters)
{
    // (1). [------- | Cost | -----] Children num
     // children_num_ (already initiated)
    // (2). [Pattern | ---- | Merge] Distinct labels
    distinct_labels_        = roaring_bitmap_create();
    // (3). [Pattern | Cost | -----] mandatory labels - OPT REQ
    mandatory_labels_       = roaring_bitmap_create();
    // (4). [------- | ---- | Merge] Children-derived schemas
    children_schema_set_    = new SchemaSet();
    // (5). children_schemas_com_kleene_
    children_schemas_com_kleene_ = new SchemaSet();
    // (6). children_num_com_kleene_
     // children_num_com_kleene_ (already initiated)
    // (7). [Pattern | Cost | -----] Labels to schemas 
        // ex) {a{SCH1}, b{SCH2, SCH4}, ..., z{SCH1, SCH5, ..., SCH8}}
    label_to_schemas_       = new LabelToSchemaSet();
    // (8). [------- | ---- | Merge] Labels counting - OPT REQ
    label_count_            = new LabelToCount();
    


    for(auto& object : *instance_forest_)
    {
        vector<strInt>& node_labels  = object->getStringLabels();
        vector<Node*>& children      = object->getChildren();
        roaring_bitmap_t* labels     = object->getLabelBitmap();
        vector<int>      label_to_threshold = object->getLabelToThreshold();
        int              current_threshold  = object->getCurrentThreshold();

        // 1. (1) Aggregate children num
        children_num_ += children.size();

        // 2. (2) Update distinct labels
        roaring_bitmap_or_inplace(distinct_labels_, labels);
        // 3. (3) Update mandatory labels
        roaring_bitmap_and_inplace(mandatory_labels_, labels);

        for(int i = 0; i < node_labels.size(); i++)
        {
            strInt label = node_labels[i];
            SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema());

            // 4. (4) Update children_schema_set -> derived schemas of all children
            children_schema_set_->insert( derived_schema ); 

            if(0 < label_to_threshold[i] && label_to_threshold[i] <= current_threshold)
            { 
                // 5. (5) Update children schemas for kleened labels only
                children_schemas_com_kleene_->insert( derived_schema );
                // 6. (6) Update children num for kleene only
                children_num_com_kleene_ += 1;
            }
            else
            {
                // 7. (7) Update label to schemas for hom-part labels
                    // Check if the key exists in the unordered_map
                auto label_to_schemas_it = label_to_schemas_->find(label);
                if (label_to_schemas_it == label_to_schemas_->end()) 
                {
                    // Key doesn't exist, create a new pair with an empty unordered_set
                    label_to_schemas_->insert( {label, SchemaSet({ derived_schema })} );
                }
                else
                {
                    label_to_schemas_it->second.insert(derived_schema);
                }

                // 8. (8) Update label count
                auto label_count_it = label_count_->find(label);
                if(label_count_it == label_count_->end())
                { label_count_->insert( {label, 1} ); }
                else 
                { (label_count_it->second)++; }
            }
        }
    }

    // MDL cost optimization
    mdlCostOptimizationAtComObj(cost_parameters);

    up_to_date_ = true;
    return;
}


void InstanceCluster::mdlCostOptimizationAtComObj(CostParameters& cost_parameters)
{
    for (auto it = label_count_->begin(); it != label_count_->end() ; )
    {
        strInt label = it->first;
        int n = instance_forest_->size();
        int m = it->second;
        SchemaSet& schemas = label_to_schemas_->at(label);

        if (
            isSubset(&schemas, children_schemas_com_kleene_) &&
            n > m * cost_parameters.getObjLenBitSize()
        )
        {
            children_num_com_kleene_ += m;
            label_to_schemas_->erase(label);
            it = label_count_->erase(it);
        }
        else
        {
            it++;
        }
    }
}


void InstanceCluster::updateHomArrCMetadata(CostParameters& cost_parameters)
{
    // (1). [Pattern | Cost | -----] Children derived schema sequence
    children_schema_seq_ = new vector<SchemaNode*>();
    
    // 1. (1) Update schema sequences
    InstanceNode* one_instance = instance_forest_->at(0);
    for(auto& child : one_instance->getChildren())
    { 
        SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(child)->getDerivedSchema());
        children_schema_seq_->push_back(derived_schema); 
    }

    up_to_date_ = true;
    return;
}


void InstanceCluster::updateHetArrCMetadata(CostParameters& cost_parameters)
{
    // 1. [Pattern | ---- | Merge] Children schemas set
    children_schema_set_ = new SchemaSet();

    for(auto& array : *instance_forest_)
    {
        // 1. Kleene Schemas
        vector<Node*>&   children    = array->getChildren();

        for(auto& child : children)
        {
            SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(child)->getDerivedSchema());
            children_schema_set_->insert(derived_schema);
        }
    }

    up_to_date_ = true;
    return;
}


string InstanceCluster::getTypeInString()
{
    switch(type_)
    {
        case kHomObjC: return "HomObj";
        case kHetObjC: return "HetObj";
        case kComObjC: return "ComObj";
        case kEmptyObjC: return "EmptyObj";
        case kHomArrC: return "HomArr";
        case kHetArrC: return "HetArr";
        case kEmptyArrC: return "EmptyArr";
    }
    cout << endl << "[TYPE]" << endl;
    cout << type_ << endl;
    cout << "[TYPE]" << endl;
    throw IllegalBehaviorError("InstanceCluster::getTypeInString - illegal cluster type");
}