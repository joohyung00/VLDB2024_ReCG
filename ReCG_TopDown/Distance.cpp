#include "Distance.hpp"

/*
    [[Usage Example of Roaring Bitmap]]

    // create a new empty bitmap
    roaring_bitmap_t *r1 = roaring_bitmap_create();
    // then we can add values
    for(uint32_t i = 100; i < 1000; i++) roaring_bitmap_add(r1, i);
    // check whether a value is contained
    roaring_bitmap_t *r2 = roaring_bitmap_create();
    for(uint32_t i = 200; i < 1000; i++) roaring_bitmap_add(r2, i);
    
    float jaccard = roaring_bitmap_jaccard_index(r1, r2);
    // compute how many bits there are:
    uint32_t cardinality = roaring_bitmap_get_cardinality(r1);
    cout << jaccard << endl;

    return 0; 
*/









//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////// Instance Distances /////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

float jaccardDistance(InstanceNode* inode_a, InstanceNode* inode_b)
{
    vector<strInt>& labels_a = inode_a->getStringLabels();
    vector<strInt>& labels_b = inode_b->getStringLabels();
    vector<strInt> common;

    findCommonElements(labels_a, labels_b, common);

    int intersection_count = common.size();
    int union_count = labels_a.size() + labels_b.size() - intersection_count;

    // Distnace Measure
    if(union_count == 0)
    { return 1; }
    else
    { return 1 - intersection_count / (float)union_count; }
}


float weightedJaccardDistance(InstanceNode* inode_a, InstanceNode* inode_b)
{
    // Label only
    roaring_bitmap_t* a_labels = inode_a->getUnkleenedLabelBitmap();
    roaring_bitmap_t* b_labels = inode_b->getUnkleenedLabelBitmap();
    
    if(a_labels != nullptr)
    {
        const uint32_t a_label_card = roaring_bitmap_get_cardinality(a_labels);
        const uint32_t b_label_card = roaring_bitmap_get_cardinality(b_labels);
        const uint32_t label_inter = roaring_bitmap_and_cardinality(a_labels, b_labels);
        const uint32_t label_union = (double)(a_label_card + b_label_card - label_inter);

        // Label + Schemas
        roaring_bitmap_t* a_hash = inode_a->getLabelChildtypeBitmap();
        roaring_bitmap_t* b_hash = inode_b->getLabelChildtypeBitmap();
        const uint32_t hash_inter = roaring_bitmap_and_cardinality(a_hash, b_hash);
        
        // Kleene part
        // int kleene_inter = 0;
        // int kleene_union = 0;
        roaring_bitmap_t* a_kleene_schemas = inode_a->getKleenedChildtypes();
        roaring_bitmap_t* b_kleene_schemas = inode_b->getKleenedChildtypes();
        const uint32_t card1 = roaring_bitmap_get_cardinality(a_kleene_schemas);
        const uint32_t card2 = roaring_bitmap_get_cardinality(b_kleene_schemas);
        uint32_t kleene_inter = roaring_bitmap_and_cardinality(a_kleene_schemas, b_kleene_schemas);
        uint32_t kleene_union = (double)(card1 + card2 - kleene_inter);



        return 1 - ((float)(0.5 * (float)label_inter + 0.5 * (float)hash_inter + (float)kleene_inter) / (float)(label_union + kleene_union));
    }
    else
    {

        roaring_bitmap_t* a_kleene_schemas = inode_a->getKleenedChildtypes();
        roaring_bitmap_t* b_kleene_schemas = inode_b->getKleenedChildtypes();
        const uint32_t card1 = roaring_bitmap_get_cardinality(a_kleene_schemas);
        const uint32_t card2 = roaring_bitmap_get_cardinality(b_kleene_schemas);
        const uint32_t kleene_inter = roaring_bitmap_and_cardinality(a_kleene_schemas, b_kleene_schemas);
        const uint32_t kleene_union = (double)(card1 + card2 - kleene_inter);

        return 1 - (float)kleene_inter / (float)kleene_union;
    }
}































///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////// Cluster Distances (MDL) /////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////


