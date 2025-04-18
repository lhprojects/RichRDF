


python Test_python.py allcoll_evt &
PID_A=$!

python readPlotMemUsage.py $PID_A "images/allcoll_evt.png" 


python Test_python.py allcoll_RDataFrame &
PID_A=$!

python readPlotMemUsage.py $PID_A "images/allcoll_RDataFrame.png" 



python Test_python.py mcrec_evt &
PID_A=$!

python readPlotMemUsage.py $PID_A "images/mcrec_evt.png" 

python Test_python.py mcrec_RDataFrame &
PID_A=$!

python readPlotMemUsage.py $PID_A "images/mcrec_RDataFrame.png" 



