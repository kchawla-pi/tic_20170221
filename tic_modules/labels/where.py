#!/usr/bin/env python

import argparse
import _utilities as util
import labels
import numpy
import nibabel
import pandas

#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #
     
     parser = argparse.ArgumentParser(prog='where')
               
     parser.add_argument("in_label",          help="Label NIFTI image" )
     parser.add_argument("out_csv",      help="CSV output points" )

     parser.add_argument("-v","--verbose",    help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("--debug",           help="Debug flag",      action="store_true", default=False )

     inArgs = parser.parse_args()

     # Create out filename
     if inArgs.out_csv == 'in':
          out_filename = util.replace_nii_or_nii_gz_suffix( inArgs.in_label, '.csv')
     else:
          out_filename = inArgs.out_csv

     #
     #
     #

     image     = nibabel.load(inArgs.in_label)
     data      = image.get_data() 
     nshape    = image.shape + (1,)

     step_01   = numpy.where(data > 0)
     label     = numpy.extract( data > 0, data )
     
     x         = step_01[0].tolist()
     y         = step_01[1].tolist()
     z         = step_01[2].tolist()

     if nshape[3]>1:
          t = step_01[3].tolist()
     else:
          t = 0 * len(x)

     comment   = [' '] * len(x)

     util.verify_inputs( [ inArgs.in_label], inArgs.debug)

     tmp          = pandas.DataFrame( { 'x':x, 'y': y, 'z' : z, 't':t,'label':label, 'comment':comment}, columns=['x','y','z','t','label','comment'] )
     iras_points  = tmp.sort_values(['label','x','y','z','t'], ascending=[1,1,1,1,1])

     labels.write_points( out_filename, iras_points, inArgs.verbose )



