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
enum parameters_    { kBranchAndBound, kGreedy, kKBeam };
enum CostModel          { kMDL, kKeySpaceEntropy };
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


class Parameters
{
    private:
        // Parameters for bottom-up schema generator
        string              in_path_;
        string              out_path_;
        parameters_     search_alg_;
        int                 beam_width_;
        int                 sample_size_;
        float               epsilon_;
        int                 min_pts_perc_;
        float               src_weight_;
        float               drc_weight_;

        CostModel           cost_model_;
    
    public:

        Parameters(){}

        // Getters
        string getInPath() { return in_path_; }
        string getOutPath() { return out_path_; }
        parameters_ getSearchMode() { return search_alg_; }
        int getBeamWidth() { return beam_width_; }
        int getSampleSize() { return sample_size_; }
        float getEpsilon() { return epsilon_; }
        int getMinPtsPerc() { return min_pts_perc_; }
        float getSrcWeight() { return src_weight_; }
        float getDrcWeight() { return drc_weight_; }
        CostModel getCostModel() { return cost_model_; }

        // Setters
        void setInPath(string in_path) { in_path_ = in_path; }
        void setOutPath(string out_path) { out_path_ = out_path; }
        void setSearchMode(parameters_ search_mode) { search_alg_ = search_mode; }
        void setBeamWidth(int beam_width) { beam_width_ = beam_width; }
        void setSampleSize(int sample_size) { sample_size_ = sample_size; }
        void setEpsilon(float epsilon) { epsilon_ = epsilon; }
        void setMinPtsPerc(int min_pts_perc) { min_pts_perc_ = min_pts_perc; }
        void setSrcWeight(float src_weight) { src_weight_ = src_weight; }
        void setDrcWeight(float drc_weight) { drc_weight_ = drc_weight; }
        void setCostModel(CostModel cost_model) { cost_model_ = cost_model; }
};

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

string searchAlgToString(parameters_ search_mode);

string costModelToString(CostModel cost_model);

#endif