#!/usr/bin/env python2

import shutil
import os
import argparse
import iwUtilities     as util
import iwCtf           as ctf
import numpy as np
import nibabel as nb

import pandas as pd

#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #
     
     parser = argparse.ArgumentParser(prog='iwCtf_where')
               
     parser.add_argument("in_image",          help="Input image" )
     parser.add_argument("in_points",          help="Input CSV points" )

     parser.add_argument("out_image",         help="Output image" )

     parser.add_argument("-v","--verbose",    help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("--debug",           help="Debug flag",      action="store_true", default=False )

     inArgs = parser.parse_args()

     #
     #
     #

     image     = nb.load(inArgs.in_image)
     data      = 0*image.get_data() 
     ndim      = len( image.get_data()) 

     points    = pd.read_csv(inArgs.in_points)


     for ii in points.values.tolist():
          data[ ii[0], ii[1], ii[2] ] = ii[4]

     out_nifti = nb.Nifti1Image( data, image.get_affine() )
     nb.save( out_nifti,  inArgs.out_image )


