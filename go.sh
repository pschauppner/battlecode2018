#!/bin/bash
echo "Running your super awesome match automation script!"

echo "Removing player in scaffold"
rm -r ../bc18-scaffold/player1

echo "copying player into scaffold"
cp -R player1/ ../bc18-scaffold/

echo "running match, output to logs/rawOutput.txt"
cd ../bc18-scaffold
./battlecode.sh -p1 player1 -p2 examplefuncsplayer-python -m socket.bc18map --replay-dir ../battlecode2018/replays > ../battlecode2018/logs/rawOutput.txt

echo "End of match automation script."
