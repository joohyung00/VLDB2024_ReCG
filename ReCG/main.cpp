#include "ReCG.hpp"
#include "ArgParser.hpp"

stateId BottomUpSchemaGenerator::unique_state_id_ = 1;
nodeId SchemaNode::unique_schema_id_ = 1;

int main(int argc, char** argv)
{

    Parameters* parameters = new Parameters();

    // string in_path;
    // string out_path;
    // parameters_ search_mode;
    // int beam_width;
    // int sample_size;
    // float epsilon;
    // int min_pts_perc;
    // float src_weight;
    // float drc_weight;

    if( parseArguments(
            argc, 
            argv, 
            parameters
        ) == -1
    )
    { return -1; }

    Klettke recg(parameters);
    
    recg.run();

    return 0;

}