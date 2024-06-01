#include "Instance.hpp"

void InstanceNode::visualizeInstanceTree(int depth)
{
    // cout << depth << endl;
    cout << instanceTypeToString(type_) << endl;

    if(type_ == kObject)
    {
        for(int child_idx = 0; child_idx < str_labels_.size(); child_idx++)
        {
            for(int i = 0; i < depth; i++)
            { cout << "   "; }
            cout << "┖{ " << str_labels_[child_idx] << " }  ";

            // Node* child_node = children_[binarySearch(str_labels_, str_labels_[child_idx])];
            if(children_->at(child_idx) == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_INSTANCE_NODE(children_->at(child_idx))->visualizeInstanceTree(depth + 1);
        }
    }
    
    if(type_ == kArray)
    {
        for(int child_idx = 0; child_idx < children_->size(); child_idx++)
        {
            for(int i = 0; i < depth; i++)
            { cout << "   ";}
            cout << "┖[ " << child_idx << " ]  ";
            if(children_->at(child_idx) == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_INSTANCE_NODE(children_->at(child_idx))->visualizeInstanceTree(depth + 1);
        }
    }


    return;
}