#!/usr/bin/env python

"""

"""
import os
import sys      
import numpy as np
import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

from scipy.ndimage.morphology import binary_erosion, binary_dilation, binary_opening

import iw_label_stats as label_stats
import iwUtilities as util
import scipy.stats as stats



def compare_images( label_nii_filename, image1_nii_filename, image2_nii_filename, requested_labels, min_volume, verbose_flag=False ):

    # Load arrays

    label_nii  = label_stats.read_nifti_file( label_nii_filename, 'Label file does not exist' )
    image1_nii = label_stats.read_nifti_file( image1_nii_filename, 'Image file does not exist' )
    image2_nii = label_stats.read_nifti_file( image2_nii_filename, 'Image file does not exist' )

    # System Checks to verify that the Array Size and Dimensions are compatible

    image1_array = image1_nii.get_data()
    image2_array = image2_nii.get_data()
    label_array = label_nii.get_data()

    label_stats.image_shape_check(image1_array)
    label_stats.image_shape_check(image2_array)

    if not image1_array.shape == image2_array.shape:
        sys.exit('Image arrays must have the same shape')

    if not len(label_array.shape) == 3:
        sys.exit('Only supports 3D label arrays')

    if not image1_array.shape[0:len(label_array.shape)] == label_array.shape:
        sys.exit('Image array and label array do not have the same voxel dimensions')

    # Find a set of acceptable labels


    labels = label_stats.get_labels( requested_labels, label_array)

    # Permute array or expand so desired stats is along first dimension

    image1_array, nVolumes = label_stats.permute_image_array( image1_array)
    image2_array, nVolumes = label_stats.permute_image_array( image2_array)

    # Gather stats

    df_stats  = pd.DataFrame(columns=( 'label_number', 'time_index', 'label_volume', 'boundary_image1_mean', 'boundary_image1_std', 'boundary_image1_min', 'boundary_image1_max',
                       'boundary_image2_mean', 'boundary_image2_std', 'boundary_image2_min', 'boundary_image2_max',
                       'image1_mean', 'image1_std', 'image1_min', 'image1_max',
                       'image2_mean', 'image2_std', 'image2_min', 'image2_max',
                       'scale', 'p_rel_scaled' ))


    for ii, ii_label in enumerate(labels):

        mask = label_array == ii_label
        boundary_mask = binary_dilation( mask , structure=np.ones((3,3,3)))
        boundary_mask -= mask

        label_volume = np.sum(mask[:])

        if label_volume >= min_volume:  # Only perform paired t-test for volumes of a minimum size

            for jj in range(0,nVolumes):

                # Calculate signal intensity of boundary pixels

                boundary_image1_mean, boundary_image1_std, boundary_image1_min, boundary_image1_max = label_stats.individual_image_stats( image1_array[jj][ boundary_mask ])
                boundary_image2_mean, boundary_image2_std, boundary_image2_min, boundary_image2_max = label_stats.individual_image_stats( image2_array[jj][ boundary_mask ])
                
                scale         = boundary_image1_mean / boundary_image2_mean
                
                # Scale image to match boundary pixels

                image1_mean, image1_std, image1_min, image1_max = label_stats.individual_image_stats(         image1_array[jj][ mask ])
                image2_mean, image2_std, image2_min, image2_max = label_stats.individual_image_stats( scale * image2_array[jj][ mask ])

                # Calculate paired t-test from region of interest across two images
                t_rel, p_rel_scaled  = stats.ttest_rel( image1_array[jj][ mask ], scale* image2_array[jj][mask])


                # Save stats
                image_array_stats  = [ ii_label, jj, label_volume, boundary_image1_mean, boundary_image1_std, boundary_image1_min, boundary_image1_max, 
                                       boundary_image2_mean, boundary_image2_std, boundary_image2_min, boundary_image2_max,
                                       image1_mean, image1_std, image1_min, image1_max,
                                       image2_mean, image2_std, image2_min, image2_max,
                                       scale, p_rel_scaled ]

                if verbose_flag:
                    print image_array_stats
                
                df_stats.loc[len(df_stats)] = image_array_stats
            
    return df_stats
        


#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='iw_compare_images')

     parser.add_argument("label_filename",    help="Label NIFTI filename ")
     parser.add_argument("image1_filename",   help="Image NIFTI filename 1" )
     parser.add_argument("image2_filename",   help="Image NIFTI filename 2 "  )
     parser.add_argument("--out",             help="CSV output filename. Unless set no output is saved.", default=None) 

     parser.add_argument("--labels",        help="Label indices to analyze", type=int, nargs="*", default = None )
     parser.add_argument("--volume",        help="Minimum label volume in pixels", type=int, default = 5 )

     parser.add_argument("-d","--display",  help="Display Results", action="store_true", default=False )
     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("--debug",         help="Debug flag",      action="store_true", default=False )
     parser.add_argument("--qi",            help="QA inputs",      action="store_true", default=False )
     parser.add_argument("--qo",            help="QA outputs",      action="store_true", default=False )
     parser.add_argument("-r", "--run",     help="Run processing pipeline",      action="store_true", default=False )

     inArgs = parser.parse_args()


     df_stats = compare_images( inArgs.label_filename, inArgs.image1_filename, inArgs.image2_filename, inArgs.labels, inArgs.volume, inArgs.verbose)

     if inArgs.out is not None:
         df_stats.to_csv(inArgs.out)
         