mergeInfo clusterDistance(InstanceCluster& cluster_a, InstanceCluster& cluster_b, CostParameters& cost_parameters)
{
    SchemaType a_type = cluster_a.getDerivedSchema()->getType();
    SchemaType b_type = cluster_b.getDerivedSchema()->getType();

    mergeInfo merge_info;
    int return_value;

    switch(a_type)
    {
        case kHomObj:
            switch(b_type)
            {
                case kHomObj:
                    return_value = homHomClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
                    break;
                case kComObj:
                    return_value = homComClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
                    break;
                case kHetObj:
                    return_value = homHetClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
                    break;
            }
            break;

        case kComObj:
            switch(b_type)
            {
                case kHomObj:
                    return_value = homComClusterDist(cluster_b, cluster_a, cost_parameters, merge_info);
                    break;
                case kComObj:
                    return_value = comComClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
                    break;
                case kHetObj:
                    return_value = comHetClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
                    break;
            }
            break;

        case kHetObj:
            switch(b_type)
            {
                case kHomObj:
                    return_value = homHetClusterDist(cluster_b, cluster_a, cost_parameters, merge_info);
                    break;
                case kComObj:
                    return_value = comHetClusterDist(cluster_b, cluster_a, cost_parameters, merge_info);
                    break;
                case kHetObj:
                    return_value = hetHetClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
                    break;
            }
            break;
    }

    if(return_value != 1)
        throw IllegalBehaviorError("clusterDistance - unexpected return");

    
    return merge_info;
}


/////////////////////////////////// Hom - Hom ///////////////////////////////////

int homHomClusterDist(InstanceCluster& a_hom, InstanceCluster& b_hom, CostParameters& cost_parameters, mergeInfo& merge_info)
{
    // 1. Check if merging is a viable one
    roaring_bitmap_t* a_labels = a_hom.getDistinctLabels();
    roaring_bitmap_t* b_labels = b_hom.getDistinctLabels();

        // Viable: Are there any common labels?
    int and_result = roaring_bitmap_and_cardinality(a_labels, b_labels);

    if(!and_result)
    {
        merge_info.setViableBit(false);
        return 1;
    }
    
    // 2. If viable, then calculate delta(MDL)
    merge_info.setViableBit(true);

    // 3. Delta SRC
    MDLCost src_delta = 0;
        // 3.1. Minus SRC for two to-be-merged schemas
    src_delta -= a_hom.getDerivedSchema()->getSRC();
    src_delta -= b_hom.getDerivedSchema()->getSRC();

        // 3.2. SRC for newly-deriving schema
    Count new_labels_num = roaring_bitmap_or_cardinality(a_labels, b_labels);
    int symbol_num = 3 + 2 * new_labels_num;

    src_delta += cost_parameters.getSchemaBitSize() * symbol_num;

    // 4. Delta DRC
        // Increase in DRC -> (new optionals * 데이터 개수) - (DRC_a + DRC_b)
        // Increase in DRC -> (anyOf 늘어난 만큼)

    // MDLCost drc_delta = 0;

    //     // 4.1. Minus DRC for two to-be-merged schemas
    // drc_delta -= a_hom.getDerivedSchema()->getDRC();
    // drc_delta -= b_hom.getDerivedSchema()->getDRC();

    //     // 4.2. DRC for newly-deriving schema -> refer to `homObjDRC`
    // Count n = a_hom.getForestSize() + b_hom.getForestSize();
    // Count new_mandatory_labels_num = roaring_bitmap_and_cardinality( 
    //     a_hom.getMandatoryLabelBitmap(),
    //     b_hom.getMandatoryLabelBitmap()
    // );

    // drc_delta += n * (new_labels_num - new_mandatory_labels_num);

    // merge_info.setDeltaMdl(src_delta + drc_delta);
    merge_info.setDeltaMdl(abs(src_delta));
    merge_info.setMergeClusterType(kHomObjC);

    return 1;
}




/////////////////////////////////// Hom - Het ///////////////////////////////////

