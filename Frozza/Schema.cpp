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

            if(children_->at(child_idx) == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_SCHEMA_NODE(children_->at(child_idx))->visualizeSchemaTree(depth + 1);
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
        for(int child_idx = 0; child_idx < children_->size(); child_idx++)
        {
            for(int i = 0; i < depth; i++)
            { cout << "   ";}
            cout << "┖ ";
            if(children_->at(child_idx) == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_SCHEMA_NODE(children_->at(child_idx))->visualizeSchemaTree(depth + 1);
        }
    
    }

    return;
}



bool isEqual(SchemaNode* a, SchemaNode* b)
{
    if(a->getType() != b->getType())
    { return false; }

    if(a->getType() == kHomObj)
    {
        if(a->getStringLabels().size() != b->getStringLabels().size())
        { return false; }

        for(int i = 0; i < a->getStringLabels().size(); i++)
        {
            if(a->getStringLabels()[i] != b->getStringLabels()[i])
            { return false; }
            if(!isEqual(TO_SCHEMA_NODE(a->getChildren()->at(i)), TO_SCHEMA_NODE(b->getChildren()->at(i))))
            { return false; }
        }
    }
    else if(a->getType() == kHetArr)
    {
        if(a->getKleeneChild() == nullptr && b->getKleeneChild() != nullptr)
        { return false; }
        else if(a->getKleeneChild() != nullptr && b->getKleeneChild() == nullptr)
        { return false; }
        else if(a->getKleeneChild() == nullptr && b->getKleeneChild() == nullptr)
        { return true; }
        if(!isEqual(TO_SCHEMA_NODE(a->getKleeneChild()), TO_SCHEMA_NODE(b->getKleeneChild())))
        { return false; }
    }
    else if(a->getType() == kAnyOf)
    {
        if(a->getChildren()->size() != b->getChildren()->size())
        { return false; }

        for(int i = 0; i < a->getChildren()->size(); i++)
        {
            if(!isEqual(TO_SCHEMA_NODE(a->getChildren()->at(i)), TO_SCHEMA_NODE(b->getChildren()->at(i))))
            { return false; }
        }

        return true;
    }
    else return true;

    return true;
}



bool compareSchemaAsNodes(Node* a, Node* b)
{
    return compareSchemas(TO_SCHEMA_NODE(a), TO_SCHEMA_NODE(b));
}

bool compareSchemas(SchemaNode* a, SchemaNode* b)
{
    if(triCompareSchemas(a, b) == kALessThanB) return true;
    else return false;
}



EqualityOp triCompareSchemas(SchemaNode* a, SchemaNode* b)
{
    if(a->getType() != b->getType())
    {
        if(schemaTypeToInt(a->getType()) < schemaTypeToInt(b->getType()))
        { return kALessThanB; }
        else return kAGreaterThanB;
    }

    if(a->getType() == kHomObj)
    {
        if(a->getStringLabels().size() < b->getStringLabels().size())
        { return kALessThanB; }
        else if(a->getStringLabels().size() > b->getStringLabels().size())
        { return kAGreaterThanB; }
        else
        {
            vector<strInt>& a_labels = a->getStringLabels();
            vector<strInt>& b_labels = b->getStringLabels();   
            for(int i = 0; i < a->getChildrenNum(); i++)
            {
                if(a_labels[i] < b_labels[i])
                { return kALessThanB; }
                else if(a_labels[i] > b_labels[i])
                { return kAGreaterThanB; }
                else
                {
                    EqualityOp result = triCompareSchemas(TO_SCHEMA_NODE(a->getChildWithIndex(i)), TO_SCHEMA_NODE(b->getChildWithIndex(i)));
                    if(result != kEqual) return result;
                }
            }
            return kEqual;
        }
    }
    else if(a->getType() == kHetArr)
    {
        if(a->getKleeneChild() == nullptr && b->getKleeneChild() != nullptr)
        { return kALessThanB; }
        else if(a->getKleeneChild() != nullptr && b->getKleeneChild() == nullptr)
        { return kAGreaterThanB; }
        else if(a->getKleeneChild() == nullptr && b->getKleeneChild() == nullptr)
        { return kEqual; }

        return triCompareSchemas(TO_SCHEMA_NODE(a->getKleeneChild()), TO_SCHEMA_NODE(b->getKleeneChild()));
    }
    else if(a->getType() == kAnyOf)
    {
        if(a->getChildren()->size() < b->getChildren()->size())
        { return kALessThanB; }
        else if(a->getChildren()->size() > b->getChildren()->size())
        { return kAGreaterThanB; }
        else
        {
            vector<Node*>* a_children = a->getChildren();
            vector<Node*>* b_children = b->getChildren();
            for(int i = 0; i < a->getChildrenNum(); i++)
            {
                EqualityOp result = triCompareSchemas(TO_SCHEMA_NODE(a_children->at(i)), TO_SCHEMA_NODE(b_children->at(i)));
                if(result != kEqual) return result;
            }
            return kEqual;
        }
    }
    else return kEqual;
}

void SchemaNode::printChildrenIds()
{
    for(auto child : *children_)
    {
        cout << TO_SCHEMA_NODE(child)->getId() << " ";
    }
    cout << endl;
}
