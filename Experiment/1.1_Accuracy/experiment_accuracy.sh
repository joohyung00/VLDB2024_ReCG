### Example Usage
# ./experiment_accuracy.sh klettke 7_Yelp /mnt/SchemaDataset/7_Yelp/merged_positive.jsonl /mnt/SchemaDataset/7_Yelp/merged_negative.jsonl 10 10 1
# ./experiment_accuracy.sh klettke 6_Wikidata /mnt/SchemaDataset/6_Wikidata/wikidata_positive.jsonl /mnt/SchemaDataset/6_Wikidata/wikidata_negative.jsonl 1 10 1


algorithm=$1
dataset_name=$2
positive=$3
negative=$4
train_perc=$5
test_perc=$6
experiment_num=$7
run_mode=$8
operation_num=$9

## Default Parameters for ReCG
beam_width="3"
epsilon="0.5"
min_pts_perc="5"
sample_size="500"

experiment_description="    [[[ Algorithm: "${algorithm}", Data: "${dataset_name}", Train: "${train_perc}%", ExpNum: "${experiment_num}" ]]]"



train_path="../accuracy_train.jsonl"
test_path="../accuracy_test.jsonl"

mkdir -p ../AccuracyResults/${algorithm}_output/${dataset_name}/train${train_perc}
mkdir -p ../AccuracyResults/${algorithm}_meta/${dataset_name}/train${train_perc}
mkdir -p ../AccuracyResults/${algorithm}_experiment_log/${dataset_name}/train${train_perc}

discovered_schema="../AccuracyResults/${algorithm}_output/"${dataset_name}"/train"${train_perc}"/"${dataset_name}"_train"${train_perc}"_test"${test_perc}"_"${experiment_num}".json"
meta_path="../AccuracyResults/"${algorithm}"_meta/"${dataset_name}"/train"${train_perc}"/meta_"${experiment_num}".json"
log_path="../AccuracyResults/"${algorithm}"_experiment_log/"${dataset_name}"/train"${train_perc}"/"${dataset_name}"_train"${train_perc}"_test"${test_perc}".txt"

echo ""
echo ""


# 1. Split data

echo ${experiment_description}" Splitting dataset"
python3 ../split_dataset.py --mode recall_precision --test_num $experiment_num --positive $positive --negative $negative --train_perc $train_perc --test_perc $test_perc --train_out $train_path --test_out $test_path --meta $meta_path





# 2. Run target algorithm

if [ $algorithm = "ReCG" ]
then
    echo ${experiment_description}" Running ReCG"
    /root/JsonExplorerSpark/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size
fi

if [ $algorithm = "ReCG(TopDown)" ]
then
    echo ${experiment_description}" Running ReCG"
    /root/JsonExplorerSpark/ReCG_TopDown/build/ReCG_TopDown --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size
fi

if [ $algorithm = "ReCG(KSE)" ]
then
    echo ${experiment_description}" Running ReCG"
    /root/JsonExplorerSpark/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size --cost_model kse
fi

if [ $algorithm = "jxplain" ]
then
    echo ${experiment_description}" Running JXPlain"
    java -jar /root/JsonExplorerSpark/target/scala-2.11/JsonExtractor.jar $train_path train 100 val 0 kse 1.0 log $discovered_schema

    echo ${experiment_description}" Correcting JXPlain"
    python3 ../jxplain_translator.py --in_path $discovered_schema --out_path $discovered_schema
fi

if [ $algorithm = "jxplainII" ]
then
    echo ${experiment_description}" Running JXPlain II"
    python3 /root/JsonExplorerSpark/JXPlain/main.py --data_path $train_path --train_ratio 100 --kse 1.0 --log $discovered_schema --te "type_entropy"
fi

if [ $algorithm = "kreduce" ]
then
    echo ${experiment_description}" Running KReduce"
    scala /root/JsonExplorerSpark/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path k -J-Xms2g -J-Xmx512g -J-Xss1g
    
    echo ${experiment_description}" Translating KReduce"
    python3 ../kreduce_translator.py --in_path hello.txt --out_path $discovered_schema
    rm hello.txt
fi

if [ $algorithm = "lreduce" ]
then
    echo ${experiment_description}" Running LReduce"
    scala /root/JsonExplorerSpark/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path l -J-Xms2g -J-Xmx512g -J-Xss1g
    
    echo ${experiment_description}" Translating LReduce"
    python3 ../kreduce_translator.py --in_path hello.txt --out_path $discovered_schema
    rm hello.txt
fi 

if [ $algorithm = "klettke" ]
then
    echo ${experiment_description}" Running Klettke"
    /root/JsonExplorerSpark/Klettke/build/Klettke --in_path $train_path --out_path $discovered_schema
fi

if [ $algorithm = "frozza" ]
then
    echo ${experiment_description}" Running Frozza"
    /root/JsonExplorerSpark/Frozza/build/Frozza --in_path $train_path --out_path $discovered_schema
fi





# 3. Calculate Recall and Precision

if [ $run_mode = "real" ]
then 
    echo ${experiment_description}" Calculating Experiment Results"
    python3 recall_precision.py --algo $algorithm --dataset $dataset_name --train_perc $train_perc --exp_num $experiment_num --schema_path $discovered_schema --test_path $test_path --operation_num $operation_num 
fi




# 4. Clean up

rm $train_path
rm $test_path