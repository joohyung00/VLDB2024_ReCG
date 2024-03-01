#ifndef INSTANCE
#define INSTANCE

#include <string>
#include <vector>
#include <unordered_set>

// Instance
#include "Schema.hpp"
#include "EdgeLabelledTree.hpp"
#include "utils.hpp"

#define TO_INSTANCE_NODE(X) static_cast<InstanceNode*>(X)

class InstanceNode : public Node
{
    private:
        // Node Type
        InstanceType        type_;
        int                 depth_;

        // 
        vector<int>         label_to_threshold_;
        int                 current_threshold_;

        // Derived Schema Management 
        Node*               derived_schema_;

        // Does not change
        roaring_bitmap_t*   str_labels_bitmap_;

        // Derived Schemas candidates
        unordered_map<stateId, vectorIdx> state_to_index_;
        vector<Node*>       derived_schema_candidates_;

        

        // CD-instance-related
            // Object
        roaring_bitmap_t*   unkleened_labels_;
        roaring_bitmap_t*   unkleened_labels_schema_hash_;
        roaring_bitmap_t*   kleened_labels_;
        roaring_bitmap_t*   kleened_schema_ids_;
        // unordered_map<nodeId, Count> schema_id_count_;

        roaring_bitmap_t*   children_schema_ids_;

    public:

        InstanceNode(InstanceType type, int depth): type_(type), depth_(depth)
        {
            derived_schema_ = nullptr;

            current_threshold_ =    10;

            // Schema candidates-related
            state_to_index_ = unordered_map<stateId, vectorIdx>();
            derived_schema_candidates_ = vector<Node*>();

            // CD-instance-related
            if(type_ == kObject)
            {
                str_labels_bitmap_              = roaring_bitmap_create();
                
                unkleened_labels_               = roaring_bitmap_create();
                unkleened_labels_schema_hash_   = roaring_bitmap_create();

                kleened_labels_                 = roaring_bitmap_create();
                kleened_schema_ids_             = roaring_bitmap_create();
                children_schema_ids_            = roaring_bitmap_create();
            }
            else if(type_ == kArray)
            {
                str_labels_bitmap_              = nullptr;
                
                unkleened_labels_               = nullptr;
                unkleened_labels_schema_hash_   = nullptr;

                kleened_labels_                 = nullptr;
                kleened_schema_ids_             = roaring_bitmap_create();
                children_schema_ids_            = roaring_bitmap_create();
            }
        }

        void addChild(const strInt edge_name, Node *child)
        {
            str_labels_.push_back(edge_name);
            children_.push_back(child);
            roaring_bitmap_add(str_labels_bitmap_, edge_name);

            child->setParent(this);
        }

        void addChild(Node *child)
        {
            int_children_num_++;
            children_.push_back(child);

            child->setParent(this);
        }

        const InstanceType getType()
        { return type_; }

        const int getDepth()
        { return depth_; }

        void setDerivedSchema(Node* derived_schema)
        { derived_schema_ = derived_schema; }

        Node* getDerivedSchema()
        { return derived_schema_; }

        void setCurrentThreshold(int current_threshold)
        { current_threshold_ = current_threshold; }

        int getCurrentThreshold()
        { return current_threshold_; }

        vector<int>& getLabelToThreshold()
        { return label_to_threshold_; }

        // Derived-schema-related

        void setDerivedSchemaForState(stateId state_id, Node* derived_schema)
        {
            derived_schema_candidates_.push_back(derived_schema);
            state_to_index_.insert( {state_id, derived_schema_candidates_.size() - 1} );
        }

        void setNodeAsState(stateId state_id)
        {
            derived_schema_ = derived_schema_candidates_[state_to_index_[state_id]];
        }

        // BitmapGetSet

        void generalizeWithThreshold(int t);

        void updateLabelSchemaHash();

        void generalizeOutlier();

        void updateBitmaps();

        roaring_bitmap_t* getLabelBitmap()
        { return str_labels_bitmap_; }

        roaring_bitmap_t* getUnkleenedLabelBitmap()
        { return unkleened_labels_; }

        roaring_bitmap_t* getLabelSchemaBitmap()
        { return unkleened_labels_schema_hash_; }

        roaring_bitmap_t* getKleenedLabels()
        { return kleened_labels_; }

        roaring_bitmap_t* getKleenedSchemas()
        { return kleened_schema_ids_; }

        roaring_bitmap_t* getChildrenSchemasBitmap()
        { return children_schema_ids_; }
};

using InstanceForest = vector<InstanceNode*>;
using InstanceSet    = unordered_set<InstanceNode*>;










class GroupedInstances
{
	private:
		vector<InstanceForest> grouped_instances_;
	
	public:

		GroupedInstances()
		{
			grouped_instances_ = vector<InstanceForest>();
            grouped_instances_.push_back(InstanceForest());     // Object
            grouped_instances_.push_back(InstanceForest());     // Array
            grouped_instances_.push_back(InstanceForest());     // Number
            grouped_instances_.push_back(InstanceForest());     // String
            grouped_instances_.push_back(InstanceForest());     // Boolean
            grouped_instances_.push_back(InstanceForest());     // Null
		}

		~GroupedInstances(){}

		void addInstance(InstanceNode* instance_node)
        { grouped_instances_[instance_node->getType()].push_back(instance_node); }

		InstanceForest& getInstanceForestByType(InstanceType type)
        { return grouped_instances_[type]; }
};










class DepthToGroupedInstances
{
	private:
		int max_depth_;
		vector<GroupedInstances> depth_to_grouped_instances_;

	public:
		DepthToGroupedInstances()
		{
			depth_to_grouped_instances_ = vector<GroupedInstances>();
		}

		~DepthToGroupedInstances(){}

		void addInstance(InstanceNode* instance_node)
        {
            int instance_depth = instance_node->getDepth();
            if(instance_depth + 1 > depth_to_grouped_instances_.size())
            { 
                depth_to_grouped_instances_.push_back(GroupedInstances()); 

                #if VERBOSE
                    if(instance_depth + 1 > depth_to_grouped_instances_.size())
                    { InitializerDepthError(); }
                #endif
            }
            depth_to_grouped_instances_[instance_depth].addInstance(instance_node);


        }

		GroupedInstances& getGroupedInstancesByDepth(int depth)
		{ return depth_to_grouped_instances_[depth]; }

        GroupedInstances* getGroupedInstancesPtrByDepth(int depth)
        { return &(depth_to_grouped_instances_[depth]); }

        int size()
        { return depth_to_grouped_instances_.size(); }

        void printData();
};

#endif