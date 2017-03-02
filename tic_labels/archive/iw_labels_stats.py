#!/usr/bin/env python2

"""

"""
from __future__ import division
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sys
import numpy
from numpy import linalg
from random import random

import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

from scipy.ndimage.morphology import binary_erosion, binary_dilation, binary_opening

import iw_labels 
import iwUtilities as util
import scipy.stats as stats


def check_limits(parameter, limits):
    return parameter >= limits[0] and parameter <= limits[1]


def calculate_bounding_box(mask):

    objs = ndimage.find_objects(mask)

    ndim = query_ndimensions(mask)

    bb_height = int(objs[0][0].stop - objs[0][0].start)
    bb_width  = int(objs[0][1].stop - objs[0][1].start)
    bb_depth  = int(objs[0][2].stop - objs[0][2].start)

    if ndim==4:
        bb_time  = int(objs[0][3].stop - objs[0][3].start)
        bb_min = numpy.min([bb_height, bb_width, bb_depth, bb_time])
        bb_volume_voxels = bb_height * bb_width * bb_depth* bb_time

    else:
        bb_time = 0
        bb_min = numpy.min([bb_height, bb_width, bb_depth])
        bb_volume_voxels = bb_height * bb_width * bb_depth

            


    return [bb_height, bb_width, bb_depth, bb_time, bb_min, bb_volume_voxels]

def query_ndimensions(mask):

    mask_shape = mask.shape + (1,1,1,1)
    mask_shape = mask_shape[0:4]

    if mask_shape[3] == 1:
        ndimensions = 3
    else:
        ndimensions = 4

    return ndimensions


def query_voxel_volume_mm3(label_nii):
    return numpy.prod( label_nii.get_header()['pixdim'][1:4] )



def calculate_center_of_mass(mask):

    ndimensions = query_ndimensions(mask)

    if ndimensions==4:
        label_x_com, label_y_com, label_z_com, label_t_com = [int(x) for x in
                                                 numpy.round(ndimage.measurements.center_of_mass(mask), 0)]
    else:
        label_t_com = 0
        label_x_com, label_y_com, label_z_com = [int(x) for x in
                                                 numpy.round(ndimage.measurements.center_of_mass(mask), 0)]

#    return ( int(label_x_com), int(label_y_com), int(label_z_com), int(label_t_com) )
    return ( label_x_com, label_y_com, label_z_com, label_t_com )

#
# Main Function
#

