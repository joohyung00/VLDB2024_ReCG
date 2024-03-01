#ifndef OCCURTREE
#define OCCURTREE

#include <vector>
#include <unordered_map>
#include <fstream>
#include <iostream>

// Initiator
#include "Schema.hpp"
#include "Instance.hpp"
#include "EdgeLabelledTree.hpp"
#include "utils.hpp"
#include "simdjson.h"


enum InitiatorMode {kRefAsSchema, kRefAsRef};

class Initiator
{
	private:

		using Count = int;

		DepthToGroupedInstances 			instance_manager_;

		strInt 								unique_long_num_ = 0;
		unordered_map<string, strInt> 		str_to_int_;
		unordered_map<strInt, string> 		int_to_str_;

		// Metadata
		Count								max_obj_len_ = 0;
		Count								max_arr_len_ = 0;

		// Schema-printing
		long converging_node_id = 1;
		unordered_map<SchemaNode*, Count> 	node_count_;
		unordered_map<SchemaNode*, string> 	converging_nodes_to_ref_names_;
		
	public:

		Initiator()
		{ instance_manager_ = DepthToGroupedInstances(); }

		~Initiator(){}

		strInt getDistinctLabelsNum()
		{ return int_to_str_.size(); }

		Count getMaxObjLen()
		{ return max_obj_len_; }

		Count getMaxArrLen()
		{ return max_arr_len_; }

		void initiateInstanceManager(string filename);

		DepthToGroupedInstances& getInstanceManager()
		{ return instance_manager_; }
		










		long translate(string str)
		{ return str_to_int_[str]; }

		string translate(long lng)
		{ return int_to_str_[lng]; }
		

		void initiateMetadata();

		void printData()
		{
			instance_manager_.printData(); 
			cout << "Total number of string labels turned into number format: " << str_to_int_.size() << endl;
		}

		void findConvergingNodes(SchemaNode* schema_node);

		void toString(SchemaNode* schema_node, string* buffer, InitiatorMode mode);
		void definitionToString(string* buffer);

	private:
		void initiateInstanceManagerRecursive(
			simdjson::simdjson_result<simdjson::fallback::ondemand::value> element,
			InstanceNode* current_instance_node,
			int depth
			);

		long incrementallyGetTranslatedLong(string& str)
		{
			if(str_to_int_.find(str) == str_to_int_.end())
			{ 
				strInt to_return = unique_long_num_;
				str_to_int_[str] = unique_long_num_;
				int_to_str_[unique_long_num_] = str;
				unique_long_num_++;
				return to_return;
			}
			return str_to_int_[str];
		}

		void traverseSchemaTree(SchemaNode* schema_node);

		InstanceType simdTypeToInstanceType(simdjson::ondemand::json_type type) const;
};


#endif