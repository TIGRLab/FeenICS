#!/usr/bin/env python

"""
Sets up file structure required to run FSL Melodic. Requires split spiral scans (sprlIN.nii and sprlOUT.nii).
Usage:
    s1_folder_setup.py <directory>

Arguments:

    <directory>             path to top experiment directory. Outputs will be created here

Options:

    -i                      alternative experiment folder containing subjectID subfolders
    -s                      alternative folder containing split spirals
    -p                      to print instuctions for running in parallel (GNU parallel) invoke this option


"""
import argparse
import os, sys, errno, shutil, fnmatch
import subprocess

parser = argparse.ArgumentParser(description="Set up the required file structure and runs FSL Melodic")
parser.add_argument("-p", "--parallel", help="flag if you would like to run FSL steps on compute cluster in parallel (i.e. scc)")
parser.add_argument("-s", "--subs", help="alternative experiment folder containing subjectID subfolders. Use this option if directory does not already contain subjectID subfolders")
parser.add_argument("-i", "--sprl", help="alternative folder containing split spirals - NOTE: MUST BE CONTAINED WITHIN SUBJECT FOLDER & BE NAMED 'sprlIN.nii' & 'sprlOUT.nii'")
parser.add_argument("directory", type=str, help="path to top experiment directory. Outputs will be created here.")

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

def main(directory, subs, sprl, scc = False):

    #  Create file structure required to run FSL Melodic. SubjectID -> sprl* -> T1_brain, sprl*.nii
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    # list all the subjects in the subject directory
    list = os.listdir(subs)
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
                    try:
                        p = subprocess.Popen(motion_corr_cmd, stdout=subprocess.PIPE)
                        p.wait()
                        if p.returncode != 0:
                            print("motion correction failed")
                    except:
                        print("FSL not on path")
                        sys.exit(1)


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
                else:
                    print("Melodic already run. Remove folder to rerun")

    # to print commands for running FSL in parallel on scc or other computing cluster to terminal
    if scc == True:

        modules = "module load /KIMEL/quarantine/modules/quarantine\nmodule load GNU_PARALLEL/20160222\nmodule load qbatch\nmodule load FSL/5.0.9-ewd\n"

        rundir ="/KIMEL/tigrlab" + directory

        setup_cmds ="cd ${rundir}\nsubs=`cd ${rundir}; ls -1d */sprl*`\nsprls=`cd /KIMEL/tigrlab/scratch/eziraldo/Data_take2/COGDBY; ls`\n"

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

    if args.sprl:
        sprl = args.sprl
    else:
        sprl = args.directory

    if args.subs:
        subs = args.subs
    else:
        subs = args.directory

    if args.parallel:
        scc = True
    else:
        scc = False

    main(directory, subs, sprl, scc)
