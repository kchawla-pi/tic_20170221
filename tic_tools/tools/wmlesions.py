#!/usr/bin/env python

"""

"""
import stat
import sys      
import os                                               # system functions
import re
import glob
import shutil
import labels 
import numpy
import pandas
import json

import argparse
import _utilities as util
import gzip
import cenc 
import subprocess

import datetime
from collections import OrderedDict
import getpass


#=======================================================================================================================
# Prepare

def prepare( input_dir ):

     cenc_dirs = cenc.directories( input_dir)

     wm_lesions_dir       = cenc_dirs['wmlesions']['dirs']['root']
     wm_lesions_input_dir = cenc_dirs['wmlesions']['dirs']['input']
     wm_lesions_lpa_dir   = cenc_dirs['wmlesions']['dirs']['lpa']

     # Create Input Directory if it doesn't exist and link files 

     files = [  os.path.abspath( os.path.join( cenc_dirs['results']['dirs']['images'], 'nu.nii.gz')), 
                os.path.abspath( os.path.join( cenc_dirs['results']['dirs']['labels'], 'mask.nii.gz')), 
                os.path.abspath( os.path.join( cenc_dirs['cenc']['reorient'], 't2flair.nii.gz'))
                ]

     util.mkcd_dir( os.path.join(  wm_lesions_input_dir ) )
     util.link_inputs( files, wm_lesions_input_dir )

#=======================================================================================================================
# Methods

def ants_register(input_file):

     # antsRegistration call:
     #--------------------------------------------------------------------------------------
     if False:

          # I am having problems callling the interface.  Same problem of bad interface.

          command = ['antsRegistration', '--dimensionality', 3, '--float', 0, 
                     '--output', '[', 'mt_Affine_nu__' + input_file +'_,', 
                     'mt_Affine_nu__' + input_file + '_Warped.nii.gz,', 
                     'mt_Affine_nu__' + input_file + '_InverseWarped.nii.gz', ']', 
                     '--interpolation', 'Linear', 
                     '--use-histogram-matching', 0,
                     '--winsorize-image-intensities', [0.005,0.995],
                     '--initial-moving-transform', '[', 'nu.nii.gz,' + input_file + '.nii.gz,', 1, ']',
                     '--transform', 'Rigid[0.1]',
                     '--metric', 'MI[nu.nii.gz,mt_m1.nii.gz,1,32,Regular,0.25]', 
                     '--convergence', '[1000x500x250x0,1e-6,10]',
                     '--shrink-factors', '8x4x2x1',
                     '--smoothing-sigmas', '3x2x1x0vox', 
                     '--transform', 'Affine[0.1]',
                     '--metric', 'MI[nu.nii.gz,' + input_file + '.nii.gz,1,32,Regular,0.25]',
                     '--convergence', '[1000x500x250x0,1e-6,10]', 
                     '--shrink-factors', '8x4x2x1', 
                     '--smoothing-sigmas', '3x2x1x0vox'
                     ]
     #--------------------------------------------------------------------------------------

      # I am having problems callling the interface.  Same problem of bad interface.
     if False:
          reg = Registration()
          reg.inputs.fixed_image = 'nu.nii.gz'
          reg.inputs.moving_image = input_file + '.nii.gz'
          reg.inputs.output_transform_prefix = "t2flair_Affine_nu__" + input_file + "_"
          reg.inputs.transforms = ['Affine']
          reg.inputs.transform_parameters = [(2.0,), (0.25, 3.0, 0.0)]
          reg.inputs.number_of_iterations = [[1000,500,200,100]]
          reg.inputs.dimension = 3
          reg.inputs.write_composite_transform = False
          reg.inputs.collapse_output_transforms = False
          reg.inputs.initialize_transforms_per_stage = False
          reg.inputs.metric = ['MI']
          reg.inputs.metric_weight = [1]
          reg.inputs.radius_or_number_of_bins = [32]
          reg.inputs.sampling_strategy = ['Random']
          reg.inputs.sampling_percentage = [0.05]
          reg.inputs.convergence_threshold = [1.e-10]
          reg.inputs.convergence_window_size = [10]
          reg.inputs.smoothing_sigmas = [[3,2,1,0]]
          reg.inputs.sigma_units = ['vox']
          reg.inputs.shrink_factors = [[8,4,2,1]]
          reg.inputs.use_estimate_learning_rate_once = [True]
          reg.inputs.use_histogram_matching = [True] # This is the default
          reg.inputs.output_warped_image = 't2flair_Affine_nu__' + input_file + '.nii.gz'
          reg.inputs.terminal_output='stream'
          print reg.cmdline
          # reg.run()


     # This simple command appears to work. 
     command = ['antsRegistrationSyNQuick.sh', '-d', '3', '-m', input_file + '.nii.gz', '-r', 'nu.nii.gz',
                '-f', 'nu.nii.gz', '-t', 'a', '-o', 't2flair_Affine_nu__' + input_file + '_' 
                ]

     util.iw_subprocess( command, True, True, False)


