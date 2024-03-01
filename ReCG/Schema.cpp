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