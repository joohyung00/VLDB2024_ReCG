

./buildJxplain.sh
./buildKReduce.sh
cd ReCG
./compile.sh
cd ..
cd ReCG_TopDown
./compile.sh
cd ..
cd Frozza
./compile.sh
cd ..
cd Klettke
./compile.sh
cd ..


cd Experiment
./runAllExperiments.sh
cd ..


cd ExperimentVisualization
./runAllExperimentVisualizations.sh
cd ..