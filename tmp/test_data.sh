scrdir=/home/grassuser/road_project_scripts
wrkdir=$PWD
csv=./station_data_test.csv
st=00
cp $scrdir/master_scripts/search_zipfiles_nounzip.py .
#cp $scrdir/master_scripts/grab_data_dsm.py .

#python calcTiles.py $wrkdir/$csv $st $wrkdir $scrdir
python3 grab_data_dsm.py -ul $wrkdir/$csv -cid $st -out $wrkdir -td $scrdir
