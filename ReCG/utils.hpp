#ifndef UTILS
#define UTILS

#include <string>
#include <cstdint>

#include <set>
#include <vector>
#include <map>
#include <unordered_set>

#include <cmath>
#include <cstdlib>
#include <random>

#include <chrono>

#include <algorithm>
#include <cassert>
#include <stdexcept>

#include "roaring.h"

// Search 
#define BNBLIMIT 6

// Data Number

// Verbose
#define VERBOSE false
#define VERBOSE2 false



// User-Defined Enumeration Types
enum SearchMode         { kBranchAndBound, kGreedy, kKBeam };
// enum StateStatus  { kUninitiated, kClusteredAndMerging, kDead };
enum DerivationPhase    { kClusteringPhase, kMergingPhase };
enum DerivationResult   { kDerived, kNoMoreDerivation };

enum InstanceType { kObject = 0, kArray = 1, kNumber = 2, kString = 3, kBoolean = 4, kNull_ = 5 };
enum SchemaType   { kHomObj, kHetObj, kComObj, kHomArr, kHetArr, kAnyOf, kNum, kStr, kBool, kNull };
enum ClusterType  { kHomObjC, kHetObjC, kComObjC, kEmptyObjC, kHomArrC, kHetArrC, kEmptyArrC };



// Data Type Wrapping for Semantics
using strInt    = uint32_t;
using stateId   = uint32_t;
using nodeId    = uint32_t;
using vectorIdx = int;
using hash32    = uint32_t;
using MDLCost   = double;
using BitSize   = int;
using length    = int;
using Count     = int;

// Namespace Using
using namespace std;
using namespace std::chrono;


class NoSuchChildError : public std::exception 
{
    public:
        NoSuchChildError(){}
};
class InitializerDepthError : public std::exception 
{
    public:
        InitializerDepthError(){}
};
class UnimplementedError : public std::exception 
{
    public:
        UnimplementedError(){}
};
// class IllegalBehaviorError : public std::exception 
// {
//     public:
//         IllegalBehaviorError(){}
// };
class IllegalBehaviorError: public std::exception 
{
    private:
        string message_;

    public:
        explicit IllegalBehaviorError(const string& message);

        const char* what() const noexcept override {
            return message_.c_str();
        }
};



template<typename Tval>
struct MyTemplatePointerHash1 {
    size_t operator()(const Tval* val) const {
        static const size_t shift = (size_t)log2(1 + sizeof(Tval));
        return (size_t)(val) >> shift;
    }
};

extern const map<InstanceType, int> InstanceTypeMap;
extern const map<SchemaType,   int> SchemaTypeMap;

bool isPrimitive(SchemaType schema_type);

void findCommonElements(const vector<strInt>& a, const vector<strInt>& b, vector<strInt>& common);

string concatenate_strings(const vector<string>& strings, const string& delimiter);

int bitSize(int num);

int encodeLength(int length);

bool isSubset(const unordered_set<strInt>& A, const unordered_set<strInt>& B);

bool isSubset(const vector<strInt>& A, const vector<strInt>& B);

bool isEqual(const unordered_set<strInt>& set1, const unordered_set<strInt>& set2);

bool contains(vector<int>& vec, int target);

bool binomialSample(double p);

#endif