int homHetClusterDist(InstanceCluster& a_hom, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info)
{
    // 1. Check if merging is a viable one
    InstanceTypeSet* a_children_types = a_hom.getChildrenTypeSet();
    InstanceTypeSet* b_children_types = b_het.getChildrenTypeSet();

        // viable: Are the children schemas same?
    if(!isEqual(a_children_types, b_children_types))
    {
        merge_info.setViableBit(false);
        return 1;
    }
    
    // 2. If viable, then calculate delta(MDL)
    merge_info.setViableBit(true);
    
    // 3. Calculate decrease in SRC
        // 3.1. Decrease in SRC -> SRC of a_hom
    MDLCost src_delta = (-1) * a_hom.getDerivedSchema()->getSRC();

    // 4. Calculate delta DRC
        // 4.1. Decrease in DRC - a_hom's DRC
    // MDLCost drc_delta = 0;
    // drc_delta -= a_hom.getDerivedSchema()->getDRC();

    //     // 4.2. Increase in DRC - a_hom to het -> refer to `hetObjDRC`
    // BitSize length_bit_size = cost_parameters.getObjLenBitSize();
    // BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

    // Count n = a_hom.getInstanceForest()->size();
    // drc_delta += n * length_bit_size;

    // Count m = a_hom.getChildrenNum();
    // drc_delta += m * kleene_bit_size;

    // merge_info.setDeltaMdl(src_delta + drc_delta);
    merge_info.setDeltaMdl(abs(src_delta));
    merge_info.setMergeClusterType(kHetObjC);
    return 1;
}





/////////////////////////////////// Het - Het ///////////////////////////////////

int hetHetClusterDist(InstanceCluster& a_het, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info)
{
    // 1. Check if merging is a viable one
    // TODO: childrenSchemaSet -> childrenTypeSet
    InstanceTypeSet* a_children_types = a_het.getChildrenTypeSet();
    InstanceTypeSet* b_children_types = b_het.getChildrenTypeSet();

        // Are there any common children schemas?
    if(!hasConjunction(a_children_types, b_children_types))
    {
        merge_info.setViableBit(false);
        return 1;
    }

    // 2. If viable, then calculate delta(MDL)
    merge_info.setViableBit(true);

    // 3. Calculate delta SRC
    MDLCost src_delta = 0;
        // 3.1. Decrease in SRC -> SRC of a_het b_het
    src_delta -= a_het.getDerivedSchema()->getSRC();
    src_delta -= b_het.getDerivedSchema()->getSRC();

        // 3.2. Increase in SRC -> SRC of newly-deriving schema
    int symbol_num = 1 + 1 + 2;
    src_delta += symbol_num * cost_parameters.getSchemaBitSize();

    // 4. Calculate delta DRC 
    // MDLCost drc_delta = 0;

         // 4.1. Decrease in DRC - a_het b_het
    // drc_delta -= a_het.getDerivedSchema()->getDRC();
    // drc_delta -= b_het.getDerivedSchema()->getDRC();

        // 4.2. Increase in DRC - newly-derived schema -> refer to `hetObjDRC`
    // BitSize length_bit_size = cost_parameters.getObjLenBitSize();
    // BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

    // Count n = a_het.getForestSize() + b_het.getForestSize();
    // drc_delta += n * length_bit_size;

    // Count m = a_het.getChildrenNum() + b_het.getChildrenNum();
    // drc_delta += m * kleene_bit_size;

    // BitSize choice_bitsize = bitSize( unionSize(a_children_schemas, b_children_schemas) );
    // drc_delta += m * choice_bitsize;

    // merge_info.setDeltaMdl(src_delta + drc_delta);
    merge_info.setDeltaMdl(abs(src_delta));
    merge_info.setMergeClusterType(kHetObjC);
    return 1;
}




/////////////////////////////////// Hom - Com ///////////////////////////////////

