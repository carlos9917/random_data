'''
This module extends and integrates the calcTiles.py script

'''
import subprocess
import os
import pandas as pd
import datetime
import sys
import numpy as np
from collections import OrderedDict
from search_zipfiles_nounzip import TIF_files as TIF_files
import os

def check_transf(files,outdir):
    check_files=[]
    print(files)
    for f in files:
        print(os.path.join(outdir,f))
        if os.path.isfile(os.path.join(outdir,f)) and "zip" in f:
            check_files.append(True)
        else:     
            check_files.append(False)
    return all(check_files)  

def get_dsm_files(files,outdir,user="cap",password="RoadProject2020!"):
    '''
    Go through all files in list of files,
    wget each and write the output in log file.
    Check if log file contains name of the file and saved.
    Example command:
    wget --user cap --password RoadProject2020! ftp://ftp.kortforsyningen.dk/dhm_danmarks_hoejdemodel/DSM/DSM_604_68_TIF_UTM32-ETRS89.zip
    '''
    user_data={'user':user,'pass':password,
               'source':'ftp://ftp.kortforsyningen.dk/dhm_danmarks_hoejdemodel/DSM',
               'log':'log_wget.txt',
               'outdir':outdir}
    #check files is a list otherwise define as such if only one element
    if type(files) is not list:
        files=[files]
    check_transfer=[]
    for dfile in files:
        cmd='wget --user '+user_data['user']+' --password '+user_data['pass']+' -o '+user_data['log']+' '+os.path.join(user_data['source'],dfile)+' -P '+user_data['outdir']
        try:
            ret=subprocess.check_output(cmd,shell=True)
            with open(user_data['log'],"r") as f:
                log_out=f.readlines()
            #second last line of log file will contain words saved and file name if all good
            if dfile  and "saved" in log_out[-2]:
                check_transfer.append(True)
            else:
                check_transfer.append(False)
                print("File %s not transferred!"%dfile)
        except subprocess.CalledProcessError as err:
            print("Error with call %s"%cmd)
            print(err)
            check_transfer.append(False)
    #if all files were transferred, this will return True, otherwise it will be False
    return all(check_transfer)

def get_dsm_files_hpc(get_files):
    '''
    Get the files from the hpc.
    Assumes user has access throgh scp
    '''
    cmd="bash "+get_files
    try:
        ret=subprocess.check_output(cmd,shell=True)
    except subprocess.CalledProcessError as err:
        print("Error with call %s"%cmd)
        print(err)



def read_tif_list(FILE):
    tif_list=np.loadtxt(FILE,delimiter=' ',dtype=str)
    return tif_list


def calc_tiles(stretchlist):
    '''
    Split the list of stations in their corresponding tiles.
    output is an ordered dict with all the tiles needed
    (formerly the /tmp/horangle-NN/tile_Norting_Easting directory).

    Each key is of the form XXXX_YYY, where XXX is the Norting
    and YYY the Easting (both divided by 1000).
    Each key contains a list with all the stretches contained in that tile

    '''
    #Calculate number of lines in the file:
    tiles_list=OrderedDict()
    #for k,stretch in enumerate(stretchlist['station'].values): #`cat $stretchlist`; do
    for k,stretch in stretchlist.iterrows(): #`cat $stretchlist`; do
        insert='|'.join([str(stretch['easting']),str(stretch['norting']),str(stretch['id1']),str(stretch['station']),str(stretch['id2'])])
        stretch_east=stretchlist['easting'][k]
        stretch_nort=stretchlist['norting'][k]
        stretch_tile = str(int(stretch_nort/1000))+'_'+str(int(stretch_east/1000))
        #print(stretch_tile)
        #define the dict comp as list if not already done
        try:
            if not isinstance(tiles_list[stretch_tile], list):
                pass
        except:
                #print("Tile %s not defined yet \n"%stretch_tile)
                tiles_list[stretch_tile] = []
        tiles_list[stretch_tile].append(insert)
        #stretchlist['easting'],'norting','id1','station','id2']
    return tiles_list

def loop_tilelist(list_tiles, tif_files):
    tileside=1
    mindist=1
    maxdistance=1000
    dist=maxdistance / 1000
    tiles=OrderedDict()
    files=OrderedDict()
    for tkey in list_tiles.keys():
        tiles_list=[]
        files_list=[]
        east = int(tkey.split('_')[1])
        north = int(tkey.split('_')[0])
        #print("east and north: %d %d"%(east,north))
        tile_east = 1000 * ( east + tileside )
        tile_west = 1000 * east
        tile_north = 1000 *( north + tileside )
        tile_south = 1000 * north
        if (dist < 1 ):
            dist=mindist # was 10, then was set to 1
        domain_east = tile_west / 1000 + dist
        domain_west = tile_west / 1000 - dist
        domain_north = tile_south / 1000 + dist
        domain_south =  tile_south / 1000 - dist
        for tfile in tif_files:
            sw_corner_east = int(tfile.split('_')[3].replace('.tif',''))
            sw_corner_north = int(tfile.split('_')[2]) 
            if ( sw_corner_east <= domain_east and sw_corner_east >= domain_west and
                 sw_corner_north <= domain_north and sw_corner_north >= domain_south):
                tiles_list.append('_'.join([str(sw_corner_north), str(sw_corner_east)]))
                files_list.append(tfile)
        tiles[tkey] = tiles_list
        files[tkey] = files_list
    return tiles, files

