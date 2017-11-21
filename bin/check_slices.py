#!/usr/bin/env python

import numpy as np
from numpy import ndarray
import nibabel as nib
import matplotlib.pyplot as plt
from matplotlib.pyplot import ylim
from scipy.fftpack import fft2, fftshift
from scipy import stats
from scipy.stats import norm
from skimage.draw import circle, ellipse
from copy import copy
import os, sys

# organize values obtained from fft masks by slice number. Will then be used to calculate per slice thresholds. Slice values are skewed by probability of a normal distribution, in order to devalue outside slices.
def slice_lists(z, masked_values, dist_factors):

    totalperSliceMed = []
    for x in range(z):
        perSliceMed = [item[x] for item in masked_values]
        perSliceFactor = dist_factors[x]*10
        totalperSliceMed.append(perSliceMed/perSliceFactor)

    return(totalperSliceMed)

# define the first and third quartiles on a per slice number basis. Calculate the outliers based on the provided multiplier
def cutoff(listB, multiplier):
    # convert to numpy array
    array = np.array(listB)

    # find 1st and 3rd quartiles
    quart_one = np.percentile(array, 25)
    quart_three = np.percentile(array, 75)

    # find difference between quartiles
    diff = quart_three-quart_one
    outliers = quart_three + diff*multiplier
    return(outliers)

