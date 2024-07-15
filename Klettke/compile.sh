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





# ./build/Klettke --in_path test_data/ckg_node_Amino_acid_sequence.jsonl --out_path something.json 