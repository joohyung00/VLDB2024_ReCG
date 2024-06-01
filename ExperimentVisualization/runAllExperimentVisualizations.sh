python3 1.1_AccExperimentVis.py
python3 2.1_MdlExperimentVis.py
python3 3.1_PerformanceExperimentVis.py
python3 4.1_ParamExperimentVis.py --exp BeamWidth
python3 4.1_ParamExperimentVis.py --exp Epsilon
python3 4.1_ParamExperimentVis.py --exp MinPtsPerc
python3 4.1_ParamExperimentVis.py --exp MDLWeights

clear

python3 1.2_AccExperimentAgg.py
python3 1.3_AccExperimentTab.py
python3 2.2_MdlExperimentAgg.py
python3 3.2_PerformanceExperimentAgg.py
python3 4.2_ParamExperimentAgg.py
python3 6.2_AblationStudyAgg.py
python3 7_checkDifferenceForEasierNegatives.py
python3 8_jxplainRuntimeKeysAnalysis.py
python3 9_analyzeRuntimeOfJxplain.py