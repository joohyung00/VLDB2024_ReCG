#include "Cost.hpp"


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////// MDL COST ///////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Hom Obj Cost ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

MDLCost homObjSRC(InstanceCluster& hom_obj_cluster, CostParameters& cost_parameters)
{
    // 1. Bitsize of a symbol
    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();

    // 2. Number of symbols
    int labels_num = hom_obj_cluster.getLabelsToSchemas()->size();
    int symbol_num = 1 + 4 * labels_num;
    
    return symbol_bitsize * symbol_num;
}

MDLCost homObjDRC(InstanceCluster& hom_obj_cluster, CostParameters& cost_parameters)
{
    // n
    int n = hom_obj_cluster.getForestSize();
    int opt_labels_num = hom_obj_cluster.getDistinctLabelsNum() - hom_obj_cluster.getMandatorylabelsNum();

    return n * opt_labels_num;
}


//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Het Obj Cost ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

MDLCost hetObjSRC(InstanceCluster& het_obj_cluster, CostParameters& cost_parameters)
{
    // 1. Bitsize of a symbol
    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();

    // 2. Number of symbols
    int symbol_num = 1 + 1 + 2;

    return symbol_bitsize * symbol_num;
}

MDLCost hetObjDRC(InstanceCluster& het_obj_cluster, CostParameters& cost_parameters)
{
    // Copied to distance.cpp -> homHetDistance
    MDLCost drc = 0;

    // 1. Calculate bit size for each case
    BitSize length_bit_size = cost_parameters.getObjLenBitSize();
    BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

    // 2. DRC for length(number of key-value pairs)-encoding
    Count n = het_obj_cluster.getInstanceForest()->size();
    drc += n * length_bit_size;

    // 3. DRC for each key encoding
    Count m = het_obj_cluster.getChildrenNum();
    drc += m * kleene_bit_size;

    return drc;
}


//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Com Obj Cost ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////


MDLCost comObjSRC(InstanceCluster& com_obj_cluster, CostParameters& cost_parameters)
{
    // 1. Bitsize of a symbol
    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();

    // 2. Number of symbols
    int labels_num = com_obj_cluster.getLabelsToSchemas()->size();
    int symbol_num = 1 + 4 * labels_num + 1 + 2;
    
    return symbol_bitsize * symbol_num;
}

MDLCost comObjDRC(InstanceCluster& com_obj_cluster, CostParameters& cost_parameters)
{
    // 1. DRC for hom-part
        // 1.1. n := number of instances
    int n = com_obj_cluster.getForestSize();
        // 1.2. number of optional labels
    int opt_labels_num = com_obj_cluster.getDistinctLabelsNum() - com_obj_cluster.getMandatorylabelsNum();

    MDLCost hom_part_drc = n * opt_labels_num;

    // 2. DRC for het-part
    MDLCost het_part_drc = 0;

        // 2.1. Bit-encoding size for each case
    BitSize length_bit_size = cost_parameters.getObjLenBitSize();
    BitSize kleene_bit_size = cost_parameters.getKleeneEncodingBitSize();

        // 2.2. DRC for length(number of additional key-value pairs)-encoding
    het_part_drc += n * length_bit_size;

        // 2.3. DRC for each key encoding
    int m = com_obj_cluster.getChildrenNumForCom();
    het_part_drc += m * kleene_bit_size;

    return hom_part_drc + het_part_drc;
}



//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Hom Arr Cost ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

MDLCost homArrSRC(InstanceCluster& hom_arr_cluster, CostParameters& cost_parameters)
{
    // 1. Bitsize of a symbol
    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();
    
    // 2. Number of symbols
    int sch_children_num = hom_arr_cluster.getChildrenSchemaSeq()->size();
    int symbol_num = 1 + 2 * sch_children_num;

    return symbol_bitsize * symbol_num;
}

MDLCost homArrDRC(InstanceCluster& hom_arr_cluster, CostParameters& cost_parameters)
{
    return 0;
}



//////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// Het Arr Cost ////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////

