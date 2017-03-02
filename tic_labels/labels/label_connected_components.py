#!/usr/bin/env python3
"""
Label connected components on an image with scipy.ndimage
"""
import sys      
import nibabel 
import scipy.ndimage
import argparse
import _utilities 
import labels
import numpy

def label_connected_components( input_file, output_file, lower_threshold=-numpy.inf, upper_threshold=numpy.inf ):

     in_nii    = labels.common.read_nifti_file( input_file, 'Label file does not exist' )
     in_array  = in_nii.get_data()

     in_array[in_array<lower_threshold] = 0
     in_array[in_array>upper_threshold] = 0

     out_array, n_out_array = scipy.ndimage.measurements.label( in_array )

     out_array = numpy.nan_to_num(out_array)

     nibabel.save( nibabel.Nifti1Image( out_array, None, in_nii.get_header()), output_file )


def main():

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='label_connected_components')

     parser.add_argument("in_nii",    help="Filename of NIFTI input label ")
     parser.add_argument("--out_nii", help="Filename of NIFTI output label. (default = label.<in> ) ", default=None)

     parser.add_argument('-l', '--lower', help="Lower threshold. (-infinity)", type=float, default=-numpy.inf)
     parser.add_argument('-u', '--upper', help="Upper threshold. (+infinity) ", type=float, default=numpy.inf)

     inArgs = parser.parse_args()

     if inArgs.out_nii == None:
          out_filename = _utilities.add_prefix_to_filename(inArgs.in_nii, 'label.')
     else:
          out_filename = inArgs.out_nii

     label_connected_components( inArgs.in_nii, out_filename, inArgs.lower, inArgs.upper)

     return 0 

#
# Main Function
#

if __name__ == "__main__":
     sys.exit(main())
