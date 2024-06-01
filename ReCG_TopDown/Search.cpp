#include "Search.hpp"





StateNode* kBeamSearch(StateNode* start_state, int beam_width)
{
    int nodes_visited_for_schema_derivation = 0;

    // Perform Branch and Bound
    vector<StateNode*> current_level;
    vector<StateNode*> next_level;

    // Initiate search
    current_level.push_back(start_state);

    while(true)
    {
        if(current_level[0]->isLeafState())
        {
            // Leaf node: assess the best one!
            StateNode* current_optimal = *current_level.begin();
            for(auto& candidate : current_level)
            {
                candidate->printInfo();

                /* ORIGINAL */
                if(candidate->getWeightedMDLCost() < current_optimal->getWeightedMDLCost())
                {
                    current_optimal = candidate;
                }
            }
            cout << endl << "# of state nodes that schema derivation happened: " << nodes_visited_for_schema_derivation << endl;

            return current_optimal;
        }
        else
        {
            // Non-leaf node: search children states! 
            for(auto& beam_state : current_level)
            {
                beam_state->printInfo();

                vector<StateNode*> children_states = beam_state->transitions();
                nodes_visited_for_schema_derivation += 1;
                next_level.insert(next_level.end(), children_states.begin(), children_states.end());
            }
        
            // Leave the k-best states.

            /* ORIGINAL */
            if(next_level.size() > beam_width)
            {
                partial_sort(next_level.begin(), next_level.begin() + beam_width, next_level.end(), compareByCost);
                next_level.resize(beam_width); 
            }


            current_level = next_level;
            next_level.clear();
        }
    }
}

StateNode* greedySearch(StateNode* start_state)
{
    StateNode* current_optimal_state = nullptr;
    StateNode* current_state = start_state;

    while(!current_state->isLeafState())
    {
        current_state->printInfo();
        
        vector<StateNode*> children_states;

        StateNode* candidate;

        // 1. Search this level
        children_states = current_state->transitions();
        
        // 2. Pick the most greedy state
        StateNode* most_greedy = *children_states.begin();
        for(auto& candidate : children_states)
        {
            if(candidate->getWeightedMDLCost() < most_greedy->getWeightedMDLCost())
            {
                most_greedy = candidate;
            }
        }
        
        // 3. Proceed to next level
        current_state = most_greedy;
    }
    cout << endl;

    StateNode* optimal_state = current_state;

    return optimal_state;
}

StateNode* branchAndBoundSearch(StateNode* start_state, int beam_width)
{
    int nodes_visited_for_schema_derivation = 0;

    // Perform Branch and Bound
    stack<StateNode*> state_stack;
    StateNode* current_optimal_state = nullptr;

    // Push to stack
    state_stack.push(start_state);

    while(!state_stack.empty())
    {
        StateNode* current_state = state_stack.top();
        state_stack.pop();

        current_state->printInfo();

        if(current_state->isLeafState())
        {
            // Case 1) Leaf State!
            if(current_optimal_state == nullptr)
            { 
                current_optimal_state = current_state; 
            }
            else if(current_state->getWeightedMDLCost() < current_optimal_state->getWeightedMDLCost())
            {
                current_optimal_state = current_state;
            }
        }
        else
        {
            if(current_optimal_state != nullptr && current_state->getWeightedMDLCost() > current_optimal_state->getWeightedMDLCost())
            {   
                // Case 2.1) Leaf node is found, and this state is hopeless
                continue;
            }
            else
            {
                // Case 2.2) This state has hope -> keep on searching in DFS manner
                vector<StateNode*> children_states = current_state->transitions();
                nodes_visited_for_schema_derivation += 1;
                
                // sort by cost
                sort(children_states.begin(), children_states.end(), compareByCost);

                // cut by beam size
                if(children_states.size() > beam_width)
                {
                    children_states.resize(beam_width);
                }

                for(auto it = children_states.rbegin(); it != children_states.rend(); it++)
                {
                    state_stack.push(*it);
                }
            }
        }
        cout << endl;
    }
    
    cout << endl << "# of state nodes that schema derivation happened: " << nodes_visited_for_schema_derivation << endl;

    StateNode* optimal_state = current_optimal_state;
    
    return optimal_state;
}




bool compareByCost(StateNode* a, StateNode* b)
{
    return a->getWeightedMDLCost() < b->getWeightedMDLCost();
}

bool compareByCostGreater(StateNode* a, StateNode* b)
{
    return a->getWeightedMDLCost() > b->getWeightedMDLCost();
}