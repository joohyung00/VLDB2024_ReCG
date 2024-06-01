#include "utils.hpp"

IllegalBehaviorError::IllegalBehaviorError(const std::string& message) 
: message_(message) 
{}

bool isPrimitive(SchemaType schema_type)
{
    if(schema_type == kNum || schema_type == kStr || schema_type == kBool || schema_type == kNull) return true;
    return false;
}

const map<InstanceType, int> InstanceTypeMap
{
    {kObject, 0}, {kArray, 1}, {kNumber, 2}, {kString, 3}, {kBoolean, 4}, {kNull_, 5}
};

const map<SchemaType, int> SchemaTypeMap
{
    {kHomObj, 0}, {kHetObj, 1}, {kComObj, 2}, {kHomArr, 3}, {kHetArr, 4}, {kAnyOf, 5}, {kNum, 6}, {kStr, 7}, {kBool, 8}, {kNull, 9}
};

void findCommonElements(const vector<strInt>& a, const vector<strInt>& b, vector<strInt>& common)
{
    size_t i = 0; // Index for vector a
    size_t j = 0; // Index for vector b

    while (i < a.size() && j < b.size()) 
    {
        if (a[i] < b[j]) 
        {
            i++; // Move to the next element in vector a
        }
        else if (a[i] > b[j]) 
        {
            j++; // Move to the next element in vector b
        } 
        else 
        {
            // Found a common element
            common.push_back(a[i]);
            i++;
            j++;
        }
    }
}

string concatenate_strings(const vector<string> &strings,
                                const string &delimiter)
{
    string result;
    for (size_t i = 0; i < strings.size(); i++)
    {
        result += strings[i];
        if (i != strings.size() - 1)
        { result += delimiter; }
    }
    return result;
}

bool isSubset(const unordered_set<strInt>& A, const unordered_set<strInt>& B) 
{
    for (const auto element : A) 
    {
        if (B.find(element) == B.end()) 
        { return false; }
    }
    return true;
}

bool isSubset(const vector<strInt>& A, const vector<strInt>& B) 
{
    // Initialize indices for vectors A and B
    size_t indexA = 0;
    size_t indexB = 0;

    // Iterate through both vectors
    while (indexA < A.size() && indexB < B.size()) {
        // If the current element in A is smaller, it's not in B
        if (A[indexA] < B[indexB]) {
            return false;
        }
        // If the elements match, move to the next element in A
        else if (A[indexA] == B[indexB]) {
            indexA++;
        }
        // If the current element in B is smaller, move to the next element in B
        else {
            indexB++;
        }
    }

    // If we've reached the end of A, it's a subset of B
    return indexA == A.size();
}


bool isEqual(const unordered_set<strInt>& set1, const unordered_set<strInt>& set2) 
{
    if (set1.size() != set2.size()) 
    { return false; }

    for (const strInt& element : set1) 
    {
        if (set2.find(element) == set2.end()) 
        { return false; }
    }

    return true;
}

bool contains(vector<int>& vec, int target)
{
    if(std::find(vec.begin(), vec.end(), target) != vec.end()) 
    {
        return true;
    } 
    else 
    {
        return false;
    }
}


bool binomialSample(double p) {
    p = ceil(p * 100);  // Convert to an integer in [1, 100]
    int q = rand() % static_cast<int>(p) + 1;  // Generate a random integer in [1, p]

    return q <= p;
}

int bitSize(int num)
{ return ceil(log2(num)); }

int encodeLength(int length)
{ return 2 * bitSize(length) + 1; }

string searchAlgToString(parameters_ search_mode)
{
    switch(search_mode)
    {
        case kGreedy: return "Greedy Search";
        case kBranchAndBound: return "Branch&Bound Search";
        case kKBeam: return "Beam Search";
        default: throw IllegalBehaviorError("Invalid search mode");
    }
}

string costModelToString(CostModel cost_model)
{
    switch(cost_model)
    {
        case kMDL: return "MDL";
        case kKeySpaceEntropy: return "Key-Space Entropy";
        default: throw IllegalBehaviorError("Invalid cost model");
    }
}