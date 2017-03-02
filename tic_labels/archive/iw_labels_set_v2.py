#!/usr/bin/env python2

"""
A function ot 
"""
import sys
import numpy as np

import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

import iw_labels as labels

def check_limits( parameter, limits ):
    return parameter >= limits[0] and parameter <= limits[1]

#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     
     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='iw_labels_sort')

     parser.add_argument("in_csv",    help="Label NIFTI filename ")
     parser.add_argument("in_nii",    help="Filename of input labels")
     parser.add_argument("out_nii",       help="Filename of CSV output file containing label stats")
     parser.add_argument("--sort",    help="Labels to sort", type=str, nargs=1, default = 'label' )

     parser.add_argument("--sort_direction",    help="Sorting direction: 0=descending, 1=ascending (default=1)", type=int, nargs=1, default = [1] )
     parser.add_argument("--limits",            help="Limits of sorted values", type=float, nargs=2, default = None )
     parser.add_argument("--stats",             help="Stats to report", type=str, nargs="*", default='volume')
     parser.add_argument("--labels",            help="Labels to report", type=float, nargs="*", default=None)

     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("-a","--verbose_all",  help="Display all rows",      action="store_true", default=False )

     parser.add_argument("--nan",  help="Keep NAN values",      action="store_true", default=False )


     inArgs = parser.parse_args()

     pd.set_option('expand_frame_repr', False)
         
     df_stats  = pd.read_csv(inArgs.in_csv)

     if inArgs.labels is not None:
         df_stats = df_stats[df_stats['label'].isin(inArgs.labels)]
         
     stats_list = ['label'] + [inArgs.stats]

     if inArgs.limits is not None:
         df_limits = df_stats[  (df_stats[inArgs.sort[0] ] >= inArgs.limits[0]) & (df_stats[inArgs.sort[0] ] <= inArgs.limits[1]) ]
     else:
         df_limits = df_stats

     df_sorted = df_limits.sort_values( inArgs.sort, ascending=inArgs.sort_direction ).reset_index()
     df_sorted = df_sorted.dropna()

     #

     in_nii    = labels.read_nifti_file( inArgs.in_nii, 'Label file does not exist' )
     in_array  = in_nii.get_data()
     out_array = np.zeros( in_array.shape )

     for ii_label, ii_value in df_sorted[ stats_list  ].get_values():
         print ii_label, ii_value
         out_array[ in_array == ii_label ] = ii_value

     print np.max(out_array[:])

     nb.save( nb.Nifti1Image( out_array, in_nii.get_affine()), inArgs.out_nii )
