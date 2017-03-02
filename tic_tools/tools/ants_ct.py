#!/usr/bin/env python
"""
   Call antsCorticalThickness.sh in stages. This was a misguided attempt to understand antsCorticalThickness.sh.
   Users should just use ants_ct.py instead.
"""

import sys      
import os                                               # system functions
import glob
import shutil
import datetime
import argparse
import json

import _qa_utilities as qa
import _utilities as util
import labels
import json_utils

from collections import OrderedDict
import getpass
import pandas

QA_CHOICES=['input', 'results', 'methods', 'segment', 'thickness', 'extract', 'normalize']

def qa_methods_extract(output_files):
     qa_display(output_files, 'extract')

def qa_methods_segment(ants_ct_info):

     output_segment_files   = [[ ants_ct_info['input']['t1'],':visible=1:colormap=grayscale'],
                               [ ants_ct_info['segment']['p_csf'], ':visible=0:colormap=heat:heatscale=0.1,0.5,1:opacity=0.5'],
                               [ ants_ct_info['segment']['p_gm_cortical'],':visible=0:colormap=heat:heatscale=0.1,0.5,1:opacity=0.5'],
                               [ ants_ct_info['segment']['p_wm'], ':visible=0:colormap=jet:colorscale=0.2,0.1:opacity=0.5'],
                               [ ants_ct_info['segment']['segment'], ':visible=1:colormap=lut:colorscale=0,6:opacity=0.75:lut='+ 
                                 brain_segmentation_lut]
                               ]

     qa_display(output_segment_files, 'segment')



def qa_methods_thickness(output_files):
     qa_display(output_files, 'thickness')

def qa_methods_normalize(output_files):
     qa_display(output_files, 'normalize')

def qa_results(output_files, ants_ct_info, verbose=True):

     if verbose:
         json_utils.print_json_redcap_instrument(ants_ct_info['results']['json'])
     
     qa_display(output_files, 'results')



def qa_display(output_files, method):

     if qa.qa_exist(output_files, False):
          qa.freeview( output_files, True, inArgs.verbose )
          
     else:
          print('Unable to QA ' + method + ' ants_ct.py')
          qa.qa_exist( output_files, True )
          print('\n')
          
          
brain_segmentation_files = ( 'BrainSegmentation0N4.nii.gz',
                       'BrainSegmentationConvergence.txt',
                       'BrainSegmentation.nii.gz',
                       'BrainSegmentationPosteriors1.nii.gz',
                       'BrainSegmentationPosteriors2.nii.gz',
                       'BrainSegmentationPosteriors3.nii.gz',
                       'BrainSegmentationPosteriors4.nii.gz',
                       'BrainSegmentationPosteriors5.nii.gz',
                       'BrainSegmentationPosteriors6.nii.gz'
                       )

registration_files = ( 'BrainNormalizedToTemplate.nii.gz',
                 'BrainSegmentationTiledMosaic.png',
                 'brainvols.csv',
                 'CorticalThickness.nii.gz',
                 'CorticalThicknessNormalizedToTemplate.nii.gz',
                 'CorticalThicknessTiledMosaic.png',
                 'BrainExtractionBrain.nii.gz',
                 'ExtractedBrain0N4.nii.gz',
                 'ExtractedTemplateBrain.nii.gz',
                 'RegistrationTemplateBrainMask.nii.gz',
                 'SubjectToTemplate0GenericAffine.mat',
                 'SubjectToTemplate1Warp.nii.gz',
                 'SubjectToTemplateLogJacobian.nii.gz',
                 'TemplateToSubject0Warp.nii.gz',
                 'TemplateToSubject1GenericAffine.mat'
                 )

