#include "Darwin.hpp"


void Darwin::run()
{
    // 1. Initiate
    cout << "[(1) Initiator Starting...]" << endl;
    auto initiate_start = high_resolution_clock::now();

    runInitiator();

    auto initiate_end = high_resolution_clock::now();
    auto initiate_total = duration_cast<milliseconds>(initiate_end - initiate_start);
    cout << "    Initiating Time: " << initiate_total.count() << " ms" << endl;
    cout << "[(1) Initiator Complete]" << endl << endl;


    // 2. Discover schema
    auto rs_constr_start = high_resolution_clock::now();
    cout << "[(2) Constructing Raw Schemas]" << endl;

    constructRawSchemas();

    auto rs_constr_end = high_resolution_clock::now();
    auto rs_constr_total = duration_cast<milliseconds>(rs_constr_end - rs_constr_start);
    cout << "    Raw Schema Construction Time: " << rs_constr_total.count() << " ms" << endl;
    cout << "[(2) Constructing Raw Schemas Complete]" << endl << endl; 



    // 3. Aggregate Raw Schemas
    auto rs_aggr_start = high_resolution_clock::now();
    cout << "[(3) Aggregating Raw Schemas]" << endl;

    aggregateRawSchemas();

    auto rs_aggr_end = high_resolution_clock::now();
    auto rs_aggr_total = duration_cast<milliseconds>(rs_aggr_end - rs_aggr_start);
    cout << "    Raw Schema Aggregation Time: " << rs_aggr_total.count() << " ms" << endl;
    cout << "[(3) Aggregating Raw Schemas Complete]" << endl << endl; 



    // 4. RSUS Construction
    auto rsus_constr_start = high_resolution_clock::now();
    cout << "[(4) RSUS Construction]" << endl;

    unionIntoRSUS();

    auto rsus_constr_end = high_resolution_clock::now();
    auto rsus_constr_total = duration_cast<milliseconds>(rsus_constr_end - rsus_constr_start);
    cout << "    RSUS Construction Time: " << rsus_constr_total.count() << " ms" << endl;
    cout << "[(4) RSUS Construction Complete]" << endl << endl;


    // 5. Printing schema in string
    auto sch_print_start = high_resolution_clock::now();
    cout << "[(5) RSUS Construction]" << endl;

    printSchema();

    auto sch_print_end = high_resolution_clock::now();
    auto sch_print_total = duration_cast<milliseconds>(sch_print_end - sch_print_start);
    cout << "    RSUS Construction Time: " << sch_print_total.count() << " ms" << endl;
    cout << "[(5) RSUS Construction Complete]" << endl << endl;


    cout << endl << "    (({{[[ TOTAL ELAPSED TIME : " << 
        initiate_total.count() + rs_constr_total.count() + rs_aggr_total.count() + rsus_constr_total.count() + sch_print_total.count() << 
        " ms" << " ]]}}))" << endl << endl;
}



void Darwin::runInitiator()
{ 
    initiator_.initiateInstanceManager(input_filepath_); 
    #if VERBOSE
        initiator_.printData();
        cout << "----------------------------------------" << endl;
    #endif
}



void Darwin::constructRawSchemas()
{
    raw_schema_constructor_.setInstanceForest(&(initiator_.getInstanceForest()));
    raw_schema_constructor_.setRawSchemas(&raw_schemas_);

    // cout << "Raw Schema #: " << raw_schemas_.size() << endl;

    raw_schema_constructor_.constructRawSchemas();

    cout << endl << endl;
    #if VISUALIZETREE
        (*(raw_schemas_.rbegin()))->visualizeSchemaTree(0);
    #endif
    cout << "Raw Schema #: " << raw_schemas_.size() << endl;

    #if VERBOSE
        cout << "Raw Schemas Constructed: " << raw_schemas_->size() << endl;
    #endif
}

void Darwin::aggregateRawSchemas()
{
    raw_schema_aggregator_.setRawSchemas(&raw_schemas_);
    raw_schema_aggregator_.setCountPerRawSchema(&count_per_raw_schema_);
    raw_schema_aggregator_.setUniqueRawSchemas(&unique_raw_schemas_);

    cout << "[START] Unique Raw Schema #: " << unique_raw_schemas_.size() << endl;

    raw_schema_aggregator_.aggregateRawSchemas();

    #if VISUALIZETREE
        unique_raw_schemas_.back()->visualizeSchemaTree(0);
    #endif

    cout << "[ END ] Unique Raw Schema #: " << unique_raw_schemas_.size() << endl;
}

void Darwin::unionIntoRSUS()
{
    rsus_constructor_.setUniqueRawSchemas(&unique_raw_schemas_);
    rsus_constructor_.setCountPerRawSchema(&count_per_raw_schema_);
    rsus_constructor_.constructRSUS();

    rsus_ = rsus_constructor_.getRSUS();
    cout << "RSUS Constructed!" << endl;

    #if VISUALIZETREE
        rsus_->visualizeSchemaTree(0);
    #endif
}



void Darwin::printSchema()
{
    // rg_tree_->visualizeSchemaTree(0);
    initiator_.toString(rsus_, discovered_schema_, kRefAsSchema);

    std::ofstream output_file(output_filepath_);

    if (output_file.is_open()) 
    {
        // cout << *discovered_schema_ << endl;
        output_file << *discovered_schema_ << endl;
        output_file.close(); 
        cout << endl << "Schema printed to the file successfully!" << std::endl;
    } 
    else 
    {
        cerr << "Error: Unable to open the file." << std::endl;
    }
    return;
}