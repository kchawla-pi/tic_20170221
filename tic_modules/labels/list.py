#!/usr/bin/env python

"""

"""
import pandas
import argparse

import labels
import _utilities as util


def list_labels(in_filename):
     in_label_nii    = labels.read_nifti_file( in_filename, 'Label file does not exist' )
     label_list = labels.get_labels( None, in_label_nii.get_data() )
     return label_list


#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='list')
     parser.add_argument("in_nii",    help="Filename of NIFTI input label ")
     inArgs = parser.parse_args()

     label_list = list_labels(inArgs.in_nii)
     se = pandas.Series( label_list, index=None, name='labels')
     print(se.to_string(index=False, header=False))


