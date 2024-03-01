#include "Instance.hpp"

void DepthToGroupedInstances::printData()
{
    int depth = 0;
    for(auto& grouped_instances : depth_to_grouped_instances_)
    {
        cout << "[Depth "       << depth << "]" << endl;
        cout << "| Object #: "  << grouped_instances.getInstanceForestByType(kObject).size()    << endl;
        cout << "| Array #: "   << grouped_instances.getInstanceForestByType(kArray).size()     << endl;
        cout << "| Number #: "  << grouped_instances.getInstanceForestByType(kNumber).size()    << endl;
        cout << "| String #: "  << grouped_instances.getInstanceForestByType(kString).size()    << endl;
        cout << "| Bool #: "    << grouped_instances.getInstanceForestByType(kBoolean).size()   << endl;
        cout << "| Null #: "    << grouped_instances.getInstanceForestByType(kNull_).size()     << endl;
        cout << endl;

        depth++;
    }
}


void InstanceNode::updateBitmaps()
{
    if(type_ == kObject)
    {
        roaring_bitmap_clear(unkleened_labels_);
        roaring_bitmap_clear(unkleened_labels_schema_hash_);
        roaring_bitmap_clear(kleened_labels_);
        roaring_bitmap_clear(kleened_schema_ids_);
        roaring_bitmap_clear(children_schema_ids_);
        // schema_id_count_.clear();
        
        vector<strInt>&    string_labels   = getStringLabels();
        vector<Node*>&     children        = getChildren();

        for(int i = 0; i < string_labels.size(); i++)
        {
            strInt a = string_labels[i];
            nodeId b = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema())->getId();
            // cout << "B: " << b << endl;

            if(0 < label_to_threshold_[i] && label_to_threshold_[i] <= current_threshold_)
            {
                roaring_bitmap_add(kleened_labels_, string_labels[i]);
                roaring_bitmap_add(kleened_schema_ids_, b);
                // auto it = schema_id_count_.find(b);
                // if(it == key_count.end())
                // { schema_id_count_.insert( {b, 1} ); }
                // else (it->second)++;
            }
            else
            {
                roaring_bitmap_add(unkleened_labels_, a);
                roaring_bitmap_add(unkleened_labels_schema_hash_, a ^ b);
            }
            //
            roaring_bitmap_add(children_schema_ids_, b);
            //
        }
    }
    else if(type_ == kArray)
    {
        roaring_bitmap_clear(kleened_schema_ids_);
        // schema_id_count_.clear();

        vector<Node*>&      children        = getChildren();

        for(int i = 0; i < children.size(); i++)
        { 
            nodeId b = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema())->getId();

            roaring_bitmap_add(kleened_schema_ids_, b); 
            // auto it = schema_id_count_.find(b);
            // if(it == key_count.end())
            // { schema_id_count_.insert( {b, 1} ); }
            // else (it->second)++;
        }
    }
}


void InstanceNode::generalizeOutlier()
{
    roaring_bitmap_clear(unkleened_labels_);
    roaring_bitmap_clear(unkleened_labels_schema_hash_);

    vector<strInt>&    string_labels   = getStringLabels();
    vector<Node*>&      children        = getChildren();
    // vector<int>   label_to_threshold_;

    for(int i = 0; i < string_labels.size(); i++)
    {
        roaring_bitmap_add(kleened_labels_, string_labels[i]);
        roaring_bitmap_add(kleened_schema_ids_, TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema())->getId());
    }

    // roaring_bitmap_printf(kleened_schema_ids_);
    // cout << '\t';
}


void InstanceNode::generalizeWithThreshold(int t)
{
    current_threshold_ = t;
    vector<strInt>&    string_labels   = getStringLabels();
    vector<Node*>&      children        = getChildren();

    for(int i = 0; i < label_to_threshold_.size(); i++)
    {
        if(label_to_threshold_[i] == t)
        {
            roaring_bitmap_remove(unkleened_labels_, string_labels[i]);
            strInt a = string_labels[i];
            nodeId b = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema())->getId();
            roaring_bitmap_remove(unkleened_labels_schema_hash_, a ^ b);

            roaring_bitmap_add(kleened_labels_, string_labels[i]);
            roaring_bitmap_add(kleened_schema_ids_, TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema())->getId());
        }
    }
}





void InstanceNode::updateLabelSchemaHash()
{
    roaring_bitmap_clear(unkleened_labels_schema_hash_);
    
    vector<strInt>&    string_labels   = getStringLabels();
    vector<Node*>&      children        = getChildren();

    for(int i = 0; i < string_labels.size(); i++)
    {
        strInt a = string_labels[i];
        nodeId b = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema())->getId();

        roaring_bitmap_add(unkleened_labels_schema_hash_, a ^ b);
    }
}