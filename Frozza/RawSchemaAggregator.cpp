#include "RawSchemaAggregator.hpp"

void RawSchemaAggregator::aggregateRawSchemas()
{
    int barWidth = 70;
    float progress = 0 / (float)raw_schemas_->size();
    int done_count = 0;


    for( SchemaNode* raw_schema : *raw_schemas_ )
    {
        
        #if SHOWPROGRESSBAR
            progress = done_count / (float)raw_schemas_->size();
            cout << "[";
            int pos = barWidth * progress;
            for (int i = 0; i < barWidth; ++i) {
                if (i < pos) cout << "=";
                else if (i == pos) cout << ">";
                else cout << " ";
            }
            cout << "] " << int(progress * 100.0) << " %\r";
            cout.flush();
        #endif

        ///////////////

        bool is_unique = true;

        int i;
        for(i = 0; i < unique_raw_schemas_->size(); i++)
        {
            if( isEqual(raw_schema, unique_raw_schemas_->at(i)) )
            {
                is_unique = false;
                break;
            }
        }

        if( is_unique )
        { 
            unique_raw_schemas_->push_back(raw_schema);
            count_per_raw_schema_->push_back(1);
        }
        else
        {
            count_per_raw_schema_->at(i)++;
        }

        ////////////////
        done_count++;
    }

    cout << endl;
}