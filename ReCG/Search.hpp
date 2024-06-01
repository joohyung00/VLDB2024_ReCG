#ifndef SEARCHALG
#define SEARCHALG

// [Search.hpp]
#include "StateNode.hpp"
// BottomUpSchemaGenerator.hpp
// Clustering.hpp
// SchemaNodeDeriver.hpp
// InstanceCluster.hpp
// Initiator.hpp
// Distance.hpp
// Schema.hpp
// Instance.hpp
// EdgeLabelledTree.hpp
// utils.hpp
// simdjson.h


StateNode* greedySearch(StateNode* start_state);

StateNode* branchAndBoundSearch(StateNode* start_state, int beam_width);

StateNode* kBeamSearch(StateNode* start_state, int beam_width);

bool compareByCost(StateNode* a, StateNode* b);

bool compareByCostGreater(StateNode* a, StateNode* b);

#endif