#include "Schema.hpp"

void SchemaNode::visualizeSchemaTree(int depth)
{
    // cout << depth << endl;
    cout << schemaTypeToString(type_) << endl;

    if(type_ == kHomObj)
    {
        for(int child_idx = 0; child_idx < str_labels_.size(); child_idx++)
        {
            for(int i = 0; i < depth; i++)
            { cout << "   "; }
            cout << "┖{ " << str_labels_[child_idx] << " }  ";

            if(children_[child_idx] == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_SCHEMA_NODE(children_[child_idx])->visualizeSchemaTree(depth + 1);
        }
    }
    
    if(type_ == kHetArr)
    {
        for(int i = 0; i < depth; i++)
        { cout << "   ";}
        cout << "┖[ " << "*" << " ]  ";

        Node* child_node = kleene_child_;
        if(child_node == nullptr)
        { cout << "nullptr" << endl; }
        else TO_SCHEMA_NODE(child_node)->visualizeSchemaTree(depth + 1);
    }


    if(type_ == kAnyOf)
    {
        for(int child_idx = 0; child_idx < children_.size(); child_idx++)
        {
            for(int i = 0; i < depth; i++)
            { cout << "   ";}
            cout << "┖ ";
            if(children_[child_idx] == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_SCHEMA_NODE(children_[child_idx])->visualizeSchemaTree(depth + 1);
        }
    
    }

    return;
}