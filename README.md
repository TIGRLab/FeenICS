# FeenICS (fē'nĭks)
A pipeline for FrEquENcy-based Ica Cleaning of Spirals. Aims to remove spiral-specific aritfact from fMRI scans.

This tool was built to work with FSL's [MELODIC](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/MELODIC).
It was created to automate the process of evaluating and removing ICA components containing spiral artifact, which is accomplished by evaulating the per slice frequency loading, and scoring components based on patterns
of low or high frequency information. The fsl_regfilt command-line program can then be used to regress out components selected for removal.

## Installation
```sh
git clone https://github.com/eziraldo/FeenICS.git
cd FeenICS
sudo python ./setup.py install
```

## Dependancies

This program requires either FSL or the outputs of FSL Melodic in order to work.
 + **FSL Melodic** http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/MELODIC

Python dependancies (these will be installed when you install FeenICS if you don't already have them):
 + nibabel
 + numpy
 + matplotlib
 + scipy
 + scikit-image (0.13.1)

## There are four executables:
+ [**s1_folder_setup.py**](#s1_1_folder_setup.py) : To create the folder structure necessary to run Melodic and the remainder of the scripts.
+ [**s2_identify_components.py**](#s2_1_identify_components.py) : To run check_slices.py for an entire folder of subjects and outputs a classification text file (default: fix4melview_Standard_thr20.txt).
+ [**s3_remove_flagged_components.py**](#s3_remove_flagged_components.py) : To remove flagged components once content with the results of the classifcation. This script reads the final line of the classification text file.
+ [**check_slices.py**](#check_slices.py) : To classify components as keep or remove. Is run by s2_identify_components.py, but can be run by itself on an individual scan.


### s1_folder_setup.py

```
Usage:
  s1_setup.py <directory> <subject_list> <sprl>

Arguments:

<directory>      path to run location (i.e. main folder where the required file stucture should be)
<subject_list>   path to folder containing subject names (as subfolders)
<sprl> 		 path to study folder containing split spirals
                    NOTE: MUST BE CONTAINED WITHIN SUBJECT FOLDER & BE NAMED "sprlIN.nii" & "sprlOUT.nii"

Options:

 --parallel, -p CLUSTER	   to print instuctions for running in parallel (GNU parallel), or to prevent from running FSL MCFLIRT, BET, and MELODIC steps

DETAILS
Makes subject and sprl subfolders within <directory>. Moves separated spiral files from <sprl> to appropriate <directory> subfolders. Subject folders are named after those contained in <subject_list>.
It is likely that two or more of these arguments will be the same path. If -p is not specified, run will motion correct using MCFLIRT, brain extract, register, and then run MELODIC.
Be aware that the script will create as many calls to MELODIC as there are sprl files.

```

### s2_identify_components.py

```
Usage:
  s2_identify_components.py <directory>

Arguments:

<directory>    path to run location (i.e. main folder where the required file stucture should be; same as s1_setup.py)

DETAILS
Feeds paths and output file names to check_slices.py for each subject within the specified directory. The default name for the output classification file is fix4melview_Standard_thr20.txt.
```

### s3_identify_components.py

```
Usage:
  s3_remove_flagged_components.py <directory> <clean_img> -o output

Arguments:
<directory>    path to run location
                    (i.e. location where subject folders and MELODIC output are contained; same as s1 and s2)

<cleaned>      path to desired location of cleaned, separated scans

Options:
    --output PATH       if csv outputs were generated in non-default location, identify path to this location

    --date, -d DATE     if processing data with a collection date straddling the scanner upgrade date, use the -d option to specify
                        Correct options are either "-d before" or "-d after". After is the default. Choosing "before" will not remove
                        any components, but will rename and place a copy of the preprocessed, but uncleaned spiral in the cleaned images path.
DETAILS
Uses fsl_regfilt to regress out the components specified in the last line of the classification file (fix4melview_Standard_thr20.txt).
The outputs are cleaned, but separated spiral niftis named subject.sprl.denoised.nii.gz, within the <cleaned> directory.
```

### check_slices.py

```
Usage:
  check_slices.py <melodic_file> <outputname>

Arguments:
<melodic_file>   path to any melodic_IC.nii.gz file
<outputname>     path to desired output classification file location

DETAILS
This script is called by s2_identify_components.py. Can be used independently to troubleshoot classification or path identification issues, or just to run one spiral scan at a time.
The algorithm scores each slice based on how much high and low frequency information is present after performing an FFT (fast fourier transform). The scores are tallied per component,
and the result deterimines whether or not a component is to be flagged for removal. The output of this script is a classification text file (fix4melview_Standard_thr20.txt), which details
the score and classification criteria per slice, as well as the removal decision per component. The final line of this document is a list of which components are to be removed. If you disagree
with the decision, change the component numbers in this list, as this line will be read into s3_remove_flagged_components.py.

```
### Usage Examples:

To run FeenICS locally for an experiment called EXPR, with additional use of Erin Dickie's ICArus package (https://github.com/edickie/ICArus) to better visualize the decisions made by the check_slices.py algorithm

#### Step 1:
~~~sh
s1_folder_setup.py /path/to/directory /path/to/subjectnames /path/to/spiralfiles
~~~

#### Step 2:
~~~sh
s2_identify_components.py /path/to/directory
~~~

#### Step 3(optional) - Run ICArus (see https://github.com/edickie/ICArus for install information):
~~~sh
MELODIC_OUTPUTS=`cd /path/to/directory; ls -1d */sprl*`
icarus-report ${MELODIC_OUTPUTS}
~~~

#### Step 4 - After you are okay with classifications, run s3_1_remove_flagged_components.py:
~~~sh
s3_remove_flagged_components.py /path/to/directory /path/to/desiredOutputFolder
~~~
