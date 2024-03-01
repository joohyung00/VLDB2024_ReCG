#ifndef SCHEMA
#define SCHEMA

#include "EdgeLabelledTree.hpp"
#include "utils.hpp"

#define TO_SCHEMA_NODE(X) static_cast<SchemaNode*>(X)

class SchemaNode : public Node
{
    private:
        static nodeId       unique_schema_id_;

        nodeId              id_;

        SchemaType          type_;
		InstanceType        generic_type_;

        MDLCost             src_;
        MDLCost             drc_;

        vector<strInt>      bold_labels_;

        SchemaNode*         kleene_child_;

    public:

        SchemaNode(SchemaType type)
        :type_(type)
        {
            id_ = SchemaNode::unique_schema_id_;
            // std::cout << "id_ = " << id_ << std::endl;
            SchemaNode::unique_schema_id_++;
            kleene_child_ = nullptr;
            src_ = 0;
            drc_ = 0;
            switch(type)
            {
                case kHomObj:
                case kHetObj:
                    generic_type_ = kObject; break;
                case kHomArr:
                case kHetArr:
                    generic_type_ = kArray; break;
                case kNum:
                    generic_type_ = kNumber; break;
                case kStr:
                    generic_type_ = kString; break;
                case kBool:
                    generic_type_ = kBoolean; break;
                case kNull:
                    generic_type_ = kNull_; break;
                default:
                    break;
            }
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

        void setSRC(MDLCost schema_cost)
        { src_ = schema_cost; }

        void addToSRC(MDLCost schema_cost)
        { src_ += schema_cost; }

        MDLCost getSRC()
        { return src_; }

        void addToDRC(MDLCost data_cost)
        { drc_ += data_cost; }

        void setDRC(MDLCost data_cost)
        { drc_ = data_cost; }

        MDLCost getDRC()
        { return drc_; }

        void sortStrChildren()
        {
            Node::sortStrChildren();
            sort( bold_labels_.begin(), bold_labels_.end() );
        }

        void sortChildren()
        {
            sort( children_.begin(), children_.end() );
        }

        void aggregateAnyOfChildrenCost();
};

using SchemaVec = vector<SchemaNode*>;
using SchemaSet = unordered_set<SchemaNode*>;

bool isEqual(const SchemaSet* a, const SchemaSet* b);
bool isSubset(const SchemaSet* a, const SchemaSet* b);
    // Returns `true` if `a` is a subset of `b`.
bool isSubset(const SchemaSet& a, const SchemaSet& b);
    // Returns `true` if `a` is a subset of `b`.
bool hasConjunction(SchemaSet* a, SchemaSet* b);
Count unionSize(const SchemaSet* a, const SchemaSet* b);
Count intersectionSize(const SchemaSet* a, const SchemaSet* b);

#endif