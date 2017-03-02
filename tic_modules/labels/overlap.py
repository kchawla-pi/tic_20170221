#!/usr/bin/env python

"""
Measures images statistics within a labels.
"""
import sys
import argparse
import labels
import _utilities as util
import numpy
import pandas
import scipy.ndimage as ndimage

def query_voxel_volume_mm3(label_nii):
    return numpy.prod( label_nii.get_header()['pixdim'][1:4] )

def measure_volume(mask, volume_per_voxel=1):

    label_volume_voxels = int(numpy.sum(mask))
    label_volume_mm3 = volume_per_voxel * label_volume_voxels

    return (label_volume_voxels, label_volume_mm3)

def overlap( label_nii_filename, label2_nii_filename, requested_labels=[], include_zero=False, verbose_flag=False, verbose_nlines=10, verbose_all_flag=False ):

    # Load arrays

    label_nii = labels.read_nifti_file( label_nii_filename, 'Label file does not exist' )
    label2_nii = labels.read_nifti_file( label2_nii_filename, 'Image file does not exist' )

    label_single_voxel_volume_mm3 = query_voxel_volume_mm3(label_nii)
    label2_single_voxel_volume_mm3 = query_voxel_volume_mm3(label2_nii)

    # System Checks to verify that the Array Size and Dimensions are compatible

    label_array = numpy.ndarray.squeeze(label_nii.get_data())
    label2_array = numpy.ndarray.squeeze(label2_nii.get_data())

    # Check size

    if len(label2_array.shape) < 2 or len(label2_array.shape) > 4:
        sys.exit('Only supports 3D and 4D image arrays')

#    if not len(label_array.shape) == 3:
#        sys.exit('Only supports 3D label arrays')

    label_ndim = len(label_array.shape)
    label2_ndim = len(label2_array.shape)

    ndim = min([label_ndim, label2_ndim])

    if not label2_array.shape[0:ndim] == label_array.shape[0:ndim]:
        sys.exit('Image array and label array do not have the same voxel dimensions')

    # Find a set of acceptable labels

    label_list = labels.get_labels( requested_labels, label_array, include_zero)
    label2_list = labels.get_labels([], label2_array, include_zero)

    # Gather stats

    if verbose_flag:
        ii_verbose=0
        pandas.set_option('expand_frame_repr', False)

    df_stats              = pandas.DataFrame(columns=('label1', 'label2', 'volume1_mm3',  'volume2_mm3', 'volume12_mm3',
                                                      'fraction12', 'x12_com', 'y12_com', 'z12_com'))

    for ii, ii_label in enumerate(label_list):

        mask1 = label_array == ii_label
        _, label1_volume_mm3 = measure_volume(mask1, label_single_voxel_volume_mm3)

        overlap_label2_list = list(numpy.unique(mask1 * label2_array))[1:]  # Remove 0 from list

        for jj, jj_label in enumerate(overlap_label2_list):
        
            mask2 = label2_array == jj_label
            mask12 = mask1 * mask2

            _, label2_volume_mm3 = measure_volume( mask2, label_single_voxel_volume_mm3)
            _, label12_volume_mm3 = measure_volume(mask12, label_single_voxel_volume_mm3)

            fraction12 = label12_volume_mm3 / label1_volume_mm3

            x12_com, y12_com, z12_com =  ndimage.measurements.center_of_mass(mask12)

            stats  = [ii_label, jj_label, label1_volume_mm3, label2_volume_mm3, label2_volume_mm3,
                      fraction12, x12_com, y12_com, z12_com ]

            if verbose_flag:
                if ii_verbose==(verbose_nlines-1):
                    df_verbose =  df_stats.tail(verbose_nlines) 
                    print('\n')
                    print (df_verbose.to_string(formatters={'label1':'{:,.0f}'.format, 'label2':'{:,.0f}'.format,
                                                            'volume1':'{:,.0f}'.format, 'volume2':'{:,.0f}'.format,
                                                            'volume12':'{:,.0f}'.format,
                                                            'fraction12':'{:,.3f}'.format,
                                                            'x12_com':'{:,.0f}'.format,
                                                            'y12_com':'{:,.0f}'.format,
                                                            'z12_com':'{:,.0f}'.format}  ))
                    ii_verbose = 0
                else:
                    ii_verbose += 1
                    
            df_stats.loc[len(df_stats)] = stats


    if verbose_flag:

        if verbose_all_flag:
            pandas.set_option('display.max_rows',len(df_stats))
            
        print('\n')
        print(df_stats.to_string(formatters={'label':'{:,.0f}'.format, 'volume':'{:,.0f}'.format, 'time_index':'{:,.0f}'.format,
                        'mean':'{:,.3f}'.format, 'std':'{:,.3f}'.format, 'min':'{:,.3f}'.format, 'max':'{:,.3f}'.format,
                        'x_com':'{:,.0f}'.format, 'y_com':'{:,.0f}'.format, 'z_com':'{:,.0f}'.format} ))
        print('\n')
            

    return df_stats


#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='overlap')

     parser.add_argument("label_filename",    help="Label NIFTI filename ")
     parser.add_argument("label2_filename",    help="Label2 NIFTI filename" )
     parser.add_argument("--out",             help="CSV Filename (default=imageFile.csv).", default = None) 

     parser.add_argument("--labels",        help="Label indices to analyze", type=float, nargs="*", default = None )

     parser.add_argument("-v","--verbose",   help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("--verbose_all",    help="When displaying data frame include all rows.",      action="store_true", default=False )
     parser.add_argument("--verbose_nlines", help="Number of lines to display (default=10)", type=int,   default=10 )

     inArgs = parser.parse_args()

     df_stats = overlap( inArgs.label_filename, inArgs.label2_filename, inArgs.labels, 
                         verbose_flag=inArgs.verbose, 
                         verbose_nlines=inArgs.verbose_nlines,
                         verbose_all_flag=inArgs.verbose_all)


     # Save measures to file

     if inArgs.out == 'in':
         out_filename = util.replace_nii_or_nii_gz_suffix(inArgs.label2_filename, '.csv')
     else:
         out_filename = inArgs.out

     if out_filename is not None:
         df_stats.to_csv(out_filename, index=False)                 

