#include "RawSchemaConstructor.hpp"


void RawSchemaConstructor::constructRawSchemas()
{
    int barWidth = 70;
    float progress = 0 / (float)instance_forest_->size();
    int done_count = 0;


    for(auto instance_node : *instance_forest_)
    { 
        #if SHOWPROGRESSBAR
            progress = done_count / (float)instance_forest_->size();
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

        raw_schemas_->push_back(constructSingleRawSchemaRecursive(instance_node));

        done_count++;
    }

    cout << endl;
}

SchemaNode* RawSchemaConstructor::constructSingleRawSchemaRecursive(InstanceNode* instance_node)
{
    if(instance_node->getType() == kObject)
    {
        SchemaNode* schema_node = new SchemaNode(kHomObj);

        vector<strInt>& str_labels = instance_node->getStringLabels();
        vector<Node*>* children = instance_node->getChildren();

        for(int i = 0; i < str_labels.size(); i++)
        {
            SchemaNode* child_schema_node = constructSingleRawSchemaRecursive(TO_INSTANCE_NODE(children->at(i)));
            schema_node->addChild(str_labels[i], child_schema_node);
        }
        return schema_node;
    }
    else if(instance_node->getType() == kArray)
    {
        // 1. Initiate a new hetArr Schema
        SchemaNode* schema_node = new SchemaNode(kHetArr);

        // 2. Get the children of the instance node
        vector<Node*>* children = instance_node->getChildren();

        // 3. Find the raw schemas for each child
        SchemaForest child_schemas;
        for(int i = 0; i < children->size(); i++)
        {
            SchemaNode* child_schema_node = constructSingleRawSchemaRecursive(TO_INSTANCE_NODE(children->at(i)));
            child_schemas.push_back(child_schema_node);
        }

        // 4. Leave on the unique ones
        SchemaForest unique_child_schemas;
        for(auto child_schema_node : child_schemas)
        {
            bool is_unique = true;
            for(auto unique_child_schema_node : unique_child_schemas)
            {
                if(isEqual(child_schema_node, unique_child_schema_node))
                {
                    is_unique = false;
                    break;
                }
            }
            if(is_unique)
            { unique_child_schemas.push_back(child_schema_node); }
        }

        // 5. Add the unique children to the schema node
        
        if(unique_child_schemas.size() == 0)
        {
            schema_node->setKleeneChild(nullptr);
        }
        else if(unique_child_schemas.size() == 1)
        {
            schema_node->setKleeneChild(unique_child_schemas[0]);
        }
        else
        {
            SchemaNode* anyof_node = new SchemaNode(kAnyOf);
            for(auto unique_child_schema_node : unique_child_schemas)
            { anyof_node->addChild(unique_child_schema_node); }

            anyof_node->sortChildren();

            schema_node->setKleeneChild(anyof_node);
        }
        return schema_node;
    }
    else if(instance_node->getType() == kNumber)
    {
        SchemaNode* schema_node = new SchemaNode(kNum);
        return schema_node;
    }
    else if(instance_node->getType() == kString)
    {
        SchemaNode* schema_node = new SchemaNode(kStr);
        return schema_node;
    }
    else if(instance_node->getType() == kBoolean)
    {
        SchemaNode* schema_node = new SchemaNode(kBool);
        return schema_node;
    }
    else if(instance_node->getType() == kNull_)
    {
        SchemaNode* schema_node = new SchemaNode(kNull);
        return schema_node;
    }
    else
    {
        cout << "Error: Invalid instance node type" << endl;
        return nullptr;
    }
    cout << "Error: Should not reach here" << endl;
    return nullptr;
}