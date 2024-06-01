#include "InstanceClusterMerge.hpp"

int mergeInstanceClusters(InstanceCluster& a, InstanceCluster& b, ClusterType merging_type, CostParameters& cost_parameters)
{   
    #if VERBOSE
      cout << "<<Merging>> " << a.getTypeInString() << ", " << b.getTypeInString() << " -> " << merging_type << endl;
    #endif
    
    switch(a.getClusterType())
    {
        case kHomObjC:
            // a == Hom
            switch(b.getClusterType())
            {
                case kHomObjC:
                    if(merging_type == kHomObjC) mergeHomHomToHom(a, b, cost_parameters);
                    else throw IllegalBehaviorError("mergeInstanceClusters : Hom Hom -/-> Hom");
                    return 2;
                case kComObj:
                    if(merging_type == kComObjC) mergeHomComToCom(a, b, cost_parameters);
                    else throw IllegalBehaviorError("mergeInstanceClusters : Hom Com -/-> Com");
                    return 2;
                case kHetObjC:
                    if(merging_type == kHetObjC) mergeHomHetToHet(a, b, cost_parameters);
                    else throw IllegalBehaviorError("mergeInstanceClusters : Hom Het -/-> Het");
                    return 2;
                default:
                    return -1;
            }
            break;

        case kComObj:
            // a == Com
            switch(b.getClusterType())
            {
                case kHomObjC:
                    if(merging_type == kComObjC) mergeHomComToCom(b, a, cost_parameters);
                    else throw IllegalBehaviorError("mergeInstanceClusters : Com Hom -/-> Com");
                    return 1;
                case kComObj:
                    if(merging_type == kComObjC) mergeComComToCom(a, b, cost_parameters);
                    else throw IllegalBehaviorError("mergeInstanceClusters : Com Com -/-> Com");
                    return 2;
                case kHetObjC:
                    if(merging_type == kComObjC)
                    {
                        mergeHetComToCom(b, a, cost_parameters);
                        return 1;
                    }
                    else if(merging_type == kHetObjC)   
                    {
                        mergeComHetToHet(a, b, cost_parameters);
                        return 2;
                    }
                    else throw IllegalBehaviorError("mergeInstanceClusters : Com Het -/-> Com | Het");
                    return -1;
                default:
                    return -1;
            }
            break;

        case kHetObjC:
            // a == Het
            switch(b.getClusterType())
            {
                case kHomObjC:
                    if(merging_type == kHetObjC) mergeHomHetToHet(b, a, cost_parameters);
                    else throw IllegalBehaviorError("mergeInstanceClusters : Het Hom -/-> Het");
                    return 1;
                case kComObj:
                    if(merging_type == kComObjC)        
                    {
                        mergeHetComToCom(a, b, cost_parameters);
                        return 2;
                    }
                    else if(merging_type == kHetObjC)   
                    {
                        // a = het
                        // b = com
                        mergeComHetToHet(b, a, cost_parameters);
                        return 1;
                    }
                    else throw IllegalBehaviorError("mergeInstanceClusters : Het Com -/-> Com | Het");
                    break;
                case kHetObjC:
                    if(merging_type == kHetObjC) mergeHetHetToHet(a, b, cost_parameters);
                    else throw IllegalBehaviorError("mergeInstanceClusters : Het Het -/-> Het");
                    return 2;
                default:
                    break;
            }
            break;
        default:
            break;
    }
    return -1;
}



void mergeHomHomToHom(InstanceCluster& a_hom, InstanceCluster& b_hom, CostParameters& cost_parameters)
{
    if(a_hom.getClusterType() != kHomObjC) throw IllegalBehaviorError("mergeHomHomToHom : a_hom != HOM");
    if(b_hom.getClusterType() != kHomObjC) throw IllegalBehaviorError("mergeHomHomToHom : b_hom != HOM");


    // (0) Instance Forests
    auto* a_forest = a_hom.getInstanceForest();
    auto* b_forest = b_hom.getInstanceForest();
    b_forest->insert(b_forest->end(), a_forest->begin(), a_forest->end());

    // (1). [------- | Cost | -----] Children num
    b_hom.setChildrenNum(a_hom.getChildrenNum() + b_hom.getChildrenNum());

    // (2). [Pattern | ---- | Merge] Distinct labels
    roaring_bitmap_t* a_distinct_labels = a_hom.getDistinctLabels();
    roaring_bitmap_t* b_distinct_labels = b_hom.getDistinctLabels();
    roaring_bitmap_or_inplace(b_distinct_labels, a_distinct_labels);

    // (3). [Pattern | Cost | -----] mandatory labels - OPT REQ
    roaring_bitmap_t* a_mandatory_labels = a_hom.getMandatoryLabelBitmap();
    roaring_bitmap_t* b_mandatory_labels = b_hom.getMandatoryLabelBitmap();
    roaring_bitmap_and_inplace(b_mandatory_labels, a_mandatory_labels);

    // (4). [Pattern | Cost | -----] Labels to schemas - {a{SCH1}, b{SCH2}, ...}
    LabelToTypeSet* a_labels_to_schemas = a_hom.getLabelToTypes();
    LabelToTypeSet* b_labels_to_schemas = b_hom.getLabelToTypes();
    mergeInplace(a_labels_to_schemas, b_labels_to_schemas);

    // (5). [------- | ---- | Merge] Labels counting - OPT REQ
    LabelToCount* a_labels_to_count = a_hom.getLabelCount();
    LabelToCount* b_labels_to_count = b_hom.getLabelCount();
    mergeInplace(a_labels_to_count, b_labels_to_count);

    // (6). [------- | ---- | Merge] Children-derived schemas
    InstanceTypeSet* a_children_schema_set = a_hom.getChildrenTypeSet();
    InstanceTypeSet* b_children_schema_set = b_hom.getChildrenTypeSet();
    unionInplace(a_children_schema_set, b_children_schema_set);


    a_hom.freeResources();
}

