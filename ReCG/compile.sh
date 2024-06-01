# 1. Build release version
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j10
cd ..

# 2. Build debugging version
cd build-debug
cmake -DCMAKE_BUILD_TYPE=Debug ..
make -j10
cd ..


# ./build/ReCG \
# --in_path test_data/ckg_node_Amino_acid_sequence.jsonl \
# --out_path something.json \
# --search_alg kbeam \
# --beam_width 3 \
# --sample_size 1000 \
# --epsilon 0.5 \
# --src_weight 0.5 \
# --drc_weight 0.5


# ./build/ReCG --in_path test_data/ckg_node_Amino_acid_sequence.jsonl --out_path something.json --search_alg kbeam --beam_width 3 --sample_size 1000 --epsilon 0.5 --src_weight 0.5 --drc_weight 0.5 --cost_model mdl