#!/usr/bin/env python3
'''
test script for protocol_check_dicom.py

usage: just run it with no arguments

'''

import sys
import os

sys.path.insert(0, os.path.abspath('../protocol_check'))

import protocol_check_dicom

protocol_check_dicom.protocol_check_dicom('000001.DCM','specfile.csv')





