#!/usr/bin/python
from config import *

procedures={\
'measure'   :['stats.py 9mo.label.gwm.nii.gz -v'],\
'mbe'       :['ellipsoid.py 9mo.label.gwm.nii.gz -v'],\
'extract'   :['extract.py 9mo.label.gwm.nii.gz -x 1 2 3 --out 123.nii.gz',\
              'stats.py 123.nii.gz -v'],
'remove'    :['remove.py 123.nii.gz -r 2 --out 13.nii.gz',\
              'stats.py 13.nii.gz -v']\
}

parser = argparse.ArgumentParser(description='Manipulating and measuring labels in NIFTI image files.\n', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-opr', metavar='abbr',type=str,nargs='+',help='define the order of operations\n'+helpTable)

args = parser.parse_args()

if args.opr==None:
    order=procedures
else:
    order=args.opr

runCmd(order)
