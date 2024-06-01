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
    {kHomObj, 0}, {kHetArr, 1}, {kAnyOf, 2}, {kNum, 3}, {kStr, 4}, {kBool, 5}, {kNull, 6}
};


SchemaType instanceTypeToSchemaType(InstanceType instance_type)
{
    switch(instance_type)
    {
        case kObject: return kHomObj;
        case kArray: return kHetArr;
        case kNumber: return kNum;
        case kString: return kStr;
        case kBoolean: return kBool;
        case kNull_: return kNull;
        default: throw IllegalBehaviorError("instanceTypeToSchemaType: Invalid InstanceType");
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

string schemaTypeToString(SchemaType schema_type)
{
    switch(schema_type)
    {
        case kHomObj:
            return "OBJ";
        case kHetArr:
            return "ARR";
        case kAnyOf: 
            return "ANYOF";
        case kNum: return "NUM";
        case kStr: return "STR";
        case kBool: return "BOOL";
        case kNull: return "NULL";
        default: throw IllegalBehaviorError("Invalid schema type");
    }

}

string instanceTypeToString(InstanceType instance_type)
{
    switch(instance_type)
    {
        case kObject: return "OBJ";
        case kArray: return "ARR";
        case kNumber: return "NUM";
        case kString: return "STR";
        case kBoolean: return "BOOL";
        case kNull_: return "NULL";
        default: throw IllegalBehaviorError("Invalid instance type");
    }
}