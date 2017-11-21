#!/usr/bin/env python

"""
Requires .csv files with final row of components to remove. Calls FSL reg_filt to regress out identified components.

Usage:
    s4_1_regfilt.py <directory> <clean_img> <-o output>

Arguments:
    <directory>      path to run location
                        (i.e. location where subject folders and MELODIC output are contained)

    <cleaned images> path to desired location of cleaned images

Options:
    --output PATH       if csv outputs were generated in non-default location, identify path to this location

"""

import argparse
import os, sys
from subprocess import call

parser = argparse.ArgumentParser(description="Regresses out identified components using fsl_regfilt. REQUIRES FSL!")
parser.add_argument("-o", "--output", help="specify location of .csv slice identification files if these were generated in non-default location")
parser.add_argument("directory", type=str, help="location of the run directory (contains subject folders)")
parser.add_argument("clean_img", type=str, help="desired final location of cleaned images")
parser.add_argument("-d", "--date", help="specify if scan was completed before or after hardware update either '--date before' or '--date after'")
args = parser.parse_args()

# this function reads the slices to be removed to a string, and submits to the reg_filt function

def regfilt(csv, clean_img, directory, i, sprl, date):

    slices2remove = []
    filename = []

# Open the final removal file; the last line contains the components to be removed
    try:
        print("Removing components from {}, {}".format(i, sprl))
        with open(csv) as file:
            slices = file.readlines()[-1]
    except Exception:
        print("Could not find file containing components to be removed")
        return

# Remove brackets
    slices2remove = slices.split(",")
    slices2remove = slices2remove[1:-1]
# Join into comma separated string
    slices2remove = ','.join(slices2remove)
# put quotes around slices to be removed
    slices2remove = '"' + slices2remove + '"'
# create file name for output image
    filename = [i,sprl,'denoised']
# move into the subject's Prestats folder
    os.chdir(os.path.join(directory, i, sprl))
# create file path for output image
    clean_img =  os.path.join(clean_img, '.'.join(filename))
    if ((slices2remove != '""') and (date == 'after')):
        # call fsl_regfilt to perform the component regression
        call(["fsl_regfilt", "-i", "filtered_func_data", "-o", clean_img, "-d", "filtered_func_data.ica/melodic_mix", "-f", slices2remove])
    elif ((slices2remove == '""') or (date == 'before')):
        clean_img = clean_img + ".nii.gz"
        call(["cp", "filtered_func_data.nii.gz", clean_img])

def main(directory, clean_img, output, date):

    list = os.listdir(directory)
    for i in list:
# name of file containing list of components to remove
        csvfilenameSPRLIN = 'fix4melview_Standard_thr20.txt'
        csvfilenameSPRLOUT = 'fix4melview_Standard_thr20.txt'

# file path to list of components to remove
        if output is not directory:
            outputcsvSPRLIN = os.path.join(output, csvfilenameSPRLIN)
            outputcsvSPRLOUT = os.path.join(output, csvfilenameSPRLOUT)
        else:
            outputcsvSPRLIN = os.path.join(directory, i, 'sprlIN', csvfilenameSPRLIN)
            outputcsvSPRLOUT = os.path.join(directory, i, 'sprlOUT', csvfilenameSPRLOUT)

# call regfilt function to regress out components
        regfilt(outputcsvSPRLIN, clean_img, directory, i, "sprlIN", date)
        regfilt(outputcsvSPRLOUT, clean_img, directory, i, "sprlOUT", date)


if __name__ == '__main__':

    directory = args.directory
    clean_img = args.clean_img

    if args.output:
        output = args.output
    else:
        output = directory

    if args.date:
        date = args.date
    else:
        date = "after"

    main(directory, clean_img, output, date)
