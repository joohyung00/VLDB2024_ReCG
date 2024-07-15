
echo "Running Accuracy Comparison Experiment Visualization"
python3 1.1_AccExperimentVis.py
echo 

echo "Running MDL Analysis Experiment Visualization"
python3 2.1_MdlExperimentVis.py
echo

echo "Running Scalability with Dataset Size Experiment Visualization"
python3 3.1_PerformanceExperimentVis.py
echo

echo "Running Parameter Sensitivity Experiment Visualization"
python3 4.1_ParamExperimentVis.py --exp BeamWidth
python3 4.1_ParamExperimentVis.py --exp Epsilon
python3 4.1_ParamExperimentVis.py --exp MinPtsPerc
python3 4.1_ParamExperimentVis.py --exp MDLWeights
echo

clear

echo "Visualizing the Analysis for the Dataset (Table 1 in the paper)"
echo
python3 python3 0_DatasetTab.py --mode all
echo
echo

echo "Visualizing Analysis for Accuracy Comparison Experiment"
echo
python3 1.2_AccExperimentAgg.py
echo
echo

echo "Printing the Latex code for Table 2 of our paper."
echo
python3 1.3_AccExperimentTab.py
echo
echo

echo "Visualizing Analysis for the MDL Experiment"
echo
python3 2.2_MdlExperimentAgg.py
echo
echo

echo "Printing the Latex code for Table 3 of our paper."
echo
python3 3.2_PerformanceExperimentAgg.py
echo
echo

echo "Printing Analysis for the Parameter Sensitivity Experiment"
echo
python3 4.2_ParamExperimentAgg.py
echo
echo

echo "Printing the Analysis for Design Factors"
echo
python3 6.2_DesignFactors.py
echo
echo

echo "Printing the Analysis about the Correlation of Jxplain Runtime and the Number of Distinct Keys in the Dataset"
echo
python3 8_jxplainRuntimeKeysAnalysis.py
echo
echo 