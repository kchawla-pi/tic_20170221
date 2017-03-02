#!/bin/env python

"""
"""

import sys      
import os                                               # system functions
import glob
import shutil
import distutils

import argparse
import subprocess
import _qa_utilities as qa
import _utilities as util

def clean( imageFile ):

    delete_files = glob.glob('[0-9].iwCreateMask.*' + imageFile)
    
    for ii in delete_files:
        os.remove( ii )


def create_mask(in_image, n4_flag=True, imopen_flag=True, thr=0, thrp=25, scale=1, imopen_iterations=0, imclose_iterations=0, 
                verbose=False, debug=False, noglc_flag=True):

    inMask = in_image

    # N4 Bias Correction
    
    if n4_flag:
        
        outMask = util.add_prefix_to_filename( in_image, 'n4')
        
        if not os.path.isfile( outMask ):
            util.iw_subprocess( ["N4BiasFieldCorrection","-d","3", "-i", inMask, "-r", "-s", "-o", outMask], verbose)
            
        inMask = outMask

    # Threshold 

    iiMask  = 1
    outMask = util.add_prefix_to_filename( in_image, str(iiMask) + ".create_mask.")
        
    util.iw_subprocess( ["fslmaths", inMask, "-mul", str(scale), "-thrp", 
                                str(thrp), "-thr", str(thr), "-bin",outMask ],           verbose, debug)

    # Fill Holes

    inMask  = outMask
    iiMask  = iiMask + 1
    outMask = util.add_prefix_to_filename( in_image, str(iiMask) + ".create_mask.")

    util.iw_subprocess( ["ImageMath","3", outMask, "FillHoles",   inMask ], verbose, debug)

    # Opening image operation

    inMask  = outMask

    if imopen_iterations > 0: 
        iiMask  = iiMask + 1
        outMask = util.add_prefix_to_filename( in_image, str(iiMask) + ".create_mask.") 
        util.iw_subprocess( ["fslmaths", inMask,  "-kernel", "2D"] + 
                                   ["-ero"]*imopen_iterations +["-dilM"]*imopen_iterations  + [outMask], verbose, debug)

    # Close image operation
    inMask  = outMask

    if imclose_iterations > 0: 
        iiMask  = iiMask + 1
        outMask = util.add_prefix_to_filename( in_image, str(iiMask) + ".create_mask.")
        util.iw_subprocess( ["fslmaths", inMask,  "-kernel", "2D"] + 
                                   ["-dilM"]*imclose_iterations +["-ero"]*imclose_iterations  + [outMask], verbose, debug)

    # Don't grab greatest larges component

    inMask = outMask
         
    if not noglc_flag:
        iiMask  = iiMask + 1
        outMask = util.add_prefix_to_filename( in_image, str(iiMask) + ".create_mask.")
        util.iw_subprocess(["ImageMath","3", outMask, "GetLargestComponent",  inMask],verbose, debug)

    # Active Contour

    inMask  = outMask
    out_mask_filename = util.add_prefix_to_filename( in_image, "mask.")

#    if inArgs.active_contour and False:  # Active contour no longer works. Talk to Craig 
#
#        util.iw_subprocess( ["matlab", "-nodisplay", "-noFigureWindows", "-nosplash", "-r", 
#                                    "iw_calculate_boundary('"+inMask+"',[ " +  str(inArgs.smoothing) + "," + 
#                                    str(inArgs.iterations) + " ],'ch."+outMask+"', 'ac." + outMask + "'); exit"], verbose)
#        shutil.copyfile("ac."+outMask, out_mask_filename)
#
#    else:
 
    shutil.copyfile(outMask, out_mask_filename)    
    util.iw_subprocess( ["fslcpgeom", in_image, out_mask_filename], verbose)


    return out_mask_filename