void mergeComComToCom(InstanceCluster& a_com, InstanceCluster& b_com, CostParameters& cost_parameters)
{
    if(a_com.getClusterType() != kComObjC) throw IllegalBehaviorError("mergeComComToCom : a_com != COM");
    if(b_com.getClusterType() != kComObjC) throw IllegalBehaviorError("mergeComComToCom : b_com != COM");


    // (0) Instance Forests
    auto* a_forest = a_com.getInstanceForest();
    auto* b_forest = b_com.getInstanceForest();
    b_forest->insert(b_forest->end(), a_forest->begin(), a_forest->end());

    // (1). [------- | Cost | -----] Children num
     // children_num_ (already initiated)
    b_com.setChildrenNum(a_com.getChildrenNum() + b_com.getChildrenNum());

    // (2). [Pattern | ---- | Merge] Distinct labels
    roaring_bitmap_t* a_distinct_labels = a_com.getDistinctLabels();
    roaring_bitmap_t* b_distinct_labels = b_com.getDistinctLabels();
    roaring_bitmap_or_inplace(b_distinct_labels, a_distinct_labels);

    // (3). [Pattern | Cost | -----] mandatory labels - OPT REQ
    roaring_bitmap_t* a_mandatory_labels = a_com.getMandatoryLabelBitmap();
    roaring_bitmap_t* b_mandatory_labels = b_com.getMandatoryLabelBitmap();
    roaring_bitmap_and_inplace(b_mandatory_labels, a_mandatory_labels);

    // (4). [------- | ---- | Merge] Children-derived schemas
    InstanceTypeSet* a_children_schema_set = a_com.getChildrenTypeSet();
    InstanceTypeSet* b_children_schema_set = b_com.getChildrenTypeSet();
    unionInplace(a_children_schema_set, b_children_schema_set);

        // !!!!!
    // (5). children_types_com_kleene_
    InstanceTypeSet* a_kchildren_schema_set = a_com.getChildrenTypeSet();
    InstanceTypeSet* b_kchildren_schema_set = b_com.getChildrenTypeSet();
    unionInplace(a_kchildren_schema_set, b_kchildren_schema_set);

        // !!!!!
    // (6). children_num_com_kleene_
    b_com.setKChildrenNum(a_com.getChildrenNumForCom() + b_com.getChildrenNumForCom());

     // children_num_com_kleene_ (already initiated)
    // (7). [Pattern | Cost | -----] Labels to schemas 
        // ex) {a{SCH1}, b{SCH2, SCH4}, ..., z{SCH1, SCH5, ..., SCH8}}
    LabelToTypeSet* a_labels_to_schemas = a_com.getLabelToTypes();
    LabelToTypeSet* b_labels_to_schemas = b_com.getLabelToTypes();
    mergeInplace(a_labels_to_schemas, b_labels_to_schemas);

    // (8). [------- | ---- | Merge] Labels counting - OPT REQ
    LabelToCount* a_labels_to_count = a_com.getLabelCount();
    LabelToCount* b_labels_to_count = b_com.getLabelCount();
    mergeInplace(a_labels_to_count, b_labels_to_count);

    b_com.mdlCostOptimizationAtComObj(cost_parameters);
    a_com.freeResources();
}

