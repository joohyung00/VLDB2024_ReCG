#include "Schema.hpp"


void SchemaNode::aggregateAnyOfChildrenCost()
{
    for(auto& child : children_)
    {
        SchemaNode* child_schema = TO_SCHEMA_NODE(child);
        if(child_schema->getType() == kAnyOf)
        {
            addToSRC(child_schema->getSRC());
            addToDRC(child_schema->getDRC());
        }
    }

    if(kleene_child_ != nullptr)
    {
        if(kleene_child_->getType() == kAnyOf)
        {
            addToSRC(kleene_child_->getSRC());
            addToSRC(kleene_child_->getDRC());
        }
    }
}


void SchemaNode::visualizeSchemaTree(int node_depth)
{
    // cout << node_depth << endl;
    cout << schemaTypeToString(type_) << endl;

    if(type_ == kHomObj || type_ == kComObj)
    {
        for(int child_idx = 0; child_idx < str_labels_.size(); child_idx++)
        {
            for(int i = 0; i < node_depth; i++)
            { cout << "   "; }
            cout << "┖( " << str_labels_[child_idx] << " )  ";

            // Node* child_node = children_[binarySearch(str_labels_, str_labels_[child_idx])];
            if(children_[child_idx] == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_SCHEMA_NODE(children_[child_idx])->visualizeSchemaTree(node_depth + 1);
        }
    }
    if(type_ == kHetObj || type_ == kComObj)
    {
        for(int i = 0; i < node_depth; i++)
        { cout << "   ";}
        cout << "┖( " << "*" << " )  ";

        Node* child_node = kleene_child_;
        if(child_node == nullptr)
        { cout << "nullptr" << endl; }
        else TO_SCHEMA_NODE(child_node)->visualizeSchemaTree(node_depth + 1);
    }
    
    if(type_ == kHomArr)
    {
        for(int child_idx = 0; child_idx < children_.size(); child_idx++)
        {
            for(int i = 0; i < node_depth; i++)
            { cout << "   ";}
            cout << "┖( " << child_idx << " )  ";
            if(children_[child_idx] == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_SCHEMA_NODE(children_[child_idx])->visualizeSchemaTree(node_depth + 1);
        }
    }
    if(type_ == kHetArr)
    {
        for(int i = 0; i < node_depth; i++)
        { cout << "   ";}
        cout << "┖( " << "*" << " )  ";

        Node* child_node = kleene_child_;
        if(child_node == nullptr)
        { cout << "nullptr" << endl; }
        else TO_SCHEMA_NODE(child_node)->visualizeSchemaTree(node_depth + 1);
    }


    if(type_ == kAnyOf)
    {
        for(int child_idx = 0; child_idx < children_.size(); child_idx++)
        {
            for(int i = 0; i < node_depth; i++)
            { cout << "   ";}
            cout << "┖ ";
            if(children_[child_idx] == nullptr)
            { cout << "nullptr" << endl; continue; }
            TO_SCHEMA_NODE(children_[child_idx])->visualizeSchemaTree(node_depth + 1);
        }
    
    }

    return;
}










bool isEqual(const InstanceTypeSet& a, const InstanceTypeSet& b)
{
    if(a.size() == b.size())
    {
        for(const auto element : a)
        {
            if(b.find(element) == b.end())
            {
                return false;
            }
        }
        return true;
    }
    return false;
}

bool isSubset(const InstanceTypeSet& a, const InstanceTypeSet& b)
{
    for(const auto element : a)
    {
        if(b.find(element) == b.end())
        {
            return false;
        }
    }
    return true;
}

bool isSubset(const InstanceTypeSet* a, const InstanceTypeSet* b)
{
    for(const auto element : *a)
    {
        if(b->find(element) == b->end())
        {
            return false;
        }
    }
    return true;
}

bool isEqual(const InstanceTypeSet* a, const InstanceTypeSet* b)
{
    if(a->size() == b->size())
    {
        for(const auto element : *a)
        {
            if(b->find(element) == b->end())
            {
                return false;
            }
        }
        return true;
    }
    return false;

}

bool hasConjunction(InstanceTypeSet* a, InstanceTypeSet* b)
{
    InstanceTypeSet* small;
    InstanceTypeSet* big;

    if(a->size() < b->size())
    {
        small = a;
        big = b;
    }
    else
    {
        small = b;
        big = a;
    }

    for(const auto element : *small)
    {
        if(big->find(element) != big->end())
        {
            return true;
        }
    }
    return false;

}



bool isEqual(const SchemaSet& A, const SchemaSet& B)
{
    if(A.size() == B.size())
    {
        for(const auto element : A)
        {
            if(B.find(element) == B.end())
            {
                return false;
            }
        }
        return true;
    }
    return false;
}

bool isSubset(const SchemaSet* a, const SchemaSet* b)
{
    for(const auto element : *a)
    {
        if(b->find(element) == b->end())
        {
            return false;
        }
    }
    return true;
}

bool isSubset(const SchemaSet& a, const SchemaSet& b)
{
    for(const auto element : a)
    {
        if(b.find(element) == b.end())
        {
            return false;
        }
    }
    return true;
}

bool isEqual(const SchemaSet* a, const SchemaSet* b)
{
    if(a->size() == b->size())
    {
        for(const auto element : *a)
        {
            if(b->find(element) == b->end())
            {
                return false;
            }
        }
        return true;
    }
    return false;
}

bool hasConjunction(SchemaSet* a, SchemaSet* b)
{
    SchemaSet* small;
    SchemaSet* big;

    if(a->size() < b->size())
    {
        small = a;
        big = b;
    }
    else
    {
        small = b;
        big = a;
    }

    for(const auto element : *small)
    {
        if(big->find(element) != big->end())
        {
            return true;
        }
    }
    return false;
}

Count unionSize(const SchemaSet* a, const SchemaSet* b)
{
    return a->size() + b->size() - intersectionSize(a, b);
}

Count intersectionSize(const SchemaSet* a, const SchemaSet* b)
{
    Count intersection_size = 0;
    
    for(const auto element : *a)
    {
        if(b->find(element) != b->end())
        { intersection_size += 1; }
    }

    return intersection_size;
}