#include "EdgeLabelledTree.hpp"

int binarySearch(const vector<strInt>& sorted_vector, strInt target)
{
    int left = 0;
    int right = sorted_vector.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (sorted_vector[mid] == target) 
        { return mid; } 
        else if (sorted_vector[mid] < target) 
        { left = mid + 1; } 
        else 
        { right = mid - 1; }
    }

    return -1;
}

int binarySearch(const vector<int>& sorted_vector, int target)
{
    int left = 0;
    int right = sorted_vector.size() - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (sorted_vector[mid] == target) 
        { return mid; } 
        else if (sorted_vector[mid] < target) 
        { left = mid + 1; } 
        else 
        { right = mid - 1; }
    }

    return -1;
}


int naiveSearch(const vector<int>& vector, strInt target)
{
    auto it = find(vector.begin(), vector.end(), target);
  
    if (it != vector.end())  
    {
        int index = it - vector.begin(); 
        return index;
    } 
    else 
    { 
        return -1;
    } 
}

int naiveSearch(const vector<strInt>& vector, strInt target)
{
    auto it = find(vector.begin(), vector.end(), target);
  
    if (it != vector.end())  
    {
        int index = it - vector.begin(); 
        return index;
    } 
    else 
    { 
        return -1;
    } 
}



void Node::sortStrChildren()
{
    vector<pair<strInt, Node*>> pairs;
    for (int i = 0; i < str_labels_.size(); ++i) 
    { pairs.emplace_back(str_labels_[i], children_[i]); }

    sort(pairs.begin(), pairs.end());

    for (size_t i = 0; i < pairs.size(); ++i) 
    {
        str_labels_[i] = pairs[i].first;
        children_[i] = pairs[i].second;
    }
}