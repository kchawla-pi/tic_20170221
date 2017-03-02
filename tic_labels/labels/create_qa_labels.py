#!/usr/bin/env python3

"""

"""
# import os
import nibabel
import argparse
import numpy

import _utilities as util


# create_qa_phase_freq_label
#

def create_qa_labels(in_nii_filename, in_qa_labels, out_nii_filename, swap=False, verbose=False):

    in_nii = util.read_nifti_file(inArgs.in_nii, in_nii_filename + 'does not exist.')
    in_array = in_nii.get_data()
    in_header = in_nii.get_header()

    nfreq, nphase, nslices = in_array.shape

    out_array = 0*in_array

    for ii in range(0,nslices):

        ii_array = in_array[:, :, ii]

        ii_mask_array = 0*ii_array
        ii_freq_array = 0*ii_array
        ii_phase_array = 0*ii_array
        ii_x_array = 0*ii_array
        ii_y_array = 0*ii_array
        ii_other_array = 0*ii_array

        ii_x_where_list = list(numpy.where(numpy.amax(ii_array, axis=1))[0])
        ii_y_where_list = list(numpy.where(numpy.amax(ii_array, axis=0))[0])

        ii_mask_array[ii_x_where_list[0]:ii_x_where_list[-1]+1,
                      ii_y_where_list[0]:ii_y_where_list[-1]+1] = 1


        if swap:
            x_label = in_qa_labels[0]
            y_label = in_qa_labels[1]
        else:
            x_label = in_qa_labels[1]
            y_label = in_qa_labels[0]


        ii_x_array[ii_x_where_list[0]:ii_x_where_list[-1]+1,:] = x_label
        ii_y_array[:, ii_y_where_list[0]:ii_y_where_list[-1] + 1] = y_label

        ii_freq_array = ii_x_array * (1-ii_mask_array)
        ii_phase_array = ii_y_array * (1-ii_mask_array)

        ii_other_array = in_qa_labels[2]* (1-((ii_phase_array + ii_freq_array + ii_mask_array)>0))

        out_array[:,:,ii] = ii_other_array + ii_phase_array + ii_freq_array



    out_nii = nibabel.Nifti1Image(out_array, in_nii.get_affine(),  in_nii.get_header())

    nibabel.save(out_nii, out_nii_filename)

    return


#
# Main Function
#

if __name__ == "__main__":

    ## Parsing Arguments
    #
    #

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='qa_phase_freq_mask')

    parser.add_argument("in_nii", help="Filename of NIFTI input label ")

    parser.add_argument("--out_nii", help='Filename of NIFTI QA background label. (qa_background_label.<in_nii> )',
                        default=None)

    parser.add_argument('--labels',
                        help="QA labels for phase, frequency and other. (100,200,300)", nargs=3, type=int,
                        default=[100,200,300])

    parser.add_argument('--swap', help="Swap phase and frequency labels. (false)",action="store_true", default=False)

    parser.add_argument("-v", "--verbose", help="Verbose flag", action="store_true", default=False)
    inArgs = parser.parse_args()


    if inArgs.out_nii is None:
        out_nii_filename = util.add_prefix_to_filename(inArgs.in_nii, 'qa_background_label.')
    else:
        out_nii_filename = inArgs.out_nii

    create_qa_labels(inArgs.in_nii, inArgs.labels, out_nii_filename, inArgs.swap, inArgs.verbose)
