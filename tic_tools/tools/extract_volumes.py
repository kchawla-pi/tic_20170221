#!/usr/bin/env python
# coding: utf-8
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Measure phase ghosts by taking the ratio of the phase background to the frequency background.
"""
import sys
import nibabel
import argparse
import labels
import _utilities as util
import tools

def extract_volumes(in_nii, in_extract, verbose=False):

     in_array = in_nii.get_data()
     out_array = in_array[:,:,:,in_extract]
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

     parser.add_argument("--out_nii", help="Filename of NIFTI output label. (default = extract.<in> ) ", default=None)

     parser.add_argument('-x','--extract',  help='Volumes to extract', type=int, nargs='*', default = 0 )
     parser.add_argument('-v','--verbose',  help='Verbose flag',      action='store_true', default=False )

     inArgs = parser.parse_args()

     # Read NIFTI File
     in_nii = nibabel.load(inArgs.in_nii)
     out_nii = extract_volumes(in_nii, inArgs.extract)

     if inArgs.out_nii is None:
          out_nii_filename = util.add_prefix_to_filename( inArgs.in_nii, 'extract.')
     else:
          out_nii_filename = inArgs.out_nii

     
     nibabel.save( out_nii, out_nii_filename)
     



