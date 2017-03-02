#!/usr/bin/env python

"""

"""
import os
import sys      
import numpy as np
import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

import _utilities as util

def remove_values_from_list(in_list, val=0):
    out_list = [value for value in in_list if value != val]
    return out_list


def read_nifti_file( nii_filename, error_message ):

    if os.path.isfile(nii_filename):
        try:
            nii = nb.load( nii_filename )
        except IOError:
            sys.exit("Unable to read NIFTI file")
    else:
        sys.exit(error_message)

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

    all_labels = np.unique(label_array[ label_array > 0 ])

    if requested_labels is None or len(requested_labels) == 0:  # In this case None means All labels present
        labels = all_labels
    else:
        labels = list( set(requested_labels) & set(all_labels))
    
    if include_background:
        labels = [ 0 ]  + labels
    else:
        labels = remove_values_from_list(labels, 0)
    

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


def calc_affine(in_rotate, in_translate, in_origin):

     affine_ctf          = np.zeros((4,4))
     affine_ctf[3,3]     = 1 
     affine_ctf[0:3,0:3] = in_rotate
     affine_ctf[0:3,3]   = in_translate

     # Calculate the Native to CTF matrix is based upon the fiducials.  antsApplyTransformToPoints use the inverse transforms of 
     # that used by antsApplyTransform.  For this reason, take the inverse so things are consistently inconsistent.

     affine_inverse_ctf = np.linalg.inv(affine_ctf)

     return affine_inverse_ctf


def calc_rotate_translate_origin( in_nas,  in_lpa, in_rpa, in_scale=1 ):

    nas = np.array( [ in_nas[0], in_nas[1], in_nas[2] ] )
    rpa = np.array( [ in_rpa[0], in_rpa[1], in_rpa[2] ] )
    lpa = np.array( [ in_lpa[0], in_lpa[1], in_lpa[2] ] )

    origin_ctf = 0.5 * (lpa+rpa)

    x_ctf = norm( nas - origin_ctf)
    z_ctf = norm( np.cross( x_ctf, lpa-rpa))
    y_ctf = norm( np.cross( z_ctf, x_ctf))
    
    meg_to_mri    = np.matrix( [ [ 0,1,0],[-1, 0,0], [0,0,1] ])
    
    rotate_ctf    = in_scale * np.dot( meg_to_mri, np.matrix( [x_ctf, y_ctf, z_ctf ]).getT().getI())
    translate_ctf = -np.dot(rotate_ctf, origin_ctf)
    

    return [rotate_ctf, translate_ctf, origin_ctf ]


def norm(x):

     x_norm = np.linalg.norm(x)

     if not x_norm == 0:
          return x/x_norm
     else:
          print("Error: norm of vector is 0")
          quit()


def scale_points( in_points, scale, verbose_flag=False):
     
     out_points    = in_points
     
     for ii in [ 0,1,2]:
          out_points[ out_points.columns[ii] ] = scale*in_points[ in_points.columns[ii] ]


     if verbose_flag:
          print('\n')
          print( out_points)
          print('\n')

     return out_points


def round_points( in_points, verbose_flag=False):
     
     out_points    = in_points
     
     for ii in [ 0,1,2]:
          out_points[ out_points.columns[ii] ] = np.round( in_points[ in_points.columns[ii] ] )


     if verbose_flag:
          print('\n')
          print( out_points)
          print('\n')

     return out_points
     

def write_points( in_filename, in_pdframe, verbose_flag=False):
     print_points( in_filename, in_pdframe, verbose_flag)
     in_pdframe.to_csv(in_filename, index=False, float_format='%.3f')



def print_points_from_file(  in_filename, verbose_flag=False):

     df_points = pd.read_csv(in_filename)
     print_points(  in_filename, df_points, verbose_flag)

     return df_points
               
def print_points( in_filename, in_pdframe, verbose_flag=False):

     if verbose_flag:
         print('\n') 
         print( in_filename )
         print( '----------------------------------------' )
         print( in_pdframe )
         print('\n')



def icsa_to_wlps(in_filename, out_filename, transform, verbose_flag=False, debug_flag=False):

     _out1 = '00_iras_to_wlps__iras.csv'
     _out2 = '00_iras_to_wlps__wras.csv'

     if debug_flag:
          print( "!!! Entering icsa_to_wlps" )
          print( in_filename )
          print( transform )
          print( _out1 )
          print( _out1 )
          print( out_filename )
          print('\n')

     icsa_to_iras(in_filename, _out1, verbose_flag, debug_flag)
     iras_to_wlps(_out1, out_filename, transform, verbose_flag, debug_flag)
