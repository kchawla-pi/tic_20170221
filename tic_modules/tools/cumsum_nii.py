#!/usr/bin/env python
"""
Measure phase ghosts by taking the ratio of the phase background to the frequency background.
"""
import sys
import nibabel
import argparse
import labels
import _utilities as util
import numpy 

def nii_4d(in_nii):
     pass

def cumsum_nii(in_nii, scale=1, verbose=False):

     # Read in NIBABEL NIFTI object
     in_array = in_nii.get_data()

     # reorder volumes.
     out_array = scale * numpy.cumsum( in_array, axis=3)

     # Create nibabel NIFTI object
     out_nii = nibabel.Nifti1Image( out_array, None, in_nii.get_header())

     return out_nii


#
# Main Function
#

if __name__ == '__main__':

     ## Parsing Arguments
     
     usage = 'usage: %prog [options] arg1 arg2'

     parser = argparse.ArgumentParser(prog='sort_nii')

     parser.add_argument('in_nii',    help='Background labels')

     parser.add_argument("--out_nii", help="Filename of NIFTI output label. (default = cumsum_nii.<in> ) ", default=None)

     parser.add_argument('-s','--scale', help='Multiply NIFTI output array by scale factor ', type=float, default=1.0)
     parser.add_argument('-v','--verbose',  help='Verbose flag',      action='store_true', default=False )

     inArgs = parser.parse_args()

     # Read NIFTI File
     in_nii = nibabel.load(inArgs.in_nii)

     out_nii = cumsum_nii(in_nii, inArgs.scale)

     if inArgs.out_nii is None:
          out_nii_filename = util.add_prefix_to_filename( inArgs.in_nii, 'cumsum_nii.')
     else:
          out_nii_filename = inArgs.out_nii

     
     nibabel.save( out_nii, out_nii_filename)
     



