#!/usr/bin/env python22

"""

"""
import os
import sys      
import numpy as np
import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

import labels
import _utilities as util

def keep(in_nii, keep_labels, keep_csv_filename, out_filename):

     
     in_label_nii    = labels.read_nifti_file( in_nii, 'Label file does not exist' )
     in_label_array  = in_label_nii.get_data()

     if len(keep_csv_filename):
          csv_keep_labels = labels.read_labels_from_csv( keep_csv_filename ) 
     else:
          csv_keep_labels = []

     all_labels    = set(labels.get_labels( None, in_label_array ))
     keep_labels   = set(labels.get_labels( keep_labels + csv_keep_labels, in_label_array ))
     remove_labels = sorted(list(all_labels.symmetric_difference(keep_labels)))

     out_label_array = in_label_array

     for ii in remove_labels:
          mask = in_label_array == ii
          out_label_array[ mask ] = 0

     nb.save( nb.Nifti1Image( out_label_array, None, in_label_nii.get_header()), out_filename )



def main():

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='keep')

     parser.add_argument("in_nii",    help="Filename of NIFTI input label ")
     parser.add_argument("--out_nii",    help="Filename of NIFTI output label. (default = keep.<in_nii> )")

     parser.add_argument('-k', "--keep",  help="Labels to remove", type=float, nargs="*", default = [] )
     parser.add_argument("--csv",           help="CSV filename containing labels to remove", default = [] )

     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )

     inArgs = parser.parse_args()

     if inArgs.out_nii == None:
          out_filename = util.add_prefix_to_filename(inArgs.in_nii, 'keep.')
     elif inArgs.out_nii == 'same':
          out_filename = inArgs.in_nii
     else:
          out_filename = inArgs.out_nii

     keep( inArgs.in_nii, inArgs.keep, inArgs.csv, out_filename)


if __name__ == "__main__":
     sys.exit(main())
