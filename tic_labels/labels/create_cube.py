#!/usr/bin/env python
"""
Creates a spherical ROI.
"""

import sys
import pandas as pd
import nibabel as nb
import numpy as np
import scipy.ndimage      as ndimage
import skimage.morphology as skimage
import argparse
import _qa_utilities

def create_roi_cube(out_roi, in_image, x,y,z, label=1, verbose=False, debug=False):

    nii_image = nb.load(in_image)

    nii_shape = nii_image.get_shape()
    nii_data = nii_image.get_data()

    roi_image = np.zeros(nii_shape)

    roi_image[ x[0]:x[1], y[0]:y[1], z[0]:z[1],...] = label

    out_nii = nb.Nifti1Image(roi_image, None, nii_image.get_header())
    nb.save(out_nii, out_roi)

    return 


def main():
    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='create_cube')
    parser.add_argument("in_image", help="Image")
    parser.add_argument("out_image", help="Image")
    parser.add_argument("--label", help="Label number", type=int, default=1000)
    parser.add_argument("-x", help="X radius", type=int, default=32)
    parser.add_argument("-y", help="Y radius", type=int, default=32)
    parser.add_argument("-z", help="Z radius", type=int, default=32)

    parser.add_argument("--center", help="X Min,Max", type=int, nargs=3, default=[84,103,64])

    parser.add_argument("-d", "--display", help="Display Results", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Verbose flag", action="store_true", default=False)
    parser.add_argument("--debug", help="Debug flag", action="store_true", default=False)

    inArgs = parser.parse_args()

    x = [inArgs.center[0]-inArgs.x, inArgs.center[0]+inArgs.x]
    y = [inArgs.center[1]-inArgs.y, inArgs.center[1]+inArgs.y]
    z = [inArgs.center[2]-inArgs.z, inArgs.center[2]+inArgs.z]

    create_roi_cube(inArgs.out_image, inArgs.in_image,x,y,z, label=inArgs.label, verbose=inArgs.verbose, debug=inArgs.debug)


#
# Main Function
#
if __name__ == '__main__':
    sys.exit(main())