def get_info(input_dir, subject_id=None, methods_dir='../methods', results_dir='../results',
             t1=None, t2=None, flair=None, verbose=False):


    base = OrderedDict(( ('subject_id', subject_id),
                         ('input', input_dir),
                         ('methods', util.path_relative_to(input_dir, methods_dir)),
                         ('results', util.path_relative_to(input_dir, results_dir))
                        ))



    t1 =  util.path_relative_to(input_dir, t1) if t1 else None
    t2 =  util.path_relative_to(input_dir, t2) if t2 else None
    flair =  util.path_relative_to(input_dir, flair) if flair else None

    input_files = OrderedDict(( ('t1', os.path.abspath(t1) if t1 else None),
                                ('t2', os.path.abspath(t2) if t2 else None),
                                ('flair',  os.path.abspath(flair) if flair else None)
                               ))


    extract_files = {'mask':os.path.join(base['methods'],'BrainExtractionMask.nii.gz')}

    segment_files = OrderedDict(( ('n4', os.path.join(base['methods'],'BrainSegmentation0N4.nii.gz')),
                                 ('convergence',os.path.join(base['methods'],'BrainSegmentationConvergence.txt')),
                                 ('segment',os.path.join(base['methods'],'BrainSegmentation.nii.gz')),
                                 ('p_csf',os.path.join(base['methods'],'BrainSegmentationPosteriors1.nii.gz')),
                                 ('p_gm_cortical',os.path.join(base['methods'],'BrainSegmentationPosteriors2.nii.gz')),
                                 ('p_wm',os.path.join(base['methods'],'BrainSegmentationPosteriors3.nii.gz')),
                                 ('p_gm_subcortical',os.path.join(base['methods'],'BrainSegmentationPosteriors4.nii.gz')),
                                 ('p_brainstem',os.path.join(base['methods'],'BrainSegmentationPosteriors5.nii.gz')),
                                 ('p_cerebellum',os.path.join(base['methods'],'BrainSegmentationPosteriors6.nii.gz'))
                               ))

    register_files = OrderedDict(( ('brain_to_template',os.path.join(base['methods'],'BrainNormalizedToTemplate.nii.gz')),
                                 ('brainseg_mosaic',os.path.join(base['methods'],'BrainSegmentationTiledMosaic.png')),
                                 ('brainvols',os.path.join(base['methods'],'brainvols.csv')),
                                 ('ct',os.path.join(base['methods'],'CorticalThickness.nii.gz')),
                                 ('ct_to_template',os.path.join(base['methods'],'CorticalThicknessNormalizedToTemplate.nii.gz')),
                                 ('ct_mosaic',os.path.join(base['methods'],'CorticalThicknessTiledMosaic.png')),
                                 ('extracted_brain_n4',os.path.join(base['methods'],'ExtractedBrain0N4.nii.gz',)),
                                 ('template_brain_mask',os.path.join(base['methods'],'RegistrationTemplateBrainMask.nii.gz',)),
                                 ('subject_to_template_affine',os.path.join(base['methods'],'SubjectToTemplate0GenericAffine.mat',)),
                                 ('subject_to_template_warp',os.path.join(base['methods'],'SubjectToTemplate1Warp.nii.gz',)),
                                 ('subject_to_template_jacobian',os.path.join(base['methods'],'SubjectToTemplateLogJacobian.nii.gz',)),
                                 ('template_to_subject_warp',os.path.join(base['methods'],'TemplateToSubject0Warp.nii.gz',)),
                                 ('template_to_subject_affine',os.path.join(base['methods'],'TemplateToSubject1GenericAffine.mat'))
                                 ))

    results_files = OrderedDict(( ('json', os.path.join(base['results'], 'ants_ct.json')),
                                  ('segment', os.path.join(base['results'], 'BrainSegmentation.nii.gz')),
                                  ('ct',os.path.join(base['results'],'CorticalThickness.nii.gz')),
                                  ('p_gm', os.path.join(base['results'], 'gm_posterior.nii.gz')),
                                  ('p_wm', os.path.join(base['results'], 'wm_posterior.nii.gz')),
                                  ('subject_to_template_affine',os.path.join(base['results'],'SubjectToTemplate0GenericAffine.mat',)),
                                  ('subject_to_template_warp',os.path.join(base['results'],'SubjectToTemplate1Warp.nii.gz',)),
                                  ('subject_to_template_jacobian',os.path.join(base['results'],'SubjectToTemplateLogJacobian.nii.gz',)),
                                  ('template_to_subject_warp',os.path.join(base['results'],'TemplateToSubject0Warp.nii.gz',)),
                                  ('template_to_subject_affine',os.path.join(base['results'],'TemplateToSubject1GenericAffine.mat'))
                                  ))

    ants_ct_info = {'base': base, 'input': input_files, 'extract': extract_files,
            'segment':segment_files, 'register':register_files, 'results':results_files}

    return ants_ct_info

