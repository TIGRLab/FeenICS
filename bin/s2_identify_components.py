#!/usr/bin/env python

"""
Requires output of FSL Melodic. Calls check_slices.py to identify components containing spiral artifact.

Usage:
    s2_identify_components.py -m <midFactor> -l <lowFactor> <directory>

Arguments:
    <directory>         path to top experiment directory

Options:
    -m, --midFactor     Cutoff multiplier for mid range frequency information. Raise this value to more aggressively remove noise components. Default is 3.
    -l, --lowFactor     Cutoff multiplier for low range frequency information. Raise this value to keep more signal components. Default is 1.

"""

import argparse
import os, sys
import check_slices

parser = argparse.ArgumentParser(description="Remove sprl noise components from all subjects in run folder")

parser.add_argument("-m", "--midFactor", help="cutoff factor for mid/high frequency -noise. Increase to remove more 'noise' components. Default is 3.")
parser.add_argument("-l", "--lowFactor", help="cutoff factor for low frequency -signal. Increase to remove more 'signal' components. Default is 1.")
parser.add_argument("directory", type=str, help="path to top experiment directory")
args = parser.parse_args()

def main(midFactor, lowFactor, directory):

    list_subs = os.listdir(directory)
    subfolders = ["sprlIN", "sprlOUT"]
    csvfilename = 'fix4melview_Standard_thr20.txt'

    midFactor = float(midFactor)
    lowFactor = float(lowFactor)

    # for each subject and each sprl condition (IN or OUT), call check_slices to create .txt file listing comps to be removed
    for i in list_subs:
        for sprl in subfolders:
            melodicfile =  os.path.join(directory, i, sprl, 'filtered_func_data.ica', 'melodic_IC.nii.gz')
            outputcsv= os.path.join(directory, i, sprl, csvfilename)

            try:
                print("Identifying components to be removed for {}, {}".format(i, sprl))
                check_slices.main(melodicfile, outputcsv, midFactor, lowFactor)
            except Exception:
                print("Could not find melodic_IC file for {}, {} or Permissions Error".format(i, sprl))
                continue

if __name__ == '__main__':

    if args.midFactor:
        midFactor = args.midFactor
    else:
        midFactor = 3

    if args.lowFactor:
        lowFactor = args.lowFactor
    else:
        lowFactor = 1

    directory = args.directory

    main(midFactor, lowFactor, directory)
