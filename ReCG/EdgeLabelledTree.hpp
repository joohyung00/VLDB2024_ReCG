#ifndef NLELTREE
#define NLELTREE

#include <iostream>
#include <string>

#include <vector>
#include <unordered_set>
#include <map>
#include <unordered_map>
#include <queue>
#include <stack>

#include <algorithm>

// EdgeLabelledTree
#include "utils.hpp"




using namespace std;

int binarySearch(const vector<strInt>& sorted_vector, int target);


class Node
{
    protected:

        int int_children_num_;  
        vector<strInt> str_labels_;

        vector<Node*> children_;

        Node* parent_node_;

    public:
        // Node(T data) : _data(data) {}
        Node()
        {
            str_labels_ = vector<strInt>();
            children_ = vector<Node*>();
            int_children_num_ = 0;
        }

        ~Node()
        {}

        // addChild overloading for string and int
        void addChild(const strInt edge_name, Node *child)
        {
            str_labels_.push_back(edge_name);
            children_.push_back(child);

            child->setParent(this);
        }

        void addChild(Node *child)
        {
            int_children_num_++;
            children_.push_back(child);

            child->setParent(this);
        }

        Node* getChild(const strInt &edge_name)
        { return children_[binarySearch(str_labels_, edge_name)]; }

        Node* getChild(const int edge_name)
        {
            // No exception for segmentation fault
            if(edge_name >= int_children_num_)
            { NoSuchChildError(); }
            return children_[edge_name];
        }

        int getChildrenNum()
        { return int_children_num_ + str_labels_.size(); }

        // void removeChild();

        vector<strInt>& getStringLabels()
        { return str_labels_; }

        vector<Node*>& getChildren()
        { return children_; }

        void sortStrChildren();

        bool checkLabelExistence(const strInt &edge_name)
        { return binarySearch(str_labels_, edge_name) == -1; }

        void setParent(Node* parent_node)
        { parent_node_ = parent_node; }

        Node* getParent()
        { return parent_node_; }
};





#endif