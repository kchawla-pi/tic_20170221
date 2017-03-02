#!/usr/bin/env python
"""
Measure phase ghosts by taking the ratio of the phase background to the frequency background.
"""
import sys
import nibabel
import argparse
import labels
import _utilities as util

def nii_4d(in_nii):
     pass

def sort_nii(in_nii, in_order, verbose=False):

     in_array = in_nii.get_data()

     set_volumes = set( range(0, in_array.shape[3]))
     set_order = set(in_order)
     
     set_remain = set_volumes - set_order

     order = in_order + list(set_remain)

     out_array = in_array[:,:,:,order]

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

     parser.add_argument("--out_nii", help="Filename of NIFTI output label. (default = sort.<in> ) ", default=None)

     parser.add_argument('-s','--sort',     help='Labels to sort', type=int, nargs='*', default = 0 )
     parser.add_argument('-v','--verbose',  help='Verbose flag',      action='store_true', default=False )

     inArgs = parser.parse_args()

     # Read NIFTI File
     in_nii = nibabel.load(inArgs.in_nii)

     out_nii = sort_nii(in_nii, inArgs.sort)

     if inArgs.out_nii is None:
          out_nii_filename = util.add_prefix_to_filename( inArgs.in_nii, 'sort_nii.')
     else:
          out_nii_filename = inArgs.out_nii

     
     nibabel.save( out_nii, out_nii_filename)
     