void mergeHetHetToHet(InstanceCluster& a_het, InstanceCluster& b_het, CostParameters& cost_parameters)
{
    if(a_het.getClusterType() != kHetObjC) throw IllegalBehaviorError("mergeHetHetToHet : a_het != HET");
    if(b_het.getClusterType() != kHetObjC) throw IllegalBehaviorError("mergeHetHetToHet : b_het != HET");


    // (0) Instance Forests
    auto* a_forest = a_het.getInstanceForest();
    auto* b_forest = b_het.getInstanceForest();
    b_forest->insert(b_forest->end(), a_forest->begin(), a_forest->end());

    // (1). [------- | Cost | -----] Children num
    b_het.setChildrenNum(a_het.getChildrenNum() + b_het.getChildrenNum());
    
    // (2). [Pattern | ---- | Merge] All children schemas - 
        // {SCH1, SCH2, ...}
    InstanceTypeSet* a_children_schema_set = a_het.getChildrenTypeSet();
    InstanceTypeSet* b_children_schema_set = b_het.getChildrenTypeSet();
    unionInplace(a_children_schema_set, b_children_schema_set);


    a_het.freeResources();
}



void mergeHomHetToHet(InstanceCluster& a_hom, InstanceCluster& b_het, CostParameters& cost_parameters)
{
    if(a_hom.getClusterType() != kHomObjC) throw IllegalBehaviorError("mergeHomHetToHet : a_hom != HOM");
    if(b_het.getClusterType() != kHetObjC) throw IllegalBehaviorError("mergeHomHetToHet : b_het != HET");


    // (0) Instance Forests
    auto* a_forest = a_hom.getInstanceForest();
    auto* b_forest = b_het.getInstanceForest();
    b_forest->insert(b_forest->end(), a_forest->begin(), a_forest->end());

    // (1). [------- | Cost | -----] Children num
    b_het.setChildrenNum(a_hom.getChildrenNum() + b_het.getChildrenNum());
    
    // (2). [Pattern | ---- | Merge] All children schemas - 
        // {SCH1, SCH2, ...}
    InstanceTypeSet* a_children_schema_set = a_hom.getChildrenTypeSet();
    InstanceTypeSet* b_children_schema_set = b_het.getChildrenTypeSet();
    unionInplace(a_children_schema_set, b_children_schema_set);


    a_hom.freeResources();
}

void mergeComHetToHet(InstanceCluster& a_com, InstanceCluster& b_het, CostParameters& cost_parameters)
{
    if(a_com.getClusterType() != kComObjC) throw IllegalBehaviorError("mergeComHetToHet : a_com != COM");
    if(b_het.getClusterType() != kHetObjC) throw IllegalBehaviorError("mergeComHetToHet : b_het != HET");


    // (0) Instance Forests
    auto* a_forest = a_com.getInstanceForest();
    auto* b_forest = b_het.getInstanceForest();
    b_forest->insert(b_forest->end(), a_forest->begin(), a_forest->end());

    // (1). [------- | Cost | -----] Children num
    b_het.setChildrenNum(a_com.getChildrenNum() + b_het.getChildrenNum());
    
    // (2). [Pattern | ---- | Merge] All children schemas - 
        // {SCH1, SCH2, ...}
    InstanceTypeSet* a_children_schema_set = a_com.getChildrenTypeSet();
    InstanceTypeSet* b_children_schema_set = b_het.getChildrenTypeSet();
    unionInplace(a_children_schema_set, b_children_schema_set);


    a_com.freeResources();
}

