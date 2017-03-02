#!/usr/bin/python
import os
import sys
import re
import argparse
import time

relativeHome='./'
pythonVersion='python2.7'
dataDir=relativeHome+'data/'
srcDir=relativeHome+'labelSrc/'
outDir=relativeHome+'output/'
sys.path.insert(0,srcDir)
from labelSrc import *

#define default opertions
abbreviations={\
'measure'   :'Measure label',\
'mbe'       :'Measure minimum bounding ellipsoid',\
'extract'   :'Extract label',\
'remove'    :'Remove label'}


#default commands, can be put into a class
procedures={\
'measure'   :['stats.py 9mo.label.gwm.nii.gz -v'],\
'mbe'       :['ellipsoid.py 9mo.label.gwm.nii.gz -v'],\
'extract'   :['extract.py 9mo.label.gwm.nii.gz -x 1 2 3 --out 123.nii.gz',\
              'stats.py 123.nii.gz -v'],
'remove'    :['remove.py 123.nii.gz -r 2 --out 13.nii.gz',\
              'stats.py 13.nii.gz -v']\
}


helpTable='\nabbreviation Table:\n\n'
for key in abbreviations:
    helpTable+=(key+'\t:'+abbreviations[key]+'\n')
helpTable+='\n'

def runCmd(order):
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    for p in order:
        print ('******************* '+abbreviations[p]+' *******************')
        print
        commands=procedures[p]
        for c in commands:
            print ('# command\t: '+c)
            fileName,argument=c.split(' ',1)
            saveTo= ' > '+outDir+argument.split(' ',1)[0]+'.dat'
            startTime=time.time()
            os.system(pythonVersion+' '+srcDir+fileName+' '+dataDir+argument+saveTo)
            print ('# runtime\t: %.6f\tseconds'%(time.time()-startTime))
            print ('# outputs\t:')
            os.system('cat'+' '+outDir+argument.split(' ',1)[0]+'.dat')
            os.system('mv'+' '+argument.split(' ',1)[0]+' '+outDir)
            print('---------------------')
            # add validation codes here process here.
            print
        print


if __name__=='__main__':
    try:
        parser = argparse.ArgumentParser(description='Manipulating and measuring labels in NIFTI image files.\n', formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-opr', metavar='abbr',type=str,nargs='+',
        help='define the order of operations\n'+helpTable)
        args = parser.parse_args()

        if args.opr==None:
            order=procedures
        else:
            order=args.opr
        runCmd(order)
    except KeyboardInterrupt:
        pass
