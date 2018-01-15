#!/bin/bash
echo "Running your super awesome match automation script!"

#update player in scaffold
echo "Updating player in scaffold"
rm -r ../bc18-scaffold/player1
cp -R player1/ ../bc18-scaffold/

#read parameter config file
# NOT IMPLEMENTED


#for each parameter set in config file,
#   insert parameter set into staged file in player folder in the scaffold
#      ->need to adjust player to try to read parameters if present (otherwise use default params)
#   run match
echo "running match, output to logs/rawOutput.txt"
echo "temporarily moving to scaffold directory"
cd ../bc18-scaffold
#./battlecode.sh -p1 player1 -p2 examplefuncsplayer-python -m socket.bc18map --replay-dir ../battlecode2018/replays > ../battlecode2018/logs/rawOutput.txt
./battlecode.sh -p1 player1 -p2 player1 -m socket --replay-dir ../battlecode2018/replays > ../battlecode2018/logs/rawOutput.txt

cd ../battlecode2018
echo "match is over, back home, parsing match output"

#   run parser to create csvs
python3 parseMatchOutput.py

echo "End of match automation script."
