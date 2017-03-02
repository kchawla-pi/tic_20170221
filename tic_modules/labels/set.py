#!/usr/bin/env python

"""
A function ot 
"""
import sys
import numpy as np

import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

import labels


def check_limits(parameter, limits):
    return parameter >= limits[0] and parameter <= limits[1]


def set(in_nii, in_csv, in_labels, in_stats, in_limits,  in_sort, out_nii):

    df_stats = pd.read_csv(in_csv)

    if inArgs.labels is not None:
        df_stats = df_stats[df_stats['label'].isin(in_labels)]

    stats_list = ['label'] + sum([in_stats], [])

    if in_limits is not None:
        df_limits = df_stats[
            (df_stats[in_sort[0]] >= in_limits[0]) & (df_stats[in_sort[0]] <= in_limits[1])]
    else:
        df_limits = df_stats

    df_sorted = df_limits.sort_values(in_sort, ascending=in_sort_direction).reset_index()
    df_sorted = df_sorted.dropna()

    in_nii = labels.read_nifti_file(in_in_nii, 'Label file does not exist')
    in_array = in_nii.get_data()
    out_array = np.zeros(in_array.shape)

    for ii_label, ii_value in df_sorted[stats_list].get_values():
        out_array[in_array == ii_label] = ii_value

    nb.save(nb.Nifti1Image(out_array, [], in_nii.get_header()), in_out_nii)

    return

#
# Main Function
#

if __name__ == "__main__":

    ## Parsing Arguments

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='set')

    parser.add_argument("in_csv", help="Label NIFTI filename ")
    parser.add_argument("in_nii", help="Filename of input labels")
    parser.add_argument("out_nii", help="Filename of CSV output file containing label stats")
    parser.add_argument("--sort", help="Labels to sort", type=str, nargs=1, default='label')

    parser.add_argument("--sort_direction", help="Sorting direction: 0=descending, 1=ascending (default=1)", type=int,
                        nargs=1, default=[1])
    parser.add_argument("--limits", help="Limits of sorted values", type=float, nargs=2, default=None)
    parser.add_argument("--stats", help="Stats to report", type=str, nargs="*", default='volume')
    parser.add_argument("--labels", help="Labels to report", type=float, nargs="*", default=None)

    parser.add_argument("-v", "--verbose", help="Verbose flag", action="store_true", default=False)
    parser.add_argument("-a", "--verbose_all", help="Display all rows", action="store_true", default=False)

    parser.add_argument("--nan", help="Keep NAN values", action="store_true", default=False)

    inArgs = parser.parse_args()

    pd.set_option('expand_frame_repr', False)


    set(inArgs.in_nii, inArgs.in_csv, inArgs.labels, inArgs.stats, inArgs.limits,  inArgs.sort, inArgs.out_nii)
