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

def measure( label_nii_filename, image_nii_filename, requested_labels=[], verbose_flag=False, verbose_nlines=10, verbose_all_flag=False ):

    # Load arrays

    label_nii = labels.read_nifti_file( label_nii_filename, 'Label file does not exist' )
    image_nii = labels.read_nifti_file( image_nii_filename, 'Image file does not exist' )

    # System Checks to verify that the Array Size and Dimensions are compatible

    image_array = image_nii.get_data()
    label_array = label_nii.get_data()

    if len(image_array.shape) < 2 or len(image_array.shape) > 4:
        sys.exit('Only supports 3D and 4D image arrays')

#    if not len(label_array.shape) == 3:
#        sys.exit('Only supports 3D label arrays')

    label_ndim = len(label_array.shape)
    image_ndim = len(image_array.shape)

    ndim = min([label_ndim, image_ndim])

    if not image_array.shape[0:ndim] == label_array.shape[0:ndim]:
        sys.exit('Image array and label array do not have the same voxel dimensions')

    # Find a set of acceptable labels

    label_list = labels.get_labels( requested_labels, label_array)


    # Permute array or expand so desired stats is along first dimension

    if image_ndim == 4:
        nVolumes = int(image_array.shape[3])
        image_array = numpy.transpose( image_array, [3,0,1,2] )

    elif image_ndim == 3:
        image_array = numpy.transpose( image_array, [2,0,1] )

    else:
        nVolumes = 1
        image_array = numpy.expand_dims(image_array, axis=0)


    label_array = numpy.expand_dims(label_array, axis=0)


    # Gather stats

    if verbose_flag:
        ii_verbose=0
        pandas.set_option('expand_frame_repr', False)

    df_stats              = pandas.DataFrame(columns=('label', 'x_com', 'y_com', 'z_com', 'time', 'mean', 'std', 'min','max' ))

    nlabels = len(label_list)

    for ii, ii_label in enumerate(label_list):

        for jj in range(0,nVolumes):
        
            if label_ndim == 3:
                mask = label_array[0,:,:,:] == ii_label
            else:
                mask = label_array[0,:,:] == ii_label

            label_mean   = numpy.mean( image_array[jj][ mask ] )
            label_std    = numpy.std( image_array[jj][ mask ] )
            label_min    = numpy.min( image_array[jj][ mask ] )
            label_max    = numpy.max( image_array[jj][ mask ] )

            if label_ndim == 3:
                x_com, y_com, z_com =  ndimage.measurements.center_of_mass(mask)
            else:
                z_com = 0
                x_com, y_com =  ndimage.measurements.center_of_mass(mask)

            stats  = [ii_label, x_com, y_com, z_com, jj, label_mean, label_std, label_min, label_max ]

            if verbose_flag and nlabels > 3*verbose_nlines:
                if ii_verbose==(verbose_nlines-1):
                    df_verbose =  df_stats.tail(verbose_nlines) 
                    print('\n')
                    print (df_verbose.to_string(formatters={'label':'{:,.0f}'.format, 'volume':'{:,.0f}'.format, 'time':'{:,.0f}'.format, 
                                                'mean':'{:,.3f}'.format, 'std':'{:,.3f}'.format, 'min':'{:,.3f}'.format, 'max':'{:,.3f}'.format,
                                                'x_com':'{:,.0f}'.format, 'y_com':'{:,.0f}'.format, 'z_com':'{:,.0f}'.format}  ))
                    ii_verbose = 0
                else:
                    ii_verbose += 1
                    
            df_stats.loc[len(df_stats)] = stats


    if verbose_flag:

        if verbose_all_flag:
            pandas.set_option('display.max_rows',len(df_stats))
            
        print('\n')

        # ['label' 'x_com' 'y_com' 'z_com' 'time' 'mean' 'std' 'min' 'max']
        print(df_stats.to_string(formatters={'label':'{:,.0f}'.format, 'time':'{:,.0f}'.format,
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

     parser = argparse.ArgumentParser(prog='measure')

     parser.add_argument("label_filename",    help="Label NIFTI filename ")
     parser.add_argument("image_filename",    help="Image NIFTI filename" )
     parser.add_argument("--out",             help="CSV Filename (default=imageFile.csv).", default = None) 

     parser.add_argument("--labels",        help="Label indices to analyze", type=float, nargs="*", default = None )

     parser.add_argument("-v","--verbose",   help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("--verbose_all",    help="When displaying data frame include all rows.",      action="store_true", default=False )
     parser.add_argument("--verbose_nlines", help="Number of lines to display (default=10)", type=int,   default=10 )

     inArgs = parser.parse_args()

     df_stats = measure( inArgs.label_filename, inArgs.image_filename, inArgs.labels, 
                         verbose_flag=inArgs.verbose, 
                         verbose_nlines=inArgs.verbose_nlines,
                         verbose_all_flag=inArgs.verbose_all)


     # Save measures to file

     if inArgs.out == 'in':
        out_filename = util.replace_nii_or_nii_gz_suffix(inArgs.image_filename, '.csv')
     else:
         out_filename = inArgs.out

     if out_filename is not None:

         # ['label' 'x_com' 'y_com' 'z_com' 'time' 'mean' 'std' 'min' 'max']
         formatters={'label':'{:,.0f}', 'time':'{:,.0f}',
                     'mean':'{:,.3f}', 'std':'{:,.3f}', 'min':'{:,.3f}', 'max':'{:,.3f}',
                     'x_com':'{:,.0f}', 'y_com':'{:,.0f}', 'z_com':'{:,.0f}'}

         for ii in ['x_com', 'y_com', 'z_com', 'time']:
             df_stats.loc[:, ii] = df_stats[ii].apply(int)

#         for key,value in formatters.iteritems():
#             print([key, value])
#             df_stats[key] = df_stats[key].map(lambda x: value % x)

         df_stats.to_csv(out_filename, index=False)                 