int homComClusterDist(InstanceCluster& a_hom, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info)
{
    // 1. Check if merging is a viable one
    roaring_bitmap_t* a_labels = a_hom.getDistinctLabels();
    roaring_bitmap_t* b_labels = b_com.getDistinctLabels();

    // TARGET: to COM

        // Are there any common labels?
    int and_result = roaring_bitmap_and_cardinality(a_labels, b_labels);

    if(!and_result)
    {
        merge_info.setViableBit(false);
        return 1;
    }

        // Are there any common children schemas?
    // TODO: childrenSchemaSet -> childrenTypeSet
    InstanceTypeSet* a_children_types = a_hom.getChildrenTypeSet();
    InstanceTypeSet* b_children_types = b_com.getChildrenTypeSet();

    if(!hasConjunction(a_children_types, b_children_types))
    {
        merge_info.setViableBit(false);
        return 1;
    }

    // 2. If viable, then calculate delta(MDL)
    merge_info.setViableBit(true);

    // 3. Aggregate metadata
    LabelToTypeSet label_to_types = *a_hom.getLabelToTypes();
    for(auto& label_types_pair : *b_com.getLabelToTypes())
    {
        strInt label = label_types_pair.first;
        auto label_to_type_it = label_to_types.find(label);
        if(label_to_type_it == label_to_types.end())
        { label_to_types.insert( {label, label_types_pair.second} ); }
        else
        { label_to_type_it->second.insert(label_types_pair.second.begin(), label_types_pair.second.end()); }
    }
    Count all_labels_num = label_to_types.size();

    // 4. Calculate delta SRC
    MDLCost src_delta = 0;
        // 4.1. Decrease in SRC -> SRC of a_het b_het
    src_delta -= a_hom.getDerivedSchema()->getSRC();
    src_delta -= b_com.getDerivedSchema()->getSRC();

        // 4.2. Increase in SRC -> SRC of newly-derived schema node
    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();

    int symbol_num = 1 + 4 * all_labels_num + 1 + 2;
    src_delta += symbol_bitsize * symbol_num;

    // 5. Calculate delta DRC
    // MDLCost drc_delta = 0;    
    // BitSize length_bit_size = cost_parameters.getObjLenBitSize();
    // BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

    // Count n_new = a_hom.getForestSize() + b_com.getForestSize();
    // Count m_new = b_com.getChildrenNumForCom();
    // Count new_mandatory_labels_num = roaring_bitmap_and_cardinality( 
    //     a_hom.getMandatoryLabelBitmap(),
    //     b_com.getMandatoryLabelBitmap()
    // );
    //     // 5.1. Decrease in DRC 
    // drc_delta -= a_hom.getDerivedSchema()->getDRC();
    // drc_delta -= b_com.getDerivedSchema()->getDRC();

    //     // 5.2. Increase in DRC
    //         // Hom part
    // drc_delta += n_new * (all_labels_num - new_mandatory_labels_num);
    //         // Het part : length encoding
    // drc_delta += n_new * length_bit_size;
    //         // Het part : key encoding
    // drc_delta += m_new * kleene_bit_size;


    // merge_info.setDeltaMdl(src_delta + drc_delta);
    merge_info.setDeltaMdl(abs(src_delta));
    merge_info.setMergeClusterType(kComObjC); 
    return 1;   
}




/////////////////////////////////// Com - Com ///////////////////////////////////

