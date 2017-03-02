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
# region Reporting

def cbf_microgl(mean_pwi_filename):
    import os
    import subprocess

    png_pwi_filename = '/Users/bkraft/cenc/mriData/34P1001/functional/cbf/methods/results/mean_pwi.png'

   # Create Figure
    command = ['/Applications/MRIcroGL/MRIcroGL.app/Contents/MacOS/MRIcroGL',
               '/Users/bkraft/PycharmProjects/tic_cbf/cbf/cbf_montage.gls']

    DEVNULL = open(os.devnull, 'wb')
    pipe = subprocess.Popen(command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

    return png_pwi_filename


# def cbf_report_initialize():
#     cbf_report = pe.Workflow(name='cbf_report')
#     cbf_report.base_dir = methods_dir
#
#     cbf_report_inputnode = pe.Node(interface=util.IdentityInterface(fields=['positive_mean_pwi_filename']), name='cbf_report_inputnode')
#
#     cbf_report_node = pe.Node(name='cbf_microgl',
#                               interface=Function(input_names=['mean_pwi_filename'],
#                                                  output_names=['png_pwi_filename'],
#                                                  function=cbf_microgl))
#
#     cbf_report_datasink = pe.Node(nio.DataSink(), name='cbf_report_sinker')
#     cbf_report_datasink.inputs.base_directory = results_dir
#
#     cbf_report_outputnode = pe.Node(interface=util.IdentityInterface(fields=['png_pwi_filename' ]),
#                             name='cbf_report_outputnode')
#
#                             #
#     cbf_report.connect([ (cbf_report_inputnode, cbf_report_node, [('positive_mean_pwi_filename','mean_pwi_filename')]),
#
#                          # Datasink Node
#                          (cbf_report_node, cbf_report_datasink, [('png_pwi_filename','results.@png_pwi_filename')]),
#
#                          # Output Node
#                          (cbf_report_node, cbf_report_outputnode,
#                           [('png_pwi_filename', 'png_pwi_filename')]),
#
#                          ])
#
#     return cbf_report

# print("Inputs:")
# print(cbf_report.inputs.m0_inputnode)
# print("Outputs:")
# print(cbf_report.outputs.m0_outputnode)
#endregion

# ======================================================================================================================
# Master Workflow


if __name__ == '__main__':


    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='cbf')

    parser.add_argument("pwi", help="Mean PWI filename. Should be a 3D NIFTI file" )
    parser.add_argument("-v","--verbose",    help="Verbose flag",      action="store_true", default=False )

    inArgs = parser.parse_args()

    # Setup preliminaries
    pwi_filename = os.path.abspath( inArgs.pwi)

    input_dir = os.path.dirname(pwi_filename)

    cbf_microgl(pwi_filename )
