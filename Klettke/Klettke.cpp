#include "Klettke.hpp"


void Klettke::run()
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
    cout << "[(2) Constructing RG...]" << endl;
    auto rg_constr_start = high_resolution_clock::now();

    constructRG();

    auto rg_constr_end = high_resolution_clock::now();
    auto rg_constr_total = duration_cast<milliseconds>(rg_constr_end - rg_constr_start);
    cout << "    RG Constructing Time: " << rg_constr_total.count() << " ms" << endl;
    cout << "[(2) RG Construction Complete]" << endl << endl; 


    // 3. Translate RG to schema in string format
    cout << "[(3) Printing RG into string format...]" << endl;
    auto string_tr_start = high_resolution_clock::now();

    printSchema();

    auto string_tr_end = high_resolution_clock::now();
    auto string_tr_total = duration_cast<milliseconds>(string_tr_end - string_tr_start);
    cout << "    String translation time: " << string_tr_total.count() << " ms" << endl;
    cout << "[(3) String Translation Complete]" << endl << endl; 
    

    cout << endl << "    (({{[[ TOTAL ELAPSED TIME : " << initiate_total.count() + rg_constr_total.count() + string_tr_total.count() << " ms" << " ]]}}))" << endl << endl;
}



void Klettke::runInitiator()
{ 
    initiator_.initiateInstanceManager(input_filepath_); 
    #if VERBOSE
        initiator_.printData();

        cout << "----------------------------------------" << endl;
    #endif
}



void Klettke::constructRG()
{
    ReducedSGConstructor rg_constructor(initiator_.getInstanceForest());

    rg_constructor.constructReducedSG();

    rg_tree_ = rg_constructor.getReducedSG();
}


void Klettke::printSchema()
{
    // rg_tree_->visualizeSchemaTree(0);
    initiator_.toString(rg_tree_, discovered_schema_, kRefAsSchema);

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
