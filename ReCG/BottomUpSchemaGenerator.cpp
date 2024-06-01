#include "BottomUpSchemaGenerator.hpp"



StateMaterials BottomUpSchemaGenerator::deriveNextSchema()
{
    StateMaterials new_state_materials;

    // 1. Cluster-related behavior
    if(derivation_phase_ == kClusteringPhase)
    {
        ////**  Clustering Phase  **////

        clusterAllGenericTypes();
        clusterAndGeneralizeObjects();

        derivation_phase_ = kMergingPhase;
		    setInitialDistanceCalculationTargets();

        ////**  Clustering Phase  **////
    }
    else if(derivation_phase_ == kMergingPhase)
    {
        ////**  Merging Phase  **////

        // 2.1. Try a merge
        bool merged = mergeToGeneralize();
        
        // 2.2. If not merged
        if(!merged)
        {
            # if VERBOSE
              printHeader();
              cout << "[Deriver] No Merge & Generalize Happened" << endl;
            #endif

            // 2.3. Free resources for clusters
                // This state(bottomUpSchemaGenerator) does not need resources anymore
            for(auto instance_cluster : object_clusters_)
                instance_cluster.freeResources();
            for(auto instance_cluster : array_clusters_)
                instance_cluster.freeResources();

            // 2.4. Return no more derivation to stateNode -> end loop in `transitions`
            new_state_materials.setDerivationResult(kNoMoreDerivation);
            return new_state_materials;
        }

        ////**  Merging Phase  **////
    }
    else 
        IllegalBehaviorError("BottomUpSchemaGenerator::deriveNextSchema - Illegal State");

    // 3. Derive schemas from each cluster
        // 3.1. Derive schema(recorded in each instances)
    deriveSchemasFromClusters();
    new_state_materials.setStateId(BottomUpSchemaGenerator::unique_state_id_);
    BottomUpSchemaGenerator::unique_state_id_++;
    
    #if VERBOSE
      printHeader();
      cout << "Derived Schema Nodes #: " << derived_schemas_.size() << endl;
    #endif

    // 4. Return state information(`state_id`) to generate that state
    new_state_materials.setDerivationResult(kDerived);
    return new_state_materials;
}


/////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////// Cluster & Generalize Step /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////






void BottomUpSchemaGenerator::clusterAllGenericTypes()
{
    #if VERBOSE
      printHeader();
      cout << "Object # : " << grouped_instances_->getInstanceForestByType(kObject).size() << endl;
      printHeader();
      cout << "Array size: " << grouped_instances_->getInstanceForestByType(kArray).size() << endl;
      printHeader();
      cout << endl;
    #endif

    InstanceForest& array_forest = grouped_instances_->getInstanceForestByType(kArray);
    if(array_forest.size() > 0)
    {
        generalizeAndClusterArrays();
    }
 
    return;
}


// Object Clustering in `BottomUpSchemaGenerator_Object.cpp`
// Array  Clustering in `BottomUpSchemaGneerator_Array.cpp`
// Merging           in `BottomUpSchemaGenerator_Merge.cpp`