int comComClusterDist(InstanceCluster& a_com, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info)
{
    // 1. Check if merging is a viable one
    InstanceTypeSet* a_kleene_types = a_com.getChildrenTypeForCom();
    InstanceTypeSet* b_kleene_types = b_com.getChildrenTypeForCom();

        // Children schemas?
        // Maybe conjunction?
    if(!isEqual(a_kleene_types, b_kleene_types))
    {
        merge_info.setViableBit(false);
        return 1;
    }

    // 2. If viable, then calculate delta(MDL)
    merge_info.setViableBit(true);

    // 3. Aggregate metadata
    LabelToTypeSet label_to_schemas = *a_com.getLabelToTypes();
    for(auto& key_types_pair : *b_com.getLabelToTypes())
    {
        strInt label = key_types_pair.first;
        auto label_to_type_it = label_to_schemas.find(label);
        if(label_to_type_it == label_to_schemas.end())
        { label_to_schemas.insert( {label, key_types_pair.second} ); }
        else
        { label_to_type_it->second.insert(key_types_pair.second.begin(), key_types_pair.second.end()); }
    }
    Count all_labels_num = label_to_schemas.size();


    // 4. Calculate delta SRC
    MDLCost src_delta = 0;
        // 4.1. Decrease in SRC -> SRC of a_het b_het
    src_delta -= a_com.getDerivedSchema()->getSRC();
    src_delta -= b_com.getDerivedSchema()->getSRC();

        // 4.2. Increase in SRC -> SRC of newly-derived schema node

    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();

    int symbol_num = 1 + 4 * all_labels_num + 1 + 2;
    src_delta += symbol_bitsize * symbol_num;
    

    // 5. Calculate delta DRC
    // MDLCost drc_delta = 0;    
    // BitSize length_bit_size = cost_parameters.getObjLenBitSize();
    // BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

    // Count n_new = a_com.getForestSize() + b_com.getForestSize();
    // Count m_new = a_com.getChildrenNumForCom() + b_com.getChildrenNumForCom();
    // Count new_mandatory_labels_num = roaring_bitmap_and_cardinality( 
    //     a_com.getMandatoryLabelBitmap(),
    //     b_com.getMandatoryLabelBitmap()
    // );
    //     // 5.1. Decrease in DRC 
    // drc_delta -= a_com.getDerivedSchema()->getDRC();
    // drc_delta -= b_com.getDerivedSchema()->getDRC();

    //     // 5.2. Increase in DRC
    //         // Hom part
    // drc_delta += n_new * (all_labels_num - new_mandatory_labels_num);
    //         // Het part : length encoding
    // drc_delta += n_new * length_bit_size;
    //         // Het part : key encoding
    // drc_delta += m_new * kleene_bit_size;


    // merge_info.setDeltaMdl(src_delta + drc_delta);
    merge_info.setDeltaMdl(abs(src_delta));
    merge_info.setMergeClusterType(kComObjC);
    return 1;
}




/////////////////////////////////// Com - Het ///////////////////////////////////

