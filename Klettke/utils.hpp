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




enum InstanceType { kObject = 0, kArray = 1, kNumber = 2, kString = 3, kBoolean = 4, kNull_ = 5 };
enum SchemaType   { kHomObj, kHetArr, kAnyOf, kNum, kStr, kBool, kNull };

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
    
    public:

        Parameters(){}

        // Getters
        string getInPath() { return in_path_; }
        string getOutPath() { return out_path_; }

        // Setters
        void setInPath(string in_path) { in_path_ = in_path; }
        void setOutPath(string out_path) { out_path_ = out_path; }
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
    private:
        string message_;

    public:
        explicit UnimplementedError(const string& message);

        const char* what() const noexcept override {
            return message_.c_str();
        }
};

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

string concatenate_strings(const vector<string>& strings, const string& delimiter);

SchemaType instanceTypeToSchemaType(InstanceType instance_type);

string schemaTypeToString(SchemaType schema_type);

string instanceTypeToString(InstanceType instance_type);


#endif