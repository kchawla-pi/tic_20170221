#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
=========
fMRI: FSL
=========

A workflow that uses fsl to perform a first level analysis on the nipype
tutorial data set::

    python fmri_fsl.py


First tell python where to find the appropriate functions.
"""

from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range

import argparse
import os                                    # system functions
import pprint
from nipype.algorithms.misc import Gunzip

import nipype.interfaces.io as nio           # Data i/o
import nipype.interfaces.fsl as fsl          # fsl
import nipype.interfaces.utility as util     # utility
import nipype.pipeline.engine as pe          # pypeline engine
import nipype.algorithms.rapidart as ra      # artifact detection
from nipype.interfaces.utility import Function
import matplotlib.pyplot as plt

from nipype import SelectFiles

import subprocess

"""
Preliminaries
-------------

Setup any package specific configuration. The output file format for FSL
routines is being set to compressed NIFTI.
"""

fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

"""
Set up a node to define all inputs required for the preprocessing workflow
"""



# Infosource - a function free node to iterate over the list of subject names
#
# data_dir = '/Users/bkraft/PycharmProjects/tic_cbf/data'
#
# templates = dict(struct='nu_brain.nii.gz',
#                  func='pcasl_raw.nii.gz'
#                  )
#
# selectfiles = Node(SelectFiles(templates), name="selectfiles", base_dir=data_dir)
#



# ======================================================================================================================
# region M0 Processing

def m0_save_png(m0_skullstrip):
    """ Creates a skull stripped M0 PNG image to be inserted in the report"""

    import os
    from nilearn import plotting, image
    import matplotlib.pyplot as plt

    xyz_direction = 'z'
    n_cuts = 15

#    cuts = plotting.find_cut_slices(image.load_img(m0_skullstrip), direction=xyz_direction, n_cuts=n_cuts, spacing='auto')

#    for ii,jj in enumerate(cuts):

    pwi_filter_dirname = os.path.dirname(m0_skullstrip).replace('m0_skullstrip', 'm0_png')
    output_file = os.path.abspath(os.path.join(pwi_filter_dirname, 'm0_skullstrip_test.png')) # '{0}_{1}_{2:03d}'.format('m0_bet_', xyz_direction, ii) + '.png'

    plotting.plot_anat(m0_skullstrip,  cmap=plt.cm.gray, black_bg=True,
                            display_mode=xyz_direction, cut_coords=n_cuts,
                            output_file=output_file, title='Skull Stripped M0')

    return output_file

def cbf_m0_preprocessing_initialize():
    """ 1) Extracts M0 image from raw pCASL data
        2) Extracts brain from M0 image using BET
        3) Creates png image for final CBF report
    """


    m0_preproc = pe.Workflow(name='m0_preproc')
    m0_preproc.base_dir = methods_dir

    m0_inputnode = pe.Node(interface=util.IdentityInterface(fields=['func']), name='m0_inputnode')
    m0_inputnode.inputs.func = pcasl

    m0_fslroi = pe.Node(fsl.ExtractROI(roi_file='m0.nii.gz', t_min=0, t_size=1), name='m0_fslroi')

    m0_skullstrip = pe.Node(fsl.BET(mask=True), name='m0_skullstrip')

    m0_png = pe.Node(name='m0_png', interface=Function(input_names=['m0_skullstrip'],
                                                                    output_names=['m0_png'],
                                                                    function=m0_save_png))

    m0_datasink = pe.Node(nio.DataSink(), name='m0_sinker')
    m0_datasink.inputs.base_directory = results_dir

    m0_outputnode = pe.Node(interface=util.IdentityInterface(fields=['m0', 'm0_brain', 'm0_mask' ]),
                         name='m0_outputnode')

    m0_preproc.connect([ (m0_inputnode, m0_fslroi, [('func','in_file')]),
                         (m0_fslroi, m0_skullstrip, [('roi_file','in_file')]),
                         (m0_skullstrip, m0_png, [['out_file', 'm0_skullstrip']]),

                         # Data Sink
                         (m0_fslroi, m0_datasink, [['roi_file', 'results.@roi_file']]),
                         (m0_skullstrip, m0_datasink, [['mask_file', 'results.@mask']]),
                         (m0_skullstrip, m0_datasink, [['out_file', 'results.@m0']]),
                         (m0_png, m0_datasink, [['m0_png', 'results.@m0_png']]),

                         # Output Node
                         (m0_fslroi, m0_outputnode, [['roi_file', 'm0']]),
                         (m0_skullstrip, m0_outputnode, [['mask_file', 'm0_mask']]),
                         (m0_skullstrip, m0_outputnode, [['out_file', 'm0_brain']]),

                         ])

    return m0_preproc

# print("Inputs:")
# print(m0_preproc.inputs.m0_inputnode)
# print("Outputs:")
# print(m0_preproc.outputs.m0_outputnode)
#endregion

# ======================================================================================================================
# region Control Label Processing
#


def cbf_cl_preprocessing_initialize():
    """ 1) Extracts control/label pairs from raw pCASL data
        2) Motion correction with mcflirt
        3) Control/Label pairwise subtraction
    """


    cl_preproc = pe.Workflow(name='cl_preproc')
    cl_preproc.base_dir = (os.getcwd())

    cl_inputnode = pe.Node(interface = util.IdentityInterface(fields = ['func', 'm0', 'm0_mask']),
                        name = 'cl_inputnode')

    print(cl_inputnode.inputs)

    cl_datasink = pe.Node(nio.DataSink(), name='cl_sinker')
    cl_datasink.inputs.base_directory = results_dir

    # Extract Control Label Pairs
    cl_fslroi = pe.Node(fsl.ExtractROI(roi_file='cl.nii.gz', t_min=1, t_size=-1),name='cl_fslroi')

    # Align Control/Label Pairs to M0 image
    cl_mcflirt = pe.Node(fsl.MCFLIRT(save_mats=True,save_plots=True), name='cl_mcflirt')

    # Mask Control Label Pairs
    cl_mask = pe.Node(fsl.ApplyMask(), name="cl_mask")


    cl_outputnode = pe.Node(interface=util.IdentityInterface(fields=['cl', 'cl_brain', 'cl_mcf', 'cl_mcf_par']),
                         name='cl_outputnode')

    cl_preproc.connect([ (cl_inputnode, cl_fslroi, [('func','in_file')]),
                         (cl_fslroi, cl_mcflirt, [['roi_file', 'in_file']]),
                         (cl_inputnode, cl_mcflirt,[['m0', 'ref_file']]),

                         (cl_mcflirt, cl_mask, [('out_file', 'in_file')]),
                         (cl_inputnode, cl_mask, [('m0_mask', 'mask_file')]),

                         (cl_fslroi, cl_datasink, [['roi_file', 'results.@cl']]),
                         (cl_mcflirt, cl_datasink,[['out_file', 'results.@mcfcl']]),
                         (cl_mask, cl_datasink, [['out_file', 'results.@cl_mask']]),

                         (cl_fslroi, cl_outputnode, [['roi_file', 'cl']]),
                         (cl_mcflirt, cl_outputnode, [['par_file', 'cl_mcf_par']]),
                         (cl_mcflirt, cl_outputnode, [['out_file', 'cl_mcf']]),
                         (cl_mask, cl_outputnode, [['out_file', 'cl_brain']])

                         ])

    return cl_preproc

# print("Inputs:")
# print(cl_preproc.inputs.cl_inputnode)
# print("Outputs:")
# print(cl_preproc.outputs.cl_mcflirt)
# print(cl_preproc.outputs.cl_outputnode)

#endregion

# ======================================================================================================================
# region Outlier Detection
#
# Detects outliers of pwi images (=control-label difference images). Three Z-score measurements are made 1) inside data,
# 2) outside data along the frequency encode direction, 3) outside data along phase encode direction.
#

def cbf_outlier_detection_initialize():
    od_preproc = pe.Workflow(name='od_preproc')
    od_preproc.base_dir=(os.getcwd())

    od_inputnode = pe.Node(interface=util.IdentityInterface(fields=['cl_mcf', 'cl_mcf_par', 'm0_mask']),
                        name='od_inputnode')


    # Artifact Detection with
    od_cl_art = pe.Node(interface=ra.ArtifactDetect(use_differences=[True, False],
                                                 use_norm=True,
                                                 norm_threshold=1,
                                                 zintensity_threshold=3,
                                                 parameter_source='FSL',
                                                 mask_type='file'),
                     name="od_cl_art")


    od_outputnode = pe.Node(interface=util.IdentityInterface(fields=['od_plot', 'od_outliers', 'od_intensity', 'od_statistic']),
                         name='od_outputnode')


    od_preproc.connect([ (od_inputnode, od_cl_art, [('cl_mcf','realigned_files')]),
                         (od_inputnode, od_cl_art, [('cl_mcf_par','realignment_parameters')]),
                         (od_inputnode, od_cl_art, [('m0_mask', 'mask_file')]),

                         (od_cl_art, od_outputnode, [['outlier_files', 'od_outliers']]),
                         (od_cl_art, od_outputnode, [['intensity_files', 'od_intensity']]),
                         (od_cl_art, od_outputnode, [['plot_files', 'od_plot']]),
                         (od_cl_art, od_outputnode, [['statistic_files', 'od_statistic']])

                         ])

    return od_preproc

    # class ArtifactDetectOutputSpec(TraitedSpec):
    #     outlier_files = OutputMultiPath(File(exists=True),
    #                                     desc=("One file for each functional run containing a list of "
    #                                           "0-based indices corresponding to outlier volumes"))
    #     intensity_files = OutputMultiPath(File(exists=True),
    #                                       desc=("One file for each functional run containing the global "
    #                                             "intensity values determined from the brainmask"))
    #     norm_files = OutputMultiPath(File,
    #                                  desc=("One file for each functional run containing the composite "
    #                                        "norm"))
    #     statistic_files = OutputMultiPath(File(exists=True),
    #                                       desc=("One file for each functional run containing information "
    #                                             "about the different types of artifacts and if design info is"
    #                                             " provided then details of stimulus correlated motion and a "
    #                                             "listing or artifacts by event type."))
    #     plot_files = OutputMultiPath(File,
    #                                  desc=("One image file for each functional run containing the "
    #                                        "detected outliers"))
    #     mask_files = OutputMultiPath(File,
    #                                  desc=("One image file for each functional run containing the mask"
    #                                        "used for global signal calculation"))
    #     displacement_files = OutputMultiPath(File,
    #                                          desc=("One image file for each functional run containing the voxel"
    #                                                "displacement timeseries"))
    #

#endregion

# ======================================================================================================================
# region Perfusion Filtering
#


# ======================================================================================================================
# region CBF Calculation
#
# Calculate CBF from subtracted control label pairs using oxford_asl
#

def pwi_to_cbf(pwi_filename, mask_filename, t1w_brain_filename, tis=[1]):
    """ Convert PWI images (=control/label pairwise difference image) to a calibrated CBF image using oxford_asl """

    import subprocess
    import os

    def pwi_save_png(perfusion_filename):
        """ Save perfusion weighted image to PNG for final report"""

        import os
        from nilearn import plotting, image
        import matplotlib.pyplot as plt

        xyz_direction = 'z'
        ncuts = 30
        col = 6
        row = 5
        perfusion_dirname = os.path.dirname(perfusion_filename)

        cuts = plotting.find_cut_slices(image.load_img(perfusion_filename), direction=xyz_direction, n_cuts=ncuts, spacing='auto')

        print()
        print(cuts)
        print()

        cuts = [ cuts[col * i: col * (i + 1)] for i in range(row)]

        print()
        print(cuts)
        print()

        output_file = []

        for ii, jj in enumerate(cuts):

            output_file += [os.path.abspath(os.path.join(perfusion_dirname,
                                                       '_{0}_perfusion.png'.format(ii) ))]

            # print(output_file)

            plotting.plot_anat(perfusion_filename, cmap=plt.cm.hot, black_bg=True,
                               display_mode=xyz_direction, cut_coords=jj,
                               output_file=output_file[ii])

        # http://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python

        # montage_output_file = os.path.abspath(os.path.join(perfusion_dirname, 'perfusion.png' ))
        montage_output_file = output_file[2]

        return montage_output_file

    # Extract directory and substitute current node
    pwi_dirname = os.path.dirname(pwi_filename).replace('pwi_cl_subtract', 'pwi_to_cbf')


    str_tis = [str(x) for x in tis ]

    command = ['oxford_asl', '-i', pwi_filename, '-m', mask_filename,
               '-o', pwi_dirname, '--tis' ] + str_tis

    print()
    print( ' '.join(command))
    print()

    DEVNULL = open(os.devnull, 'wb')
    process = subprocess.Popen(command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    process.wait()

    #  List of output files
    native_dirname = os.path.join(pwi_dirname,'native_space')
    perfusion_filename = os.path.join(native_dirname, 'perfusion.nii.gz')
    arrival_filename = os.path.join(native_dirname, 'arrival.nii.gz')

    perfusion_png_filename = pwi_save_png(perfusion_filename)

    return perfusion_filename, arrival_filename, perfusion_png_filename


def cl_to_pwi(cl_mcf_filename, mask_filename):
    from nipype import logging
    import nibabel
    import numpy
    import os

    pwi_dirname  = os.path.dirname(cl_mcf_filename).replace('cl_preproc', 'pwi_preproc')
    pwi_dirname = pwi_dirname.replace('cl_mcflirt', 'pwi_cl_subtract')

    pwi_filename = os.path.abspath(os.path.join(pwi_dirname, 'pwi.nii.gz'))

    iflogger = logging.getLogger('interface')
    iflogger.info(pwi_filename)

    nii_cl = nibabel.load(cl_mcf_filename)
    cl = nii_cl.get_data()

    nii_mask =  nibabel.load(mask_filename)
    mask = nii_mask.get_data()

    pwi = (cl[:, :, :, 1::2] - cl[:, :, :, 0::2]) * mask[:, :, :, numpy.newaxis]

    nibabel.save(nibabel.Nifti1Image(pwi, None, nii_cl.get_header()), pwi_filename)

    return pwi_filename


def masked_stat(in_array, mask_3d):
        import numpy

        nVolumes = in_array.shape[3]

        mean_array = numpy.zeros([nVolumes])
        std_array  = numpy.zeros([nVolumes])
        min_array  = numpy.zeros([nVolumes])
        max_array  = numpy.zeros([nVolumes])

        data_array = numpy.transpose(in_array, (3,0,1,2))
        print(data_array.shape)
        print(mask_3d.shape)

        for ii in range(0, nVolumes):
            print(ii)
            # Calculate Image stats
            ii_data_array = data_array[ii]

            masked_array = ii_data_array[mask_3d]

            mean_array[ii] = numpy.mean(masked_array)
            std_array[ii]  = numpy.std(masked_array)
            min_array[ii]  = numpy.min(masked_array)
            max_array[ii]  = numpy.max(masked_array)

            print([ii, masked_array.shape, mask.shape, mean_array[ii], std_array[ii] ])

        return mean_array, std_array, min_array, max_array


def pwi_filter(pwi_filename, mask_filename):
    from nipype import logging
    import nibabel
    import numpy
    import os
    import pandas
    import json
    from collections import OrderedDict

    pwi_filter_dirname = os.path.dirname(pwi_filename).replace('pwi_cl_subtract', 'pwi_filter')

    mean_pwi_filename = os.path.abspath(os.path.join(pwi_filter_dirname, 'mean.pwi.nii.gz'))
    positive_mean_pwi_filename = os.path.abspath(os.path.join(pwi_filter_dirname, 'positive.mean.pwi.nii.gz'))

    std_pwi_filename = os.path.abspath(os.path.join(pwi_filter_dirname, 'std.pwi.nii.gz'))

    iflogger = logging.getLogger('interface')
    iflogger.info(pwi_filename)

    nii_pwi = nibabel.load(pwi_filename)
    pwi = nii_pwi.get_data()

    nii_mask = nibabel.load(mask_filename)
    mask = nii_mask.get_data()

    mean_pwi = numpy.mean(pwi,axis=3)

    pos_mean_pwi = mean_pwi
    pos_mean_pwi[ mean_pwi<0 ] = 0

    std_pwi  = numpy.std(pwi,axis=3)

    nibabel.save(nibabel.Nifti1Image(mean_pwi, None, nii_pwi.get_header()), mean_pwi_filename)
    nibabel.save(nibabel.Nifti1Image(pos_mean_pwi, None, nii_pwi.get_header()), positive_mean_pwi_filename)
    nibabel.save(nibabel.Nifti1Image(std_pwi,  None, nii_pwi.get_header()), std_pwi_filename)

    return mean_pwi_filename, std_pwi_filename, positive_mean_pwi_filename


def cbf_pwi_preprocess_initialize():

    pwi_preproc = pe.Workflow(name='pwi_preproc')
    pwi_preproc.base_dir = methods_dir

    pwi_inputnode = pe.Node(interface=util.IdentityInterface(fields=['m0_mask', 'cl_mcf', 't1w_brain']),
                            name='pwi_inputnode')

    pwi_inputnode.inputs.func = pcasl

    pwi_datasink = pe.Node(nio.DataSink(), name='pwi_datasink')

    print(results_dir)

    pwi_datasink.inputs.base_directory = results_dir


    # Calculate PWI image
    pwi_cl_subtract = pe.Node(name='pwi_cl_subtract', interface=Function(input_names=['cl_mcf_filename', 'mask_filename'],
                                                                         output_names=['pwi_filename'],
                                                                         function=cl_to_pwi))

    pwi_to_cbf_node = pe.Node(name='pwi_to_cbf', interface=Function(input_names=['pwi_filename', 'mask_filename',
                                                                                 't1w_brain_filename'],
                                                                         output_names=['perfusion_filename',
                                                                                       'arrival_filename',
                                                                                       'perfusion_png_filename'],
                                                                         function=pwi_to_cbf))

    pwi_outputnode = pe.Node(interface=util.IdentityInterface(fields=['native_perfusion']),
                             name='pwi_outputnode')

#    pwi_filter_node = pe.Node(name='pwi_filter', interface=Function(input_names=['pwi_filename', 'mask_filename'],
#                                                                    output_names=['mean_pwi_filename', 'std_pwi_filename',
#                                                                                  'positive_mean_pwi_filename'],
#                                                                    function=pwi_filter))


    pwi_preproc.connect([(pwi_inputnode, pwi_cl_subtract, [('cl_mcf', 'cl_mcf_filename')]),
                         (pwi_inputnode, pwi_cl_subtract, [('m0_mask', 'mask_filename')]),

                         (pwi_cl_subtract, pwi_to_cbf_node, [('pwi_filename', 'pwi_filename')]),
                         (pwi_inputnode, pwi_to_cbf_node, [('m0_mask', 'mask_filename')]),
                         (pwi_inputnode, pwi_to_cbf_node, [('t1w_brain', 't1w_brain_filename')]),

                         #                        (pwi_cl_subtract, pwi_filter_node, [('pwi_filename', 'pwi_filename')]),
 #                        (pwi_inputnode, pwi_filter_node, [('m0_mask', 'mask_filename')]),

                         # Data Sink
                         (pwi_to_cbf_node, pwi_datasink, [('perfusion_filename', 'results.@perfusion_filename')]),
                         (pwi_to_cbf_node, pwi_datasink, [('arrival_filename', 'results.@arrival_filename')]),
                         (pwi_to_cbf_node, pwi_datasink, [('perfusion_png_filename', 'results.@perfusion_png_filename')])
 #                        (pwi_filter_node, pwi_datasink, [['mean_pwi_filename', 'results.@mean_pwi']]),
 #                        (pwi_filter_node, pwi_datasink, [['mean_pwi_filename', 'results.@std_pwi']]),
 #                        (pwi_filter_node, pwi_datasink, [['positive_mean_pwi_filename', 'results.@positive_mean_pwi']]),

                         # Output Node
#                         (pwi_to_cbf_node, pwi_outputnode, [('perfusion_filename', 'native_perfusion')])
                         #(pwi_filter_node, pwi_outputnode, [['mean_pwi_filename', 'mean_pwi']]),
                         #(pwi_filter_node, pwi_outputnode, [['std_pwi_filename', 'std_pwi']]),
                         #(pwi_filter_node, pwi_outputnode, [['positive_mean_pwi_filename', 'positive_mean_pwi']])

                         ])

    return pwi_preproc

    # print("Inputs:")
    # print(pwi_preproc.inputs.m0_inputnode)
    # print("Outputs:")
    # print(m0_preproc.outputs.m0_outputnode)

# endregion

# ======================================================================================================================
# region Reporting

def cbf_microgl(mean_pwi_filename):
    import os
    import subprocess

    png_pwi_filename = '/Users/bkraft/cenc/mriData/34P1001/functional/cbf/methods/results/mean_pwi.png'

   # Create Figure
    command = ['/Applications/MRIcroGL/MRIcroGL.app/Contents/MacOS/MRIcroGL',
               '/Users/bkraft/PycharmProjects/tic_cbf/cbf/cbf_nipype.gls']

    DEVNULL = open(os.devnull, 'wb')
    pipe = subprocess.Popen(command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

    return png_pwi_filename


def cbf_report_initialize():
    cbf_report = pe.Workflow(name='cbf_report')
    cbf_report.base_dir = methods_dir

    cbf_report_inputnode = pe.Node(interface=util.IdentityInterface(fields=['positive_mean_pwi_filename', 't1w']), name='cbf_report_inputnode')

    cbf_report_node = pe.Node(name='cbf_microgl',
                              interface=Function(input_names=['mean_pwi_filename'],
                                                 output_names=['png_pwi_filename'],
                                                 function=cbf_microgl))

    cbf_report_datasink = pe.Node(nio.DataSink(), name='cbf_report_sinker')
    cbf_report_datasink.inputs.base_directory = results_dir

    cbf_report_outputnode = pe.Node(interface=util.IdentityInterface(fields=['png_pwi_filename' ]),
                            name='cbf_report_outputnode')

                            #
    cbf_report.connect([ (cbf_report_inputnode, cbf_report_node, [('positive_mean_pwi_filename','mean_pwi_filename')]),

                         # Datasink Node
                         (cbf_report_node, cbf_report_datasink, [('png_pwi_filename','results.@png_pwi_filename')]),

                         # Output Node
                         (cbf_report_node, cbf_report_outputnode,
                          [('png_pwi_filename', 'png_pwi_filename')]),

                         ])

    return cbf_report

#endregion

# ======================================================================================================================
# Master Workflow


def cbf_initialize_workflows(pcasl, t1w_brain):

    m0_preproc = cbf_m0_preprocessing_initialize()
    cl_preproc = cbf_cl_preprocessing_initialize()
    od_preproc = cbf_outlier_detection_initialize()
    pwi_preproc = cbf_pwi_preprocess_initialize()
    cbf_report = cbf_report_initialize()

    cbf_workflow = pe.Workflow(name="cbf_preproc", base_dir=methods_dir)

    inputnode = pe.Node(interface=util.IdentityInterface(fields=['func', 't1w_brain' ]),
                        name='inputspec')

    inputnode.inputs.func=pcasl
    inputnode.inputs.t1w_brain=t1w_brain


    cbf_workflow.connect([ (inputnode, m0_preproc, [("func", "m0_inputnode.func")]),
                           (inputnode, cl_preproc, [("func", "cl_inputnode.func")]),
                           (m0_preproc, cl_preproc, [("m0_outputnode.m0", "cl_inputnode.m0")]),
                           (m0_preproc, cl_preproc, [("m0_outputnode.m0_mask", "cl_inputnode.m0_mask")]),
                           (m0_preproc, od_preproc, [("m0_outputnode.m0_mask",    "od_inputnode.m0_mask")]),
                           (cl_preproc, od_preproc, [("cl_outputnode.cl_mcf",     "od_inputnode.cl_mcf")]),
                           (cl_preproc, od_preproc, [("cl_outputnode.cl_mcf_par", "od_inputnode.cl_mcf_par")]),
                           (m0_preproc, pwi_preproc, [("m0_outputnode.m0_mask", "pwi_inputnode.m0_mask")]),
                           (cl_preproc, pwi_preproc, [("cl_outputnode.cl_mcf", "pwi_inputnode.cl_mcf")]),
                           (inputnode, pwi_preproc, [("t1w_brain", "pwi_inputnode.t1w_brain")]),
#                           (pwi_preproc, cbf_report, [('pwi_outputnode.positive_mean_pwi',
#                                                       'cbf_report_inputnode.positive_mean_pwi_filename')])
                           ])

    return cbf_workflow



if __name__ == '__main__':

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='cbf')

    parser.add_argument("in_raw_pcasl",      help="PCASL Raw NII data" )
    parser.add_argument("in_t1w_brain",      help="Brain extracted t1w NII image" )
    parser.add_argument("--mask",            help="mask", default = None )
    parser.add_argument("--working_dir",     help="Working directory (default=cwd)", default = os.getcwd() )
    parser.add_argument("--out_basename",    help="Output basename" )
    parser.add_argument("--std_criterion",   help="Standard Deviation criterion (default=2.25)", default=2.25,
                            type=float )

    parser.add_argument("-v","--verbose",    help="Verbose flag",      action="store_true", default=False )

    inArgs = parser.parse_args()

    # Setup preliminaries
    pcasl = os.path.abspath( inArgs.in_raw_pcasl )
    t1w_brain = os.path.abspath( inArgs.in_t1w_brain )

    input_dir = os.path.dirname(pcasl)
    methods_dir = os.path.abspath(os.path.join(input_dir, '..', 'methods'))
    results_dir = os.path.join(methods_dir)


    # Run Workflow
    cbf_workflow = cbf_initialize_workflows(pcasl, t1w_brain)

    cbf_workflow.write_graph(graph2use='orig', format='png', simple_form=True)
    cbf_workflow.run()


