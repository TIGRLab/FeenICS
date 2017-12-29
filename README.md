# FeenICS (fē'nĭks)
A pipeline for FrEquENcy-based Ica Cleaning of Spirals. Aims to remove spiral-specific aritfact from fMRI scans.

This tool was built to work with FSL's [MELODIC](http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/MELODIC).
It was created to automate the process of evaluating and removing ICA components containing spiral artifact, which is accomplished by evaulating the per slice frequency loading, and scoring components based on patterns
of low or high frequency information. The fsl_regfilt command-line program can then be used to regress out components selected for removal.

## Installation
```
1. Download Dockerfile
2. sudo apt-get install docker.io (if you don't have docker already installed)
3. cd /path/to/Dockerfile
4. sudo docker build -t feenics .
5. sudo docker run -v /path/to/data:/input -i -t feenics
    NOTE: where /path/to/data is a folder that you want access to from inside
    the container; 'input' will be the name of this folder inside the container.

```

## Dependancies

This program requires either FSL or the outputs of FSL Melodic in order to work.
 + **FSL Melodic** http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/MELODIC

Python dependancies (these will be installed when you install FeenICS if you don't already have them):
 + nibabel
 + numpy
 + matplotlib
 + scipy
 + scikit-image (>=0.13.1)

## There are four executables:
+ [**s1_folder_setup.py**](#s1_folder_setup.py) : To create the folder structure necessary to run Melodic and the remainder of the scripts.
+ [**s2_identify_components.py**](#s2_identify_components.py) : To run check_slices.py for an entire folder of subjects and outputs a classification text file (default: fix4melview_Standard_thr20.txt).
+ [**s3_remove_flagged_components.py**](#s3_remove_flagged_components.py) : To remove flagged components once content with the results of the classifcation. This script reads the final line of the classification text file.
+ [**check_slices.py**](#check_slices.py) : To classify components as keep or remove. Is run by s2_identify_components.py, but can be run by itself on an individual scan.


### s1_folder_setup.py

```
Usage:
  s1_folder_setup.py -p -i PATH -s PATH <directory>

Arguments:

  <directory>         Path to top experiment directory. Outputs will be created
                      here.
Options:

  --sprl, -i PATH     Specify alternative folder containing split spirals.

  --subs, -s PATH     Specify alternative experiment folder containing
                      subjectID subfolders.

  --parallel, -p      Print instuctions for running in parallel (GNU parallel)
                      instead of running FSL steps on machine in series.

DETAILS
Makes subject and sprl subfolders within <directory>. Moves separated spiral
files to appropriate subfolders. If split spirals are not already contained
within <directory>, use the "-i" option to specify an alternative path. Specify
"-p" if you would not like to run FSL preprocessing steps at this time. It will
print instructions to run MCFLIRT, BET, and MELODIC using GNU parallel.
```

### s2_identify_components.py

```
Usage:
  s2_identify_components.py -m FLOAT -l FLOAT <directory>

Arguments:
  <directory>         Path to top experiment directory.

Options:
  --midFactor, -m     Cutoff multiplier for mid range frequency information.
                      Raise this value to more aggressively remove noise
                      components. Default is 3.

  --lowFactor, -l     Cutoff multiplier for low range frequency information.
                      Raise this value to keep more signal components.
                      Default is 1.

DETAILS
Feeds paths, multipliers, and output file names to check_slices.py for each
subject within the specified directory. The default name for the output
classification file is fix4melview_Standard_thr20.txt.
```

### s3_remove_flagged_components.py

```
Usage:
  s3_remove_flagged_components.py -c PATH -o PATH <directory>

Arguments:
  <directory>         Path to top experiment directory.

Options:
  --clean_img, -c     Path to desired location of cleaned images.

  --output, -o        If csv outputs were generated in non-default location,
                      identify path to this location.

DETAILS
Uses fsl_regfilt to regress out the components specified in the last line of the
classification file (fix4melview_Standard_thr20.txt). The outputs are cleaned,
but still separated spiral niftis. They will be named subject.sprl.denoised.nii.gz.
```

### icarus-report (optional)

An html report creation tool written by [E.Dickie](https://github.com/edickie).
This step is optional, but will make checking your data much easier.

Follow the sample in **Usage Examples**, below or click [here](https://github.com/edickie/ICArus)
for futher instructions.


### check_slices.py

```
Usage:
  check_slices.py <melodic_file> <outputname> <factorA> <factorB>

Arguments:
  <melodic_file>      Path to any melodic_IC.nii.gz file.

  <outputname>        Path to desired output classification file location.

  <factorA>           Multiplier to be used to determine mid/high frequency
                      cutoffs. If called from s2, default is 3.

  <factorB>           Multiplier to be used to determine low frequency cutoffs.
                      If called from s2, default is 1.

DETAILS
This script is called by s2_identify_components.py. Can be used independently to
troubleshoot classification or path identification issues, or just to run one
spiral scan at a time. The algorithm scores each slice based on how much high
and low frequency information is present after performing an FFT (fast fourier
transform). The scores are tallied per component, and the result determines
whether or not a component is to be flagged for removal. The output of this script
is a classification text file (fix4melview_Standard_thr20.txt), which details the
score and classification criteria per slice, as well as the removal decision
per component. The final line of this document is a list of which components are
to be removed. If you disagree with the decision, change the component numbers in
this list, as this line will be read into s3_remove_flagged_components.py.

```
### Usage Examples:

To run FeenICS locally for an experiment called EXPR, with additional use of Erin Dickie's ICArus package (https://github.com/edickie/ICArus) to better visualize the decisions made by the check_slices.py algorithm

#### Step 1:
~~~sh
s1_folder_setup.py /path/to/EXPR
~~~

#### Step 2:
~~~sh
s2_identify_components.py /path/to/EXPR
~~~

#### Step 3(optional) - Run ICArus (see https://github.com/edickie/ICArus for more information):
~~~sh
sprls=`cd /path/to/EXPR; ls -1d */sprl*`
icarus-report ${sprls}
~~~

#### Step 4 - After you are okay with classifications, run s3_1_remove_flagged_components.py:
~~~sh
s3_remove_flagged_components.py /path/to/EXPR
~~~
