
algorithm=$1
dataset_name=$2
positive=$3
negative=$4
train_perc=$5
test_perc=$6
experiment_num=$7





train_path="../train.jsonl"
test_path="../test.jsonl"

mkdir -p ../AccuracyResults/${algorithm}_output/${dataset_name}/train${train_perc}
mkdir -p ../AccuracyResults/${algorithm}_meta/${dataset_name}/train${train_perc}
mkdir -p ../AccuracyResults/${algorithm}_experiment_log/${dataset_name}/train${train_perc}



discovered_schema="../AccuracyResults/${algorithm}_output/"${dataset_name}"/train"${train_perc}"/"${dataset_name}"_train"${train_perc}"_test"${test_perc}"_"${experiment_num}".json"
meta_path="../AccuracyResults/"${algorithm}"_meta/"${dataset_name}"/train"${train_perc}"/meta_"${experiment_num}".json"
log_path="../AccuracyResults/"${algorithm}"_experiment_log/"${dataset_name}"/train"${train_perc}"/"${dataset_name}"_train"${train_perc}"_test"${test_perc}".txt"

echo ${experiment_num}". Splitting dataset"

python3 ../split_dataset.py --mode recall_precision --test_num $experiment_num --positive $positive --negative $negative --train_perc $train_perc --test_perc $test_perc --train_out $train_path --test_out $test_path --meta $meta_path

if [ $algorithm = "ReCG" ]
then
    echo ${experiment_num}." Running ReCG"
    /root/jsdReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --mode kbeam --beam 3 --sample_size 1000 --epsilon 0.5
fi

if [ $algorithm = "jxplain" ]
then
    echo ${experiment_num}." Running JXPlain"
    # java -jar /root/jsdReCG/target/scala-2.11/JsonExtractor.jar $train_path train 100 val 0 kse 1.0 log hello.json
    java -jar /root/jsdReCG/target/scala-2.11/JsonExtractor.jar $train_path train 100 val 0 kse 1.0 log $discovered_schema

    echo ${experiment_num}." Correcting JXPlain"
    python3 ../jxplain_translator.py --in_path $discovered_schema --out_path $discovered_schema
fi

if [ $algorithm = "jxplainII" ]
then
    echo ${iexperiment_num}." Running JXPlain II"
    python3 /root/jsdReCG/JXPlain/main.py --data_path $train_path --train_ratio 100 --kse 1.0 --log $discovered_schema --te "type_entropy"
fi

if [ $algorithm = "kreduce" ]
then
    echo ${experiment_num}." Running KReduce"
    scala /root/jsdReCG/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path k -J-Xms2g -J-Xmx512g -J-Xss1g
    
    echo ${experiment_num}." Translating KReduce"
    python3 ../kreduce_translator.py --in_path hello.txt --out_path $discovered_schema
    rm hello.txt
fi

echo ${experiment_num}." Calculating Experiment Results"
python3 recall_precision.py --algo $algorithm --dataset $dataset_name --train_perc $train_perc --exp_num $experiment_num --schema_path $discovered_schema --test_path $test_path

rm $train_path
rm $test_path