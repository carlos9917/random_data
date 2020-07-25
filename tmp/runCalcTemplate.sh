#!/bin/bash
######################################################
# Template script to run the calcShadows script
# This script is called by runGrassBatchMode.sh
######################################################

WRKDIR=/home/cap/GIS/road_project_scripts
tilesDir=$PWD


cd $WRKDIR

now=`date '+%Y%m%d_%H%M%S'`
st=REPLACE #CHANGED by runGrassBatchMode.sh
echo "--------------------------------"
echo "REMEMBER TO LOAD GRASS FIRST!!!"
echo "--------------------------------"

echo "Running calcShadows"
python3 ./calculateShadows.py -sl $tilesDir/station_data_test.csv -si $st >& out_${st}_$now
echo "calcShadows done"
cd -
