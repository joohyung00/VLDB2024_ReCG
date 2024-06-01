#ifndef INSTCLUSTER
#define INSTCLUSTER


// [InstanceCluster]
#include "Schema.hpp"
#include "Instance.hpp"
// EdgeLabelledTree.hpp
// utils.hpp


class CostParameters
{
    private:
        strInt          distinct_labels_num_;
        int             max_obj_len_;
        int             max_arr_len_;

        int             meta_characeters_num_ = 12;

    public:
        CostParameters()
        {}

        CostParameters(
            strInt         distinct_labels_num,
            int             max_obj_len,
            int             max_arr_len
        )
        : distinct_labels_num_(distinct_labels_num),
        max_obj_len_(max_obj_len),
        max_arr_len_(max_arr_len)
        {}

        strInt getDistinctLabelsNum()
        { return distinct_labels_num_; }

        int getMaxObjLen()
        { return max_obj_len_; }

        int getMaxArrLen()
        { return max_arr_len_; }

        BitSize getSchemaBitSize()
        { return bitSize(meta_characeters_num_ + distinct_labels_num_); }

        BitSize getKleeneEncodingBitSize()
        { return bitSize(distinct_labels_num_); }

        BitSize getObjLenBitSize()
        { return bitSize(max_obj_len_); }

        BitSize getArrLenBitSize()
        { return bitSize(max_arr_len_); }
};



using LabelToSchemaSet = unordered_map<strInt, SchemaSet>;
using LabelToTypeSet   = unordered_map<strInt, InstanceTypeSet>;
using LabelToCount     = unordered_map<strInt, Count>;
using SchemaSeq        = vector<SchemaNode*>;
using InstanceTypeSeq  = vector<InstanceType>;







class InstanceCluster
{
    private:

        ClusterType                         type_;

        bool                                up_to_date_ = false;

        // Fundamental information
        InstanceForest*                     instance_forest_;
        SchemaNode*                         derived_schema_;

        // Light, transitive
        roaring_bitmap_t*                   distinct_labels_;
        roaring_bitmap_t*                   mandatory_labels_;
        InstanceTypeSet*                    children_type_set_;
        InstanceTypeSeq*                    children_type_seq_;
        int                                 children_num_;
            // Com
        int                                 children_num_com_kleene_;
        InstanceTypeSet*                    children_types_com_kleene_;

        // Hom
        LabelToTypeSet*                     label_to_types_;

            // Currently not in use
        LabelToCount*                       label_count_;

        


    public:
        InstanceCluster()
        { initiateInstanceClusterVariables(); }
        
        explicit InstanceCluster(ClusterType type)
        : type_(type)
        { initiateInstanceClusterVariables(); }

        void initiateInstanceClusterVariables()
        {
            instance_forest_                = new InstanceForest();
            derived_schema_                 = nullptr;
            distinct_labels_                = nullptr;
            mandatory_labels_               = nullptr;
            children_type_set_              = nullptr;
            children_type_seq_              = nullptr;
            children_num_                   = 0;
            children_num_com_kleene_        = 0;
            children_types_com_kleene_      = nullptr;
            label_to_types_                 = nullptr;
            label_count_                    = nullptr;
        }

        void freeResources()
        {
            if(instance_forest_ != nullptr)
            {
                delete instance_forest_;
                instance_forest_ = nullptr;
            }
            freeMetadataResources();
        }

        void freeMetadataResources()
        {
            if(distinct_labels_ != nullptr)
            {
                roaring_bitmap_free(distinct_labels_);
                distinct_labels_ = nullptr;
            }
            if(mandatory_labels_ != nullptr)
            {
                roaring_bitmap_free(distinct_labels_);
                mandatory_labels_ = nullptr;
            }
            if(children_type_set_ != nullptr)
            {
                delete children_type_set_;
                children_type_set_ = nullptr;
            }
            if(children_type_seq_ != nullptr)
            {
                delete children_type_seq_;
                children_type_seq_ = nullptr;
            }
            if(children_types_com_kleene_ != nullptr)
            {
                delete children_types_com_kleene_;
                children_types_com_kleene_ = nullptr;
            }
            if(label_to_types_ != nullptr)
            {
                delete label_to_types_;
                label_to_types_ = nullptr;
            }
            if(label_count_ != nullptr)
            {
                delete label_count_;
                label_count_ = nullptr;
            }
        }

        // [GetSet]

        void setClusterType(ClusterType type)
        { type_ = type; }

        ClusterType getClusterType()
        { return type_; }

        void setUpToDateBit()
        { up_to_date_ = true; }

        void unsetUpToDateBit()
        { up_to_date_ = false; }

        bool getUpToDateBit()
        { return up_to_date_; }

        void setDerivedSchema(SchemaNode* node)
        { derived_schema_ = node; }

        SchemaNode* getDerivedSchema()
        { return derived_schema_; }

        InstanceForest* getInstanceForest()
        { return instance_forest_; }

        int getForestSize()
        { return instance_forest_->size(); }

        void setChildrenNum(int children_num)
        { children_num_ = children_num; }

        void setKChildrenNum(int k_children_num)
        { children_num_com_kleene_ = k_children_num; }

        int getChildrenNum()
        { return children_num_; }

        void addInstance(InstanceNode* instance)
        { instance_forest_->push_back(instance); }

        void setChildrenTypeSet(InstanceTypeSet& schema_set)
        { 
            children_type_set_ = new InstanceTypeSet();
            *children_type_set_ = schema_set; 
        }

        InstanceTypeSet* getChildrenTypeSet()
        { return children_type_set_; }

        InstanceTypeSeq* getChildrenTypeSeq()
        { return children_type_seq_; }

        InstanceTypeSet* getChildrenTypeForCom()
        { return children_types_com_kleene_; }

        Count getChildrenNumForCom()
        { return children_num_com_kleene_; }

        LabelToTypeSet* getLabelToTypes()
        { return label_to_types_; }

        LabelToCount* getLabelCount()
        { return label_count_; }

        roaring_bitmap_t* getDistinctLabels()
        { return distinct_labels_; }

        int getDistinctLabelsNum()
        { return roaring_bitmap_get_cardinality(distinct_labels_); }

        roaring_bitmap_t* getMandatoryLabelBitmap()
        { return mandatory_labels_; }

        int getMandatorylabelsNum()
        { return roaring_bitmap_get_cardinality(mandatory_labels_); }

        

        


        void setInstanceForest(InstanceSet& instance_set);

        void setInstanceForest(InstanceForest& instance_forest);

        void updateClusterType();

        string getTypeInString();

        void updateClusterMetadata(CostParameters& cost_parameters);

        // Update metadata for each type of cluster
        void updateHomObjCMetadata(CostParameters& cost_parameters);
        void updateHetObjCMetadata(CostParameters& cost_parameters);
        void updateComObjCMetadata(CostParameters& cost_parameters);

        void updateHomArrCMetadata(CostParameters& cost_parameters);
        void updateHetArrCMetadata(CostParameters& cost_parameters);

        void mdlCostOptimizationAtComObj(CostParameters& cost_parameters);
};



void printLabelToSchemaSet(LabelToSchemaSet& label_to_schema_set);




#endif