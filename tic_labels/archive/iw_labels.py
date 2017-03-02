#!/usr/bin/env python2

"""

"""
import os
import sys      
import numpy as np
import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

import iwUtilities as util

class label(object):
    """An excess blob is represented by a position, radius and peak value."""  
    def __init__(self, label_number, label_array, image_array):
        self.number          = label_number
        self.label_filename  = label_filename
        self.image_filename  = image_filename
        self.label_array     = label_array
        self.image_array     = image_array
        self.pixel_size = 1

    def __str__(self):
        """Is called by the print statement"""
        return 'label: {0:3d}'.format(self.label)


class image(object):
    """An excess blob is represented by a position, radius and peak value."""  
    def __init__(self, label_number, label_array, image_array):
        self.number          = label_number
        self.image_filename  = image_filename
        self.pixel_size = 1

    def __str__(self):
        """Is called by the print statement"""
        return 'label: {0:3d}'.format(self.label)


def read_nifti_file( nii_filename, error_message ):

    if os.path.isfile(nii_filename):
        try:
            nii = nb.load( nii_filename )
        except IOError:
            sys.exit("Unable to read NIFTI file. " + nii_filename)
    else:
        sys.exit(error_message + ' ' + nii_filename)

    return nii

def read_labels_from_csv( filename ):

    if os.path.isfile(filename):
        df = pd.read_csv(filename)
        csv_labels  = list(pd.to_numeric( df['label'].get_values()) )
    else:
        sys.exit('CSV file does not exist')

    return csv_labels


def read_from_csv( filename ):

    if os.path.isfile(filename):
        df = pd.read_csv(filename, header=None )
        
        # I need to figure out how to drop non numeric values without assumming that they are in the 
        # first row

        s  = [ pd.to_numeric( df.iloc[x,:], errors='coerce') for x in range(1, len(df.index)) ]
 #       s  = s.dropna()
        #csv_data = np.ndarray.tolist( s.values)        
    else:
        sys.exit('CSV file does not exist')

    return s # csv_data



def get_labels( requested_labels, label_array, include_background=False ):

    

    all_labels = np.unique(label_array[ label_array > 0 - include_background ])

    if requested_labels == None:  # In this case None means All labels present
        labels = all_labels
    else:
        labels = list( set(requested_labels) & set(all_labels))
    
    if include_background:
       labels = [ 0 ]  + labels

    if not len(labels) :
        sys.exit('Labels requested do not exist in the label array')

    return sorted( list(labels)) 


def image_shape_check( image_array ):

    if len(image_array.shape) < 2 or len(image_array.shape) > 4:
        sys.exit('Only supports 3D and 4D image arrays')


def individual_image_stats( image_array ) :

    label_mean   = np.mean( image_array )
    label_std    = np.std( image_array )
    label_min    = np.min( image_array )
    label_max    = np.max( image_array )

    return [label_mean, label_std, label_min, label_max]

def permute_image_array( image_array ):

    if len(image_array.shape) == 4:
        nVolumes = int(image_array.shape[3])
        image_array = np.transpose( image_array, [3,0,1,2] )
    else:
        nVolumes = 1
        image_array = np.expand_dims(image_array, axis=0)

    return image_array, nVolumes


def measure_image_stats( label_nii_filename, image_nii_filename, requested_labels=None, image_limits=[None,None], verbose_flag=False, verbose_nlines=10, verbose_all_flag=False ):

    # Load arrays

    label_nii = read_nifti_file( label_nii_filename, 'measure-image_stats.py: Label file does not exist.' )
    image_nii = read_nifti_file( image_nii_filename, 'measure-image_stats.py: Image file does not exist' )

    # System Checks to verify that the Array Size and Dimensions are compatible

    image_array = image_nii.get_data()
    label_array = label_nii.get_data()

    if len(image_array.shape) < 2 or len(image_array.shape) > 4:
        sys.exit('Only supports 3D and 4D image arrays')

#    if not len(label_array.shape) == 3:
#        sys.exit('Only supports 3D label arrays')

    if not image_array.shape[0:3] == label_array.shape[0:3]:
        sys.exit('Image array and label array do not have the same voxel dimensions')

    # Find a set of acceptable labels

    labels = get_labels( requested_labels, label_array)


    # Permute array or expand so desired stats is along first dimension

    if len(image_array.shape) == 4:
        nVolumes = int(image_array.shape[3])
        image_array = np.transpose( image_array, [3,0,1,2] )
    else:
        nVolumes = 1
        image_array = np.expand_dims(image_array, axis=0)


    label_array = np.expand_dims(label_array, axis=0)



    # Gather stats

    if verbose_flag:
        ii_verbose=0
        pd.set_option('expand_frame_repr', False)

    df_stats              = pd.DataFrame(columns=('label', 'label_volume', 'x_com', 'y_com', 'z_com', 'time', 'image_volume', 'mean', 'std', 'min','max' ))


    # This should be done with a label comprehension.  I just haven't had a chance to refactor the code.

    for ii, ii_label in enumerate(labels):

        for jj in range(0,nVolumes):

            if not image_limits[0] == None:
                image_mask_min = (image_array[jj] >= image_limits[0])
            else:
                image_mask_min = np.ones( image_array[jj].shape ) == 1


            if not image_limits[1] == None:
                image_mask_max = (image_array[jj] <= image_limits[1])
            else:
                image_mask_max = np.ones( image_array[jj].shape ) == 1

            image_mask = image_mask_min & image_mask_max

            label_mask = label_array[0,:,:,:] == ii_label
            x_com, y_com, z_com =  ndimage.measurements.center_of_mass(label_mask)
            label_volume = int(np.sum(label_mask))

            stats = [ii_label, label_volume, x_com, y_com, z_com, jj ]

            # Calculate Image stats
            image_for_stats = image_array[jj][ label_mask * image_mask ]

            if image_for_stats.size:
             
                image_volume = int(np.sum(label_mask * image_mask))
                image_mean   = np.mean( image_for_stats ) 
                image_std    = np.std(  image_for_stats ) 
                image_min    = np.min(  image_for_stats ) 
                image_max    = np.max(  image_for_stats ) 
                
                stats += [ image_volume, image_mean, image_std, image_min, image_max ]

            else:
                stats += [ np.NAN ]*5

                
            if verbose_flag:
                if ii_verbose==(verbose_nlines-1):
                    print
                    df_verbose =  df_stats.tail(verbose_nlines) 
                    print df_verbose.to_string(formatters={'label':'{:,.0f}'.format, 'label_volume':'{:,.0f}'.format, 'image_volume':'{:,.0f}'.format,
                                                           'time_index':'{:,.0f}'.format, 
                                                           'x_com':'{:,.1f}'.format,'y_com':'{:,.1f}'.format,'z_com':'{:,.1f}'.format})
                    ii_verbose = 0
                else:
                    ii_verbose += 1


            df_stats.loc[len(df_stats)] = stats


    if verbose_flag:

        if verbose_all_flag:
            pd.set_option('display.max_rows',len(df_stats))
            
        print
        print df_stats
        print
            

    return df_stats
        

def extract(extract_labels, in_array):

     out_array = np.zeros( in_array.shape )

     for ii in extract_labels:
          mask = in_array == ii
          out_array[ mask ] = in_array[ mask ]

     return out_array
