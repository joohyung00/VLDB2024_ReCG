#include "Klettke.hpp"
#include "ArgParser.hpp"

nodeId SchemaNode::unique_schema_id_ = 1;

int main(int argc, char** argv)
{
    Parameters* parameters = new Parameters();

    if( parseArguments( argc, argv, parameters ) == -1 )
    { return -1; }

    Klettke klettke(parameters);
    
    klettke.run();

    return 0;
}