int comHetClusterDist(InstanceCluster& a_com, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info)
{   
    // 1. Check if merging is a viable one
    // TODO: childrenSchemaSet -> childrenTypeSet
    // TODO: childrenSchemaForCom -> childrenTypeForCom
    InstanceTypeSet* a_children_types = a_com.getChildrenTypeSet();
    InstanceTypeSet* a_com_types = a_com.getChildrenTypeForCom();
    InstanceTypeSet* b_children_types = b_het.getChildrenTypeSet();

    // 2. Check if this merge is viable
    if(!hasConjunction(a_children_types, b_children_types))
    {
        merge_info.setViableBit(false);
        return 1;
    }
        
    // cout << a_children_schemas->size() << endl;
    // for(auto& child_schema_id : *a_children_schemas)
    // {
    //     cout << child_schema_id << " ";
    // }
    // cout << endl;
    // cout << b_children_schemas->size() << endl;
    // for(auto& child_schema_id : *b_children_schemas)
    // {
    //     cout << child_schema_id << " ";
    // }
    // cout << endl;

    if(isEqual(a_children_types, b_children_types))
    {
        // All same children
        // TARGET: to HET
        merge_info.setMergeClusterType(kHetObjC);

        // 3. Calculate delta SRC
        MDLCost src_delta = 0;
            // 3.1. Decrease in SRC -> SRC of a_com b_het
        src_delta -= a_com.getDerivedSchema()->getSRC();
        src_delta -= b_het.getDerivedSchema()->getSRC();

            // 3.2. Increase in SRC -> SRC of newly-deriving schema
        int symbol_num = 1 + 1 + 2;
        src_delta += symbol_num * cost_parameters.getSchemaBitSize();

        // 4. Calculate delta DRC 
        // MDLCost drc_delta = 0;

        //     // 4.1. Decrease in DRC - a_het b_het
        // drc_delta -= a_com.getDerivedSchema()->getDRC();
        // drc_delta -= b_het.getDerivedSchema()->getDRC();

        //     // 4.2. Increase in DRC - newly-derived schema -> refer to `hetObjDRC`
        // BitSize length_bit_size = cost_parameters.getObjLenBitSize();
        // BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

        // Count n_new = a_com.getForestSize() + b_het.getForestSize();
        // drc_delta += n_new * length_bit_size;

        // Count m_new = a_com.getChildrenNum() + b_het.getChildrenNum();
        // drc_delta += m_new * kleene_bit_size;

        // BitSize choice_bitsize = bitSize( a_children_schemas->size() );
        // drc_delta += m_new * choice_bitsize;

        // merge_info.setDeltaMdl(src_delta + drc_delta);
        merge_info.setDeltaMdl(abs(src_delta));
    }
    else if(isSubset(b_children_types, a_com_types))
    {
        // Het's children are 
        // TARGET: to COM
        merge_info.setMergeClusterType(kComObjC);

        // 3. Aggregate metadata
        Count all_labels_num = a_com.getLabelToTypes()->size();

        MDLCost src_delta = 0;
            // 4.1. Decrease in SRC -> SRC of a_het b_het
        src_delta -= a_com.getDerivedSchema()->getSRC();
        src_delta -= b_het.getDerivedSchema()->getSRC();

            // 4.2. Increase in SRC -> SRC of newly-derived schema node

        BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();

        int symbol_num = 1 + 4 * all_labels_num + 1 + 2;
        src_delta += symbol_bitsize * symbol_num;
        

        // 5. Calculate delta DRC
        // MDLCost drc_delta = 0;    
        // BitSize length_bit_size = cost_parameters.getObjLenBitSize();
        // BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

        // Count n_new = a_com.getForestSize() + b_het.getForestSize();
        // Count m_new = a_com.getChildrenNumForCom() + b_het.getChildrenNumForCom();
        // Count new_mandatory_labels_num = 0;
        //     // 5.1. Decrease in DRC 
        // drc_delta -= a_com.getDerivedSchema()->getDRC();
        // drc_delta -= b_het.getDerivedSchema()->getDRC();

        //     // 5.2. Increase in DRC
        //         // Hom part
        // drc_delta += n_new * (all_labels_num - new_mandatory_labels_num);
        //         // Het part : length encoding
        // drc_delta += n_new * length_bit_size;
        //         // Het part : key encoding
        // drc_delta += m_new * kleene_bit_size;

        // merge_info.setDeltaMdl(src_delta + drc_delta);
        merge_info.setDeltaMdl(abs(src_delta));
    }
    else
    {
        merge_info.setViableBit(false);
        return 1;
    }
    
    merge_info.setViableBit(true);
    return 1;
}































// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// ///////////////////////////////////////////// Cluster Distances (KSE) /////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// mergeInfo KSEDistance(InstanceCluster& cluster_a, InstanceCluster& cluster_b, CostParameters& cost_parameters)
// {
//     SchemaType a_type = cluster_a.getDerivedSchema()->getType();
//     SchemaType b_type = cluster_b.getDerivedSchema()->getType();

//     mergeInfo merge_info;
//     int return_value;

//     switch(a_type)
//     {
//         case kHomObj:
//             switch(b_type)
//             {
//                 case kHomObj:
//                     return_value = homHomKSEClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
//                     break;
//                 case kComObj:
//                     return_value = homComKSEClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
//                     break;
//                 case kHetObj:
//                     return_value = homHetKSEClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
//                     break;
//             }
//             break;

//         case kComObj:
//             switch(b_type)
//             {
//                 case kHomObj:
//                     return_value = homComKSEClusterDist(cluster_b, cluster_a, cost_parameters, merge_info);
//                     break;
//                 case kComObj:
//                     return_value = comComKSEClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
//                     break;
//                 case kHetObj:
//                     return_value = comHetKSEClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
//                     break;
//             }
//             break;

//         case kHetObj:
//             switch(b_type)
//             {
//                 case kHomObj:
//                     return_value = homHetKSEClusterDist(cluster_b, cluster_a, cost_parameters, merge_info);
//                     break;
//                 case kComObj:
//                     return_value = comHetKSEClusterDist(cluster_b, cluster_a, cost_parameters, merge_info);
//                     break;
//                 case kHetObj:
//                     return_value = hetHetKSEClusterDist(cluster_a, cluster_b, cost_parameters, merge_info);
//                     break;
//             }
//             break;
//     }