#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='create_mask')
     parser.add_argument("image",             help="Input image")
     parser.add_argument("--thrp",            help="FSL percentage threshold (default=25)", default=25, type=int)
     parser.add_argument("--thr",             help="FSL percentage threshold (default=0)",  default=0)
     parser.add_argument("--scale",           help="Mutliply incoming image by scale factor. Useful for masking label images. (default = 1.0)", default=1.0, type=float)
     parser.add_argument("-s", "--sigma",     help="ANTs ImageMath MC sigma (default = 2.0)", default=2.0, type=float)
     parser.add_argument("-d","--display",    help="Display Results", action="store_true", default=False )
     parser.add_argument("-v","--verbose",    help="Verbose flag",      action="store_true", default=False )

     parser.add_argument("--active_contour",  help="Perform active contour around mask",      action="store_true", default=False )
     parser.add_argument("--iterations",      help="Number of iterations for active contours (default=100)",    type=int,   default=100 )
     parser.add_argument("--smoothing",       help="Smoothing parameter for active contours (default = 8)",     type=float, default=8 )

     parser.add_argument("--debug",           help="Debug flag",      action="store_true", default=False )
     parser.add_argument("--clean",           help="Clean directory by deleting intermediate files",      action="store_true", default=False )
     parser.add_argument("--qi",              help="QA inputs",      action="store_true", default=False )
     parser.add_argument("--qo",              help="QA outputs",      action="store_true", default=False )
     parser.add_argument("--noglc",           help="Get Largest Component Flag (default = False )",      action="store_true", default=False )
     parser.add_argument("--n4",              help="Apply N4 Bias correction on image before creating mask (default = False )",      action="store_true", default=False )
     parser.add_argument("--imclose",         help="Number of iterations of 2D fslmaths closing operation (default = 0 )", type=int, default=0 )
     parser.add_argument("--imopen",         help="Number of iterations of 2D fslmaths closing operation (default = 0 )", type=int, default=0 )
     parser.add_argument("-r", "--run",       help="Run processing pipeline",      action="store_true", default=False )

     inArgs = parser.parse_args()

     if inArgs.debug:
         print('\n')
         print( "inArgs.display  = " +  str(inArgs.display) )
         print( "inArgs.debug    = " +  str(inArgs.debug) )
         print( "inArgs.verbose  = " +  str(inArgs.verbose) )
         print('\n')

     if inArgs.clean:
         clean( inArgs.image)

     #
     #  Checks  
     #    
     
     baseName1, ext1 = os.path.splitext(inArgs.image)
     baseName2, ext2 = os.path.splitext(baseName1)
     
     if not ( (os.getenv("FSLOUTPUTTYPE") == "NIFTI_GZ") and 
              ( ext1 == ".gz" ) and (ext2 == ".nii") ):
         

#         print( [ ext1, ext2, os.getenv("FSLOUTPUTTYPE") ] )

         print("Unable to create mask.  " +  inArgs.image + " must be nii.gz")
         quit()
         

     # Quality Assurance input
     #
         
     input_files    = [[ inArgs.image, ":colormap=grayscale"]]

     output_files   = [[ "mask."+inArgs.image, ":colormap=jet:opacity=0.4"]]

     if inArgs.n4:
         output_files = [[ "n4."+inArgs.image, ":colormap=grayscale"]] + output_files

     if inArgs.active_contour:
         ac_output_files = [[ "ch.mask."+inArgs.image, ":colormap=jet:opacity=0.4"],
                            [ "ac.mask."+inArgs.image, ":colormap=jet:opacity=0.4"]]
     else:
         ac_output_files = [[None, None]]

     if inArgs.debug:
         intermediate_files = [[ "1.iwCreateMask."+inArgs.image, ":visible=0:colormap=jet"],
                               [ "2.iwCreateMask."+inArgs.image, ":visible=0:colormap=jet"],
                               [ "3.iwCreateMask."+inArgs.image, ":visible=0:colormap=jet"],
                               [ "4.iwCreateMask."+inArgs.image, ":visible=0:colormap=jet"]]
         
         if not inArgs.noglc:
             intermediate_files = intermediate_files + [[ "5.iwCreateMask."+inArgs.image, ":visible=0:colormap=jet"]]

     else:
         intermediate_files = [];

     if  inArgs.qi:
         iwQa.qa_input_files( input_files, True )
         iwQa.freeview( input_files, inArgs.display, inArgs.verbose )

     #
     # Run    
     # 
   
     if  inArgs.run:
         create_mask(inArgs.image, n4_flag=inArgs.n4, noglc_flag=inArgs.noglc, thr=inArgs.thr, 
                     thrp=inArgs.thrp, scale=inArgs.scale, imopen_iterations=inArgs.imopen, 
                     imclose_iterations=inArgs.imclose, verbose=False)
         

     # Quality Assurance output
     #

     if  inArgs.qo:

         if inArgs.debug:
             qa_utilities.freeview( input_files + intermediate_files + output_files + ac_output_files, True, inArgs.verbose ) 
         else:
             qa_utilities.freeview( input_files + output_files + ac_output_files, True, inArgs.verbose ) 

     # Remove intermediate files
     # 
     #
         
     if not inArgs.debug:
         clean( inArgs.image)

