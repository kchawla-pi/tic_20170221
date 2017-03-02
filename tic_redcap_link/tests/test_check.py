#!/usr/bin/env python3
'''
test script for redcap_check.py

'''

import sys
import os
sys.path.insert(0,os.path.abspath('../redcap_link'))

import redcap_check as rcc

rcc.redcap_check('CENC','mt.json','../redcap_link/upcap.ini')





