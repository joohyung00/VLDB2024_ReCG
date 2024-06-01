#include "RSUSConstructor.hpp"


void RSUSConstructor::constructRSUS()
{
    // 1. Starting part
    SchemaNode* first_root_node = *(unique_raw_schemas_->begin());
    rsus_ = new SchemaNode(first_root_node->getType());

    bool first = true;



    int barWidth = 70;
    float progress = 0 / (float)unique_raw_schemas_->size();
    int done_count = 0;


    // for(auto instance_node : *unique_raw_schemas_)
    for(int i = 0; i < unique_raw_schemas_->size(); i++)
    { 
        #if SHOWPROGRESSBAR
            progress = done_count / (float)unique_raw_schemas_->size();
            cout << "[";
            int pos = barWidth * progress;
            for (int i = 0; i < barWidth; ++i) {
                if (i < pos) cout << "=";
                else if (i == pos) cout << ">";
                else cout << " ";
            }
            cout << "] " << int(progress * 100.0) << " %\r";
            cout.flush();
        #endif

        rsus_ = constructRSUSRecursive(unique_raw_schemas_->at(i), count_per_raw_schema_->at(i), rsus_); 

        done_count++;
    }

    cout << endl;
    boldifyLabelsRecursive(rsus_);
}



SchemaNode* RSUSConstructor::constructRSUSRecursive(SchemaNode* raw_schema_node, Count occur_count, SchemaNode* rsus_node)
{

    // TODO: Add aggregation of occur_count

    // Case 1. raw_schema_node == anyOf, rsus_node != anyOf
    if(raw_schema_node->getType() == kAnyOf && rsus_node->getType() != kAnyOf)
    {
        bool all_types_same = true;
        vector<Node*>* raw_children = raw_schema_node->getChildren();

        for(auto raw_child : *raw_children)
        {
            if(TO_SCHEMA_NODE(raw_child)->getType() != rsus_node->getType())
            {
                all_types_same = false;
                break;
            }
        }

        if(all_types_same)
        {
            // 1.1. All types of raw_schema_node's children are same with rsus_node's type
                // Then just recursively call constructRSUSRecursive
                // The returned node will always be the same
            SchemaNode* returned_node;
            for(auto raw_child : *raw_children)
            { 
                rsus_node->incrementCountWithValue(occur_count);
                returned_node = constructRSUSRecursive(TO_SCHEMA_NODE(raw_child), occur_count, rsus_node);
            }

            return returned_node;
        }
        else
        {
            // 1.2. Not all types of raw_schema_node's children are same with rsus_node's type
                // Then we have to add anyOf node in between
                //  and then call constructRSUSRecursive again
            SchemaNode* anyof_node = new SchemaNode(kAnyOf);
            anyof_node->addChild(rsus_node);

            return constructRSUSRecursive(raw_schema_node, occur_count, anyof_node);
        }
    }
    
    // Case 2. raw_schema_node == anyOf, rsus_node == anyOf
    else if(raw_schema_node->getType() == kAnyOf && rsus_node->getType() == kAnyOf)
    {
        vector<Node*>* raw_children  = raw_schema_node->getChildren();

        vector<Node*>* rsus_children = rsus_node->getChildren();
        for(auto raw_child : *raw_children)
        {
            bool found = false;

            for(auto rsus_child : *rsus_children)
            {
                if(TO_SCHEMA_NODE(raw_child)->getType() == TO_SCHEMA_NODE(rsus_child)->getType())
                {
                    constructRSUSRecursive(TO_SCHEMA_NODE(raw_child), occur_count, TO_SCHEMA_NODE(rsus_child));
                    found = true;
                    break;
                }
            }
            if(!found)
            {
                SchemaNode* new_rg_child = new SchemaNode(TO_SCHEMA_NODE(raw_child)->getType());
                rsus_node->addChild(new_rg_child);
                constructRSUSRecursive(TO_SCHEMA_NODE(raw_child), occur_count, new_rg_child);
                rsus_children = rsus_node->getChildren();
            }
        }

        rsus_node->aggregateChildrenCount();
        return rsus_node;
    }

    // Case 3. raw_schema_node != anyOf, rsus_node == anyOf
    else if(raw_schema_node->getType() != kAnyOf && rsus_node->getType() == kAnyOf)
    {
        vector<Node*>* rsus_children = rsus_node->getChildren();
        bool found = false;
        for(auto child : *rsus_children)
        {
            if(TO_SCHEMA_NODE(child)->getType() == raw_schema_node->getType())
            {   
                // Case 3.1. Found a child of rsus_node with the same type as raw_schema_node 
                constructRSUSRecursive(raw_schema_node, occur_count, TO_SCHEMA_NODE(child));
                return rsus_node;
            }
        }

        // Case 3.2. Did not find a child of rsus_node with the same type as raw_schema_node
            // Thus we add a child to rsus_node
        SchemaNode* new_rg_child = new SchemaNode(raw_schema_node->getType());
        rsus_node->addChild(new_rg_child);
        constructRSUSRecursive(raw_schema_node, occur_count, new_rg_child);

        rsus_node->aggregateChildrenCount();
        return rsus_node;
    }

    // Case 4. raw_schema_node != anyOf, rsus_node != anyOf
    else
    {
        // Case 4.1 raw_schema_node->getType() == rsus_node->getType()
        if(raw_schema_node->getType() == rsus_node->getType())
        {
            rsus_node->incrementCountWithValue(occur_count);

            // Case 4.1.1. Object schema
            if(raw_schema_node->getType() == kHomObj)
            {
                // 1. Get the children of raw_schema_node
                vector<strInt>& raw_labels = raw_schema_node->getStringLabels();
                vector<Node*>* raw_children = raw_schema_node->getChildren();

                // 2. Get the children of rsus_node
                vector<strInt> rsus_labels = rsus_node->getStringLabels();
                vector<Node*>* rsus_children = rsus_node->getChildren();

                // 3. For each child in children, check if it is already in rg_children
                for(int i = 0; i < raw_labels.size(); i++)
                {
                    SchemaNode* returned_node;
                    int found_index = naiveSearch(rsus_labels, raw_labels[i]);

                    
                    if(found_index == -1)
                    {
                        SchemaNode* new_rsus_child = new SchemaNode(TO_SCHEMA_NODE(raw_children->at(i))->getType());

                        rsus_node->addChild(raw_labels[i], new_rsus_child);
                        returned_node = constructRSUSRecursive(TO_SCHEMA_NODE(raw_children->at(i)), occur_count, new_rsus_child);
                    }
                    else
                    {
                        returned_node = constructRSUSRecursive(TO_SCHEMA_NODE(raw_children->at(i)), occur_count, TO_SCHEMA_NODE(rsus_children->at(found_index)));
                        if(returned_node != TO_SCHEMA_NODE(rsus_children->at(found_index)))
                        { rsus_node->replaceChildWithLabel(raw_labels[i], returned_node); }
                    }
                    rsus_labels = rsus_node->getStringLabels();
                    rsus_children = rsus_node->getChildren();
                }
                return rsus_node;
            }
            // Case 4.1.2. Array schema
            else if(raw_schema_node->getType() == kHetArr)
            {
                // 1. Get the children of instance_node
                SchemaNode* raw_child = raw_schema_node->getKleeneChild();
                if(raw_child == nullptr) return rsus_node;

                // 2. Get the child of rsus_node
                SchemaNode* rsus_child = rsus_node->getKleeneChild();

                // 3. Check if rsus_child in nullptr to evade segmentation fault
                if(rsus_child == nullptr && raw_child != nullptr)
                {
                    SchemaNode* new_node = new SchemaNode(TO_SCHEMA_NODE(raw_child)->getType());
                    rsus_node->setKleeneChild(new_node); 
                }

                // 4. Recursively call constructRSUSRecursive
                SchemaNode* returned_node = constructRSUSRecursive(TO_SCHEMA_NODE(raw_child), occur_count, TO_SCHEMA_NODE(rsus_node->getKleeneChild())); 
                if(returned_node != rsus_node->getKleeneChild())
                { rsus_node->setKleeneChild(returned_node); }

                return rsus_node;
            }
            // Case 4.1.3. Other schemas
            else if(
                raw_schema_node->getType() == kNum || 
                raw_schema_node->getType() == kStr || 
                raw_schema_node->getType() == kBool || 
                raw_schema_node->getType() == kNull
            )
            { return rsus_node; }
            else 
            { throw IllegalBehaviorError("constructRSUSRecursive: Case 3: Unanticipated InstanceType"); }
        }

        // Case 4.2. raw_schema_node->getType() != rsus_node->getType()
            // add anyOf node
        else if(raw_schema_node->getType() != rsus_node->getType())
        {
            SchemaNode* anyof_node = new SchemaNode(kAnyOf);
            SchemaNode* new_rg_child = new SchemaNode(raw_schema_node->getType());
            anyof_node->addChild(rsus_node);
            anyof_node->addChild(new_rg_child);
            constructRSUSRecursive(raw_schema_node, occur_count, new_rg_child);

            anyof_node->aggregateChildrenCount();
            return anyof_node;
        }

        else
        { throw IllegalBehaviorError("constructRSUSRecursive: Unanticipated case for instance_node and rsus_node"); }
    }
        
}


