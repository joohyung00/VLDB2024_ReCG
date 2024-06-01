#ifndef SCHEMA
#define SCHEMA

#include "EdgeLabelledTree.hpp"

#define TO_SCHEMA_NODE(X) static_cast<SchemaNode*>(X)


class SchemaNode;
using SchemaForest = vector<SchemaNode*>;

bool isEqual(SchemaNode* a, SchemaNode* b);
bool compareSchemas(SchemaNode* a, SchemaNode* b);
bool compareSchemaAsNodes(Node* a, Node* b);
EqualityOp triCompareSchemas(SchemaNode* a, SchemaNode* b);


class SchemaNode : public Node
{
    private:
        static nodeId       unique_schema_id_;

        nodeId              id_;

        SchemaType          type_;
        
        Count               count_;

        vector<strInt>      bold_labels_;

        SchemaNode*         kleene_child_;

    public:

        SchemaNode(SchemaType type)
        :type_(type)
        {
            id_ = SchemaNode::unique_schema_id_;
            SchemaNode::unique_schema_id_++;
            kleene_child_ = nullptr;
            count_ = 0;
        }

        SchemaNode(const SchemaNode& schema_node)
        {
        }

        nodeId getId()
        { return id_; }

        const SchemaType getType() const
        { return type_; }

        void setBoldLabels(const vector<strInt>& bold_labels) 
        { bold_labels_ = bold_labels; }

        void boldifyLabel(const strInt bold_label)
        { bold_labels_.push_back(bold_label); }

        vector<strInt>& getBoldLabels() 
        { return bold_labels_; }

        void setKleeneChild(SchemaNode* node)
        { kleene_child_ = node; }

        SchemaNode* getKleeneChild()
        { return kleene_child_; }

        void sortStrChildren()
        {
            Node::sortStrChildren();
            sort( bold_labels_.begin(), bold_labels_.end() );
        }

        void sortChildren()
        {
            sort( children_->begin(), children_->end() , compareSchemaAsNodes );
        }

        void incrementCount()
        { count_++; }

        void incrementCountWithValue(Count count_to_add)
        { count_ += count_to_add; }

        void aggregateChildrenCount()
        {
            count_ = 0;
            for(auto child : *children_)
            { count_ += TO_SCHEMA_NODE(child)->getCount(); }
        }

        Count getCount()
        { return count_; } 

        void visualizeSchemaTree(int depth);

        void printChildrenIds();
};




#endif