MDLCost hetArrSRC(InstanceCluster& het_arr_cluster, CostParameters& cost_parameters)
{
    // 1. Bitsize of a symbol
    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();
    
    // 2. Number of symbols
    int symbol_num = 3;

    return symbol_bitsize * symbol_num;
}

MDLCost hetArrDRC(InstanceCluster& het_arr_cluster, CostParameters& cost_parameters)
{
    MDLCost data_cost = 0;

    using length = int;
    using Count = int;

    // 1. Calculate bit size
    BitSize length_bit_size = cost_parameters.getArrLenBitSize();

    // 2. DRC for length(number of key-value pairs)-encoding
    int n = het_arr_cluster.getForestSize();
    data_cost += n * length_bit_size;

    return data_cost;
}


////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// AnyOf Cost ////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////


MDLCost anyOfSRC(SchemaNode* any_of, CostParameters& cost_parameters, int instance_num)
{
    BitSize symbol_bitsize = cost_parameters.getSchemaBitSize();

    int symbol_num = 1 + 2 * any_of->getChildrenNum();

    return symbol_bitsize * symbol_num; 
}

MDLCost anyOfDRC(SchemaNode* any_of, CostParameters& cost_parameters, int instance_num)
{
    BitSize choice_size = bitSize( any_of->getChildrenNum() );

    return instance_num * choice_size;
}







////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////// KSE COST ///////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

MDLCost homObjKSE(SchemaNode* schema, InstanceCluster& cluster, CostParameters& cost_parameters)
{
    // 1. Initiate a vector that counts each label
    strInt distinct_labels_num = cost_parameters.getDistinctLabelsNum();
    vector<Count> label_to_count(distinct_labels_num, 0);
    Count kleene_count = 0;

    // 2. Count the number of each label
    for(auto& instance : *cluster.getInstanceForest())
    {
        for(auto& label : instance->getStringLabels())
        { label_to_count[label]++; }
        if(roaring_bitmap_get_cardinality(instance->getKleenedLabels()))
        { kleene_count++; }
    }

    // 3. Calculate entropy
    MDLCost entropy = 0;
    for(auto& label : schema->getStringLabels())
    {
        if(label_to_count[label] != 0)
        {
            double p = (double)label_to_count[label] / cluster.getForestSize();
            entropy += p * log2(p);
        }
    }
    if(schema->getKleeneChild() != nullptr)
    {
        double p = (double)kleene_count / cluster.getForestSize();
        entropy += -p * log2(p);
    }

    return entropy;
}

MDLCost hetObjKSE(SchemaNode* schema, InstanceCluster& cluster, CostParameters& cost_parameters)
{
    return homObjKSE(schema, cluster, cost_parameters);
}

MDLCost comObjKSE(SchemaNode* schema, InstanceCluster& cluster, CostParameters& cost_parameters)
{
    return homObjKSE(schema, cluster, cost_parameters);
}

MDLCost homArrKSE(SchemaNode* schema, InstanceCluster& cluster, CostParameters& cost_parameters)
{
    if(schema->getKleeneChild() != nullptr)
    { return 0; }

    // 1. Initiate a vector that counts each length
    strInt max_arr_len = cost_parameters.getMaxArrLen();
    vector<Count> arr_len_to_count(max_arr_len + 1, 0);

    // 2. Count the number of each length
    for(auto& instance : *cluster.getInstanceForest())
    { arr_len_to_count[instance->getChildrenNum()]++; }

    // 3. Calculate entropy
    MDLCost entropy = 0;
    for(auto& count : arr_len_to_count)
    {
        if(count != 0)
        {
            double p = (double)count / cluster.getForestSize();
            entropy += -p * log2(p);
        }
    }

    return entropy;
}

MDLCost hetArrKSE(SchemaNode* schema, InstanceCluster& cluster, CostParameters& cost_parameters)
{
    return homArrKSE(schema, cluster, cost_parameters);
}

MDLCost anyOfKSE(SchemaNode* any_of, int instance_num)
{
    return 0;
}