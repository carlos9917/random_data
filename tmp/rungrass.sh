#!/bin/bash

#Master script to run grass through a list of stations

# Steps:
#0. Generate list of required tiles (see calcTiles.py in calc_tiles_hpc)
#1. Pull out the station data from hpcdev (the necessary script
#   is generated in step 0
#2.

#Loop through several Grass sessions for each station list
getZipFiles=0

WRKDIR=/home/grassuser/gis/road_project_scripts
tilesDir=$WRKDIR/calc_tiles_hpc
now=`date '+%Y%m%d_%H%M%S'`
for i in 00; do # note: can also do 00..NN and it will add the leading 0
 st=`printf "%02d" $i`
 echo "Doing station list $st"	
 #pull out and uncompress data
 if [ $getZipFiles == 1 ]; then
     echo "Pulling out zip files"
     cd $tilesDir/stations_${st}
     /bin/bash ./get_zipfiles_${st}.sh
     pid=$!
     wait $pid
     echo "Pulling zip files DONE. Unzipping files"
     cp $tilesDir/uncomp.sh .
     /bin/bash ./uncomp.sh >& ./decomp.txt
     pid=$!
     wait $pid
 else
     echo "Not getting zip files"	 
 fi
 cd $WRKDIR
 echo "Files unzip DONE. Calling Grass. Doing station list $st"
 time /bin/bash ./runGrassBatchMode.sh $st >& salida_${st}
 pid=$!
 wait $pid
 echo "Station list $st finished."
 echo "Removing tif files for this station list"
 cd $WRKDIR/calc_tiles_hpc/stations_${st}
 echo "Keeping tif files"
 #rm -f *.tif *.zip *.md5
 pid=$!
 wait $pid
 #time ./calcShadows3.sh calc_tiles_hpc/csv_split_92_files/final_list_utm_${st} $st >& out_${st}_$now
done
echo "Finished"
