#!/usr/bin/env python2

"""

"""
from __future__ import division
import sys
import numpy

import pandas
import scipy.ndimage as ndimage
import argparse
import _utilities as util
import labels


def check_limits(parameter, limits):
    return parameter >= limits[0] and parameter <= limits[1]


def calculate_bounding_box(mask):

    objs = ndimage.find_objects(mask)

    ndim = len(mask.shape)

    bb_time   = 1
    bb_height = int(objs[0][0].stop - objs[0][0].start)
    bb_width  = int(objs[0][1].stop - objs[0][1].start)

    if ndim > 2:
        bb_depth  = int(objs[0][2].stop - objs[0][2].start)
    else:
        bb_depth = 1


    if ndim==4:
        bb_time  = int(objs[0][3].stop - objs[0][3].start)
        bb_min = numpy.min([bb_height, bb_width, bb_depth, bb_time])

    elif ndim==3:
        bb_min = numpy.min([bb_height, bb_width, bb_depth])

    else:
        bb_min = numpy.min([bb_height, bb_width])

    bb_volume_voxels = bb_height * bb_width * bb_depth * bb_time
            
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

    ndimensions = len(mask.shape)

    if ndimensions==4:
        label_x_com, label_y_com, label_z_com, label_t_com = [int(x) for x in
                                                 numpy.round(ndimage.measurements.center_of_mass(mask), 0)]
    elif ndimensions==3:
        label_t_com = 0
        label_x_com, label_y_com, label_z_com = [int(x) for x in
                                                 numpy.round(ndimage.measurements.center_of_mass(mask), 0)]
    else:
        label_t_com = 0
        label_z_com = 0
        label_x_com, label_y_com = [int(x) for x in
                                                 numpy.round(ndimage.measurements.center_of_mass(mask), 0)]

#    return ( int(label_x_com), int(label_y_com), int(label_z_com), int(label_t_com) )
    return ( label_x_com, label_y_com, label_z_com, label_t_com )

#
# Main Function
#

def properties(in_label_nii_filename, label_list=[], background=False,  stats=[], out_filename=None, limits_volume_voxels=[0, numpy.inf],
            limits_bb_volume_voxels=[0, numpy.inf], limits_fill_factor=[0,1], sort='label', 
            verbose=False, verbose_nlines=20):

    label_nii = labels.read_nifti_file( in_label_nii_filename, 'labels.properties.py: Label file does not exist. ')

    single_voxel_volume_mm3 = query_voxel_volume_mm3( label_nii )

    label_array = label_nii.get_data()

    label_list = labels.get_labels(label_list, label_array, background)

    all_stats = [
    'label', 'volume_voxels', 'volume_mm3', 'com_x', 'com_y', 'com_z', 'com_t', 'com_in', 'bb_dx', 'bb_dy', 'bb_dz', 'bb_dt', 'bb_dmin', 'bb_volume_voxels',
    'fill_factor']

    df_stats = pandas.DataFrame(columns=all_stats)

    if len(stats)==0:
        stats_list = ['label', ] + all_stats
    else:
        stats_list = ['label', ] + list(stats)

    if verbose:
        jj = 0
        pandas.set_option('expand_frame_repr', False)

    for ii in label_list:

        # Create logical mask

        mask = (label_array == ii)
        ndim = len(mask.shape)

        # Calculate Volume
        label_volume_voxels = int(numpy.sum(mask))
        label_volume_mm3    = single_voxel_volume_mm3 * label_volume_voxels

        if check_limits(label_volume_voxels, limits_volume_voxels):

            bb_dx, bb_dy, bb_dz, bb_dt, bb_dmin, bb_volume_voxels = calculate_bounding_box(mask)

            if check_limits(bb_volume_voxels, limits_bb_volume_voxels):

                label_x_com, label_y_com, label_z_com, label_t_com = calculate_center_of_mass(mask)

                if ndim == 4:
                    label_com_in = mask[label_x_com, label_y_com, label_z_com, label_t_com]
                elif ndim==3:
                    label_t_com = 0
                    label_com_in = mask[label_x_com, label_y_com, label_z_com]
                else:
                    label_z_com = label_t_com = 0
                    label_com_in = mask[label_x_com, label_y_com]

                fill_factor = label_volume_voxels / bb_volume_voxels

                if check_limits(fill_factor, limits_fill_factor):

                    label_stats = [ii, label_volume_voxels, label_volume_mm3, label_x_com, label_y_com, label_z_com, label_t_com, label_com_in, bb_dx, bb_dy,
                                   bb_dz, bb_dt, bb_dmin, bb_volume_voxels, fill_factor]

                    df_stats.loc[len(df_stats)] = label_stats

                    if verbose:
                        if jj == (verbose_nlines - 1):
                            print('\n')
                            df_verbose = df_stats.tail(verbose_nlines)
                            df_verbose = df_verbose[stats_list]
                            print(df_verbose.to_string(
                                formatters={'volume_voxels': '{:,.0f}'.format, 'volume_mm3': '{:,.3f}'.format,
                                            'com_x': '{:,.0f}'.format,
                                            'com_y': '{:,.0f}'.format, 'com_z': '{:,.0f}'.format,
                                            'com_t': '{:,.0f}'.format,
                                            'com_in': '{:,.0f}'.format, 'bb_dx': '{:,.0f}'.format,
                                            'bb_dy': '{:,.0f}'.format, 'bb_dz': '{:,.0f}'.format, 'bb_dt': '{:,.0f}'.format,
                                            'bb_volume_voxels': '{:,.0f}'.format,
                                            'fill_factor': '{:,.3f}'.format 
                                            }
                                ))

                            jj = 0
                        else:
                            jj += 1

    df_sorted = df_stats.sort_values([sort], ascending=[1]).reset_index(drop=True)

    if verbose:
        print('\n')
        print(df_sorted[stats_list])
        print('\n')

    if not out_filename == None:
        df_sorted[stats_list].to_csv(out_filename, index=False)

    return df_sorted


def main():
    ## Parsing Arguments
    #
    #

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='properties')

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

    in_filename = inArgs.in_label_nii_filename

    if inArgs.out == 'in':
        out_filename = util.replace_nii_or_nii_gz_suffix(in_filename, '.csv')
    else:
        out_filename = inArgs.out

    properties(in_filename, label_list=inArgs.labels, background=inArgs.background, 
            stats=inArgs.stats, out_filename=out_filename, limits_volume_voxels=inArgs.limits_volume_voxels, 
            limits_bb_volume_voxels=inArgs.limits_bb_volume_voxels, limits_fill_factor=inArgs.limits_fill_factor,
            sort=inArgs.sort, verbose=inArgs.verbose, verbose_nlines=inArgs.verbose_nlines)



if __name__ == "__main__":
    sys.exit(main())
