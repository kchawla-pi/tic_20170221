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

import labels
import _utilities as util
import scipy.stats as stats

def extract(in_filename, in_csv, in_extract_labels, out_filename, verbose=False, merge=None):

     # Read in label array

     in_nii    = labels.read_nifti_file( in_filename, 'Label file does not exist' )
     in_array  = in_nii.get_data()
     
     if len(in_csv):
          csv_extract_labels = labels.read_labels_from_csv( in_csv)
     else:
          csv_extract_labels = []

#     print ( inArgs.extract.shape)
#     print ( csv_extract_labels.shape)

     requested_labels = in_extract_labels + csv_extract_labels

     extract_labels  = labels.get_labels( requested_labels, in_array )

     if verbose:
          print ('Requested labels for extraction not found', list(set(requested_labels) - set(extract_labels)))

     out_array = np.zeros( in_array.shape, dtype = np.int8 )

     for ii in extract_labels:
          mask = in_array == ii
          out_array[ mask ] = in_array[ mask ]

     if merge is not None and merge!=0: # isinstance(map, (int, long, float)) and float(map) !=0:
          out_array = merge*(out_array > 0)

     nb.save( nb.Nifti1Image( out_array, None, in_nii.get_header()), out_filename )

     return


#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='labels_extract')

     parser.add_argument("in_nii",    help="Filename of NIFTI input label ")
     parser.add_argument("--out_nii",    help="Filename of NIFTI output label. (default = --in ) ")

     parser.add_argument('-x', "--extract", help="Labels to extract and save to output file", type=float, nargs="*", default = [] )
     parser.add_argument("--csv",           help="CSV filename containing labels to remove", default = [] )
     parser.add_argument("-m","--merge",     help="Merge labels into a single label (None).",  type = float, default=None )
     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )
     inArgs = parser.parse_args()


     if inArgs.out_nii == None:
          out_filename = inArgs.in_nii
     else:
          out_filename = inArgs.out_nii

     extract(inArgs.in_nii, inArgs.csv, inArgs.extract, out_filename, verbose=inArgs.verbose, merge=inArgs.merge)
