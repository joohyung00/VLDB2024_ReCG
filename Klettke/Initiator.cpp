#include "Initiator.hpp"





void Initiator::initiateInstanceManager(string filename)
{
    simdjson::ondemand::parser parser;
    simdjson::padded_string json = simdjson::padded_string::load(filename);
    // auto json = simdjson::padded_string::load(filename);    //jsonl
    simdjson::ondemand::document_stream docs = parser.iterate_many(json, 1000000000);

    cout << "    [Parsing Instances...]" << endl;

    for(auto doc : docs)
    {
        auto element = doc.get_value();
        auto type = simdTypeToInstanceType(element.type());

        InstanceNode* instance_root = new InstanceNode(type, 0);

        initiateInstanceManagerRecursive(element, instance_root, 0);

        instance_manager_.addInstance(instance_root);
    }
    cout << "    [Parsing Instances Done]" << endl << endl;

    cout << "    [Initiating Kleene Info]" << endl;
    // initiateMetadata();
    cout << "    [Initiating Kleene Info Done]" << endl << endl;
}


void Initiator::initiateInstanceManagerRecursive(
    simdjson::simdjson_result<simdjson::fallback::ondemand::value> element,
    InstanceNode* current_instance_node,
    int depth
)
{
    auto type = simdTypeToInstanceType(element.type());

    // Register current `InstanceNode*` to depth_wise_instance storage

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



void Initiator::toString(SchemaNode* schema_node, string* buffer, InitiatorMode mode)
{


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


        case kHetArr:
            if(schema_node->getKleeneChild() == nullptr)
            {
                (*buffer) += R"({"type": "array", "maxItems": 0})";
                return;
            }
            (*buffer) += R"({"type": "array", "items": )";
            toString(TO_SCHEMA_NODE(schema_node->getKleeneChild()), buffer, kRefAsRef);
            (*buffer) += R"(})";
            break;

    }
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
