#!/usr/bin/env python

"""
Requires .csv files with final row of components to remove. Calls FSL reg_filt to regress out identified components.

Usage:
    s3_1_regfilt.py <directory>

Arguments:
    <directory>         path to top experiment directory

Options:
    -c, --clean_img      path to desired location of cleaned images
    -o, --output         if csv outputs were generated in non-default location, identify path to this location

"""

import argparse
import os, sys
from subprocess import call

parser = argparse.ArgumentParser(description="Regresses out identified components using fsl_regfilt. REQUIRES FSL!")
parser.add_argument("-c", "--clean_img", help="alternative output location for cleaned images")
parser.add_argument("-o", "--output", help="specify location of .csv slice identification files if these were generated in non-default location")
parser.add_argument("directory", type=str, help="path to top experiment directory")
args = parser.parse_args()

# this function reads the slices to be removed to a string, and submits to the reg_filt function

def regfilt(csv, clean_img, directory, i, sprl):

    slices2remove = []
    filename = []

# Open the final removal file; the last line contains the components to be removed
    try:
        print("Removing components from {}, {}".format(i, sprl))
        with open(csv) as file:
            slices = file.readlines()[-1]
    except Exception:
        print("fix4melview_Standard_thr20.txt not found. Have you run s2_identify_components.py?")
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

    if (clean_img != directory):
        clean_img = directory + clean_img + '/' + '.'.join(filename)
    else:
        clean_img = os.path.join(clean_img, '.'.join(filename))

    if (slices2remove != '""'):
        # call fsl_regfilt to perform the component regression
        call(["fsl_regfilt", "-i", "filtered_func_data", "-o", clean_img, "-d", "filtered_func_data.ica/melodic_mix", "-f", slices2remove])
    elif (slices2remove == '""'):
        clean_img = clean_img + ".nii.gz"
        call(["cp", "filtered_func_data.nii.gz", clean_img])

def main(directory, clean_img, output):

    list = os.listdir(directory)

    for i in list:
        if os.path.isdir(os.path.join(directory, i, 'sprlIN')) == True:
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
            regfilt(outputcsvSPRLIN, clean_img, directory, i, "sprlIN")
            regfilt(outputcsvSPRLOUT, clean_img, directory, i, "sprlOUT")

if __name__ == '__main__':

    directory = args.directory

    if args.clean_img:
        clean_img = args.clean_img
    else:
        clean_img = args.directory

    if args.output:
        output = args.output
    else:
        output = args.directory

    main(directory, clean_img, output)
