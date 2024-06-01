#include "EdgeLabelledTree.hpp"

int binarySearch(const vector<strInt>& sorted_vector, int target)
{
    // int left = 0;
    // int right = sorted_vector.size() - 1;

    // while (left <= right) {
    //     int mid = left + (right - left) / 2;

    //     if (sorted_vector[mid] == target) 
    //     { return mid; } 
    //     else if (sorted_vector[mid] < target) 
    //     { left = mid + 1; } 
    //     else 
    //     { right = mid - 1; }
    // }

    // return -1;

    for(int i = 0; i < sorted_vector.size(); i++)
    {
        if(sorted_vector[i] == target)
        { return i; }
    }
    return -1;
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