#!/usr/bin/env python

"""
Sets up file structure required to run FSL Melodic. Requires split spiral scans (sprlIN.nii and sprlOUT.nii).
Usage:
    s1_1_setup.py -p cluster_name <run_location> <subject_list> <sprl*.nii>

Arguments:

    <sprl*.nii>         path to study folder containing split spirals
                            NOTE: MUST BE CONTAINED WITHIN SUBJECT FOLDER & BE NAMED "sprlIN.nii" & "sprlOUT.nii"

    <run_location>      path to run location (i.e. main folder where the required file stucture should be)
    <subject_list>      path to folder containing subject names (as subfolders)

Options:

    -p                  to print instuctions for running in parallel (GNU parallel) invoke this option

"""
import argparse
import os, sys, errno, shutil, fnmatch
import subprocess
import nibabel as nib

parser = argparse.ArgumentParser(description="Set up the required file structure and runs FSL Melodic")
parser.add_argument("-p", "--parallel", help="flag if you would like to run FSL steps on compute cluster in parallel (i.e. scc)")
parser.add_argument("directory", type=str, help="location of the run directory (contains MELODIC output folders)")
parser.add_argument("sub_list", type=str, help="file path containing subject names as subfolders")
parser.add_argument("sprl", type=str, help="path to study folder containing split spirals - NOTE: MUST BE CONTAINED WITHIN SUBJECT FOLDER & BE NAMED 'sprlIN.nii' & 'sprlOUT.nii'")

args = parser.parse_args()

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def copy(source, dest):
    try:
        shutil.copy(source[0], dest)
    except:
        print("File already exists")
        return