def main(input_comps, output_csv, plot=False):

    # input_comps = '/scratch/eziraldo/STOPPD_cleaning/2017_STOPPD_SpiralINOUT/20151110_Ex04578_STOP1MR_STKR063_SpiralSeparated/sprlIN/Prestats.feat/filtered_func_data.ica/melodic_IC.nii.gz'
    # load sprl nifti
    data = nib.load(input_comps).get_data()
    x, y, z, comps =  data.shape

    lo_comp, mid_comp = [], []
    lo_comp_quart, mid_comp_quart, ratio_comp_quart = [], [], []
    lo_byslice, mid_byslice, ratio_byslice = [], [], []
    cutoff_mid_list, cutoff_lo_list, cutoff_ratio_list = [], [], []

    remove_list = []
    noise_comps = []
    slices_list = []
    dist_factors = []

    # defines the sizes of the masks
    # mid mask is an ellipse stretching from the bottom left to top right corners of the matrix
    mid_mask = np.zeros((x,y))
    rr, cc = ellipse(x/2, y/2, x/4, y/2, rotation=np.deg2rad(40))
    mid_mask[rr,cc] = 1
    mid_mask = mid_mask.astype(np.bool)

    # low mask is very centre of image (1/5th radius)
    lo_mask = np.zeros((x,y))
    rr, cc = circle(x/2, y/2, x/5)
    lo_mask[rr, cc] = 1
    lo_mask = lo_mask.astype(np.bool)

    # append slice numbers into list, calculate the mean, std and probability distribution. Will be used to skew weight of slices based on relative position in the brain. i.e. outside slices are not as valuable when deciding to keep or remove a component
    for zslice in range(z):
        slices_list.append(zslice+1)

    mean = np.mean(slices_list)
    std = np.std(slices_list)

    for x in slices_list:
        dist = norm.pdf(x, mean, std)
        dist_factors.append(dist)

    # calculate thresholds for each component
    for comp in range(comps):

        lo_slices, mid_slices, ratio_slices = [], [], []
        lo_slices_quart, mid_slices_quart, ratio_slices_quart = [], [], []

        for zslice in range(z):

            # take the fast fourier transform of each slice and shift so that from center to edge the frequency moves from low to high. Images contian mostly low frequency information
            pxx = abs(fftshift(fft2(data[:,:,zslice, comp]))**2)

            # if plot option is specified, a colour map of each slice fft will be displayed
            if plot==True:
                plt.imshow(pxx, vmin = 0, vmax = 200000)
                plt.colorbar()
                plt.title('comp={} slice {}'.format(comp+1, zslice+1))
                plt.show()

            # use masks to isolate lo and mid frequency areas of fft representation
            mid_pxx = pxx[mid_mask - lo_mask]
            lo_pxx = pxx[lo_mask]

            # append sorted slices into a list
            mid_slices.append(ndarray.tolist(mid_pxx))
            lo_slices.append(ndarray.tolist(lo_pxx))

        # appended components into list of lists
        mid_comp.append(mid_slices)
        lo_comp.append(lo_slices)

    #  create lists sorted per slice number (ie. slice #1 for every component together)
    mid_byslice = slice_lists(z, mid_comp, dist_factors)
    lo_byslice = slice_lists(z, lo_comp, dist_factors)

    # calculate the cutoff for each slice (both mid frequency and low frequency)
    for slices in mid_byslice:

        cutoff_mid = cutoff(slices, 3)
        cutoff_mid_list.append(cutoff_mid)
        #     print(cutoff_mid)
        # print('\n')

    for slices in lo_byslice:
        cutoff_lo = cutoff(slices, 1)
        cutoff_lo_list.append(cutoff_lo)

    # print(cutoff_mid_list)
    # print(cutoff_lo_list)

    # count how many masked fft elements pass the appropriate slice threshold
    for comp in range(comps):
        lo_slices_quart, mid_slices_quart, ratio_slices_quart = [], [], []
        for zslice in range(z):

            # use masks to isolate lo and mid frequency areas of fft representation
            pxx = abs(fftshift(fft2(data[:,:,zslice, comp]))**2)
            mid_pxx = pxx[mid_mask - lo_mask]
            lo_pxx = pxx[lo_mask]

            count_mid = np.asarray(np.where(mid_pxx > cutoff_mid_list[zslice]))
            count_lo = np.asarray(np.where(lo_pxx > cutoff_lo_list[zslice]))

            mid_count = count_mid.shape
            lo_count = count_lo.shape

            lo_slices_quart.append(lo_count[1])
            mid_slices_quart.append(mid_count[1])
            ratio_slices_quart.append(lo_count[1]-mid_count[1])

        lo_comp_quart.append(lo_slices_quart)
        mid_comp_quart.append(mid_slices_quart)
        ratio_comp_quart.append(ratio_slices_quart)

    # Evaluation criteria for deciding to assign points to slices for noise or signal. Positive points indicate noise, negative points indicate signal.
    for comp in range(comps):
        flag = False
        remove = False
        points = 0
        a = 0

        for zslice in range(z):

            # print("{} {} {} {} {}".format(comp+1, zslice+1, mid_comp_quart[comp][zslice], lo_comp_quart[comp][zslice], ratio_comp_quart[comp][zslice]))

            # this is the artifact case. Negative ratio comp indicates overwhelming contribution from mid fequency loading
            if ratio_comp_quart[comp][zslice] < -100 and a == 0:

                a = 1
                points = points + 2
                remove_list.append("{},{},{},{},{},2".format(comp+1, zslice+1, mid_comp_quart[comp][zslice], lo_comp_quart[comp][zslice], ratio_comp_quart[comp][zslice]))
                # print("{},{},{},{},{},noise".format(comp+1, zslice+1, mid_comp_quart[comp][zslice], lo_comp_quart[comp][zslice], ratio_comp_quart[comp][zslice]))

            # this case exists to acknowledge the possibility of more than one slice with artifact, but not apply further points if the previous statement has already been executed
            elif ratio_comp_quart[comp][zslice] < -100:

                remove_list.append("{},{},{},{},{},0".format(comp+1, zslice+1, mid_comp_quart[comp][zslice], lo_comp_quart[comp][zslice], ratio_comp_quart[comp][zslice]))
                # print("{},{},{},{},{},noise".format(comp+1, zslice+1, mid_comp_quart[comp][zslice], lo_comp_quart[comp][zslice], ratio_comp_quart[comp][zslice]))

            if lo_comp_quart[comp][zslice] > 20 and ratio_comp_quart[comp][zslice] >= 10 :

                value = -1
                remove_list.append("{},{},{},{},{},-1".format(comp+1, zslice+1, mid_comp_quart[comp][zslice], lo_comp_quart[comp][zslice], ratio_comp_quart[comp][zslice]))
                # print("{},{},{},{},{},signal".format(comp+1, zslice+1, mid_comp_quart[comp][zslice], lo_comp_quart[comp][zslice], ratio_comp_quart[comp][zslice]))
                points = points - 1

                # print("{} {} {} {}".format(comp+1, zslice+1, lo_comp_quart[comp][zslice], lo_comp[comp][zslice]))

        # If the total component points are greater than 0, then remove the component
        if points > 0:
            flag = True
        else:
            flag = False

        if flag == True:
            noise_comps.append(str(comp+1))

        remove_list.append("Comp: {}, Total Points: {}, Flag: {}".format(comp+1, points, flag))

    thresholds_list = []

    for zslice in range(z):
        thresholds = ','.join(map(str, (zslice+1, round(cutoff_mid_list[zslice], 1), round(cutoff_lo_list[zslice], 1))))
        thresholds_list.append("{}".format(thresholds))

    thresh_text = ('\n'.join(thresholds_list))
    headerA = "slice, midThresh, lowThresh"
    headerB = "comp, slice, midCount, lowCount, difference, results, points"
    text = str("\n".join(remove_list))
    #
    f = open(output_csv, 'w')
    f.write(headerA)
    f.write('\n')
    f.write(thresh_text)
    f.write("\n")
    f.write(headerB)
    f.write('\n')
    f.write(text)
    f.write('\n')
    f.write('[' + ','.join(noise_comps) + ']' + '\n')


if __name__ == '__main__':

    input_comps = sys.argv[1]
    output = sys.argv[2]
    if len(sys.argv) == 4:
        if sys.argv[3] == 'plot':
            main(input_comps, output, plot=True)
    main(input_comps, output)