void RSUSConstructor::boldifyLabelsRecursive(SchemaNode* schema_node)
{
    if(schema_node->getType() == kHomObj)
    {
        vector<strInt>& labels = schema_node->getStringLabels();
        vector<Node*>* children = schema_node->getChildren();

        for(int i = 0; i < labels.size(); i++)
        {
            if(TO_SCHEMA_NODE(children->at(i))->getCount() == schema_node->getCount())
            { schema_node->boldifyLabel(labels[i]); }
        }
        for(auto child : *(schema_node->getChildren()))
        { boldifyLabelsRecursive(TO_SCHEMA_NODE(child)); }

        // for(auto& label : schema_node->getStringLabels())
        // { 
        //     if(schema_node->getCount() == TO_SCHEMA_NODE(schema_node->getChildWithLabel(label))->getCount())
        //     { schema_node->boldifyLabel(label); }
        // }
    }
    else if(schema_node->getType() == kHetArr)
    {
        if(schema_node->getKleeneChild() != nullptr)
        { boldifyLabelsRecursive(TO_SCHEMA_NODE(schema_node->getKleeneChild())); }
    }
    else if(schema_node->getType() == kAnyOf)
    {
        for(auto child : *(schema_node->getChildren()))
        { boldifyLabelsRecursive(TO_SCHEMA_NODE(child)); }
    }
    else if(schema_node->getType() == kNum || schema_node->getType() == kStr || schema_node->getType() == kBool || schema_node->getType() == kNull)
    {
        return;
    }
    else
    {
        throw IllegalBehaviorError("boldifyLabelsRecursive: Unanticipated SchemaType");
    }
}