//     if(return_value != 1)
//     { throw IllegalBehaviorError("clusterDistance - unexpected return"); }
    

//     return merge_info;
// }


// /////////////////////////////////// Hom - Hom ///////////////////////////////////

// int homHomKSEClusterDist(InstanceCluster& a_hom, InstanceCluster& b_hom, CostParameters& cost_parameters, mergeInfo& merge_info)
// {
//     // 1. Check if merging is a viable one
//     roaring_bitmap_t* a_labels = a_hom.getDistinctLabels();
//     roaring_bitmap_t* b_labels = b_hom.getDistinctLabels();

//         // viable: Are there any common labels?
//     int and_result = roaring_bitmap_and_cardinality(a_labels, b_labels);

//     if(!and_result)
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }
    
//     // 2. If viable, then calculate delta(MDL)
//     merge_info.setViableBit(true);

//     // TODO: Calculate delta SRC
//     MDLCost distance = calculateKSEForTwoClusters(a_hom, b_hom, cost_parameters);

//     merge_info.setDeltaMdl(abs(distance));
//     merge_info.setMergeClusterType(kHomObjC);

//     return 1;
// }




// /////////////////////////////////// Hom - Het ///////////////////////////////////

// int homHetKSEClusterDist(InstanceCluster& a_hom, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info)
// {
//     // 1. Check if merging is a viable one
//     SchemaSet* a_children_schemas = a_hom.getChildrenTypeSet();
//     SchemaSet* b_children_schemas = b_het.getChildrenTypeSet();

//         // viable: Are the children schemas same?
//     if(!isEqual(a_children_schemas, b_children_schemas))
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }
    
//     // 2. If viable, then calculate delta(MDL)
//     merge_info.setViableBit(true);
    
//     MDLCost distance = calculateKSEForTwoClusters(a_hom, b_het, cost_parameters);

//     merge_info.setDeltaMdl(abs(distance));
//     merge_info.setMergeClusterType(kHetObjC);
//     return 1;
// }





// /////////////////////////////////// Het - Het ///////////////////////////////////

// int hetHetKSEClusterDist(InstanceCluster& a_het, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info)
// {
//     // 1. Check if merging is a viable one
//     SchemaSet* a_children_schemas = a_het.getChildrenTypeSet();
//     SchemaSet* b_children_schemas = b_het.getChildrenTypeSet();

//         // Are there any common children schemas?
//     if(!hasConjunction(a_children_schemas, b_children_schemas))
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }

//     // 2. If viable, then calculate delta(MDL)
//     merge_info.setViableBit(true);

//     MDLCost distance = calculateKSEForTwoClusters(a_het, b_het, cost_parameters);

//     merge_info.setDeltaMdl(abs(distance));
//     merge_info.setMergeClusterType(kHetObjC);
//     return 1;
// }




// /////////////////////////////////// Hom - Com ///////////////////////////////////

// int homComKSEClusterDist(InstanceCluster& a_hom, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info)
// {
//     // 1. Check if merging is a viable one
//     roaring_bitmap_t* a_labels = a_hom.getDistinctLabels();
//     roaring_bitmap_t* b_labels = b_com.getDistinctLabels();

//     // TARGET: to COM

//         // Are there any common labels?
//     int and_result = roaring_bitmap_and_cardinality(a_labels, b_labels);

//     if(!and_result)
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }

//         // Are there any common children schemas?
//     SchemaSet* a_children_schemas = a_hom.getChildrenTypeSet();
//     SchemaSet* b_children_schemas = b_com.getChildrenTypeSet();

//     if(!hasConjunction(a_children_schemas, b_children_schemas))
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }

//     // 2. If viable, then calculate delta(MDL)
//     merge_info.setViableBit(true);

//     MDLCost distance = calculateKSEForTwoClusters(a_hom, b_com, cost_parameters);