def measure(in_label_nii_filename, labels, background, stats, out_filename, limits_volume_voxels=[0, numpy.inf], 
            limits_bb_volume_voxels=[0, numpy.inf], limits_fill_factor=[0,1], sort='volume', 
            verbose=False, verbose_nlines=20):

    label_nii = iw_labels.read_nifti_file( in_label_nii_filename, 'iw_label_stats.py: Label file does not exist. ')

    single_voxel_volume_mm3 = query_voxel_volume_mm3( label_nii )

    label_array = label_nii.get_data()

    label_list = iw_labels.get_labels(labels, label_array, background)

    df_stats = pd.DataFrame(columns=(
    'label', 'volume_voxels', 'volume_mm3', 'com_x', 'com_y', 'com_z', 'com_t', 'com_in', 'bb_dx', 'bb_dy', 'bb_dz', 'bb_dt', 'bb_dmin', 'bb_volume_voxels',
    'fill_factor'))

    stats_list = ['label', ] + list(stats)

    if verbose:
        jj = 0
        pd.set_option('expand_frame_repr', False)

    for ii in label_list:

        # Create logical mask

        mask = (label_array == ii)
        ndim = query_ndimensions(mask)

        # Calculate Volume
        label_volume_voxels = int(numpy.sum(mask))
        label_volume_mm3    = single_voxel_volume_mm3 * label_volume_voxels

        if check_limits(label_volume_voxels, limits_volume_voxels):

            bb_dx, bb_dy, bb_dz, bb_dt, bb_dmin, bb_volume_voxels = calculate_bounding_box(mask)

            if check_limits(bb_volume_voxels, limits_bb_volume_voxels):

                label_x_com, label_y_com, label_z_com, label_t_com = calculate_center_of_mass(mask)

                if ndim == 4:
                    label_com_in = mask[label_x_com, label_y_com, label_z_com, label_t_com]
                else:
                    label_com_in = mask[label_x_com, label_y_com, label_z_com]

                fill_factor = label_volume_voxels / bb_volume_voxels

                if check_limits(fill_factor, limits_fill_factor):

                    label_stats = [ii, label_volume_voxels, label_volume_mm3, label_x_com, label_y_com, label_z_com, label_t_com, label_com_in, bb_dx, bb_dy,
                                   bb_dz, bb_dt, bb_dmin, bb_volume_voxels, fill_factor]

                    df_stats.loc[len(df_stats)] = label_stats

                    if verbose:
                        if jj == (verbose_nlines - 1):
                            print
                            df_verbose = df_stats.tail(verbose_nlines)
                            df_verbose = df_verbose[stats_list]
                            print df_verbose.to_string(
                                formatters={'volume_voxels': '{:,.0f}'.format, 'volume_mm3': '{:,.3f}'.format,
                                            'com_x': '{:,.0f}'.format,
                                            'com_y': '{:,.0f}'.format, 'com_z': '{:,.0f}'.format,
                                            'com_t': '{:,.0f}'.format,
                                            'com_in': '{:,.0f}'.format, 'bb_dx': '{:,.0f}'.format,
                                            'bb_dy': '{:,.0f}'.format, 'bb_dz': '{:,.0f}'.format, 'bb_dt': '{:,.0f}'.format,
                                            'bb_volume_voxels': '{:,.0f}'.format,
                                            'fill_factor': '{:,.3f}'.format 
                                            }
                                )

                            jj = 0
                        else:
                            jj += 1

    df_sorted = df_stats.sort_values([sort], ascending=[1]).reset_index(drop=True)

    if verbose:
        print
        print df_sorted[stats_list]
        print

    if not out_filename == None:
        df_sorted[stats_list].to_csv(out_filename, index=False)


def main():
    ## Parsing Arguments
    #
    #

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='iw_compare_images')

    parser.add_argument("in_label_nii_filename", help="Label NIFTI filename ")
    parser.add_argument("--out", help="Filename of CSV output file containing label stats", default=None)
    parser.add_argument("--stats", help="Stats to report", type=str, nargs="*",
                        default=('volume_voxels', 'volume_mm3',  'com_x', 'com_y', 'com_z', 'com_t', 'com_in', 'bb_dx', 'bb_dy', 'bb_dz', 'bb_dt', 'bb_dmin',
                                 'bb_volume_voxels', 'fill_factor'))

    parser.add_argument("--labels", help="Label indices to analyze", type=int, nargs="*", default=None)
    parser.add_argument("--sort", help="Label indices to analyze", type=str, default='label')

    parser.add_argument("--limits_volume_voxels", help="Report labels within these limits", type=int, nargs=2,
                        default=[0, numpy.inf])

    parser.add_argument("--limits_fill_factor", help="Report labels within these limits", type=int, nargs=2,
                        default=[0, 1.0])

    parser.add_argument("--limits_bb_volume_voxels", help="Report labels within these limits", type=int, nargs=2,
                        default=[0, numpy.inf])

    parser.add_argument("--background", help="Report background label (i.e label=0)", action="store_true",
                        default=False)

    parser.add_argument("-d", "--display", help="Display Results", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Verbose flag", action="store_true", default=False)
    parser.add_argument("--verbose_nlines", help="Number of lines to display (default=10)", default=10)

    inArgs = parser.parse_args()

    measure(inArgs.in_label_nii_filename, inArgs.labels, inArgs.background, 
            inArgs.stats, inArgs.out, inArgs.limits_volume_voxels, 
            inArgs.limits_bb_volume_voxels, inArgs.limits_fill_factor, inArgs.sort, 
            inArgs.verbose, inArgs.verbose_nlines)



if __name__ == "__main__":
    sys.exit(main())
