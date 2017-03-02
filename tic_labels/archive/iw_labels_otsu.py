#!/usr/bin/env python2

"""
A function ot 
"""
import sys
import numpy as np

import nibabel as nb
import scipy.ndimage as ndimage
from skimage import filters
import argparse

import iw_labels as labels


#
# Main Function
#
def main():

    # Parsing Arguments

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='iw_labels_otsu')

    parser.add_argument("in_labels", help="Filename of input labels")
    parser.add_argument("in_image", help="Filename of input labels")
    parser.add_argument("otsu_labels", help="Filename of output NII otsu mask")

    parser.add_argument("-v", "--verbose", help="Verbose flag", action="store_true", default=False)
    inArgs = parser.parse_args()

    in_label_nii = labels.read_nifti_file(inArgs.in_labels, 'Label file does not exist')
    in_label_array = in_label_nii.get_data()

    in_image_nii = labels.read_nifti_file(inArgs.in_image, 'Label file does not exist')
    in_image_array = in_image_nii.get_data()

    out_array_low = np.zeros(in_label_array.shape)
    out_array_high = np.zeros(in_label_array.shape)

    for ii in xrange(1, 4):
        ii_label_array = in_label_array[:, :, :, ii]
        ii_image_array = in_image_array[:, :, :, ii]
        ii_labels = labels.get_labels(None, ii_label_array)

        for jj in ii_labels:
            print ii, jj
            jj_mask = ndimage.binary_dilation(ii_label_array == jj)
            jj_image = jj_mask * ii_image_array

            val = filters.threshold_otsu(jj_image)
            jj_image_high = jj * (jj_image >= val) * jj_mask
            jj_image_low =  jj * (jj_image < val ) * jj_mask

            out_array_low[:,:,:,ii] += jj_image_low
            out_array_high[:,:,:,ii] += jj_image_high

    nb.save(nb.Nifti1Image(out_array_low, in_image_nii.get_affine()), 'low.' + inArgs.otsu_labels)
    nb.save(nb.Nifti1Image(out_array_high, in_image_nii.get_affine()), 'high.' + inArgs.otsu_labels)

if __name__ == '__main__':
    sys.exit(main())
