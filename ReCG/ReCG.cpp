#include "ReCG.hpp"



void ReCG::run()
{
    // 1. Initiate
        // Parse .jsonl files
        // Generate instance nodes
    cout << "  [Running Initiator...]" << endl;
    auto initiate_start = high_resolution_clock::now();

    runInitiator();

    auto initiate_end = high_resolution_clock::now();
    auto initiate_total = duration_cast<milliseconds>(initiate_end - initiate_start);
    cout << "  Initiating Time: " << initiate_total.count() << endl;
    cout << "  [Run Initiator Complete]" << endl << endl;


    // 2. Discover schema
    cout << "  [Discovering Schema...]" << endl;
    auto discover_start = high_resolution_clock::now();

    discoverSchema();

    auto discover_end = high_resolution_clock::now();
    auto discover_total = duration_cast<milliseconds>(discover_end - discover_start);
    cout << "  Discovering Time: " << discover_total.count() << endl;
    cout << "  [Discovering Schema Complete]" << endl << endl;


    // 3. Discover schema
    printSchema();

    cout << endl << "\t(({{[[ TOTAL ELAPSED TIME : " << initiate_total.count() + discover_total.count() << " ]]}}))" << endl << endl;
}


void ReCG::runInitiator()
{ 
    initiator_.initiateInstanceManager(input_filepath_); 
    #if VERBOSE
        initiator_.printData();

        cout << "----------------------------------------" << endl;
    #endif
}


void ReCG::discoverSchema()
{
    int lowest_depth = initiator_.getInstanceManager().size() - 1;

    if(search_mode_ == kBranchAndBound)
    {
        cout << "//////////////////////." << endl;
        // cout << "// MAX DEPTH:  " << lowest_depth << "    //" << endl;
        cout << "// BRANCH AND BOUND //" << endl;
        cout << "//////////////////////" << endl << endl;
        searchBranchAndBound();
    }
    else if(search_mode_ == kKBeam)
    {
        cout << "///////////////////" << endl;
        // cout << "// MAX DEPTH: " << lowest_depth << " //" << endl;
        cout << "// KBEAM SERCH  //" << endl;
        cout << "// BEAM SIZE: " << beam_size_ << " //" << endl;
        cout << "///////////////////" << endl << endl;
        searchKBeam();
    }
    else if(search_mode_ == kGreedy)
    {   
        cout << "///////////////////" << endl;
        // cout << "// MAX DEPTH: " << lowest_depth << " //" << endl;
        cout << "// GREEDY SEARCH //" << endl;
        cout << "///////////////////" << endl << endl;
        searchGreedy();
    }
    else
    {
        throw IllegalBehaviorError("ReCG::discoverSchema - illegal search mode");
    }
}


void ReCG::searchKBeam()
{
    int lowest_depth = initiator_.getInstanceManager().size() - 1;

    // Initialize initial state
    StateNode* initial_state = new StateNode(
        0,
        lowest_depth, 
        lowest_depth, 
        CostParameters(
            initiator_.getDistinctLabelsNum(),
            initiator_.getMaxObjLen(),
            initiator_.getMaxArrLen()
        ),
        initiator_.getInstanceManager(),
        sample_size_,
        epsilon_
    );

    // Set MDL Cost of initial state
    initial_state->setCost(0);

    StateNode* discovered_state = kBeamSearch(initial_state, beam_size_);

    initiator_.findConvergingNodes(discovered_state->getFinalSchema());
    initiator_.toString(discovered_state->getFinalSchema(), discovered_schema_, kRefAsRef);
    initiator_.definitionToString(discovered_schema_);
}



void ReCG::searchBranchAndBound()
{
    int lowest_depth = initiator_.getInstanceManager().size() - 1;
    int beam_size;

    // Initialize initial state
    StateNode* initial_state = new StateNode(
        0,
        lowest_depth, 
        lowest_depth, 
        CostParameters(
            initiator_.getDistinctLabelsNum(),
            initiator_.getMaxObjLen(),
            initiator_.getMaxArrLen()
        ),
        initiator_.getInstanceManager(),
        sample_size_,
        epsilon_
    );

    // Set MDL Cost of initial state
    initial_state->setCost(0);

    if(lowest_depth < 5)
    {
        beam_size = 100;
    }
    else if(lowest_depth < 7)
    {
        beam_size = 3;
    }
    else
    {
        beam_size = 2;
    }
    cout << "BEAM SIZE: " << beam_size << endl;

    StateNode* discovered_state = branchAndBoundSearch(initial_state, beam_size);

    initiator_.findConvergingNodes(discovered_state->getFinalSchema());
    initiator_.toString(discovered_state->getFinalSchema(), discovered_schema_, kRefAsRef);
    initiator_.definitionToString(discovered_schema_);
}

void ReCG::searchGreedy()
{

    int lowest_depth = initiator_.getInstanceManager().size() - 1;

    // Initialize initial state
    StateNode* initial_state = new StateNode(
        0,
        lowest_depth, 
        lowest_depth, 
        CostParameters(
            initiator_.getDistinctLabelsNum(),
            initiator_.getMaxObjLen(),
            initiator_.getMaxArrLen()
        ),
        initiator_.getInstanceManager(),
        sample_size_,
        epsilon_
    );

    // Set MDL Cost of initial state
    initial_state->setCost(0);

    StateNode* discovered_state = greedySearch(initial_state);

    initiator_.findConvergingNodes(discovered_state->getFinalSchema());
    initiator_.toString(discovered_state->getFinalSchema(), discovered_schema_, kRefAsRef);
    initiator_.definitionToString(discovered_schema_);
}







void ReCG::printSchema() const
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
