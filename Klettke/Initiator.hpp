#ifndef INITIATOR
#define INITIATOR

#include <fstream>
#include <iostream>

// Initiator
#include "Instance.hpp"
#include "simdjson.h"


enum InitiatorMode {kRefAsSchema, kRefAsRef};

class Initiator
{
	private:

		using Count = int;

		InstanceForestManager 				instance_manager_;

		strInt 								unique_long_num_ = 0;
		unordered_map<string, strInt> 		str_to_int_;
		unordered_map<strInt, string> 		int_to_str_;

	public:

		Initiator()
		{ instance_manager_ = InstanceForestManager(); }

		~Initiator(){}

		void initiateInstanceManager(string filename);

		InstanceForest& getInstanceForest()
		{ return instance_manager_.getInstanceForest(); }


		strInt getDistinctLabelsNum()
		{ return int_to_str_.size(); }

		long translate(string str)
		{ return str_to_int_[str]; }

		string translate(long lng)
		{ return int_to_str_[lng]; }

		void toString(SchemaNode* schema_node, string* buffer, InitiatorMode mode);

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

		InstanceType simdTypeToInstanceType(simdjson::ondemand::json_type type) const;
};


#endif