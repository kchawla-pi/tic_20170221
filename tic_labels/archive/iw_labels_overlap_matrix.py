#!/usr/bin/env python2

"""

"""
from __future__ import division
import sys
import numpy as numpy
import nibabel as nb
import pandas as pd
import argparse

import iw_labels as labels
import iwUtilities as util

#
# Main Function
#

def main():
    ## Parsing Arguments
    #
    #

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='iw_compare_images')

    parser.add_argument("in_label_nii_filename", help="Label NIFTI filename ")
    parser.add_argument("in_label2_nii_filename", help="Label NIFTI filename ")

    parser.add_argument("--out", help="Filename of CSV output file containing label stats", default=None)
    parser.add_argument("--stats", help="Stats to report", type=str, nargs="*",
                        default=('volume', 'com_x', 'com_y', 'com_z', 'com_in', 'bb_dx', 'bb_dy', 'bb_dz', 'bb_dmin',
                                 'bb_volume', 'fill_factor'))

    parser.add_argument("--labels", help="Label indices to analyze", type=int, nargs="*", default=None)
    parser.add_argument("--sort", help="Label indices to analyze", type=str, default='label')

    parser.add_argument("--limits_volume", help="Report labels within these limits", type=int, nargs=2,
                        default=[0, numpy.inf])
    parser.add_argument("--limits_fill_factor", help="Report labels within these limits", type=int, nargs=2,
                        default=[0, 1.0])
    parser.add_argument("--limits_bb_volume", help="Report labels within these limits", type=int, nargs=2,
                        default=[0, numpy.inf])

    parser.add_argument("--limits_background", help="Report background label (i.e label=0)", action="store_true",
                        default=False)

    parser.add_argument("-d", "--display", help="Display Results", action="store_true", default=False)
    parser.add_argument("-v", "--verbose", help="Verbose flag", action="store_true", default=False)
    parser.add_argument("--verbose_nlines", help="Number of lines to display (default=10)", default=10)

    inArgs = parser.parse_args()

    label1_nii = labels.read_nifti_file(inArgs.in_label_nii_filename, 'Label file does not exist')
    label1_array = label1_nii.get_data()

    label2_nii = labels.read_nifti_file(inArgs.in_label2_nii_filename, 'Label file does not exist')
    label2_array = label2_nii.get_data()

    label1_list = labels.get_labels(inArgs.labels, label1_array, inArgs.limits_background)
    label2_list = labels.get_labels(None, label2_array, inArgs.limits_background)

    label1_dict = dict(zip( label1_list, range(0, len(label1_list))))
    label2_dict = dict(zip( label2_list, range(0, len(label2_list))))

    print label1_dict
    print label2_dict


    overlap_matrix = numpy.zeros( [ len(label1_list), len(label2_list) ] ) 

    for ii in label1_list:
        mask1 = 1.*(label1_array == ii)        

        ii_label2_list = numpy.unique(mask1 * label2_array)
        ii_label2_list = ii_label2_list[ii_label2_list>0]

        for jj in ii_label2_list:

            mask2 = 1.*(label2_array == jj)            
            overlap_matrix[ label1_dict[ii], label2_dict[jj] ] = numpy.sum(mask1 * mask2 )

            print ii,label1_dict[ii], jj, label2_dict[jj], numpy.sum(mask1), numpy.sum(mask2), overlap_matrix[ label1_dict[ii], label2_dict[jj] ]
            

    overlap_matrix.tofile('overlap.csv',sep=',',format='%10.5f')

if __name__ == "__main__":
    sys.exit(main())
