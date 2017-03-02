#!/usr/bin/env python

"""
create volume brain mask from pial surface and aseg
"""
import shutil

import argparse
import os
from nipype.interfaces.freesurfer import VolumeMask
from nipype.interfaces.freesurfer import MRIConvert
from nipype.interfaces.freesurfer import Surface2VolTransform

import sys
import labels
import _utilities as util

import logging

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

#
#
#
# mri_surf2vol --hemi lh --surf pial --o mask_surf2vol.pial_lh.nii.gz --identity 34P1029 --template ../../mri/brain.mgz --mkmask --fillribbon --fill-projfrac -2 0 0.05
# mri_surf2vol --hemi rh --surf pial --o mask_surf2vol.pial_rh.nii.gz --identity 34P1029 --template ../../mri/brain.mgz --mkmask --fillribbon --fill-projfrac -2 0 0.05
#
# fslmaths mask_surf2vol.pial_rh.nii.gz -add mask_surf2vol.pial_lh.nii.gz -bin pial.nii.gz
#
# tic_labels_remove aseg.nii.gz --out_nii mask.nii.gz --remove 46 47 7 8 42 3 16 15 --bin
#
# fslmaths mask.nii.gz -dilM -ero 1.mask.nii.gz
# fslmaths 1.mask.nii.gz -add pial.nii.gz -bin -fillh -dilM -ero -fillh -ero -dilM 2.mask.nii.gz

def clean(remove_files):
    for ii in remove_files:
        os.remove(ii)


def create_pial_mask(subject_id, subjects_dir, output_filename, output_directory, reference=None, mo_radius=7, 
                     verbose=False, save=False):

    mri_directory = os.path.abspath( os.path.join( subjects_dir, subject_id, 'mri'))

    if False:

        # I attempted to use nipype to call the mri_surf2vol.  This did not work so I had to use the subprocess method.
        surf2vol = Surface2VolTransform()