//     merge_info.setDeltaMdl(abs(distance));
//     merge_info.setMergeClusterType(kComObjC); 
//     return 1;   
// }




// /////////////////////////////////// Com - Com ///////////////////////////////////

// int comComKSEClusterDist(InstanceCluster& a_com, InstanceCluster& b_com, CostParameters& cost_parameters, mergeInfo& merge_info)
// {
//     // 1. Check if merging is a viable one
//     SchemaSet* a_kleene_schemas = a_com.getChildrenTypeForCom();
//     SchemaSet* b_kleene_schemas = b_com.getChildrenTypeForCom();

//         // Children schemas?
//         // Maybe conjunction?
//     if(!isEqual(a_kleene_schemas, b_kleene_schemas))
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }

//     // 2. If viable, then calculate delta(MDL)
//     merge_info.setViableBit(true);

//     MDLCost distance = calculateKSEForTwoClusters(a_com, b_com, cost_parameters);

//     merge_info.setDeltaMdl(abs(distance));
//     merge_info.setMergeClusterType(kComObjC);
//     return 1;
// }




// /////////////////////////////////// Com - Het ///////////////////////////////////

// int comHetKSEClusterDist(InstanceCluster& a_com, InstanceCluster& b_het, CostParameters& cost_parameters, mergeInfo& merge_info)
// {   
//     // 1. Check if merging is a viable one
//     SchemaSet* a_children_schemas = a_com.getChildrenTypeSet();
//     SchemaSet* a_com_schemas = a_com.getChildrenTypeForCom();
//     SchemaSet* b_children_schemas = b_het.getChildrenTypeSet();

//     // 2. Check if this merge is viable
//     if(!hasConjunction(a_children_schemas, b_children_schemas))
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }
        
//     if(isEqual(a_children_schemas, b_children_schemas) || isSubset(b_children_schemas, a_com_schemas))
//     {
//         MDLCost distance = calculateKSEForTwoClusters(a_com, b_het, cost_parameters);
        
//         merge_info.setDeltaMdl(abs(distance));
//         merge_info.setMergeClusterType(kHetObjC);
//     }
//     else
//     {
//         merge_info.setViableBit(false);
//         return 1;
//     }
    
//     merge_info.setViableBit(true);
//     return 1; 
// }


// MDLCost calculateKSEForTwoClusters(InstanceCluster& a, InstanceCluster& b, CostParameters& cost_parameters)
// {
//     // 1. Initiate a vector that counts each label
//     strInt distinct_labels_num = cost_parameters.getDistinctLabelsNum();
//     vector<Count> label_to_count_a(distinct_labels_num, 0);
//     vector<Count> label_to_count_b(distinct_labels_num, 0);
//     vector<Count> label_to_count_both(distinct_labels_num, 0);

//     // 2. Count the number of each label
//     for(auto& instance : *a.getInstanceForest())
//     {
//         for(auto& label : instance->getStringLabels())
//         { 
//             label_to_count_a[label]++;
//             label_to_count_both[label]++;
//         }
//     }

//     for(auto& instance : *b.getInstanceForest())
//     {
//         for(auto& label : instance->getStringLabels())
//         { 
//             label_to_count_b[label]++;
//             label_to_count_both[label]++;
//         }
//     }

//     // 3. Calculate entropy
//     MDLCost entropy_a = 0;
//     MDLCost entropy_b = 0;
//     MDLCost entropy_both = 0;
//     for(auto& count : label_to_count_a)
//     {
//         if(count != 0)
//         {
//             double p = (double)count / a.getForestSize();
//             entropy_a += -p * log2(p);
//         }
//     }
//     for(auto& count : label_to_count_b)
//     {
//         if(count != 0)
//         {
//             double p = (double)count / b.getForestSize();
//             entropy_b += -p * log2(p);
//         }
//     }
//     for(auto& count : label_to_count_both)
//     {
//         if(count != 0)
//         {
//             double p = (double)count / (a.getForestSize() + b.getForestSize());
//             entropy_both += -p * log2(p);
//         }
//     }

//     return entropy_a + entropy_b - entropy_both;
// }