def methods_01_register( input_dir, verbose ):

    cenc_dirs = cenc.directories( input_dir)

    wm_lesions_dir       = cenc_dirs['wmlesions']['dirs']['root']
    wm_lesions_lpa_dir   = cenc_dirs['wmlesions']['dirs']['lpa']

    # Register

    util.mkcd_dir( [ cenc_dirs['wmlesions']['dirs']['register'] ], True)

    files = [  os.path.join( cenc_dirs['wmlesions']['dirs']['input'], 'nu.nii.gz'),
            os.path.join( cenc_dirs['wmlesions']['dirs']['input'], 't2flair.nii.gz'),
            os.path.join( cenc_dirs['results']['dirs']['labels'], 'mask.nii.gz')
            ]

    util.link_inputs( files, cenc_dirs['wmlesions']['dirs']['register'] )

    ants_register('t2flair')


def methods_02_lpa( input_dir, verbose ):

    cenc_dirs = cenc.directories( input_dir)

    wm_lesions_dir       = cenc_dirs['wmlesions']['dirs']['root']
    wm_lesions_lpa_dir   = cenc_dirs['wmlesions']['dirs']['lpa']


    util.mkcd_dir( [ cenc_dirs['wmlesions']['dirs']['lpa'] ], True)

    util.copy_inputs( [ os.path.join( cenc_dirs['wmlesions']['dirs']['register'], 't2flair_Affine_nu__t2flair_Warped.nii.gz') ],
                    cenc_dirs['wmlesions']['dirs']['lpa'] )

    glob_files =  glob.glob('*.gz')

    for ii in glob_files:
      os.system('gunzip ' + ii)
      os.chmod( str.replace(ii, '.gz',''), stat.S_IRUSR | stat.S_IRGRP | stat.S_IWUSR | stat.S_IWGRP)


    # Run Matlab

    command = ['cenc_wmlesions_run.sh', cenc_dirs['wmlesions']['dirs']['lpa'] ]
    util.iw_subprocess( command, verbose, verbose, False)

    os.chdir(cenc_dirs['wmlesions']['dirs']['lpa'])

    for ii in glob.glob('*.nii'):
      os.system('gzip ' + ii)
      os.chmod( str.replace(ii, '.nii','.nii.gz'), stat.S_IRUSR | stat.S_IRGRP | stat.S_IWUSR | stat.S_IWGRP)

