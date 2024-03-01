#include "Initiator.hpp"





void Initiator::initiateInstanceManager(string filename)
{
    simdjson::ondemand::parser parser;
    simdjson::padded_string json = simdjson::padded_string::load(filename);
    // auto json = simdjson::padded_string::load(filename);    //jsonl
    simdjson::ondemand::document_stream docs = parser.iterate_many(json, 1000000000);

    auto start_time = high_resolution_clock::now();

    cout << "[Parsing Instances...]" << endl;

    for(auto doc : docs)
    {
        auto element = doc.get_value();
        auto type = simdTypeToInstanceType(element.type());

        InstanceNode* instance_root = new InstanceNode(type, 0);

        initiateInstanceManagerRecursive(element, instance_root, 0);
    }
    cout << "[Parsing Instances Done]" << endl << endl;

    cout << "[Initiating Kleene Info]" << endl;
    initiateMetadata();
    cout << "[Initiating Kleene Info Done]" << endl << endl;

    auto end_time = high_resolution_clock::now();
    auto initiation_runtime = duration_cast<milliseconds>(end_time - start_time);

    cout << "Initiation Runtime: " << initiation_runtime.count() << endl;
}


void Initiator::initiateInstanceManagerRecursive(
    simdjson::simdjson_result<simdjson::fallback::ondemand::value> element,
    InstanceNode* current_instance_node,
    int depth)
{
    auto type = simdTypeToInstanceType(element.type());

    // Register current `InstanceNode*` to depth_wise_instance storage
    instance_manager_.addInstance(current_instance_node);

    switch(type)
    {
        case kObject:
            for (auto field : element.get_object())
            {
                // Get Key-value pairs
                std::string_view keyv = field.unescaped_key();
                std::string key(keyv);

                strInt str_key = incrementallyGetTranslatedLong(key);

                // Generate `InstanceNode`s from JSON string
                InstanceType nested_value_type = simdTypeToInstanceType(field.value().type());
                InstanceNode* new_instance_node = new InstanceNode(nested_value_type, depth + 1);

                current_instance_node->addChild(str_key, new_instance_node);

                initiateInstanceManagerRecursive(field.value(), new_instance_node, depth + 1);
            }

            current_instance_node->sortStrChildren();
            break;

        case kArray:
            for (auto child : element.get_array())
            {
                // Generate `InstanceNode` from JSON string
                InstanceType nested_value_type = simdTypeToInstanceType(child.value().type());
                InstanceNode* new_instance_node = new InstanceNode(nested_value_type, depth + 1);
                current_instance_node->addChild(new_instance_node);

                initiateInstanceManagerRecursive(child, new_instance_node, depth + 1);
            }
            break;

        case kNumber:
        case kString:
        case kBoolean:
        case kNull_:
        default:
            return;
    }
    return;
}




void Initiator::initiateMetadata()
{
    using Count = int;

    vector<Count> thresholds({ 5 });
    int max_depth = instance_manager_.size() - 1;

    for(int depth = 0; depth <= max_depth; depth++)
    {
        GroupedInstances& grouped_instances = instance_manager_.getGroupedInstancesByDepth(depth);
        InstanceForest& instance_forest = grouped_instances.getInstanceForestByType(kObject);

        map<strInt, Count> key_count;

        // 1. Build key_count map
        for(auto& instance : instance_forest)
        {
            // 1. Key-Count
            for(auto& key : instance->getStringLabels())
            {
                auto it = key_count.find(key);
                if(it == key_count.end())
                { key_count[key] = 1; }
                else (it->second)++;
            }

            // Update `max_obj_len_`

            int children_num = instance->getChildrenNum();
            if(children_num > max_obj_len_)
            { max_obj_len_ = children_num; }
        }

        // 2. Erase keys from `key_count` that surpass the threshold
        for(auto it = key_count.cbegin(); it != key_count.cend();)
        {
            if (it->second > thresholds.back())
                it = key_count.erase(it);
            else
                ++it;
        }

        // 3. Fill in each instance's threshold vector
        for(auto& instance : instance_forest)
        {
            auto& thrs = instance->getLabelToThreshold();
            auto& labels = instance->getStringLabels();

            for(int i = 0; i < labels.size(); i++)
            {
                auto it = key_count.find(labels[i]);
                if(it == key_count.end()) thrs.push_back(-1);
                else
                {
                    int count = it->second;
                    thrs.push_back(0);
                    for(auto& threshold : thresholds)
                    {
                        if(count <= threshold)
                        { thrs.back() = threshold; }
                        else break;
                    }
                }
            }
        }

        InstanceForest& array_forest = grouped_instances.getInstanceForestByType(kArray);

        for(auto& instance : array_forest)
        {
            // Update `max_arr_len_`

            int children_num = instance->getChildrenNum();
            if(children_num > max_arr_len_)
            { max_arr_len_ = children_num; }
        }
    }
}




