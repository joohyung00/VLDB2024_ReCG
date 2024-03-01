#include "ReCG.hpp"
#include "ArgParser.hpp"

stateId BottomUpSchemaGenerator::unique_state_id_ = 1;
nodeId SchemaNode::unique_schema_id_ = 1;

int main(const int argc, const char *const *const argv)
{

    string in_path;
    string out_path;
    SearchMode search_mode;
    int beam_size;
    int sample_size;
    float epsilon;

    if( parseArguments(
            argc, 
            argv, 
            in_path, 
            out_path, 
            search_mode,
            beam_size,
            sample_size,
            epsilon
        ) == -1
    )
    { return -1; }
        
    ReCG recg(
        in_path, 
        out_path, 
        search_mode, 
        beam_size, 
        sample_size, 
        epsilon
    );
    
    recg.run();

    return 0;

}