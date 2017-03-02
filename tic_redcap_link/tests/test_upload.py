#!/usr/bin/env python3
'''
test script for redcap_upload.py

'''

import sys
import os
sys.path.insert(0,os.path.abspath('../redcap_link'))

import redcap_upload as rcu

rcu.redcap_upload('CENC','mt.json','../redcap_link/upcap.ini')