#     wras_to_wlps(_out2, out_filename, verbose_flag, debug_flag)

     if not debug_flag:
          for ii in [ _out1 ]:
               os.remove(ii)


def wlps_to_icsa(in_filename, out_filename, transform, verbose_flag=False, debug_flag=False):

     _out1 = '00_wlps_to_icsa__wiras.csv'

     if debug_flag:
          print( "!!! Entering wlps_to_icsa" )
          print( in_filename )
          print( transform )
          print( _out1 )
          print( out_filename )
          print('\n')

     wlps_to_iras(in_filename, _out1, transform, verbose_flag, debug_flag)
     iras_to_icsa(_out1, out_filename, verbose_flag)

     if not debug_flag:
          for ii in [ _out1 ]:
               os.remove(ii)



def icsa_to_iras(in_filename, out_filename, verbose_flag=False, debug_flag=False):
     
     if debug_flag:
          print( "!!! Entering icsa_to_iras" )
          print( in_filename)
          print( out_filename)
          print('\n')

     in_points = pd.read_csv(in_filename, names=['c','s','a','t','label', 'comment'], skiprows=[0])
     
     print_points( in_filename, in_points, verbose_flag)

     out_points = in_points.copy()
     out_points.columns = ['r','a','s','t','label','comment']

     out_points['r'] = 255-in_points['s']
     out_points['a'] = 255-in_points['c']
     out_points['s'] = 255-in_points['a']

     write_points( out_filename, out_points, verbose_flag)

     return out_points



def iras_to_icsa(in_filename, out_filename, verbose_flag=False):
     
     in_points = pd.read_csv(in_filename, names=['r','a','s','t','label', 'comment'], skiprows=[0])
     
     print_points( in_filename, in_points, verbose_flag)

     out_points = in_points.copy()
     out_points.columns = ['c','s','a','t','label','comment']

     out_points['s'] = 255-in_points['r']
     out_points['c'] = 255-in_points['a']
     out_points['a'] = 255-in_points['s']

     write_points( out_filename, out_points, verbose_flag)

     return out_points


def meg_to_mri(in_filename, out_filename, verbose_flag=False):
     
     in_points = pd.read_csv(in_filename, names=['x','y','z','t','label', 'comment'], skiprows=[0])
     
     print_points( in_filename, in_points, verbose_flag)

     out_points = in_points.copy()
     out_points.columns = ['l','p','s','t','label','comment']

     scale = 10 # cm to mm

     out_points['l'] = in_points['y'].apply(lambda x:  scale*x)
     out_points['p'] = in_points['x'].apply(lambda x: -scale*x)
     out_points['s'] = in_points['z'].apply(lambda x:  scale*x)

     write_points( out_filename, out_points, verbose_flag)

     return out_points

def mri_to_meg(in_filename, out_filename, verbose_flag=False):
     
     in_points = pd.read_csv(in_filename, names=['l','p','s','t','label', 'comment'], skiprows=[0])
     
     print_points( in_filename, in_points, verbose_flag)

     out_points = in_points.copy()
     out_points.columns = ['x','y','z','t','label','comment']

     scalar = 0.10 # mm to cm

     out_points['y'] = in_points['l'].apply(lambda x:  scalar*x)
     out_points['x'] = in_points['p'].apply(lambda x: -scalar*x)
     out_points['z'] = in_points['s'].apply(lambda x:  scalar*x)

     write_points( out_filename, out_points, verbose_flag)

     return out_points


def wlps_to_wctf(in_filename, out_filename, transform, verbose_flag=False, debug_flag=False):

     apply_affine_transform(in_filename, out_filename, transform, True, verbose_flag )


def wctf_to_wlps(in_filename, out_filename, transform, verbose_flag=False, debug_flag=False):

     apply_affine_transform(in_filename, out_filename, transform, False, verbose_flag )



def iras_to_wlps(in_filename, out_filename, transform, verbose_flag=False, debug_flag=False):

     apply_affine_transform(in_filename, out_filename, transform, False, verbose_flag )


def wlps_to_iras(in_filename, out_filename, transform, verbose_flag=False, debug_flag=False):

     print_points_from_file(in_filename, verbose_flag)
     _pd1 = apply_affine_transform(in_filename, out_filename, transform, True, False )
     write_points(out_filename, round_points(_pd1), verbose_flag)



