# Experiment

`Experiment` is a directory saving the `Python` implementations of experiments conducted in "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".


## Prerequisites

- It is necessary for the user to build all implementations of `ReCG`, `Jxplain` and `KReduce` (refer to `build` files in the upper directory) before running the experiments.

- The `Datasets` directory has to exist, with all 20 datasets conforming to their designated names.

## Quick Usage


You can run every experiments with a single line.
The anticipated runtime of the whole experiment process is over 4 full days, so we recomment you to run the process using `tmux`!

```bash
tmux new-session -t experiment
tmux attach -t experiment
# Inside tmux
./runAllExperiments.sh
```

If you want a more fine-grained manner of running the experiments or more details about 

## Description of Each Experiment

### (A) Accuracy Comparison (Section 5.2)

Run accuracy experiment and return to this directory.
```bash
cd 1.1_Accuracy
python3 run_acc_exp.py
cd ..
```

The accuracy experiment goals to measure F1 score, recall, and precision for the schemas found by each algorithm.
This experiment aims to measure how accurately each schema discovery algorithm discovers the ground truth schema.

`1%`, `10%`, `50%`, or `90%` of positive samples are drawn from $D^+$ to form the train dataset which is given to each algorithm as input.
Non-overlapping `10%` of $D^+$ and `90%` of $D^-$ are drawn to from the test dataset.
The JSON documents in the test datasets are validated against the schema discovered by each algorithm.


### (B) MDL Cost Analysis (Section 5.3)

Run MDL experiment and return to this directory.
```bash
cd 2_MDL
python3 run_mdl_exp.py
cd ..
```

The MDL experiment measures the SRC, DRC for the schemas found by each algorithm, and for the ground truth schema.
The lower the MDL (i.e., SRC + MDL), the better the discovered schema.

### (C) Scalability with Dataset Size (Section 5.4)

Run performance experiment and return to this directory.
```bash
cd 3_Performance
python3 run_perf_exp.py
cd ..
```

The performance experiment measures the runtime of each algorithms for each dataset.

We use all 20 datasets, and sample `10%`, `20%` $\dots$, `100%` of JSON documents for each dataset and see how the runtime increases for each algorithm.


### (D) Parameter Sensitivity (Section 5.5)

Run performance experiment and return to this directory.
```bash
cd 4.1_Parameters
python3 run_param_exp.py
cd ..

```


### (E) Impact of Design Factors to Accuracy (Section 5.6)

Run accuracy experiment for two different versions of `ReCG`

- ReCG with top-down approach
- ReCG that is guided with Key-Space Entropy introduced by Jxplain 

This experiment is acutally included in (A) Accuracy Comparison.
The two algorithms are run alongside `ReCG` and other competitors, so you do not have to run any additional codes.