void mergeHomComToCom(InstanceCluster& a_hom, InstanceCluster& b_com, CostParameters& cost_parameters)
{
    if(a_hom.getClusterType() != kHomObjC) throw IllegalBehaviorError("mergeHomComToCom : a_hom != HOM");
    if(b_com.getClusterType() != kComObjC) throw IllegalBehaviorError("mergeHomComToCom : b_com != COM");


    // (0) Instance Forests
    auto* a_forest = a_hom.getInstanceForest();
    auto* b_forest = b_com.getInstanceForest();
    b_forest->insert(b_forest->end(), a_forest->begin(), a_forest->end());

    // (1). [------- | Cost | -----] Children num
     // children_num_ (already initiated)
    b_com.setChildrenNum(a_hom.getChildrenNum() + b_com.getChildrenNum());

    // (2). [Pattern | ---- | Merge] Distinct labels
    roaring_bitmap_t* a_distinct_labels = a_hom.getDistinctLabels();
    roaring_bitmap_t* b_distinct_labels = b_com.getDistinctLabels();
    roaring_bitmap_or_inplace(b_distinct_labels, a_distinct_labels);

    // (3). [Pattern | Cost | -----] mandatory labels - OPT REQ
    roaring_bitmap_t* a_mandatory_labels = a_hom.getMandatoryLabelBitmap();
    roaring_bitmap_t* b_mandatory_labels = b_com.getMandatoryLabelBitmap();
    roaring_bitmap_and_inplace(b_mandatory_labels, a_mandatory_labels);

    // (4). [------- | ---- | Merge] Children-derived schemas
    InstanceTypeSet* a_children_schema_set = a_hom.getChildrenTypeSet();
    InstanceTypeSet* b_children_schema_set = b_com.getChildrenTypeSet();
    unionInplace(a_children_schema_set, b_children_schema_set);

     // children_num_com_kleene_ (already initiated)
    // (7). [Pattern | Cost | -----] Labels to schemas 
        // ex) {a{SCH1}, b{SCH2, SCH4}, ..., z{SCH1, SCH5, ..., SCH8}}
    LabelToTypeSet* a_labels_to_schemas = a_hom.getLabelToTypes();
    LabelToTypeSet* b_labels_to_schemas = b_com.getLabelToTypes();
    mergeInplace(a_labels_to_schemas, b_labels_to_schemas);

    // (8). [------- | ---- | Merge] Labels counting - OPT REQ
    LabelToCount* a_labels_to_count = a_hom.getLabelCount();
    LabelToCount* b_labels_to_count = b_com.getLabelCount();
    mergeInplace(a_labels_to_count, b_labels_to_count);

        // !!!!!
    // (5). children_types_com_kleene_
    InstanceTypeSet* b_kchildren_schema_set = b_com.getChildrenTypeSet();
    Count kleene_children_num_to_add = 0;
    for(auto& object : *a_hom.getInstanceForest())
    {
        vector<strInt>&     node_labels         = object->getStringLabels();
        vector<Node*>&      children            = object->getChildren();
        vector<int>         label_to_threshold  = object->getLabelToThreshold();
        int                 current_threshold   = object->getCurrentThreshold();

        for(int i = 0; i < node_labels.size(); i++)
        {
            strInt label = node_labels[i];
            // SchemaNode* derived_schema = TO_SCHEMA_NODE(TO_INSTANCE_NODE(children[i])->getDerivedSchema());
            InstanceType child_type = TO_INSTANCE_NODE(children[i])->getType();

            if(0 < label_to_threshold[i] && label_to_threshold[i] <= current_threshold)
            { 
                // 5. (5)
                b_kchildren_schema_set->insert( child_type );
                // 6. (6)
                kleene_children_num_to_add++;
            }
        }
    }

    // (6). children_num_com_kleene_
    b_com.setKChildrenNum(b_com.getChildrenNumForCom() + kleene_children_num_to_add);


    b_com.mdlCostOptimizationAtComObj(cost_parameters);
    a_hom.freeResources();
}


void mergeHetComToCom(InstanceCluster& a_het, InstanceCluster& b_com, CostParameters& cost_parameters)
{
    if(a_het.getClusterType() != kHetObjC) throw IllegalBehaviorError("mergeHetComToCom : a_het != HET");
    if(b_com.getClusterType() != kComObjC) throw IllegalBehaviorError("mergeHomComToCom : b_com != COM");


    // (0) Instance Forests
    auto* a_forest = a_het.getInstanceForest();
    auto* b_forest = b_com.getInstanceForest();
    b_forest->insert(b_forest->end(), a_forest->begin(), a_forest->end());

    b_com.freeMetadataResources();
    b_com.unsetUpToDateBit();
    b_com.updateClusterMetadata(cost_parameters);
    a_het.freeResources();
}



void unionInplace(SchemaSet* from, SchemaSet* to)
{
    for(auto schema_node : *from)
    { to->insert(schema_node); }
}

void mergeInplace(LabelToSchemaSet* from, LabelToSchemaSet* to)
{
    for(auto& label_schemas_pair : *from)
    {
        strInt label = label_schemas_pair.first;
        SchemaSet& schema_set = label_schemas_pair.second;

        auto it = to->find(label);
        if(it == to->end())
        {
            // not found -> Simple insert
            to->insert( {label, schema_set} );
        }
        else
        {
            // found -> Union sets
            to->at(label).insert(schema_set.begin(), schema_set.end());
        }
    }
}

void mergeInplace(LabelToCount* from, LabelToCount* to)
{
    for(auto& label_count_pair : *from)
    {
        strInt label = label_count_pair.first;
        Count count = label_count_pair.second;

        auto it = to->find(label);
        if(it == to->end())
        {
            // not found -> Simple insert
            to->insert( {label, count} );
        }
        else
        {
            // found -> Union sets
            to->at(label) += count;
        }
    }
}




void unionInplace(InstanceTypeSet* from, InstanceTypeSet* to)
{
    for(InstanceType type : *from)
    { to->insert(type); }
}

void mergeInplace(LabelToTypeSet* from, LabelToTypeSet* to)
{
    for(auto& label_types_pair : *from)
    {
        strInt label = label_types_pair.first;
        InstanceTypeSet& type_set = label_types_pair.second;

        auto it = to->find(label);
        if(it == to->end())
        {
            // not found -> Simple insert
            to->insert( {label, type_set} );
        }
        else
        {
            // found -> Union sets
            to->at(label).insert(type_set.begin(), type_set.end());
        }
    }
}