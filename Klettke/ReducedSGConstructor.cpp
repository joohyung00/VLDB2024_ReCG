#include "ReducedSGConstructor.hpp"


void ReducedSGConstructor::constructReducedSG()
{
    // 1. Starting part
    InstanceNode* first_root_node = *(instance_forest_.begin());
    reduced_graph_ = new SchemaNode(instanceTypeToSchemaType(first_root_node->getType()));

    bool first = true;

    int count = 0;
    for(auto instance_node : instance_forest_)
    { 
        // cout << count++ << " ";
        // instance_node->visualizeInstanceTree(0);
        reduced_graph_ = constructReducedSGRecursive(instance_node, reduced_graph_); 
    }
    cout << endl;
    cout << "REDUCED SG COUNT: " << count << endl;

    boldifyLabelsRecursive(reduced_graph_);
}

SchemaNode* ReducedSGConstructor::constructReducedSGRecursive(InstanceNode* instance_node, SchemaNode* rg_node)
{
    // Check if rg_node's type is anyOf -> have to navigate
    if(rg_node->getType() == kAnyOf)
    {
        vector<Node*>& rg_children = rg_node->getChildren();
        bool found = false;
        for(auto child : rg_children)
        {
            if(TO_SCHEMA_NODE(child)->getType() == instanceTypeToSchemaType(instance_node->getType()))
            {
                constructReducedSGRecursive(instance_node, TO_SCHEMA_NODE(child));
                found = true;
                break;
            }
        }
        if(!found)
        {
            SchemaNode* new_rg_child = new SchemaNode(instanceTypeToSchemaType(instance_node->getType()));
            rg_node->addChild(new_rg_child);
            constructReducedSGRecursive(instance_node, new_rg_child);
        }
        
        return rg_node;
    }

    // Check if rg_node's type is not anyOf but different with instanceTypeToSchemaType(instance_node->getType))
        // Then we have to add anyOf node in between
    else if(rg_node->getType() != instanceTypeToSchemaType(instance_node->getType()))
    {
        SchemaNode* anyof_node = new SchemaNode(kAnyOf);
        SchemaNode* new_rg_child = new SchemaNode(instanceTypeToSchemaType(instance_node->getType()));
        // rg_node->addChild(anyof_node);
        anyof_node->addChild(rg_node);
        anyof_node->addChild(new_rg_child);
        constructReducedSGRecursive(instance_node, new_rg_child);

        return anyof_node;
    }

    // Check if rg_node's type is the same with instanceTypeToSchemaType(instance_node->getType))
    else if(rg_node->getType() == instanceTypeToSchemaType(instance_node->getType()))
    {
        rg_node->incrementCount();

        if(instance_node->getType() == kObject)
        {
            // 1. Get the children of instance_node
            vector<strInt>& instance_labels = instance_node->getStringLabels();
            vector<Node*>& instance_children = instance_node->getChildren();

            // 2. Get the children of rg_node
            vector<strInt>& rg_labels = rg_node->getStringLabels();
            vector<Node*>& rg_children = rg_node->getChildren();

            // 3. For each child in children, check if it is already in rg_children
            int i = 0;
            for(auto label : instance_labels)
            {
                SchemaNode* returned_node;
                bool found = false;
                int found_index = naiveSearch(rg_labels, label);

                if(found_index == -1)
                {
                    SchemaNode* new_rg_child = new SchemaNode(instanceTypeToSchemaType(TO_INSTANCE_NODE(instance_children[i])->getType()));
                    rg_node->addChild(label, new_rg_child);
                    returned_node = constructReducedSGRecursive(TO_INSTANCE_NODE(instance_children[i]), new_rg_child);
                }
                else
                {
                    returned_node = constructReducedSGRecursive(TO_INSTANCE_NODE(instance_children[i]), TO_SCHEMA_NODE(rg_children[found_index]));
                    if(returned_node != TO_SCHEMA_NODE(rg_children[found_index]))
                    { rg_node->replaceChildWithLabel(label, returned_node); }
                }
                i++;
            }
            return rg_node;
        }
        else if(instance_node->getType() == kArray)
        {
            // 1. Get the children of instance_node
            vector<Node*>& instance_children = instance_node->getChildren();

            // 2. Get the children of rg_node
            SchemaNode* rg_child = rg_node->getKleeneChild();

            // 3. For each child in children, check if it is already in rg_children
            if(rg_child == nullptr && instance_children.size() > 0)
            {
                SchemaNode* new_node = new SchemaNode(instanceTypeToSchemaType(TO_INSTANCE_NODE(instance_children[0])->getType()));
                rg_node->setKleeneChild(new_node); 
            }

            SchemaNode* returned_node;
            for(auto child : instance_children)
            { 
                returned_node = constructReducedSGRecursive(TO_INSTANCE_NODE(child), rg_node->getKleeneChild()); 
                
                if(returned_node != rg_node->getKleeneChild())
                { rg_node->setKleeneChild(returned_node); }
            }

            return rg_node;
        }
        else if(instance_node->getType() == kNumber || instance_node->getType() == kString || instance_node->getType() == kBoolean || instance_node->getType() == kNull_) return rg_node;
        else throw IllegalBehaviorError("constructReducedSGRecursive: Case 3: Unanticipated InstanceType");
    }

    else
    {
        throw IllegalBehaviorError("constructReducedSGRecursive: Unanticipated case for instance_node and rg_node");
    }
}


void ReducedSGConstructor::boldifyLabelsRecursive(SchemaNode* schema_node)
{
    if(schema_node->getType() == kHomObj)
    {
        for(auto& label : schema_node->getStringLabels())
        { 
            if(schema_node->getCount() == TO_SCHEMA_NODE(schema_node->getChildWithLabel(label))->getCount())
            { schema_node->boldifyLabel(label); }
        }
        for(auto child : schema_node->getChildren())
        { boldifyLabelsRecursive(TO_SCHEMA_NODE(child)); }
    }
    else if(schema_node->getType() == kHetArr)
    {
        if(schema_node->getKleeneChild() != nullptr)
        { boldifyLabelsRecursive(TO_SCHEMA_NODE(schema_node->getKleeneChild())); }
    }
    else if(schema_node->getType() == kAnyOf)
    {
        for(auto child : schema_node->getChildren())
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