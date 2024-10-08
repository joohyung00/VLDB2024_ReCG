cmake_minimum_required(VERSION 3.0.0)
project(ReCG VERSION 0.1.0)

set(CMAKE_CXX_FLAGS "-std=c++17")

include(CTest)
enable_testing()

add_executable(Klettke
    main.cpp
    ArgParser.hpp
    Klettke.cpp
    Initiator.cpp
    ReducedSGConstructor.cpp
    Instance.cpp
    Schema.cpp
    EdgeLabelledTree.cpp
    utils.cpp
    simdjson.cpp
    roaring.c
)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)

# cmake -DCMAKE_BUILD_TYPE=Release ..
# make -j10

# cmake -DCMAKE_BUILD_TYPE=Debug ..
# make -j10

# ./ReCG --in_path ../data/ckg_node_Amino_acid_sequence.jsonl --out_path ../something.json --search_alg kbeam --beam_width 3 --sample_size 500 --epsilon 0.5