def methods_03_stats(input_dir, verbose=False, min_lesion_volume = 10):

    cenc_dirs = cenc.directories(input_dir)

    wm_lesions_dir = cenc_dirs['wmlesions']['dirs']['root']
    wm_lesions_lpa_dir = cenc_dirs['wmlesions']['dirs']['lpa']

    util.mkcd_dir([cenc_dirs['wmlesions']['dirs']['stats']], True)

    wm_lesions_stats_filename =  os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.csv')

    # Create labels file from LPA probability map
    iw_labels_label.create(
      os.path.join(cenc_dirs['wmlesions']['dirs']['lpa'], 'ples_lpa_mt2flair_Affine_nu__t2flair_Warped.nii.gz'),
      os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.nii.gz'))


    # Measure statistics of labels
    iw_labels_stats.measure(os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.nii.gz'),
                          None, False, ['volume_mm3'],
                          wm_lesions_stats_filename,
                          limits_volume_voxels=[min_lesion_volume, numpy.inf],
                          limits_bb_volume_voxels=[0, numpy.inf], limits_fill_factor=[0, 1], sort='volume_mm3',
                          verbose=verbose, verbose_nlines=20)

    # Keep labels greater than 10 mm^3.  Limit is set above
    iw_labels_keep.keep(os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.nii.gz'),
                      [],
                      wm_lesions_stats_filename,
                      os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.nii.gz')
                      )
    #  1)
    #  2) Create a WM Lesions mask
    #  3)

    command = [['fslmaths', os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.nii.gz'),
              '-bin', '-mul', os.path.join(cenc_dirs['wmlesions']['dirs']['lpa'],
                                           'ples_lpa_mt2flair_Affine_nu__t2flair_Warped.nii.gz'),
              '-mas', os.path.join(cenc_dirs['wmlesions']['dirs']['input'], 'mask.nii.gz'),
              os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_pmap.nii.gz')
              ],

             ['fslmaths', os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.nii.gz'),
              '-bin', os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_mask.nii.gz')
              ],

             ['fslmaths',
              os.path.join(cenc_dirs['wmlesions']['dirs']['lpa'], 'mt2flair_Affine_nu__t2flair_Warped.nii.gz'),
              '-mas', os.path.join(cenc_dirs['wmlesions']['dirs']['input'], 'mask.nii.gz'),
              os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_t2flair.nii.gz')
              ]
             ]

    for ii in command:
      util.iw_subprocess(ii, verbose, verbose, False)

    # Write out JSON file with RedCap Instrument
    methods_write_json_redcap_instrument(input_dir, wm_lesions_stats_filename, verbose)




#=======================================================================================================================
# Results

def results( input_dir):

    cenc_dirs = cenc.directories( input_dir)
    util.mkcd_dir( [ cenc_dirs['wmlesions']['dirs']['results'] ], True)

    # Link Files

    link_result_files =   [ [  os.path.join( cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_t2flair.nii.gz'),
                               os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'wmlesions_lpa_t2flair.nii.gz') ],

                               [ os.path.join( cenc_dirs['wmlesions']['dirs']['input'],    'nu.nii.gz'),
                               os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'nu.nii.gz') ],

                               [ os.path.join( cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_pmap.nii.gz'),
                               os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'wmlesions_lpa_pmap.nii.gz')],

                               [ os.path.join( cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions.json'),
                               os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'wmlesions.json')],

                               [os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.nii.gz'),
                               os.path.join(cenc_dirs['wmlesions']['dirs']['results'], 'wmlesions_lpa_labels.nii.gz')],

                               [os.path.join(cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_labels.csv'),
                               os.path.join(cenc_dirs['wmlesions']['dirs']['results'], 'wmlesions_lpa_labels.csv')],

                               [ os.path.join( cenc_dirs['wmlesions']['dirs']['stats'], 'wmlesions_lpa_mask.nii.gz'),
                               os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'wmlesions_lpa_mask.nii.gz')],

                               [ os.path.join( cenc_dirs['wmlesions']['dirs']['results'], 'wmlesions_lpa_pmap.nii.gz'),
                               os.path.join( cenc_dirs['results']['dirs']['images'],  'wmlesions_lpa_pmap.nii.gz')],

                               [ os.path.join( cenc_dirs['wmlesions']['dirs']['results'], 'wmlesions_lpa_mask.nii.gz'),
                               os.path.join( cenc_dirs['results']['dirs']['labels'],  'wmlesions_lpa_mask.nii.gz')],

                               [ os.path.join( cenc_dirs['wmlesions']['dirs']['results'], 'wmlesions_lpa_labels.nii.gz'),
                               os.path.join( cenc_dirs['results']['dirs']['labels'],  'wmlesions_lpa_labels.nii.gz')
                               ]
                               ]

    for ii in link_result_files:
        util.force_hard_link( ii[0], ii[1])



def methods_write_json_redcap_instrument(in_dir, labels_stats_csv, verbose):
    """ Writes out REdCap instrument measures to a JSON file"""
    cenc_dirs = cenc.directories(in_dir)

    df = pandas.read_csv(labels_stats_csv)

    number_of_lesions, _ = df.shape

    if number_of_lesions > 0:
        total_lesion_volume = df['volume_mm3'].sum()
        mean_lesion_volume = df['volume_mm3'].mean()
        std_lesion_volume = df['volume_mm3'].std()
        largest_lesion_volume = df['volume_mm3'].max()
    else:
        total_lesion_volume = 0
        mean_lesion_volume = 0
        std_lesion_volume = 0
        largest_lesion_volume = 0

    dict_redcap = OrderedDict((('subject_id', cenc_dirs['cenc']['id']),
                            ('wm_lesions_analyst', getpass.getuser()),
                            ('wm_lesions_datetime', '{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now())),

                            ('wm_lesions_number', '{0:d}'.format(int(number_of_lesions))),
                            ('wm_lesions_total_volume_mm3', '{0:5.1f}'.format(total_lesion_volume)),
                            ('wm_lesions_mean_volume_mm3', '{0:5.1f}'.format(mean_lesion_volume)),
                            ('wm_lesions_std_volume_mm3', '{0:5.1f}'.format(std_lesion_volume)),
                            ('wm_lesions_largest_lesion_volume_mm3', '{0:5.1f}'.format(largest_lesion_volume))
                            )
                           )

    wmlesions_json_filename = os.path.join(os.path.dirname(labels_stats_csv), 'wmlesions.json')

    with open(wmlesions_json_filename, 'w') as outfile:
        json.dump(dict_redcap, outfile, indent=4, ensure_ascii=True, sort_keys=False)

    if verbose:
        cenc.print_json_redcap_instrument(wmlesions_json_filename)




# =======================================================================================================================
# Status

def status_results(input_dir, verbose=False):
     cenc_dirs = cenc.directories( input_dir)

     result_files =   [ os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'wmlesions_lpa_t2flair.nii.gz'),
                        os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'nu.nii.gz'),
                        os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'wmlesions_lpa_pmap.nii.gz'),
                        os.path.join( cenc_dirs['wmlesions']['dirs']['results'],  'wmlesions_lpa_labels.nii.gz')
                        ]

     wmlesions_status = util.check_files(result_files, False)

     if verbose:
          print( cenc_dirs['cenc']['id'] + ', cenc_wmlesions, results,' + str(wmlesions_status) )

     return wmlesions_status


