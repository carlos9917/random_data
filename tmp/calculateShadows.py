'''
Python version of the calculateShadows.sh bash script
originally used to call Grass
'''
import sqlite3
from datetime import datetime
import argparse
from argparse import RawTextHelpFormatter
import configparser
from collections import OrderedDict
import shadowFunctions as sf
import os
import pandas as pd
import sys
import logging

#logger = logging.getLogger(__name__)
def setup_logger(logFile,outScreen=False):
    '''
    Set up the logger output
    '''
    global logger
    global fmt
    global fname
    logger = logging.getLogger(__name__)
    fmt_debug = logging.Formatter('%(levelname)s:%(name)s %(message)s - %(asctime)s -  %(module)s.%(funcName)s:%(lineno)s')
    fmt_default = logging.Formatter('%(levelname)-8s:  %(asctime)s -- %(name)s: %(message)s')
    fmt = fmt_default
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fname = logFile
    fh = logging.FileHandler(fname, mode='w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    if outScreen:
        logger.addHandler(ch) # Turn on to also log to screen


def main(args):
    stretchlist=args.stretch_list #${1-stretchlist_utm.csv}
    stretchnum=args.stretch_id  #the number of the stretch list
    cfile=args.config_file
    shpars=sf.read_conf(cfile)
    #print(shpars)
    tilesDir=shpars['tilesDir']
    resolution=shpars['resolution']
    horizonstep=shpars['horizonstep']
    tileside=shpars['tileside']
    maxdistance=shpars['maxdistance']
    mindist=shpars['mindist']
    mintiles=shpars['mintiles']
    csv_set=stretchnum #CHANGE
    Decomp_dir=os.path.join(tilesDir,'stations_'+stretchnum)
    tilesdir=Decomp_dir
    out_dir='_'.join(['lh',maxdistance,resolution,horizonstep,csv_set])
    now=datetime.strftime(datetime.now(),'%Y%m%d_%H%M%S')
    print("Starting on %s"%now)
    print("Processing stretch  %s"%stretchlist)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        print("Output directory %s already exists"%out_dir)
    logFile=os.path.join(out_dir,args.log_file)
    setup_logger(logFile,outScreen=False)
    logger.info("Starting shadow calculation")
    #PRE-PROCESSING
    logger.info("Reading data from %s"%stretchlist)    
    stretch_data=sf.read_stretch(stretchlist)
    tiles_list = sf.calc_tiles(stretch_data)
    tif_files=sf.read_tif_list('/home/grassuser/road_project_scripts/list_of_tif_files.txt')
    #tiles_needed, files_needed = sf.loop_tilelist(tiles_list,tif_files,tilesdir)
    tiles_needed = sf.loop_tilelist(tiles_list,tif_files,tilesdir)
    #print("Tiles needed")
    #print(tiles_needed.keys())
    #print(tiles_needed['coords'])
    #print(tiles_needed['station_tile'])
    #print(tiles_needed['surrounding_tile'])
    sf.call_grass("set_resolution",shpars)
    #SHADOW CALCULATION
    sf.calc_shadows(stretch_data,tiles_needed,shpars,out_dir)
    logger.info("Shadow calculation done")
    '''
    #############################################################
    #Turning this off 20200604
    #copy the data to freyja
    #echo "transferring the data to freyja"
    #echo "command: scp -r $WD/$out_dir freyja-2.dmi.dk:/data/cap/DSM_DK/FinalResults_Sept2019"
    #scp -r $WD/$out_dir freyja-2.dmi.dk:/data/cap/DSM_DK/FinalResults_Sept2019
    #############################################################
    '''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''If no argument provided it will take the default config file
             Example usage: ./calculateShadows.py -c shadows_conf.ini''', formatter_class=RawTextHelpFormatter)

    parser.add_argument('-c','--config_file',
           metavar='config file to be read',
           type=str,
           default='./shadows_conf.ini',
           required=False)

    parser.add_argument('-sl','--stretch_list',
           metavar='list of stations to be processed',
           type=str,
           default="./stretchlist_utm.csv",
           required=False)

    parser.add_argument('-si','--stretch_id',
           metavar='Number identifying the stretch. To be used in data output files',
           type=str,
           default='0',
           required=False)

    parser.add_argument('-lg','--log_file',metavar='Log file name',
                                type=str, default='shadows.log', required=False)

    try:
        args = parser.parse_args()
        main(args)
    except:
        print("Error. Printing main options")
        #main(args)
        parser.print_help()
        main(args)