#endregion

def status_methods( ants_ct_info, verbose=False, debug=False ):

     register_files =  [ value for key, value in ants_ct_info['register'].items() ]
        
     ants_ct_status = util.check_files(register_files,debug)

     if verbose:
          print( ants_ct_info['base']['input'] + ', ants_ct, ' + 'methods' + ', ' + str(ants_ct_status) )

     return ants_ct_status


def status_results( ants_ct_info, verbose=False, debug=False ):

     result_files =  [ value for key, value in ants_ct_info['results'].items() ]
        
     ants_ct_status = util.check_files(result_files, debug)

     if verbose:
          print( ants_ct_info['base']['input'] + ', ants_ct, ' + 'results' + ', ' + str(ants_ct_status) )

     return ants_ct_status



def ants_ct_status( out_directory, out_prefix):

     check_files =  [os.path.abspath( os.path.join(out_directory, out_prefix + f)) for f in brain_segmentation_files ]
     check_files += [os.path.abspath( os.path.join(out_directory, out_prefix + f)) for f in registration_files ]

     ants_ct_status = False

     for ii in check_files:
          if os.path.isfile(ii): 
               return True

     return ants_ct_status



def clean( out_dir ):

     os.chdir(out_dir)

     for ii in registration_files + brain_segmentation_files:
          delete_files = glob.glob('*' + ii )     # Delete files regardless of prefix

          for jj in delete_files:
               os.remove( jj )

def archive( out_dir, in_archive_dir='archive' ):
                   
     archive_dir = util.path_relative_to(out_dir,in_archive_dir)
     files_to_move = os.listdir(out_dir)

     if os.path.isdir(archive_dir):
          print('\nArchive directory already exists. Only one archive directory per output directory is allowed\n')
          exit()
     else:
          os.mkdir(archive_dir)

     for item_path in files_to_move: 
          shutil.move(os.path.join(out_dir, item_path) , os.path.join(archive_dir, item_path))



def results(ants_ct_info, verbose=False):

     # Create results directory and populate

     util.mkcd_dir( [ ants_ct_info['base']['results'] ], True )

     files_to_link = [ ( ants_ct_info['segment']['p_wm'], ants_ct_info['results']['p_wm']),
                       ( ants_ct_info['segment']['segment'], ants_ct_info['results']['segment']),
                       ( ants_ct_info['register']['ct'], ants_ct_info['results']['ct']), 
                       ( ants_ct_info['register']['subject_to_template_affine'], ants_ct_info['results']['subject_to_template_affine']),
                       ( ants_ct_info['register']['subject_to_template_warp'], ants_ct_info['results']['subject_to_template_warp']),
                       ( ants_ct_info['register']['subject_to_template_jacobian'], ants_ct_info['results']['subject_to_template_jacobian']),
                       ( ants_ct_info['register']['template_to_subject_affine'], ants_ct_info['results']['template_to_subject_affine']),
                       ( ants_ct_info['register']['template_to_subject_warp'], ants_ct_info['results']['template_to_subject_warp'])
                       ]

     for ii in files_to_link:
          util.force_hard_link( ii[0],ii[1])

     fsl_command = ['fslmaths', ants_ct_info['segment']['p_gm_cortical'], '-add',  ants_ct_info['segment']['p_gm_subcortical'],
                    ants_ct_info['results']['p_gm']]

     util.iw_subprocess(fsl_command)

     methods_write_json_redcap_ants_ct_instrument(ants_ct_info, verbose)
     

