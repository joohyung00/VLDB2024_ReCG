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

meta_path="mdl_experiment_meta.json"
discovered_schema="../AccuracyResults/${algorithm}_output/"${dataset_name}"/train"${train_perc}"/"${dataset_name}"_train"${train_perc}"_test"${test_perc}"_"${experiment_num}".json"

echo ${experiment_num}". Splitting dataset"
python3 ../split_dataset.py --mode recall_precision --test_num $experiment_num --positive $positive --negative $negative --train_perc $train_perc --test_perc $test_perc --train_out $train_path --test_out $test_path --meta $meta_path

if [ $algorithm = "groundtruth" ]
then
    echo ${experiment_num}." Ground Truth Schema"
fi

if [ $algorithm = "ReCG" ]
then
    echo ${experiment_num}." Running ReCG"
    /root/jsdReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --mode kbeam --beam 3 --sample_size 1000 --epsilon 0.5
fi

if [ $algorithm = "jxplain" ]
then
    echo ${i}." Running JXPlain"
    java -jar /root/jsdReCG/target/scala-2.11/JsonExtractor.jar $train_path train 100 val 0 kse 1.0 log mdl_temp.txt

    echo ${i}." Translating JXPlain"
    python3 ../jxplain_translator.py --in_path mdl_temp.txt --out_path $discovered_schema
    rm mdl_temp.txt
fi

if [ $algorithm = "kreduce" ]
then
    echo ${experiment_num}." Running KReduce"
    scala /root/jsdReCG/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path k -J-Xms2g -J-Xmx512g -J-Xss1g
    
    echo ${experiment_num}." Translating KReduce"
    python3 ../kreduce_translator.py --in_path hello.txt --out_path $discovered_schema
    rm hello.txt
fi

python3 mdlExperiment.py --algo $algorithm --dataset $dataset_name --train_perc $train_perc --exp_num $experiment_num --schema_path $discovered_schema --instance_path $train_path

rm $train_path
rm $test_path
rm $meta_path





# if [ $algorithm = "ReCG" ]
# then
#     echo ${i}." Running ReCG"
#     /root/jsdReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --mode kbeam --beam 3 --sample_size 1000
# fi



# if [ $algorithm = "kreduce" ]
# then
#     echo ${i}." Running KReduce"
#     scala /root/jsdReCG/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path k -J-Xms2g -J-Xmx512g

#     echo ${i}." Translating KReduce"
#     python3 ../kreduce_translator.py --in_path hello.txt --out_path $discovered_schema
#     rm hello.txt
# fi