#=======================================================================================================================
# QA
def qa_results(in_dir, verbose=False):

     cenc_dirs = cenc.directories( in_dir )

     cenc.print_json_redcap_instrument(os.path.join(cenc_dirs['wmlesions']['dirs']['results'], 'wmlesions.json'))

     result_files = [ os.path.join( cenc_dirs['wmlesions']['dirs']['results'],'nu.nii.gz') + ':colormap=grayscale:visible=0',
                      os.path.join( cenc_dirs['wmlesions']['dirs']['results'],'wmlesions_lpa_t2flair.nii.gz') + ':colormap=grayscale',
                      os.path.join( cenc_dirs['wmlesions']['dirs']['results'],'wmlesions_lpa_pmap.nii.gz') +':colormap=jet:visible=0:opacity=0.5', 
                      os.path.join( cenc_dirs['wmlesions']['dirs']['results'],'wmlesions_lpa_labels.nii.gz') + ':colormap=jet:opacity=0.5' 
                      ] 


     qa_command   = ['freeview', '-v' ] + result_files

     if verbose:
          print
          print(' '.join(qa_command))
          print

     DEVNULL = open(os.devnull, 'wb')
     pipe = subprocess.Popen( [ ' '.join(qa_command) ], shell=True,
                              stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)



#=======================================================================================================================
# Main

def main():

    ## Parsing Arguments
    #
    #

    usage = 'usage: %prog [options] arg1 arg2'

    parser = argparse.ArgumentParser(prog='cenc_wmlesions')

    parser.add_argument('--in_dir',   help='Participant directory', default=os.getcwd() )
    parser.add_argument('--prepare',  help='Gather necessary inputs for Freesurfer analysis', action='store_true', default=False )

    parser.add_argument("--methods", help="Methods [all, 01_register, 02_lpa, 03_stats]", nargs='*',
                        choices=['all', '01_register', '02_lpa', '03_stats'],
                        default=[None])

    parser.add_argument('--results',  help='Gather results',  action='store_true', default=False )
    parser.add_argument('--status',   help='Check status',  choices=['all', 'results'], default=None)
    parser.add_argument('--qa',       help='QA',  choices=['results','methods','input'], default=None)
    parser.add_argument("--redcap",   help="Calculate RedCap results",  action="store_true", default=False )

    parser.add_argument('--force',    help='Force operation regardless of status',  action='store_true', default=False )

    parser.add_argument('-v', '--verbose',    help='Verbose',  action='store_true', default=False )

    inArgs = parser.parse_args()

    #
    #
    #

    cenc_dirs = cenc.directories( inArgs.in_dir)

    if inArgs.prepare:
      prepare( inArgs.in_dir )

    if not None in inArgs.methods:

        if '01_register' in inArgs.methods or 'all' in inArgs.methods:
            methods_01_register( inArgs.in_dir, inArgs.verbose )

        if '02_lpa' in inArgs.methods or 'all' in inArgs.methods:
            methods_02_lpa( inArgs.in_dir, inArgs.verbose )

        if '03_stats' in inArgs.methods or 'all' in inArgs.methods:
            methods_03_stats(inArgs.in_dir, inArgs.verbose)

    if inArgs.results:

      if not status_results(inArgs.in_dir) or inArgs.force:
           results( inArgs.in_dir )
      else:
           print( cenc_dirs['cenc']['id'] + ': cenc_wmlesions.py --results has already been run')
           sys.exit()

    if inArgs.qa in ['results']:
      qa_results(inArgs.in_dir)


    if inArgs.status in ['results'] or inArgs.status in ['all']:
      status_results(inArgs.in_dir, True)


     
#
# Main Function
#

if __name__ == '__main__':
    sys.exit(main())
