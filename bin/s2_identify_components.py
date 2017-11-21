#!/usr/bin/env python

"""
Requires output of FSL Melodic. Calls check_slices.py to identify components containing spiral artifact.

Usage:
    s2_1_RemoveNoise.py <directory>

Arguments:
    <directory>      path to run location
                        (i.e. main folder where the required file stucture should be)

"""

import argparse
import os, sys
import check_slices_byNum

parser = argparse.ArgumentParser(description="Remove sprl noise components from all subjects in run folder")

parser.add_argument("directory", type=str, help="location of the run directory (contains subject folders)")
args = parser.parse_args()

def main(directory):

    list_subs = os.listdir(directory)
    subfolders = ["sprlIN", "sprlOUT"]
    csvfilename = 'fix4melview_Standard_thr20.txt'

    # for each subject and each sprl condition (IN or OUT), call check_slices to create .txt file listing comps to be removed
    for i in list_subs:
        for sprl in subfolders:
            melodicfile =  os.path.join(directory, i, sprl, 'filtered_func_data.ica', 'melodic_IC.nii.gz')
            outputcsv= os.path.join(directory, i, sprl, csvfilename)

            try:
                print("Identifying components to be removed for {}, {}".format(i, sprl))
                check_slices_byNum.main(melodicfile, outputcsv)
            except Exception:
                print("Could not find melodic_IC file for {}, {} or Permissions Error".format(i, sprl))
                continue

if __name__ == '__main__':

    directory = args.directory

    main(directory)
