# About ReCG

`ReCG` is an algorithm that discovers a JSON schema from a bag of JSON documents.

`ReCG` processes JSON documents in a bottom-up manner, which is devised to solve the problems top-down algorithms that perform poorly in real-life datasets.
It builds up schemas from leaf elements upward in the JSON document tree and, thus, can make more informed decisions of the schema node types.

In addition, `ReCG` adopts MDL (Minimum Description Length) principles systematically while building up the schemas to choose among candidate schemas the most concise yet accurate one with well-balanced generality.

`ReCG` is implemented with ![C++](https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white).


## Build

Simply compile `ReCG` with the following line:
```bash
./compile.sh
```

This compiles both the release mode and the debug mode of `ReCG`.

## Usage

You can run `ReCG` in release mode with the following command:
```bash
./root/VLDB2024_ReCG/ReCG/build/ReCG
    --in_path [pathToInputFile (.jsonl)]
    --out_path [pathToOutputSchema (.json)]
    --search_alg kbeam
    --beam_width [int]
    --epsilon [float | 0 < x && x <= 1]
    --min_pts_perc [int | 0 < x && x <= 100]
    --sample_size [int | x > 0]
    --src_weight [float | 0 <= src_weight && src_weight <= 1.0 && src_weight + drc_weight == 1]
    --drc_weight [float | 0 <= drc_weight && src_weight <= 1.0 && src_weight + drc_weight == 1]
    --cost_model [{mdl, kse}]
```

You may also run it in the debugging mode with the following command:
```bash
./root/VLDB2024_ReCG/ReCG/build-debug/ReCG
    --in_path [pathToInputFile (.jsonl)]
    --out_path [pathToOutputSchema (.json)]
    --search_alg kbeam
    --beam_width [int]
    --epsilon [float | 0 < x && x <= 1]
    --min_pts_perc [int | 0 < x && x <= 100]
    --sample_size [int | x > 0]
    --src_weight [float | 0 <= src_weight && src_weight <= 1.0 && src_weight + drc_weight == 1]
    --drc_weight [float | 0 <= drc_weight && src_weight <= 1.0 && src_weight + drc_weight == 1]
    --cost_model [{mdl, kse}]
```

Example code: try out this one!

```bash
./root/VLDB2024_ReCG/ReCG/build/ReCG
    --in_path test_data/ckg_node_Amino_acid_sequence.jsonl \
    --out_path something.json \
    --search_alg kbeam \
    --beam_width 3 \
    --sample_size 1000 \
    --epsilon 0.5 \
    --src_weight 0.5 \
    --drc_weight 0.5
```

## Explanation About Implementation

- `ReCG.hpp`, `ReCG.cpp`

The upper files define the `ReCG` class, which
    - Initiates the instance trees from the input .jsonl file.
    - Calls the basic beam search function of `Search.hpp`.


- `StateNode.hpp`, `StateNode.cpp`

The upper files define the `StateNode` class, which correspond to the $state$ introduced in Section 4.2.1 of the paper.
The `StateNode` class contains the CD-instances (their connections with PD-instances are saved inside CD-instances) to derive schema from, in the variable called the `instance_manager_`.

The key functionality of a state node is to generate children states, and this mainly done by the member object `bottomUpSchemaGenerator`.
Further explanation about this class will be explained below.

- `BottomUpSchemaGenerator.hpp`
This header file defines the `BottomUpSchemaGenerator` class that derives candidate schemas from a bag of CD-instances.
This corresponds to Algorithm 2 of the paper, `GenerateChildrenStates`.

    - `BottomUpSchemaGenerator.cpp`

    This is the file that directly corresponds to Algorithm 2.
    It splits the CD-instances to $\mathcal{C}_{prm}$, $\mathcal{C}_{obj}$, $\mathcal{C}_{arr}$.
    Each of the CD-instance bags are given to the corresponding functions defined below.

    - `BottomUpSchemaGenerator_Object.cpp`

    This is the file that implements the basic functions introduced in Section 4.5, CD-Instance Clustering.
    It first performs multiple DBSCANs with sampled CD-instances, until no cluster is found.
    The CD-instances of the biggest cluster are used to create a pattern (i.e., schema), and we filter all the CD-instances that are accepted by the pattern.

    When DBSCAN stops, the outliers are generalized and clustered again with the same process. 
    
    - `BottomUpSchemaGenerator_Merge.cpp`

    This is the file that implements the basic functions introduced in Section 4.7, Repetitive Generalization of Schemas.
    Each and all possible pairs of clusters are checked by their viableness of the merge, and their distances are calculated.
    The pair with the smallest distance are merged iteratively (i.e., hierachically), and schema sets are generated for each hierarchy.

    - `BottomUpSchemaGenerator_Array.cpp`

    This file implements the basic functionality of deriving arrays schemas from a bag of array CD-instances.
    The overall process resembles that of objects.

    
- `SchemaNodeDeriver.hpp`, `SchemaNodeDeriver.cpp`
    
These files define the functions that derive a schema node from a cluster.
They correspond to Section 4.6, Schema Derivation From Each Cluster.