#    surf2vol.inputs.reg_file = 'register.mat'
 
        surf2vol.inputs.template_file = os.path.abspath(os.path.join(mri_directory,'brain.mgz'))
        surf2vol.inputs.subjects_dir = subjects_dir
        surf2vol.inputs.subject_id = subject_id
        surf2vol.mkmask = True
        surf2vol.projfrac = 0.05
        surf2vol.surf_name = 'pial'
        surf2vol.args = '--fillribbon --fill-projfrac -2 0 0.05'
        
        
        for ii in ['lh', 'rh']:
            surf2vol.inputs.hemi = 'lh'
            surf2vol.transformed_file = os.path.abspath( os.path.join(output_directory, '_cpm_mask_surf2vol.pial_' + ii + '.nii.gz'))

            if verbose:
                surf2vol.cmdline 

    else:

        for ii in ['lh', 'rh']:
            
            ii_output = os.path.abspath( os.path.join(output_directory, '_cpm_mask_surf2vol.pial_' + ii + '.nii.gz'))

            command = ['mri_surf2vol', '--hemi', ii, '--surf', 'pial', 
                       '--o',  ii_output,
                       '--identity', subject_id, 
                       '--template',  os.path.abspath(os.path.join(subjects_dir, subject_id, 'mri','brain.mgz')), 
                       '--mkmask',
                       '--fillribbon',
                       '--fill-projfrac',
                       '-2', '0', '0.05']

            if not os.path.isfile( ii_output):
                util.iw_subprocess(command, verbose_flag=verbose)

            if not os.path.isfile( ii_output):
                print( ii_output + ' does not exist. Exiting!')
                exit()


    # Convert aseg.nii.gz


    aseg_nii_gz = os.path.abspath( os.path.join( output_directory, '_cpm_aseg.nii.gz'))

    if not os.path.isfile(aseg_nii_gz):
        mri_convert = MRIConvert( in_file  = os.path.abspath( os.path.join( mri_directory, 'aseg.mgz')),
                                  out_file = aseg_nii_gz,
                                  out_type = 'niigz'
                                  )
        mri_convert.run()


    # Remove GM Cortex from aseg.nii.gz 

    mask_aseg_without_gm_cortex = os.path.join( output_directory, '_cpm_mask.aseg_without_gm_cortex.nii.gz')

    if not os.path.isfile( mask_aseg_without_gm_cortex):
        labels.remove( aseg_nii_gz, [3, 42], [], mask_aseg_without_gm_cortex, merge=1)

    # 1) Combine masks into a single mask
    # 2) Threshold and invert mask
    # 3) Grab largest component
    # 4) Threshold image to remove negative numbers
    # 5) ImageMath Opening operation with radius 3
    # 6) Threshold image to remove negative numbers
    # 7) ImageMath Closing operation with radius 3
    # 8) Threshold and invert mask.

    if not os.path.isfile( os.path.join( output_directory,'_cpm_01.mask.nii.gz')):
        os.chdir(output_directory)
        
        commands = [ ['fslmaths',  os.path.join( output_directory, '_cpm_mask.aseg_without_gm_cortex.nii.gz'), '-add',
                      os.path.abspath( os.path.join(output_directory, '_cpm_mask_surf2vol.pial_lh.nii.gz')), '-add', 
                      os.path.abspath( os.path.join(output_directory, '_cpm_mask_surf2vol.pial_rh.nii.gz')), 
                      '-bin', '-fillh26',  
                      os.path.abspath( os.path.join(output_directory, '_cpm_01.mask.nii.gz'))
                      ],
                     ['fslmaths', os.path.join( output_directory,'_cpm_01.mask.nii.gz'),'-thr', 0, '-binv',
                      os.path.join( output_directory,'_cpm_02.mask.nii.gz')],
                     ['ImageMath', 3, '_cpm_03.mask.nii.gz', 'GetLargestComponent', '_cpm_02.mask.nii.gz'],
                     ['ImageMath', 3, '_cpm_04.mask.nii.gz', 'MO', '_cpm_03.mask.nii.gz', 7],
                     ['fslmaths', '_cpm_04.mask.nii.gz', '-thr', 0, '-bin',  '_cpm_05.mask.nii.gz'],
                     ['ImageMath', 3, '_cpm_06.mask.nii.gz', 'MC', '_cpm_05.mask.nii.gz', 7],
                     ['fslmaths', '_cpm_06.mask.nii.gz', '-thr', 0, '-binv', '_cpm_07.mask.nii.gz']
                     ]
        
        for ii in commands:
            util.iw_subprocess(ii, verbose_flag=verbose)


    if reference is not None:
        command = ['antsApplyTransforms',
                   '-i', os.path.join( output_directory,'_cpm_07.mask.nii.gz'), 
                   '-r', reference,
                   '-n', 'Multilabel',
                   '-o', os.path.join( output_directory,output_filename), 
                   '-t', 'identity'

                   ]

        util.iw_subprocess(command, verbose_flag=verbose)

    else:
        shutil.copy2(os.path.join( output_directory,'_cpm_07.mask.nii.gz'), os.path.join( output_directory,out_filename))


    if not save:

        remove_files = [ os.path.join( output_directory,'_cpm_01.mask.nii.gz'),
                         os.path.join( output_directory,'_cpm_02.mask.nii.gz'),
                         os.path.join( output_directory,'_cpm_03.mask.nii.gz'),
                         os.path.join( output_directory,'_cpm_04.mask.nii.gz'),
                         os.path.join( output_directory,'_cpm_05.mask.nii.gz'),
                         os.path.join( output_directory,'_cpm_06.mask.nii.gz'),
                         os.path.join( output_directory,'_cpm_07.mask.nii.gz'),
                         os.path.join( output_directory, '_cpm_aseg.nii.gz'),
                         os.path.join( output_directory, '_cpm_mask.aseg_without_gm_cortex.nii.gz'),
                         os.path.abspath( os.path.join(output_directory, '_cpm_mask_surf2vol.pial_lh.nii.gz')),
                         os.path.abspath( os.path.join(output_directory, '_cpm_mask_surf2vol.pial_rh.nii.gz'))
                         ]    

        clean(remove_files)

    return

# ======================================================================================================================
# region Main Function
#

def main():
    ## Parsing Arguments
    #
    #

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='create_pial_mask')

    parser.add_argument("subject_id", help="Subject ID", default=os.getcwd())
    parser.add_argument("--subjects_dir", help="Subject's Directory (default=$SUBJECTS_DIR)",
                        default=os.getenv('SUBJECTS_DIR'))

    parser.add_argument('--out',             help='Output filename', default = 'mask.nii.gz' )
    parser.add_argument('--outdir',          help='Output directory', default = './' )
    parser.add_argument('-r', '--reference', help='Reference file to create mask with same orientation and image dimensions (None)', default = None )

    parser.add_argument('-v', '--verbose', help="Verbose flag", action="store_true", default=False)
    parser.add_argument('--keep', help="Keep intermediate files", action="store_true", default=False)

    inArgs = parser.parse_args()

    output_directory = os.path.abspath(inArgs.outdir)

    reference_with_full_path = os.path.abspath(inArgs.reference)

    util.mkcd_dir( output_directory, cd_flag=False)

    create_pial_mask(inArgs.subject_id, inArgs.subjects_dir, inArgs.out, output_directory, 
                     reference=reference_with_full_path, verbose=inArgs.verbose, save=inArgs.keep)


#endregion

if __name__ == "__main__":
    sys.exit(main())
