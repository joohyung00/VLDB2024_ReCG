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

### (A) Visualizing 'Accuracy Comparison' (Section 5.2)


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

### (B) Visualizing 'MDL Cost Analysis' (Section 5.3)

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

### (C) Visualizing 'Scalability with Dataset Size' (Section 5.4)

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



### (D) Visualizing 'Parameter Sensitivity' (Section 5.5)

```bash
python3 4.1_ParamExperimentVis.py --exp BeamWidth
python3 4.1_ParamExperimentVis.py --exp Epsilon
python3 4.1_ParamExperimentVis.py --exp MinPtsPerc
python3 4.1_ParamExperimentVis.py --exp MDLWeights
```

This plots the accuracies of the disovered schemas for each algorithm.

Here is an example of the output: 

<p align = "center">
<img src="images/4_param.png" alt="drawing" width="400"/>
</p>


```bash
python3 4.2_ParamExperimentAgg.py
```

This prints the values that we used in our paper.




### (E) Visualizing 'Impact of Design Factors to Accuracy' (Section 5.6)

```bash
python3 6.2_AblationStudyAgg.py
```

This prints the latex table and the values that we used in our paper.





### (F) Visualizing the Impact of Easier Negative Samples

```bash
python3 7_checkDifferenceForEasierNegatives.py
```

This prints the values, for the accuracies that we get if we use an easier negative sample set.



### (G) Analyzing the Correlation between Jxplain's Runtime & Number of Distinct Keys in the Dataset

```bash
python3 8_jxplainRuntimeKeysAnalysis.py
```
This prints the correlation between Jxplain's runtime and the total number of distinct keys.



### (H) Analyzing Runtime Bottleneck of Jxplain

```bash
python3 9_analyzeRuntimeOfJxplain.py
```
This prints the value for how much percentage of total Jxplain's time is consumed by its heterogeneity determination and clustering.

