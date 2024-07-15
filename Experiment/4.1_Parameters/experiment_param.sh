
exp_type=$1
dataset_name=$2
positive=$3
negative=$4
train_perc=$5
test_perc=$6
experiment_num=$7
beam_width=$8
epsilon=$9
min_pts_perc=${10}
sample_size=${11}
src_weight=${12}
drc_weight=${13}




train_path="../train_param.jsonl"
test_path="../test_param.jsonl"



output_dir=../4.2_ParametersResults/output/${dataset_name}
meta_dir=../4.2_ParametersResults/meta/${dataset_name}
log_dir=../4.2_ParametersResults/experiment_log/${dataset_name}

# discovered_schema=$output_dir/train_${train_perc}_beam_${beam_width}_sample_${sample_size}_epsilon${epsilon}_minptsperc${min_pts_perc}__${experiment_num}.json
# meta_path=$meta_dir/train_${train_perc}_beam_${beam_width}_sample_${sample_size}_epsilon${epsilon}_minptsperc${min_pts_perc}__${experiment_num}.json
# log_path=$log_dir/train_${train_perc}_beam_${beam_width}_sample_${sample_size}_epsilon${epsilon}_minptsperc${min_pts_perc}__${experiment_num}.txt


discovered_schema=$output_dir/train_${train_perc}_beam_${beam_width}_sample_${sample_size}_epsilon${epsilon}_minptsperc${min_pts_perc}_mdlweights${src_weight},${drc_weight}__${experiment_num}.json
meta_path=$meta_dir/train_${train_perc}_beam_${beam_width}_sample_${sample_size}_epsilon${epsilon}_minptsperc${min_pts_perc}_mdlweights${src_weight},${drc_weight}__${experiment_num}.json
log_path=$log_dir/train_${train_perc}_beam_${beam_width}_sample_${sample_size}_epsilon${epsilon}_minptsperc${min_pts_perc}_mdlweights${src_weight},${drc_weight}__${experiment_num}.txt


mkdir -p $output_dir
mkdir -p $meta_dir
mkdir -p $log_dir



# 1. Generate dataset
echo ${i}". Splitting dataset"
python3 ../split_dataset.py --mode recall_precision --test_num $experiment_num --positive $positive --negative $negative --train_perc $train_perc --test_perc 10 --train_out $train_path --test_out $test_path --meta $meta_path 

# 2. Run ReCG
echo ${i}." Running ReCG"
if [ $exp_type = "Performance" ]
then
    echo Performance,$dataset_name,$train_perc,$experiment_num,$beam_width,$epsilon,$min_pts_perc,$sample_size,$src_weight,$drc_weight,\
    `/root/VLDB2024_ReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size --src_weight $src_weight --drc_weight $drc_weight  | grep "TOTAL ELAPSED TIME" | grep -o "[0-9]\+"` >> ../exp4_param.txt
    exit
fi

if [ $exp_type = "Accuracy" ]
then
     /root/VLDB2024_ReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size --src_weight $src_weight --drc_weight $drc_weight
fi

# if [ $exp_type = "MDL" ]
# then
#      /root/VLDB2024_ReCG/ReCG/build/ReCG --in_path $train_path --out_path $discovered_schema --search_alg kbeam --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size --src_weight $src_weight --drc_weight $drc_weight
# fi



# 3. Calculate results
echo ${i}." Calculating Experiment Results"

    # 3.1. Accuracy
if [ $exp_type = "Accuracy" ]
then
    python3 recall_precision.py --dataset $dataset_name --train_perc $train_perc --exp_num $experiment_num --schema_path $discovered_schema --test_path       $test_path --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size --src_weight $src_weight --drc_weight $drc_weight
fi

if [ $exp_type = "MDL" ]
then
    # 3.2. MDL
    python3 mdlExperiment.py    --dataset $dataset_name --train_perc $train_perc --exp_num $experiment_num --schema_path $discovered_schema --instance_path $train_path  --beam_width $beam_width --epsilon $epsilon --min_pts_perc $min_pts_perc --sample_size $sample_size --src_weight $src_weight --drc_weight $drc_weight
fi



rm $train_path
rm $test_path