def main(directory, sub_list, sprl, scc = False):

    #  Create file structure required to run FSL Melodic. SubjectID -> sprl* -> T1_brain, sprl*.nii
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # list all the subjects in the subject directory
    list = os.listdir(sub_list)
    # define subfolders
    subfolders = ['sprlIN', 'sprlOUT']

    # only want to read TR once
    load_worked = False

    # iterate through subjects
    for i in list:
        sprlIN_tf = False
        sprlOUT_tf = False

        # locate the original spirals
        sprlIN_tf = os.path.exists(os.path.join(directory, i, "sprlIN", "sprlIN.nii"))
        sprlOUT_tf = os.path.exists(os.path.join(directory, i, "sprlOUT", "sprlOUT.nii"))

        # if sprlIN_tf == False:
        sprlIN_location = find('sprlIN.nii', os.path.join(sprl, i))

        # if sprlOUT_tf == False:
        sprlOUT_location = find('sprlOUT.nii', os.path.join(sprl, i))

        # Read TR from nifti header
        # if load_worked == False:
        #     try:
        #         imgIN = nib.load(sprlIN_location[0])
        #         hdrIN = imgIN.header
        #         TR = "--tr=" + str((hdrIN['pixdim'][4]))
        #         vol = str(hdrIN['dim'][4])
        #     except:
        #         print("Could not load image, {}".format(i))
        #         continue
        #     else:
        #         load_worked = True

        # make sprlIN and sprlOUT folders
        for subfolder in subfolders:
            if (sprlIN_tf == False) or (sprlOUT_tf == False):
                try:
                    os.makedirs(os.path.join(directory , i, subfolder))
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        continue

            # move sprl files into appropriate subfolders
                try:
                    print("Copying sprl files for subject {}, {}".format(i, subfolder))
                    if subfolder == 'sprlIN':
                        copy(sprlIN_location, os.path.join(directory, i, subfolder))
                    elif subfolder == 'sprlOUT':
                        copy(sprlOUT_location, os.path.join(directory, i, subfolder))
                except IndexError as e:
                    print("Error copying subject {}: {}".format(i, e))
                    continue

                # to run FSL commands locally
            if scc == False:
                os.chdir(os.path.join(directory, i, subfolder))

                # check if motion corrected file exists, call mcflirt if it does not
                mc_tf = os.path.exists("motion_corr.nii.gz")
                if mc_tf == False:
                    print("Motion correcting {}, {}".format(i, subfolder))
                    motion_corr_cmd = ["mcflirt", "-in", subfolder, "-refvol","2", "-out", "motion_corr", "-plots"]
                    p = subprocess.Popen(motion_corr_cmd, stdout=subprocess.PIPE)
                    p.wait()
                    if p.returncode != 0:
                        print("motion correction failed")

                # check if brain extracted file exists, if not call bet
                bet_tf = os.path.exists("mask_mask.nii.gz")
                if bet_tf == False:
                    print("Brain extracting {}, {}".format(i, subfolder))
                    bet_cmd = ["bet", "motion_corr", "mask", "-f", "0.4", "-m", "-n"]
                    p = subprocess.Popen(bet_cmd, stdout=subprocess.PIPE)
                    p.wait()
                    if p.returncode != 0:
                        print("brain extraction failed")

                # check if masked file exists, if not call fslmaths
                mask_tf = os.path.exists("filtered_func_data.nii.gz")
                if mask_tf == False:
                    print("Masking {}, {}".format(i, subfolder))
                    mask_cmd = ["fslmaths", "motion_corr", "-mas", "mask_mask", "filtered_func_data"]
                    p = subprocess.Popen(mask_cmd, stdout=subprocess.PIPE)
                    p.wait()
                    if p.returncode != 0:
                        print("masking failed")

                # check if melodic_IC file exists, if not call melodic
                melodic_tf = os.path.exists(os.path.join("filtered_func_data.ica", "melodic_IC.nii.gz"))
                if melodic_tf == False:
                    print("Running ICA (melodic) {}, {}. Check filtered_func_data.ica/log.txt for process details".format(i, subfolder))
                    melodic_cmd = ["melodic", "-i", "filtered_func_data", "-o", "filtered_func_data.ica", "-v", "--nobet", "--bgthreshold=0", "-d", "0", "--report", "--guireport=../../report.html"]
                    p = subprocess.Popen(melodic_cmd, stdout=open(os.devnull, 'wb'))

    # to print commands for running FSL in parallel on scc or other computing cluster to terminal
    if scc == True:

        modules = "module load /KIMEL/quarantine/modules/quarantine\nmodule load GNU_PARALLEL/20160222\nmodule load qbatch\nmodule load FSL/5.0.9-ewd\n"

        rundir ="/KIMEL/tigrlab" + directory

        setup_cmds ="cd ${rundir}\nsubs=`cd ${rundir}; ls -1d */sprl*`\nsprls=`cd /KIMEL/tigrlab/scratch/eziraldo/Data_take2/COGDBY/2015_0707_PR031_SpiralSeparated; ls`\n"

        mcflirtBET_cmd= "echo mcflirt -in ${rundir}/{}/{/}.nii -refvol 2 -out {}/motion_corr -plots; echo bet {}/motion_corr {}/mask -f 0.4 -m -n; fslmaths ${rundir}/{}/motion_corr -mas ${rundir}/{}/mask_mask ${rundir}/{}/filtered_func_data"
        melodic_cmd = "echo melodic -i ${rundir}/{}/filtered_func_data -o {}/filtered_func_data.ica -v --nobet --bgthreshold=0 -d 0 --report --guireport=../../report.html"

        fsl_cmd = 'parallel -k "' + mcflirtBET_cmd + melodic_cmd + '" ::: ${subs} ${sprls} ${subs}| qbatch --walltime' + " '02:00:00' --ppj 6 -c 3 -j 3 -N melodicSTUDYNAME -"


        print("\nPrint the following in the terminal:\n")
        print(modules)
        print("rundir={}".format(rundir))
        print(setup_cmds)
        print(fsl_cmd)


if __name__ == '__main__':

    directory = args.directory
    sub_list = args.sub_list
    sprl = args.sprl

    if args.parallel:
        scc = True
    else:
        scc = False

    main(directory, sub_list, sprl, scc)
