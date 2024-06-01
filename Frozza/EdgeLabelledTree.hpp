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

int binarySearch(const vector<strInt>& sorted_vector, strInt target);
int binarySearch(const vector<int>& sorted_vector, int target);
int naiveSearch(const vector<int>& vector, strInt target);
int naiveSearch(const vector<strInt>& vector, strInt target);


class Node
{
    protected:

        Count           int_children_num_;  
        vector<strInt>  str_labels_;
        vector<Node*>*   children_;

        Node*           parent_node_;

    public:
        // Node(T data) : _data(data) {}
        Node()
        {
            int_children_num_ = 0;
            children_ = new vector<Node*>({});
        }

        ~Node()
        {
        }



        // addChild overloading for string and int
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

        Node* getChildWithLabel(const strInt &edge_name)
        { return children_->at(naiveSearch(str_labels_, edge_name)); }

        Node* getChildWithIndex(const int index)
        {
            // No exception for segmentation fault
            if(index >= int_children_num_)
            { NoSuchChildError(); }
            return children_->at(index);
        }

        int getChildrenNum()
        { return int_children_num_ + str_labels_.size(); }

        // void removeChild();

        vector<strInt>& getStringLabels()
        { return str_labels_; }

        vector<Node*>* getChildren()
        { return children_; }

        void sortStrChildren();

        void checkSorted()
        {
            if(str_labels_.size() <= 1)
            { return; }
            for(int i = 0; i < str_labels_.size() - 1; i++)
            {
                if(str_labels_[i] > str_labels_[i + 1])
                { cout << "Not sorted!" << endl; }
            }
        }

        // bool checkLabelExistence(const strInt &edge_name)
        // { return binarySearch(str_labels_, edge_name) == -1; }

        void replaceChildWithLabel(const strInt &edge_name, Node *new_child)
        {
            int index = naiveSearch(str_labels_, edge_name);
            // cout << edge_name << index << endl;
            if(index == -1)
            { NoSuchChildError(); }
            children_->at(index) = new_child;
        }

        void replaceChildWithIndex(const int index, Node *new_child)
        {
            if(index >= int_children_num_)
            { NoSuchChildError(); }
            children_->at(index) = new_child;
        }

        void setParent(Node* parent_node)
        { parent_node_ = parent_node; }

        Node* getParent()
        { return parent_node_; }
};





#endif