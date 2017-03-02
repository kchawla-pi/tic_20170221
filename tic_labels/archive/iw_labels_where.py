#!/usr/bin/env python2

import sys
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

def main():

     ## Parsing Arguments
     #
     #
     
     parser = argparse.ArgumentParser(prog='iwCtf_where')
               
     parser.add_argument("in_image",          help="Input image" )
     parser.add_argument("out_filename",      help="CSV output points" )

     parser.add_argument("-v","--verbose",    help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("--debug",           help="Debug flag",      action="store_true", default=False )

     inArgs = parser.parse_args()

     #
     #
     #

     image     = nb.load(inArgs.in_image)
     data      = image.get_data() 
     nshape    = image.shape  + (1,1,1)

     step_01   = np.where(data > 0)
     label     = np.extract( data > 0, data )
     
     x         = step_01[0].tolist()
     y         = step_01[1].tolist()
     z         = step_01[2].tolist()

     if nshape[3]>1:
          t = step_01[3].tolist()
     else:
          t = 0 * len(x)

     comment   = [' '] * len(x)

     util.verify_inputs( [ inArgs.in_image], inArgs.debug)

     tmp          = pd.DataFrame( { 'x':x, 'y': y, 'z' : z, 't':t,'label':label, 'comment':comment}, columns=['x','y','z','t','label','comment'] )
     iras_points  = tmp.sort_values(['label','x','y','z','t'], ascending=[1,1,1,1,1])

     ctf.write_points( inArgs.out_filename, iras_points, inArgs.verbose )



if __name__ == "__main__":
    sys.exit(main())
