#include "ReCG.hpp"



void Klettke::printParameters()
{
    cout << endl;
    cout << "  ------------------------------------------------"  << endl;
    cout << "  [Parameters]" << endl;
    cout << "  Input File Path: \t"     << input_filepath_ << endl;
    cout << "  Output File Path: \t"    << output_filepath_ << endl;
    cout << "  Search Algorithm: \t"    << searchAlgToString(search_alg_) << endl;
    cout << "  Beam Width: \t\t"        << beam_width_ << endl;
    cout << "  Epsilon: \t\t"           << recg_parameters_->getEpsilon() << endl;
    cout << "  MinPts Percentage: \t"   << recg_parameters_->getMinPtsPerc() << "%" << endl;
    cout << "  Sample Size: \t\t"       << recg_parameters_->getSampleSize() << endl;
    cout << "  SRC Weight: \t\t"        << recg_parameters_->getSrcWeight() << endl;
    cout << "  DRC Weight: \t\t"        << recg_parameters_->getDrcWeight() << endl;
    cout << "  ------------------------------------------------"  << endl << endl;
}

void Klettke::run()
{
    // 1. Initiate
        // Parse .jsonl files
        // Generate instance nodes
    printParameters();


    cout << "[Initiator Starting...]" << endl;
    auto initiate_start = high_resolution_clock::now();

    runInitiator();

    auto initiate_end = high_resolution_clock::now();
    auto initiate_total = duration_cast<milliseconds>(initiate_end - initiate_start);
    cout << "    Initiating Time: " << initiate_total.count() << " ms" << endl;
    cout << "[Initiator Complete]" << endl << endl;


    // 2. Discover schema
    cout << "[Discovering Schema...]" << endl;
    cout << endl << "  ================================================"  << endl;
    cout <<         "  ================================================"  << endl << endl;
    auto discover_start = high_resolution_clock::now();

    discoverSchema();

    auto discover_end = high_resolution_clock::now();
    auto discover_total = duration_cast<milliseconds>(discover_end - discover_start);
    cout << endl << "  ================================================"  << endl;
    cout <<         "  ================================================"  << endl << endl;
    cout << "    Discovering Time: " << discover_total.count() << " ms" << endl;
    cout << "[Discovering Schema Complete]" << endl << endl;


    // 3. Discover schema
    printSchema();

    cout << endl << "    (({{[[ TOTAL ELAPSED TIME : " << initiate_total.count() + discover_total.count() << " ms" << " ]]}}))" << endl << endl;
}







void Klettke::runInitiator()
{ 
    initiator_.initiateInstanceManager(input_filepath_); 
    #if VERBOSE
        initiator_.printData();

        cout << "----------------------------------------" << endl;
    #endif
}








void Klettke::discoverSchema()
{
    int lowest_depth = initiator_.getInstanceManager().size() - 1;

    if(search_alg_ == kBranchAndBound)
    {
        cout << "//////////////////////." << endl;
        cout << "// BRANCH AND BOUND //" << endl;
        cout << "//////////////////////" << endl << endl;
        searchBranchAndBound();
    }
    else if(search_alg_ == kKBeam)
    {
        cout << "///////////////////" << endl;
        cout << "// KBEAM SERCH  //" << endl;
        cout << "// BEAM WIDTH: " << beam_width_ << " //" << endl;
        cout << "///////////////////" << endl << endl;
        searchKBeam();
    }
    else if(search_alg_ == kGreedy)
    {   
        cout << "///////////////////" << endl;
        cout << "// GREEDY SEARCH //" << endl;
        cout << "///////////////////" << endl << endl;
        searchGreedy();
    }
    else
    { throw IllegalBehaviorError("Klettke::discoverSchema - undefined search mode"); }
}


void Klettke::searchKBeam()
{
    StateNode* initial_state = setInitialState();

    StateNode* discovered_state = kBeamSearch(initial_state, beam_width_);

    SchemaNode* final_schema = discovered_state->getFinalSchema();

    // final_schema->visualizeSchemaTree(0);

    initiator_.findConvergingNodes(final_schema);
    initiator_.toString(final_schema, discovered_schema_, kRefAsRef);
    initiator_.definitionToString(discovered_schema_);
}



void Klettke::searchBranchAndBound()
{
    int lowest_depth = initiator_.getInstanceManager().size() - 1;
    int beam_width;

    StateNode* initial_state = setInitialState();

    if(lowest_depth < 5)
    { beam_width = 100; }
    else if(lowest_depth < 7)
    { beam_width = 3; }
    else
    { beam_width = 2; }
    cout << "BEAM WIDTH: " << beam_width << endl;

    StateNode* discovered_state = branchAndBoundSearch(initial_state, beam_width);

    initiator_.findConvergingNodes(discovered_state->getFinalSchema());
    initiator_.toString(discovered_state->getFinalSchema(), discovered_schema_, kRefAsRef);
    initiator_.definitionToString(discovered_schema_);
}

void Klettke::searchGreedy()
{

    StateNode* initial_state = setInitialState();

    StateNode* discovered_state = greedySearch(initial_state);

    initiator_.findConvergingNodes(discovered_state->getFinalSchema());
    initiator_.toString(discovered_state->getFinalSchema(), discovered_schema_, kRefAsRef);
    initiator_.definitionToString(discovered_schema_);
}



StateNode* Klettke::setInitialState()
{
    int lowest_depth = initiator_.getInstanceManager().size() - 1;

    // Initialize initial state
    StateNode* initial_state = new StateNode(
        0,
        0,
        lowest_depth, 
        CostParameters(
            initiator_.getDistinctLabelsNum(),
            initiator_.getMaxObjLen(),
            initiator_.getMaxArrLen()
        ),
        initiator_.getInstanceManager(),
        recg_parameters_
    );

    // Set MDL Cost of initial state
    initial_state->setWeightedMDLCost(0);

    return initial_state;
}











void Klettke::printSchema() const
{
    std::ofstream output_file(output_filepath_);

    if (output_file.is_open()) 
    {
        // cout << *discovered_schema_ << endl;
        output_file << *discovered_schema_ << endl;
        output_file.close(); 
        cout << "String printed to the file successfully!" << std::endl;
    } 
    else 
    {
        cerr << "Error: Unable to open the file." << std::endl;
    }
    return;
}
