
mode=$1
algorithm=$2
dataset_name=$3
positive=$4
negative=$5
train_perc=$6
test_perc=$7
experiment_num=$8


# Default Parameters for ReCG
beam_width="3"
epsilon="0.5"
min_pts_perc="5"
sample_size="500"


# Example Usage
# ./experiment_performance.sh ReCG 1_NewYorkTimes /mnt/SchemaDataset/1_NewYorkTimes/new_york_times_positive.jsonl /mnt/SchemaDataset/1_NewYorkTimes/new_york_times_negative.jsonl      10 10 1


temp_result_file="temp_result_file.txt"
train_path="performance_train.jsonl"
test_path="performance_test.jsonl"

# for i in $(seq $start_phase $end_phase)
# do

meta_file="somethong.json"
discovered_schema="something.json"


echo ""
echo ""
echo ""


echo ${experiment_num}". Splitting dataset"
python3 ../split_dataset.py --mode recall_precision --test_num $experiment_num --positive $positive --negative $negative --train_perc $train_perc --test_perc $test_perc --train_out $train_path --test_out $test_path --meta $meta_file

if [ $algorithm = "ReCG" ]
then
    echo ${experiment_num}." Running ReCG"
    (/usr/bin/time -v /root/VLDB2024_ReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size) &>> $temp_result_file
    rm $discovered_schema
    # echo $algorithm,$experiment_num,$dataset_name,$positive,$negative,$train_perc,$test_perc,`/root/VLDB2024_ReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width 3 --epsilon 0.5 --min_pts_perc 10 --sample_size 1000  | grep "TOTAL ELAPSED TIME" | grep -o "[0-9]\+"` >> ../exp_perf.txt
fi

if [ $algorithm = "jxplain" ]
then
    echo ${experiment_num}." Running JXPlain"
    (/usr/bin/time -v java -jar /root/VLDB2024_ReCG/target/scala-2.11/JsonExtractor.jar $train_path train 100 val 0 kse 1.0 log $discovered_schema) &>> $temp_result_file
    rm $discovered_schema
fi

if [ $algorithm = "kreduce" ]
then
    echo ${experiment_num}." Running KReduce"
    (/usr/bin/time -v scala /root/VLDB2024_ReCG/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path k -J-Xms2g -J-Xmx512g -J-Xss1g) &>> $temp_result_file
fi

if [ $algorithm = "lreduce" ]
then
    echo ${experiment_num}." Running LReduce"
    (/usr/bin/time -v scala /root/VLDB2024_ReCG/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path l -J-Xms2g -J-Xmx512g -J-Xss1g) &>> $temp_result_file
fi


if [ $algorithm = "klettke" ]
then
    echo ${experiment_num}." Running Klettke"
    (/usr/bin/time -v /root/VLDB2024_ReCG/Klettke/build/Klettke --in_path $train_path --out_path $discovered_schema) &>> $temp_result_file
    rm $discovered_schema
fi

if [ $algorithm = "frozza" ]
then
    echo ${experiment_num}" Running Frozza"
    (/usr/bin/time -v /root/VLDB2024_ReCG/Frozza/build/Frozza   --in_path $train_path --out_path $discovered_schema) &>> $temp_result_file
    rm $discovered_schema
fi


python3 parse_temp_result.py --mode $mode --algorithm $algorithm --dataset_name $dataset_name --train_perc $train_perc --experiment_num $experiment_num --temp_file_path $temp_result_file

rm $temp_result_file
rm $train_path
rm $test_path
rm $meta_file

# done