def look_for_tiles(tiles,cdir):
    lookup_tifs=[]
    for item in tiles:
        lookup_tifs.append(''.join(['DSM_1km_',item,'.tif']))
  
    #cdir='/home/cap/GIS/road_project_scripts/'
    outdir=cdir
    avail_tifs=TIF_files(zipfiles=os.path.join(cdir,'zip_files_list.txt'),zipdir=os.path.join(cdir,'list_zip_contents'),outdir=outdir)
    zipfiles=avail_tifs.find_zipfiles(lookup_tifs)
    #zipfiles = locate_zipfiles(lookup_tifs,cdir,outdir)
    return zipfiles

def main(args):
    utmlist=args.utm_list
    stnum=args.csv_id
    outdir=args.out_dir
    tifdir=args.tif_dir
    usehpc=args.local_zipfiles #true if data in hpc or in local dir
    gen_bash_file=args.gen_bash_file

    stretchlist=pd.read_csv(utmlist,sep='|',header=None)
    stretchlist.columns=['easting','norting','id1','station','id2']
    tif_files=read_tif_list(os.path.join(tifdir,'list_of_tif_files.txt'))
    import time
    t0 = time.time()
    #this one needs the argument 1:
    tiles_list = calc_tiles(stretchlist) #takes 11.9 sec for the whole thing
    t1 = time.time()
    total=t1-t0
    print("timing for calc_tiles %g"%total)
    t0 = time.time()
    tiles, files = loop_tilelist(tiles_list, tif_files)
    t1 = time.time()
    total=t1-t0
    print("timing for loop_tilelist %g"%total)

    #locate zip files corresponding to a particular set of tiles:
    outdir=os.path.join(outdir,'stations_'+str(stnum))
    try:
        os.mkdir(outdir)
    except:
        print("%s exists"%outdir)
    import csv
    t0 = time.time()
    zip_files=[]
    for k,tkey in enumerate(tiles.keys()):
        zip_files.extend(look_for_tiles(tiles[tkey],tifdir))
        #now write the data
        with open(os.path.join(outdir,'tilesneeded_'+str(k).zfill(3)+'.txt'), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=" ", lineterminator=os.linesep)
            writer.writerow(tiles[tkey])

        with open(os.path.join(outdir,'filesneeded_'+str(k).zfill(3)+'.txt'), 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=" ", lineterminator=os.linesep)
            writer.writerow(files[tkey])
    uniq_zips=set(zip_files) #many will be repeated, so clean this up
    zip_files=sorted(uniq_zips)

    if gen_bash_file:
        gfile=os.path.join(outdir,'get_zipfiles_'+str(stnum)+'.sh')    
        with open(gfile,'w') as ofile:
            for zfile in zip_files:
                if usehpc:
                    hpcfile=os.path.join('/data/cap/DSM_DK/',zfile)
                    ofile.write('scp freyja-2.dmi.dk:'+hpcfile+' . \n')
                else:
                    print("printing only the zip file names")
                    ofile.write(zfile+'\n')
        t1 = time.time()
        total=t1-t0
        print("timing for the writing part: %g"%total)
    else:
        if not check_transf(zip_files,outdir):
            status=get_dsm_files(zip_files,outdir)
            if status:
                print("All files transferred")
            else:
                print("Some of the files were not transferred")
                print("Check error logs")
        else:
            print("Files already transferred")

if __name__ == '__main__':
    import argparse
    from argparse import RawTextHelpFormatter

    parser = argparse.ArgumentParser(description='''If no argument provided it will take the default config file
             Example usage: ./TODO''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-ul','--utm_list',
           metavar='the csv file with the stations in utm coordinates',
           type=str,
           default=None,
           required=True)
    parser.add_argument('-cid','--csv_id',
           metavar='the number of the csv file',
           type=str,
           default=None,
           required=True)

    parser.add_argument('-out','--out_dir',
           metavar='where to write the data',
           type=str,
           default=None,
           required=True)

    parser.add_argument('-td','--tif_dir',
           metavar='where to find list of tif files',
           type=str,
           default=None,
           required=True)

    parser.add_argument('-lz','--local_zipfiles',action='store_true') # false by default
    parser.add_argument('-bf','--gen_bash_file',action='store_true') # false by default


    try:
        args = parser.parse_args()
        main(args)
    except:
        print("Error. Printing main options")
        parser.print_help()
        main(args) # so I can see where the error is occurring

