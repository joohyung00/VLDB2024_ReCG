# Experiment Visualization

`ExperimentVisualization` is a directory saving the `Python` implementations that visualize (either as printing in consoles or as drawing plots) experiments conducted in "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".

## Prerequisites

1. The `Datasets` directory has to exist, with all 20 datasets conforming to their designated names.
It would not be a problem as long as you have not modified any directory structures or files after you created the docker container.

2. It is necessary for the user to build all implementations of `ReCG`, `Jxplain` and `KReduce` (refer to `build` files in the upper directory) before running the experiments.

3. It is necessary for the user to run all the experiments listed below.
    - Accuracy Comparison
    - MDL Cost Analysis
    - Scalability with Dataset Size
    - Parameter Sensitivity
    - Impact of Design Factors to Accuracy

## Quick Usage

```bash
runAllExperimentVisualizations.sh
```

## Description of Each Visualization



### (A) Statistics of Datasets (Section 5.1.3)

```bash
python3 0_DatasetTab.py
```
Print the latex code for *Table 1: Statistics of 20 datasets used in experiments*.

The output include the information about
- Schema tree
    - Height
    - Number of nodes
    - Number of nodes of each type
- Instance trees
    - Number of instances
    - Average number of nodes

This is an example output
```txt
 & NYT & 6 & 92 & 9 & 0 & 0 & 0 & 3 & 14 & 10000 & 85.21 \\ \cline{2-12}
 & Twitter & \infty & \infty & 20 & 1 & 0 & 12 & 10 & 16 & 10000 & 206.17 \\ \cline{2-12}
 & Github & 11 & 3471 & 171 & 0 & 3 & 0 & 29 & 335 & 10000 & 116.65 \\ \cline{2-12}
 ...
```


### (B) Visualizing 'Accuracy Comparison' (Section 5.2)


```bash
python3 1.1_AccExperimentVis.py
```
Visualize the accuracy experiment as a plot.
Aggregate (average) the F1 score, recall and precision of each algorithm's schemas for all 20 datasets, when run with a percent of train dataset.
Your results are saved at the `Accuracy` directory.
Here is an example of your result:

<p align = "center">
<img src="images/1_precision.png" alt="drawing" width="400"/>
</p>

```bash
python3 1.2_AccExperimentAgg.py
```
This code aggregates the accuracy measures of `ReCG`, `Jxplain` and `KReduce`.
It shows on console the relationship of F1 score, recall and precision for the three algorithms.

```bash
python3 1.3_AccExperimentTab.py
```
This code generates the latex code for Table 2 of the paper "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".

### (C) Visualizing 'MDL Cost Analysis' (Section 5.3)

```bash
python3 2.1_MdlExperimentVis.py
```

This code 
- Shows the MDL cost (SRC, DRC) of the schemas found by `ReCG`, `Jxplain` and `KReduce`.
It also shows the accuracies alongside, enabling one to recognize the negative relationship between MDL cost and accuracy.  
- Aggregates the MDL cost and accuracies for all datasets, and show their relationship.

Here is an example of the output: 

<p align = "center">
<img src="images/2_mdl.png" alt="drawing" width="400"/>
</p>

```bash
python3 2.2_MdlExperimentAgg.py
```

This code shows the followings on the console:
- The relationship between the MDL costs of schemas found by `ReCG`, `Jxplain`, `KReduce` and the `ground truth schema`s.
- The correlation between `MDL`, `SRC`, `DRC` and `F1 score`, `recall`, `precision`.

### (D) Visualizing 'Scalability with Dataset Size' (Section 5.4)

```bash
python3 3.1_PerformanceExperimentVis.py
```

This code shows the runtime of each algorithm for each dataset, when the proportion of the used dataset is increased by `10%`.

Here is an example of the output: 

<p align = "center">
<img src="images/3_runtime.png" alt="drawing" width="400"/>
</p>


```bash
python3 3.2_PerformanceExperimentAgg.py
```

This code generates the latex code for Table 4 of the paper "ReCG: Bottom-Up JSON Schema Discovery Using a Repetitive Cluster-and-Generalize Framework".



### (E) Visualizing 'Parameter Sensitivity' (Section 5.5)

```bash
python3 4.1_ParamExperimentVis.py --exp BeamWidth
python3 4.1_ParamExperimentVis.py --exp Epsilon
python3 4.1_ParamExperimentVis.py --exp MinPtsPerc
python3 4.1_ParamExperimentVis.py --exp MDLWeights
```

This code  plots the accuracies of the disovered schemas for each algorithm.

Here is an example of the output: 

<p align = "center">
    <img src="images/4_param.png" alt="drawing" width="400"/>
</p>


```bash
python3 4.2_ParamExperimentAgg.py
```

This code prints the values that we used in our paper.


### (F) Analyzing the Impact of Design Factors to Accuracy (Section 5.6)

```bash
python3 6.2_DesignFactors.py
```

This code prints the latex code for *Table 4: Impact of MDL cost model and bottom-up style to the overall accuracy of ReCG.*

Here is an example and expected output.

```text
    \texttt{ReCG} (KSE as cost model)               & 1.00      & 0.83  & 0.89  \\\hline
    \texttt{ReCG} (Top-down schema generation)      & 1.00      & 0.88  & 0.92  \\\specialrule{1.0pt}{0.5pt}{0.5pt}
    \texttt{ReCG}                                   & 1.00      & 0.92  & 0.95  \\\hline
```


### (G) Analyzing the Correlation between Jxplain's Runtime & Number of Distinct Keys in the Dataset (Section 5.4, Paragraph 1)

```bash
python3 8_jxplainRuntimeKeysAnalysis.py
```
This code prints the correlation between Jxplain's runtime and the number of distinct keys within a dataset.