def apply_affine_transform(in_filename, out_filename, transform, inverse_flag = False, verbose_flag=False):
 
     if isinstance(transform, basestring):
          transform = [transform]

     in_points = pd.read_csv(in_filename, names=['x','y','z','t','label', 'comment'], skiprows=[0])
     
     print_points( in_filename, in_points, verbose_flag)

     cmd1 =[ 'antsApplyTransformsToPoints', '-d', '3', '-i', in_filename,  '-o', out_filename ]

     if inverse_flag:
          cmd2 = [ "-t", "[" ] +  transform  + [ ",", "1", "]" ]
     else:
          cmd2 =  [ "-t"] + transform

     util.iw_subprocess( cmd1 + cmd2 ,  False, False)
     
     out_points = pd.read_csv(out_filename, names=['x','y','z','t','label', 'comment'], skiprows=[0])
     out_points['label'] = in_points['label']
     out_points['comment'] = in_points['comment']

     write_points(out_filename, out_points, verbose_flag)

     return out_points


#
#
#

def sort_fiducials(in_fiducials):

     return out_fiducials



def check_fiducials(df_fiducials):

     lpa = np.asarray(df_fiducials.values[0,0:3])
     nas = np.asarray(df_fiducials.values[1,0:3])
     rpa = np.asarray(df_fiducials.values[2,0:3])
                    
     if not ( (lpa[0] > nas[0]) and (nas[0] > rpa[0])  ):
          print('\n')
          print( 'Fiducials must be listed left to right in OUT fiducial file')
          print('\n')
          print( df_fiducials.values )
          print('\n')
          sys.exit()
                         
     return [ lpa, nas, rpa ]


def calc_matrix( in_fiducials, out_matrix, ctf_scale=1, verbose_flag=False):

     df_fiducials = pd.read_csv( in_fiducials, sep=',',header=0)

     if verbose_flag:
          print_points( in_fiducials, df_fiducials, verbose_flag)

     [ lpa, nas, rpa ] = check_fiducials( df_fiducials ) 
                    
     [ rotate_ctf, translate_ctf, origin_ctf ] = calc_rotate_translate_origin( nas, lpa, rpa, ctf_scale)

     print(rotate_ctf)
     
     affine_wlps_to_wctf = calc_affine( rotate_ctf, translate_ctf, 0*origin_ctf)
     
     util.write_itk_affine_matrix( affine_wlps_to_wctf, [0,0,0], out_matrix, verbose_flag )

     return affine_wlps_to_wctf




def transform_points(in_filename, out_filename, in_transforms, scale, verbose_flag, debug_flag):

     if type(in_filename) is list:
          filename = in_filename
     else:
          filename = [ in_filename ]

     if type(in_transforms) is list:
          transforms = in_transforms
     else:
          transforms = [ in_transforms ]

     input_files = filename + transforms 

     if debug_flag:
          print('\n')
          print('!!! ctf.transform_points ')
          print(input_files)
          print('\n')

     util.verify_inputs( filename )

     in_points = print_points_from_file(in_filename, verbose_flag)

     cmd = [ "antsApplyTransformsToPoints", "-d", "3", "-i", in_filename, "-o", out_filename , "-t"] + transforms

     util.iw_subprocess(cmd, debug_flag, debug_flag)

     # Perform scaling

     out_points = pd.read_csv(out_filename, sep=',',header=0)
     out_points = scale_points( out_points, scale, debug_flag )
     
     # Fix Comment Column
     out_points['label'] = in_points['label']
     out_points['comment'] = in_points['comment']

     #
     write_points( out_filename, out_points, verbose_flag)


def transform_image(in_filename, out_filename, reference_filename, in_transforms, interpolation_method, verbose_flag, debug_flag):

     if type(in_filename) is list:
          filename = in_filename
     else:
          filename = [ in_filename ]

     if type(in_transforms) is list:
          transforms = in_transforms
     else:
          transforms = [ in_transforms ]

     input_files = filename + reference_filename + transforms 

     if debug_flag:
          print('\n')
          print( '!!! ctf.transform_image ')
          print(input_files)
          print('\n')

     util.verify_inputs( filename )


     cmd = [ "antsApplyTransforms", "-d", "3", "-i", in_filename[0], "-o", out_filename[0], "-r", reference_filename[0], 
             "-n", interpolation_method,"-t"] + transforms

     util.iw_subprocess(cmd, debug_flag, debug_flag)


def extract_affine(in_image, out_affine_filename, lps_flag=False, verbose_flag=False):

     img           = nb.load(in_image)
     header        = img.get_header()

     # Save transform

     affine_wras_to_wlps = util.wras_to_wlps_matrix();
     affine_iras_to_wras = np.asarray(img.get_affine())

     if lps_flag:
          out_affine = np.dot(affine_wras_to_wlps, affine_iras_to_wras)
     else:
          out_affine = affine_iras_to_wras
          
     util.write_itk_affine_matrix(out_affine, [0,0,0], out_affine_filename, verbose_flag )

