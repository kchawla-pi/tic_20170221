#!/usr/bin/env python
"""
Removes labels from a current label NIFTI image.
"""
import sys
import nibabel
import argparse
import labels
import _utilities as util


def remove(in_nii, remove_labels, remove_csv_filename, out_filename, merge=None):

    in_label_nii = labels.read_nifti_file(in_nii, 'Label file does not exist')
    in_label_array = in_label_nii.get_data()

    if len(remove_csv_filename):
        csv_remove_labels = labels.read_labels_from_csv(remove_csv_filename)
    else:
        csv_remove_labels = []

    remove_labels = set(labels.get_labels(remove_labels + csv_remove_labels, in_label_array))

    out_label_array = in_label_array

    for ii in remove_labels:
        mask = in_label_array == ii
        out_label_array[mask] = 0

    if merge is not None and merge!=0: # isinstance(map, (int, long, float)) and float(map) !=0:
        out_label_array = merge*(out_label_array > 0)

    nibabel.save(nibabel.Nifti1Image(out_label_array, None, in_label_nii.get_header()), out_filename)


# Main Function
#

def main():

     ## Parsing Arguments

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='remove')

     parser.add_argument("in_nii",    help="Filename of NIFTI input label ")
     parser.add_argument("--out_nii", help="Filename of NIFTI output label. If <out_nii> is set to in then overwrite "
                                           "input file (default = remove.<in_nii> )")

     parser.add_argument('-r', "--remove",  help="Labels to remove", type=float, nargs="*", default = [] )
     parser.add_argument("--csv",           help="CSV filename containing labels to remove", default = [] )

     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )

     inArgs = parser.parse_args()

     # Set output filename
     if inArgs.out_nii == None:
          out_filename = util.add_prefix_to_filename(inArgs.in_nii, 'remove.')

     elif inArgs.out_nii == 'in':
          out_filename = inArgs.in_nii

     else:
          out_filename = inArgs.out_nii



     remove( inArgs.in_nii, inArgs.remove, inArgs.csv, out_filename)


if __name__ == "__main__":
     sys.exit(main())
