#ifndef INSTANCE
#define INSTANCE

// Instance
#include "Schema.hpp"

#define TO_INSTANCE_NODE(X) static_cast<InstanceNode*>(X)

class InstanceNode : public Node
{
    private:
        // Node Type
        InstanceType        type_;
        int                 depth_;

    public:

        InstanceNode(InstanceType type, int depth): type_(type), depth_(depth)
        {}

        void addChild(const strInt edge_name, Node *child)
        {
            str_labels_.push_back(edge_name);
            children_->push_back(child);
            child->setParent(this);
        }

        void addChild(Node *child)
        {
            int_children_num_++;
            children_->push_back(child);
            child->setParent(this);
        }

        const InstanceType getType()
        { return type_; }

        const int getDepth()
        { return depth_; }

        void visualizeInstanceTree(int depth);
};

using InstanceForest = vector<InstanceNode*>;
using InstanceSet    = unordered_set<InstanceNode*>;





class InstanceForestManager
{
	private:
		InstanceForest instance_forest_;
	
	public:

		InstanceForestManager()
		{ instance_forest_ = InstanceForest(); }

		~InstanceForestManager(){}

		void addInstance(InstanceNode* instance_node)
        { instance_forest_.push_back(instance_node); }

		InstanceForest& getInstanceForest()
        { return instance_forest_; }
};






#endif