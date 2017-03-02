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

def create_roi_formula(in_point, in_image, label, radius, affine_iras_to_wras, in_verbose_flag):

    y =   -in_point[0]
    x =   -in_point[1]
    z =    in_point[2]

    if in_verbose_flag:
        print(">>>>> create_roi_formula", x,y,z, radius, label)



    xxx, yyy, zzz = create_mesh_grid(in_image, affine_iras_to_wras, in_verbose_flag)

    big_sphere = (((xxx - x) ** 2
                         + (yyy - y ) ** 2
                          + (zzz - z) ** 2) <= radius ** 2)

    small_sphere = (((xxx - x) ** 2
                         + (yyy - y ) ** 2
                         + (zzz - z) ** 2) <= (radius/5) ** 2)

    roi_image = label * ( big_sphere - small_sphere )


    print(label, np.amax(roi_image))
    return roi_image

def create_roi_convolution(iras_point, point_image, label, radius, in_verbose_flag=False):

    if in_verbose_flag:
        print (">>>>> create_roi_convolution", iras_point, radius)

    kernel = skimage.ball(radius)

    roi_image = 0 * point_image  # reset image
    roi_image[iras_point[0], iras_point[1], iras_point[2]] = 1

    roi_image = ndimage.convolve(roi_image, kernel) * label

    roi_image[iras_point[0], iras_point[1], iras_point[2]] = 0

    return roi_image

def create_mesh_grid(nii_data, affine_iras_to_wras, inVerboseFlag):

    lower_left  = np.dot(affine_iras_to_wras, [0, 0, 0, 1])
    upper_right = np.dot(affine_iras_to_wras, [x - 1 for x in list(nii_data.shape)] + [1])

    x = [0, 0, 0]

    for ii in [0, 1, 2]:
        if ii in [0]:
            sign = -1
        else:
            sign = 1

        x[ii] = sign * np.linspace(lower_left[ii], upper_right[ii], nii_data.shape[ii])
        print (np.amin(x[ii]), np.amax(x[ii]))

    return np.meshgrid(-1*x[0], -1*x[1], x[2], sparse=True)

def create_roi(out_roi, in_image, in_df_points, inRadius=3, inMethod='convolution', inVerboseFlag=False,
               inDebugFlag=False):


    nii_image = nb.load(in_image)
    nii_shape = nii_image.get_shape()
    nii_data = nii_image.get_data()

    affine_iras_to_wras = np.asarray(nii_image.get_affine())

    # Loop over points

    in_points = in_df_points.values.tolist()
    n_points = len(in_points)

    point_image = np.zeros(nii_shape)
    roi_image = np.zeros(nii_shape + (n_points,))

    for ii, wlps_point in enumerate(in_points):


        # Convert from wLPS to wRAS
        wras_point = [-wlps_point[0], -wlps_point[1], wlps_point[2]]
        iras_point = [round(i, 0) for i in np.dot(np.linalg.inv(affine_iras_to_wras), wras_point + [1])]

        print (ii, wras_point, iras_point)

        if inMethod == 'equation':
            roi_image[:, :, :, ii] += create_roi_formula(wras_point, roi_image[:, :, :, ii], wlps_point[4], inRadius,
                                                         affine_iras_to_wras, inVerboseFlag)

        else:
            roi_image[:, :, :, ii] = create_roi_convolution(iras_point, roi_image[:, :, :, ii], wlps_point[4], inRadius)

        print ('create_roi', wlps_point[4], np.amax(roi_image))

    sum_image = np.sum(roi_image, axis=3)

    sum_nii = nb.Nifti1Image(roi_image, nii_image.get_affine())
    nb.save(sum_nii, 'sum.' + out_roi)

    out_nii = nb.Nifti1Image(sum_image, nii_image.get_affine())
    nb.save(out_nii, out_roi)

    return roi_image, sum_image


def main():
    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='create_sphere')
    parser.add_argument("in_image", help="Image")
    parser.add_argument("in_csv", help="CSV file containing coordinates")
    parser.add_argument("out_image", help="Image")

    parser.add_argument("--label", help="Label number", type=int, default=1000)
    parser.add_argument("--radius", help="Radius of ROI", type=int, default=5)
    parser.add_argument("--roi_prefix", help="ROI prefix added to --image", default="roi.")
    parser.add_argument("--roi_add", help="Display Results", action="store_true", default=False)
    parser.add_argument("--roi_type", help="ROI Type (sphere, point)", choices=['sphere', 'point'], default='sphere')
    parser.add_argument("--merge", help="Merge ROIs", action="store_true", default=True)
    parser.add_argument("--collapse", help="Collapse ROIs", action="store_true", default=True)
    parser.add_argument("-d", "--display", help="Display Results", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Verbose flag", action="store_true", default=False)
    parser.add_argument("--debug", help="Debug flag", action="store_true", default=False)
    parser.add_argument("--method", help="Method ( 'equation', 'convolution')", choices = ('convolution, equation'),
    default='convolution')

    parser.add_argument("--qi", help="QA inputs", action="store_true", default=False)
    parser.add_argument("--qo", help="QA outputs", action="store_true", default=False)
    parser.add_argument("-r", "--run", help="Run processing pipeline", action="store_true", default=False)

    #     group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument("--point", help="Input a single point", nargs=3, type=float, default=None)

    inArgs = parser.parse_args()

    input_files = [[inArgs.in_image, ':colormap=grayscale']]

    #     output_files = [[ inArgs.image, ':colormap=grayscale'],
    #                     [ roiImage, ':colormap=jet']]

    if inArgs.roi_type == 'sphere':
        radius = inArgs.radius
    else:
        radius = 0

    if inArgs.debug:
        print ("inArgs.in_image    = " + str(inArgs.in_image))
        print ("inArgs.in_csv      = " + str(inArgs.in_csv))
        print ("inArgs.out_image   = " + str(inArgs.out_image))
        print ("inArgs.radius      = " + str(inArgs.radius))
        print
        print ("radius             = " + str(radius))
        print
        print ("inArgs.display     = " + str(inArgs.display))
        print ("inArgs.debug       = " + str(inArgs.debug))
        print ("inArgs.verbose     = " + str(inArgs.verbose))
        print
        #         print ("ROI image          = " +  roiImage)
        print

    if inArgs.qi:
        _qa_utilities.qa_input_files(input_files, inArgs.verbose, False)

    in_points = pd.read_csv(inArgs.in_csv)

    create_roi(inArgs.out_image, inArgs.in_image, in_points, inArgs.radius, inArgs.method, inArgs.verbose, inArgs.debug)


#
# Main Function
#
if __name__ == '__main__':
    sys.exit(main())