void BottomUpSchemaGenerator::deriveSchemasFromClusters()
{
    derived_schemas_.clear();
    //////////////////////////////////////////////////////////////////////////////////////////////////
    // Derive Schemas for Objects from Object Clusters
    //////////////////////////////////////////////////////////////////////////////////////////////////

    int object_num = grouped_instances_->getInstanceForestByType(kObject).size();
    int mapped_object_num = 0;

    #if VERBOSE
      printHeader();
      cout << endl;
      printHeader();
      cout << "[OBJECTS]" << endl;
      printHeader();
      cout << "Object Cluster #: " << object_clusters_.size() << endl;
    #endif

    #if VERBOSE2
      int cluster_num = 1;
    #endif

    for(auto& object_cluster : object_clusters_)
    {
        SchemaNode* derived_schema = deriveSchemaFromCluster(object_cluster, cost_parameters_, recg_parameters_);
        assert(derived_schema != nullptr);

        mapInstancesForState(unique_state_id_, object_cluster.getInstanceForest(), derived_schema);
        
        derived_schemas_.push_back(derived_schema);

        mapped_object_num += object_cluster.getForestSize();

        #if VERBOSE2
          printHeader();
          cout << "| #" << cluster_num++ << " (" << object_cluster.getTypeInString() << "): " << object_cluster.getForestSize() << endl;
          printHeader();
          cout << "|-| [SC] " <<  object_cluster.getDerivedSchema()->getSRC() << "\t[DC] " << object_cluster.getDerivedSchema()->getDRC() << endl;
        #endif
    }

    #if VERBOSE
      printHeader();
      cout << "Derived Objects #: " << mapped_object_num << endl;
    #endif

    #if VERBOSE
      assert(mapped_object_num == object_num);
    #endif

    //////////////////////////////////////////////////////////////////////////////////////////////////
    // Derive Schemas for Objects from Object Clusters
    //////////////////////////////////////////////////////////////////////////////////////////////////

    int array_num = grouped_instances_->getInstanceForestByType(kArray).size();
    int mapped_array_num = 0;

    #if VERBOSE
      printHeader();
      cout << endl;
      printHeader();
      cout << "[ARRAYS]" << endl;
      printHeader();
      cout << "Array Cluster #: " << array_clusters_.size() << endl;
      printHeader();
      cout << endl;
    #endif

    #if VERBOSE2
      cluster_num = 1;
    #endif

    for(auto& array_cluster : array_clusters_)
    {
        SchemaNode* derived_schema = deriveSchemaFromCluster(array_cluster, cost_parameters_, recg_parameters_);
        assert(derived_schema != nullptr);

        mapInstancesForState(unique_state_id_, array_cluster.getInstanceForest(), derived_schema);
        
        derived_schemas_.push_back(derived_schema);

        mapped_array_num += array_cluster.getForestSize();

        #if VERBOSE2
          printHeader();
          cout << "| #" << cluster_num++ << " (" << array_cluster.getTypeInString() << "): " << array_cluster.getForestSize() << endl;
        #endif
    }

    #if VERBOSE
      printHeader();
      cout << "Derived Arrays #: " << mapped_array_num << endl;
    #endif

    #if VERBOSE
      assert(mapped_array_num == array_num);
    #endif

    //////////////////////////////////////////////////////////////////////////////////////////////////
    // Derive and Map Schemas for Primitive Types
    //////////////////////////////////////////////////////////////////////////////////////////////////

    InstanceForest& number_forest = grouped_instances_->getInstanceForestByType(kNumber);
    if(number_forest.size() > 0)
    {
        SchemaNode* number_schema = new SchemaNode(kNum);

        mapInstancesForState(unique_state_id_, number_forest, number_schema);

        derived_schemas_.push_back(number_schema);
    }

    InstanceForest& string_forest = grouped_instances_->getInstanceForestByType(kString);
    if(string_forest.size() > 0)
    {
        SchemaNode* string_schema = new SchemaNode(kStr);

        mapInstancesForState(unique_state_id_, string_forest, string_schema);

        derived_schemas_.push_back(string_schema);
    }

    InstanceForest& bool_forest = grouped_instances_->getInstanceForestByType(kBoolean);
    if(bool_forest.size() > 0)
    {
        SchemaNode* bool_schema = new SchemaNode(kBool);

        mapInstancesForState(unique_state_id_, bool_forest, bool_schema);

        derived_schemas_.push_back(bool_schema);
    }

    InstanceForest& null_forest = grouped_instances_->getInstanceForestByType(kNull_);
    if(null_forest.size() > 0)
    {
        SchemaNode* null_schema = new SchemaNode(kNull);

        mapInstancesForState(unique_state_id_, null_forest, null_schema);

        derived_schemas_.push_back(null_schema);
    }
}









void BottomUpSchemaGenerator::printHeader()
{
    int times = max_depth_ - current_depth_;

    cout << "="; 
    for(int i = 0; i < times; i++)
    {
        cout << "====";
    }
    cout << "| "; 
}

void mapInstancesForState(stateId state_id, InstanceForest& instance_forest, SchemaNode* derived_schema)
{
    for(auto& instance : instance_forest)
    {
        instance->setDerivedSchemaForState(state_id, derived_schema);
    }
}
void mapInstancesForState(stateId state_id, InstanceForest* instance_forest, SchemaNode* derived_schema)
{
    for(auto& instance : *instance_forest)
    {
        instance->setDerivedSchemaForState(state_id, derived_schema);
    }
}
