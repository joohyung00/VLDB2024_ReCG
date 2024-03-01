
algorithm=$1
dataset_name=$2
positive=$3
negative=$4
train_perc=$5
test_perc=$6
experiment_num=$7
# beam_size=$9
# sample_size=${10}
# epsilon=${11}
beam_size="3"
sample_size="1000"
epsilon="0.5"


# algorithm=$1
# start_phase=$2
# end_phase=$3
# name=$4
# positive=$5
# negative=$6
# train=$7
# test=$8



train_path="train.jsonl"
test_path="test.jsonl"

# for i in $(seq $start_phase $end_phase)
# do

meta_path="somethong.json"
# experiment_num=$i
discovered_schema="something.json"

echo ${experiment_num}". Splitting dataset"
# python3 ../split_dataset.py --test_num $experiment_num --algorithm $algorithm --positive $positive --negative $negative --train_perc $train_perc --test_perc $test_perc --train_out $train_path --test_out $test_path --meta $meta_path
python3 ../split_dataset.py --mode recall_precision --test_num $experiment_num --positive $positive --negative $negative --train_perc $train_perc --test_perc $test_perc --train_out $train_path --test_out $test_path --meta $meta_path


if [ $algorithm = "ReCG" ]
then
    echo ${experiment_num}." Running ReCG"
    echo $algorithm,$experiment_num,$dataset_name,$positive,$negative,$train_perc,$test_perc,`/root/jsdReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --mode kbeam --beam $beam_size --sample_size $sample_size --epsilon $epsilon | grep "TOTAL ELAPSED TIME" | grep -o "[0-9]\+"` >> ../exp_perf.txt
fi

if [ $algorithm = "jxplain" ]
then
    echo ${experiment_num}." Running JXPlain"
    echo $algorithm,$experiment_num,$dataset_name,$positive,$negative,$train_perc,$test_perc,`java -jar /root/jsdReCG/target/scala-2.11/JsonExtractor.jar $train_path train 100 val 0 kse 1.0 log $discovered_schema | grep "Total Time: " | grep -o "[0-9]\+"` >> ../exp_perf.txt
fi

if [ $algorithm = "kreduce" ]
then
    echo ${experiment_num}." Running KReduce"
    echo $algorithm,$experiment_num,$dataset_name,$positive,$negative,$train_perc,$test_perc,`scala /root/jsdReCG/target_KREDUCE/scala-2.11/jsonSchemaInferenceLight-assembly-1.0.jar $train_path k -J-Xms2g -J-Xmx512g -J-Xss1g | grep "Total Time: " | grep -o "[0-9]\+"` >> ../exp_perf.txt
fi

rm $train_path
rm $test_path
# rm $discovered_schema
rm $meta_path

# done