void Initiator::findConvergingNodes(SchemaNode* schema_node)
{
    traverseSchemaTree(schema_node);

    for(auto& node_count : node_count_)
    {
        SchemaNode* node = node_count.first;
        Count n_count = node_count.second;

        // 1. Is a converging node
        if(n_count > 1)
        {
            // 2. Is not a primitive schema node
                // This will be too bad to see
            if(
                node->getType() != kNum &&
                node->getType() != kStr &&
                node->getType() != kBool &&
                node->getType() != kNull
            )
            {
                converging_nodes_to_ref_names_.insert(
                    {node, to_string(converging_node_id++)}
                );
            }
            
        }
    }
}

void Initiator::traverseSchemaTree(SchemaNode* schema_node)
{
    // Increment this node to `node_count_`
    auto it = node_count_.find(schema_node);
    if(it == node_count_.end())
    { node_count_[schema_node] = 1; }
    else (it->second)++;

    // Traverse over to children nodes
    vector<Node*> children_nodes = schema_node->getChildren();
    for(auto& child_node : children_nodes)
    { traverseSchemaTree(TO_SCHEMA_NODE(child_node)); }
}

void Initiator::toString(SchemaNode* schema_node, string* buffer, InitiatorMode mode)
{
    auto it = converging_nodes_to_ref_names_.find(schema_node);
    if(it != converging_nodes_to_ref_names_.end() && mode == kRefAsRef)
    {
        // Print "$ref": 'schema_ref_name'
        (*buffer) += "{\"$ref\": \"#/definitions/";
        (*buffer) += it->second;
        (*buffer) += "\"}";
        return;
    }

    SchemaType type = schema_node->getType();
    if(type == kNum || type == kStr || type == kBool || type == kNull)
    {
        switch(type)
        {
            case kNum: (*buffer) += R"({"type": "number"})"; break;
            case kStr: (*buffer) += R"({"type": "string"})"; break;
            case kBool: (*buffer) += R"({"type": "boolean"})"; break;
            case kNull: (*buffer) += R"({"type": "null"})"; break;
        }
        return;
    }

    vector<strInt> string_labels;
    vector<Node*>   string_children;
    vector<strInt> bold_labels;

    switch(type)
    {
        case kAnyOf:
            (*buffer) += "{\"anyOf\": [";

            for (auto child : schema_node->getChildren())
            {
                toString(TO_SCHEMA_NODE(child), buffer, kRefAsRef);
                (*buffer) += ", ";
            }
            if (schema_node->getChildrenNum() > 0)
            { buffer->erase(buffer->size() - 2, 2); }

            (*buffer) += "]}";
            break;

        case kHomObj:
        
            (*buffer) += R"({"type": "object", "properties": {)";

            string_labels      = schema_node->getStringLabels();
            string_children    = schema_node->getChildren();
            bold_labels        = schema_node->getBoldLabels();

            for (int i = 0; i < string_labels.size(); i++)
            {
                (*buffer) += "\"";
                (*buffer) += translate(string_labels[i]);
                (*buffer) += "\": ";
                toString(TO_SCHEMA_NODE(string_children[i]), buffer, kRefAsRef);
                (*buffer) += ", ";
            }
            if (string_labels.size())
            {
                buffer->erase(buffer->size() - 2, 2);
            }
            (*buffer) += "}";

            if (bold_labels.size())
            {
                (*buffer) += ", \"required\": [";
                for (strInt bold_label : bold_labels)
                { (*buffer) += "\"" + translate(bold_label) + "\", "; }
                buffer->erase(buffer->size() - 2, 2);
                (*buffer) += "]";
            }

            (*buffer) += ", \"additionalProperties\": false}";

            break;

        case kHetObj:
            (*buffer) += R"({"type": "object", "additionalProperties": )";
            toString(TO_SCHEMA_NODE(schema_node->getKleeneChild()), buffer, kRefAsRef);
            (*buffer) += R"(})";
            break;

        case kComObj:
        
            (*buffer) += R"({"type": "object", "properties": {)";

            string_labels      = schema_node->getStringLabels();
            string_children    = schema_node->getChildren();
            bold_labels        = schema_node->getBoldLabels();

            for (int i = 0; i < string_labels.size(); i++)
            {
                (*buffer) += "\"";
                (*buffer) += translate(string_labels[i]);
                (*buffer) += "\": ";
                toString(TO_SCHEMA_NODE(string_children[i]), buffer, kRefAsRef);
                (*buffer) += ", ";
            }
            if (string_labels.size())
            {
                buffer->erase(buffer->size() - 2, 2);
            }
            (*buffer) += "}";

            if (bold_labels.size())
            {
                (*buffer) += ", \"required\": [";
                for (strInt bold_label : bold_labels)
                { (*buffer) += "\"" + translate(bold_label) + "\", "; }
                buffer->erase(buffer->size() - 2, 2);
                (*buffer) += "]";
            }

            (*buffer) += R"(, "additionalProperties": )";
            toString(TO_SCHEMA_NODE(schema_node->getKleeneChild()), buffer, kRefAsRef);
            (*buffer) += R"(})";
            break;

        case kHomArr:
            (*buffer) += R"({"type": "array", "prefixItems": [)";
            
            for (auto child : schema_node->getChildren())
            {
                toString(TO_SCHEMA_NODE(child), buffer, kRefAsRef);
                (*buffer) += ", ";
            }

            if (schema_node->getChildrenNum())
            { 
                buffer->erase(buffer->size() - 2, 2); 
                (*buffer) += "], \"minItems\": " + to_string(schema_node->getChildrenNum());
                (*buffer) += ", \"maxItems\": " + to_string(schema_node->getChildrenNum());
            }
            else
            {
                buffer->erase(buffer->size() - 16, 16);
                (*buffer) += "\"maxItems\": 0";
            }
            
            (*buffer) += "}";
            break;

        case kHetArr:
            (*buffer) += R"({"type": "array", "items": )";
            toString(TO_SCHEMA_NODE(schema_node->getKleeneChild()), buffer, kRefAsRef);
            (*buffer) += R"(})";
            break;

    }
}

void Initiator::definitionToString(string* buffer)
{
    if(converging_nodes_to_ref_names_.size() == 0) return;

    buffer->erase(buffer->size() - 1, 1);
    (*buffer) += R"(, "definitions": {)";

    for(auto& node_name : converging_nodes_to_ref_names_)
    {
        SchemaNode* node = node_name.first;
        string name = node_name.second;

        (*buffer) += R"(")";
        (*buffer) += name;
        (*buffer) += R"(":)";
        toString(node, buffer, kRefAsSchema);
        (*buffer) += R"(, )";
    }
    buffer->erase(buffer->size() - 2, 2);

    (*buffer) += R"(}})";
}


InstanceType Initiator::simdTypeToInstanceType(simdjson::ondemand::json_type type) const
{
    switch (type)
    {
        case simdjson::ondemand::json_type::object:
            return kObject;
        case simdjson::ondemand::json_type::array:
            return kArray;
        case simdjson::ondemand::json_type::number:
            return kNumber;
        case simdjson::ondemand::json_type::string:
            return kString;
        case simdjson::ondemand::json_type::boolean:
            return kBoolean;
        case simdjson::ondemand::json_type::null:
            return kNull_;
    }
    throw 100;
}