def methods_write_json_redcap_ants_ct_instrument(ants_ct_info, verbose):
    """ Write ANTs CT Instrument to JSON output file"""

    df_stats = labels.properties(ants_ct_info['segment']['segment'])

    dict_redcap = OrderedDict((('subject_id', ants_ct_info['base']['subject_id']),
                               ('ants_ct_analyst', getpass.getuser()),
                               ('ants_ct_datetime', '{:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now())),
                               ('ants_ct_csf_volume_mm3', '{0:4.3f}'.format(df_stats.iloc[0]['volume_mm3'])),
                               ('ants_ct_gm_cortical_volume_mm3', '{0:4.3f}'.format(df_stats.iloc[1]['volume_mm3'])),
                               ('ants_ct_wm_volume_mm3', '{0:4.3f}'.format(df_stats.iloc[2]['volume_mm3'])),
                               ('ants_ct_gm_subcortical_volume_mm3','{0:4.3f}'.format(df_stats.iloc[3]['volume_mm3'])),
                               ('ants_ct_brainstem_volume_mm3','{0:4.3f}'.format(df_stats.iloc[4]['volume_mm3'])),
                               ('ants_ct_cerebellum_volume_mm3', '{0:4.3f}'.format(df_stats.iloc[5]['volume_mm3']))
                               )
                              )

    with open( ants_ct_info['results']['json'], 'w') as outfile:
        json.dump(dict_redcap, outfile, indent=4, ensure_ascii=True, sort_keys=False)

    if verbose:
        print(json.dumps(dict_redcap, indent=4, ensure_ascii=True, sort_keys=False))

    return

def methods( t1full, t2full, t2flair, options, verbose=False, debug=False, nohup=False):

     print('\nRunnning ants_ct.py\n')
          
     if  qa.qa_input_files( input_files, False):
          
          if not os.path.exists( out_directory ):
               os.makedirs( out_directory )
               
          callCommand = ['antsCorticalThickness.sh', '-d', '3', '-t', options['t_option'], '-w', '0.25',
                         '-e', options['e_option'], '-m', options['m_option'], '-f', options['f_option'], '-p', options['p_option'], 
                         '-o', options['o_option'] 
                         ]
               
          callCommand = callCommand + [ '-a', t1full ] 
          
          if not t2full == None:
               callCommand = callCommand + [ '-a', t2full ] 
               
          if not inArgs.t2flair == None:
               callCommand = callCommand + [ '-a', t2flair ] 
               
          util.iw_subprocess( callCommand, verbose, debug,  nohup )
                    
     else:
          print('\nUnable to run iwAntsCT.py. Failed input QA.')
          qa.qa_exist( input_files, True )
          print('\n')



#
# Main Function
#

if __name__ == '__main__':

     ## Parsing Arguments
     #
     #

     usage = 'usage: %prog [options] arg1 arg2'

     parser = argparse.ArgumentParser(prog='ants_ct')
     parser.add_argument('--t1full',          help='Full T1w image (default = t1w.nii.gz )', default = 't1w.nii.gz' )
     parser.add_argument('--t2full',          help='T2 TSE used in QI and QO (default = None )', default = None )
     parser.add_argument('--t2flair',         help='T2 Flair used in QI and QO (default = None )', default = None )

     parser.add_argument('-i', '--indir',           help='Input directory', default = os.getcwd() )
     parser.add_argument('--outdir',          help='Output directory', default = '../methods' )

     parser.add_argument('--outprefix',       help='Output prefix', default = '' )

     parser.add_argument('--mask',            help='Mask to use for antsCorticalThickness.sh.', default = None)

     parser.add_argument('-d','--display',    help='Display Results', action='store_true', default=False )
     parser.add_argument('-t','--template',   help='Template', default='inia19', choices=['inia19', 'ixi'])
     parser.add_argument('-v','--verbose',    help='Verbose flag',      action='store_true', default=False )
     parser.add_argument('--debug',           help='Debug flag',      action='store_true', default=False )
     parser.add_argument('--clean',           help=('Clean --outdir by removing files created during'
                                                    'antsCorticalThickness.sh Segmentation and Registration stages. '
                                                    'This will allow you to rerun antsCorticalThickness.sh after you '
                                                    'have edited BrainExtractionMask.nii.gz '),
                         action='store_true', default=False )

     parser.add_argument('--archive',           help=('Archive the files in --outdir by moving them to the subdirectory archive'
                                                    'This will allow you to rerun antsCorticalThickness.sh after you '
                                                    'have edited BrainExtractionMask.nii.gz and compare the results. '),
                         action='store_true', default=False )

     parser.add_argument("--status", help="Status check. choices=[methods,results]", nargs='*',
                        choices=['methods','results'], default=[None])


     parser.add_argument('--methods',         help='Run processing pipeline',      action='store_true', default=False )
     parser.add_argument('--nohup',           help='nohup',           action='store_true', default=False )

     parser.add_argument('--qa', help='QA methods (input, results, methods)', nargs='*', choices=QA_CHOICES, default=[None])

     parser.add_argument('--results',         help='Create JSON file', action='store_true', default=False)
     parser.add_argument('--results_dir',     help='Results directory', default = '../results/' )

     parser.add_argument('--subject_id',      help='Subject ID. Only used for dumping JSON file.  If not defined then '
                                                   'and empyt Subject ID is used.', default='')

     inArgs = parser.parse_args()

     # Change director to input directory

     input_files = [[ inArgs.t1full,':colormap=grayscale']]

     optional_files = [[inArgs.t2flair, ':visible=0:colormap=grayscale']]

     if inArgs.template == 'ixi':
          
          template_dir    =  os.getenv('TEMPLATE_IXI')
          template_prefix = 'ixiTemplate2'

          e_option = template_dir +  template_prefix + '_e_T1wFullImage.nii.gz'
          t_option = template_dir +  template_prefix + '_t_T1wSkullStripped.nii.gz'
          m_option = template_dir +  template_prefix + '_m_BrainCerebellumProbabilityMask.nii.gz'
          f_option = template_dir +  template_prefix + '_f_BrainCerebellumExtractionMask.nii.gz'
          p_option = template_dir + 'priors%d.nii.gz'
          
          p1_option = template_dir + 'priors1.nii.gz'
          p2_option = template_dir + 'priors2.nii.gz'
          p3_option = template_dir + 'priors3.nii.gz'
          p4_option = template_dir + 'priors4.nii.gz'
          p5_option = template_dir + 'priors5.nii.gz'
          p6_option = template_dir + 'priors6.nii.gz'

     elif inArgs.template == 'inia19':

          template_dir    =  os.getenv('TEMPLATE_INIA19')
          template_prefix = 'inia19'

          e_option = os.path.join( template_dir, template_prefix + '_e_T1wFullImage.nii.gz')
          t_option = os.path.join( template_dir, template_prefix + '_t_T1wSkullStripped.nii.gz')
          m_option = os.path.join( template_dir, template_prefix + '_m_BrainProbabilityMask.nii.gz')
          f_option = os.path.join( template_dir, template_prefix + '_f_BrainExtractionMask.nii.gz')
          p_option = os.path.join( template_dir, template_prefix + '_priors0%d.nii.gz')
          
          p1_option = os.path.join( template_dir, template_prefix + '_priors01.nii.gz')
          p2_option = os.path.join( template_dir, template_prefix + '_priors02.nii.gz')
          p3_option = os.path.join( template_dir, template_prefix + '_priors03.nii.gz')
          p4_option = os.path.join( template_dir, template_prefix + '_priors04.nii.gz')
          p5_option = os.path.join( template_dir, template_prefix + '_priors05.nii.gz')
          p6_option = os.path.join( template_dir, template_prefix + '_priors06.nii.gz')
          
     else:
          print('Unknown template')
          quit()




     # Grab info
     ants_ct_info = get_info( os.path.abspath(inArgs.indir), subject_id=inArgs.subject_id, methods_dir=inArgs.outdir,
                             results_dir=inArgs.results_dir, t1=inArgs.t1full, t2=inArgs.t2full, flair=inArgs.t2flair,
                             verbose=inArgs.verbose)

     out_directory = ants_ct_info['base']['methods']

     # 

     brain_segmentation_lut = os.path.abspath( os.path.join( os.path.dirname(os.path.abspath(__file__)), 'AntsCorticalThicknessColorLUT.txt'))


     outFull       = os.path.join(out_directory, inArgs.outprefix)

     output_extract_files =  [[ ants_ct_info['input']['t1'],':visible=1:colormap=grayscale'],
                              [ ants_ct_info['extract']['mask'], ':visible=1:colormap=jet:opacity=0.5']
                              ]


     output_thickness_files =   [[ outFull+'ExtractedBrain0N4.nii.gz',':visible=1:colormap=grayscale'], 
                                 [ outFull+'CorticalThickness.nii.gz',':visible=1:colormap=heat:opacity=0.75']
                                 ]

     output_normalize_files =   [[ t_option,                                    ':visible=0:colormap=grayscale'],
                                 [ outFull+'BrainNormalizedToTemplate.nii.gz',  ':visible=1:colormap=grayscale'],
                                 [ outFull+'CorticalThicknessNormalizedToTemplate.nii.gz', ':visible=1:colormap=heat:opacity=0.75']
                                 ]
     

     output_result_files   = [[ ants_ct_info['input']['t1'],':visible=1:colormap=grayscale'],
                              [ ants_ct_info['results']['p_gm'], ':visible=0:colormap=heat:heatscale=0.1,0.5,1:opacity=0.5'],
                              [ ants_ct_info['results']['p_wm'], ':visible=0:colormap=heat:heatscale=0.1,0.5,1:opacity=0.5'],
                              [ ants_ct_info['results']['ct'],':visible=0:colormap=heat:opacity=0.75'],        
                              [ ants_ct_info['results']['segment'], ':visible=1:colormap=lut:colorscale=0,6:opacity=0.75:lut='+ 
                                brain_segmentation_lut],                             
                               ]



     input_files = [[ inArgs.t1full,':visible=1:colormap=grayscale'],
                    [ inArgs.t2full,':visible=1:colormap=jet:opacity=0.5'],
                    [ e_option, ':visible=0:colormap=grayscale'],
                    [ t_option, ':visible=0:colormap=grayscale'],
                    [ m_option, ':visible=0:colormap=grayscale'],
                    [ f_option, ':visible=0:colormap=grayscale'],
                    [ p1_option, ':visible=0:colormap=jet'],
                    [ p2_option, ':visible=0:colormap=jet'],
                    [ p3_option, ':visible=0:colormap=jet'],
                    [ p4_option, ':visible=0:colormap=jet'],
                    [ p5_option, ':visible=0:colormap=jet'],
                    [ p6_option, ':visible=0:colormap=jet']]
     

     options = { 'e_option': e_option, 't_option':t_option, 'm_option':m_option, 'f_option':f_option,
                 'p_option': p_option, 'p_options':[p1_option, p2_option, p3_option, p4_option, p5_option, p6_option],
                 'o_option': inArgs.outdir + '/' + inArgs.outprefix }


     # QA inputs
     #
         
     if 'input' in inArgs.qa:
          qa.qa_input_files( input_files, True, False )
          qa.freeview( input_files[:2], True, inArgs.verbose )
          qa.freeview( input_files[2:], True, inArgs.verbose )
          
     # Archive/Clean Directory

     if inArgs.archive:
          archive( out_directory, 'archive')

     if inArgs.clean:
          clean( out_directory )


     # Replace Mask

     if inArgs.mask is not None:
          
          if not os.path.exists(out_directory):
               os.makedirs(out_directory)
          else:
               if ants_ct_status( out_directory, inArgs.outprefix):
                    print('\nThe output directory should be cleaned before proceeding \n'
                          'or a new output directory should be set. \n')
                    exit()               
               
          shutil.copy2( util.path_relative_to(ants_ct_info['base']['input'], inArgs.mask ), ants_ct_info['extract']['mask'] ) 

               
               
     # Methods
     # 
   
     if  inArgs.methods or inArgs.nohup:
          methods(inArgs.t1full, inArgs.t2full, inArgs.t2flair, options, inArgs.verbose, inArgs.debug, inArgs.nohup)

     if 'extract' in inArgs.qa or 'methods' in inArgs.qa:
          qa_methods_extract(output_extract_files)

     if 'segment' in inArgs.qa or 'methods' in inArgs.qa:
          qa_methods_segment(ants_ct_info)

     if 'thickness' in inArgs.qa or 'methods' in inArgs.qa:
          qa_methods_normalize(output_thickness_files)

     if 'normalize' in inArgs.qa or 'methods' in inArgs.qa:
          qa_methods_normalize(output_normalize_files)

     # Results
     #

     if inArgs.results:
          results(ants_ct_info, inArgs.verbose)

     # Status

     if 'methods' in inArgs.status  or 'all' in inArgs.status:
          status_methods(ants_ct_info, True, inArgs.debug)

     if 'results' in inArgs.status  or 'all' in inArgs.status:
          status_results(ants_ct_info, True, inArgs.debug)

     # QA Results
     #

     if 'results' in inArgs.qa:
          qa_results(output_result_files, ants_ct_info, inArgs.verbose)

