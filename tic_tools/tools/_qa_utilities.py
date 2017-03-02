#!/aging1/software/anaconda/bin/python
"""

"""

import sys      
import os                                               # system functions
import glob
import shutil
import distutils
import re
import argparse
import subprocess


def display_command( command, verboseFlag=False ):

    if verboseFlag:
        print()
        print(command)
        print()

def  qa_exist(fileList, displayFlag=False):
     qaExistStatus = qa_input_files(fileList, displayFlag)
     return qaExistStatus

def  qa_input_files(fileList, verboseFlag=False, displayFlag=False):
    
    fileNames           = [ ii[0] for ii in fileList ] 
    maxFileStringLength = max(map(len, filter(None, fileNames) )) + 4

    if verboseFlag:
        print()

    qaInputStatus       = True
        
    for ii in fileList:

        if ( (ii[0] == None) or (ii[0] != None) and (os.path.isfile(ii[0]))): 
            fileInputStatus = True

        else:
            fileInputStatus = False
            qaInputStatus   = False

        if verboseFlag and (ii[0] != None):
            print("\t{1:{0}s} {2:4s}".format(maxFileStringLength, str( ii[0] ), passfail(fileInputStatus)))

        
            
    if displayFlag:
        freeview(fileList, verboseFlag)
     
    if verboseFlag:
        print("\n\t{1:{0}s} {2:4s}\n".format(maxFileStringLength, "Quality Assurance Inputs", passfail(qaInputStatus)))
        
    return qaInputStatus
   
def  passfail( inBoolean ):

    if inBoolean:
        return 'PASS'
    else:
        return 'FAIL'



def  freeview( fileList, displayFlag=False, verboseFlag=False ):

    freeviewCommand = "freeview "

    for ii in fileList:

        if (ii[0] != None) and os.path.isfile(ii[0]): 
            
            if ( ( ii[0].endswith(".nii.gz") or ii[0].endswith(".nii")) and
                 ( ii[1] != None) ) :
                
                freeviewCommand = freeviewCommand + " " + str(ii[0]) + str(ii[1])
                
     
    if displayFlag:
        DEVNULL = open(os.devnull, 'wb')
        pipe = subprocess.Popen([freeviewCommand], shell=True,
                                stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        
