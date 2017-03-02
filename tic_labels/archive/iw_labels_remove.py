#!/usr/bin/env python2

"""

"""
import os
import sys      
import numpy as np
import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

import iw_labels as labels
import iwUtilities as util

#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='iw_labels_remove')

     parser.add_argument("in_nii",    help="Filename of NIFTI input label ")
     parser.add_argument("--out_nii",    help="Filename of NIFTI output label. (default = --in_nii ) ")

     parser.add_argument('-r', "--remove",  help="Labels to remove", type=float, nargs="*", default = [] )
     parser.add_argument("--csv",           help="CSV filename containing labels to remove", default = [] )

     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )

     inArgs = parser.parse_args()


     #
     
     in_label_nii    = labels.read_nifti_file( inArgs.in_nii, 'Label file does not exist' )
     in_label_array  = in_label_nii.get_data()

     if inArgs.out_nii == None:
          out_filename = inArgs.in_nii
     else:
          out_filename = inArgs.out_nii

     if len(inArgs.csv):
          csv_remove_labels = labels.read_labels_from_csv( inArgs.csv)
     else:
          csv_remove_labels = []


     remove_labels  = labels.get_labels( inArgs.remove + csv_remove_labels, in_label_array )



     if inArgs.verbose:
          print sorted(inArgs.remove + csv_remove_labels)

     out_label_array = in_label_array

     for ii in remove_labels:
          mask = in_label_array == ii
          out_label_array[ mask ] = 0

     nb.save( nb.Nifti1Image( out_label_array, None, in_label_nii.get_header()), out_filename )
