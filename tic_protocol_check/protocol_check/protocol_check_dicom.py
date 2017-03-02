#!/usr/bin/env python
"""
This script checks a DICOM file for compliance with a CSV specification file

@author: cahamilton
"""

import sys
import argparse
import dicom as dcm
import csv


def protocol_check_dicom(dimg, spec_file):
    # ~~~~~~~~~~~~~~   parse command line   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # read the spec_file into the dictionary 'specs' {key,tuple}
    #   the tuple contains (standard, min, max) values

    ifile = open(spec_file, 'rt')
    reader = csv.reader(ifile)
    specs = {}

    rownum = 0
    for line in reader:
        # print(line)
        if rownum > 0:
            key = line[0]
            stan = line[1]
            mn = line[2]
            mx = line[3]
            try:
                specs[key] = tuple((float(stan), float(mn), float(mx)))
            except ValueError:
                specs[key] = tuple((stan.strip(), mn.strip(), mx.strip()))   # strings
        rownum += 1

    ifile.close()

    # verify the spec_file has ranges that encompass the standard value
    for value in list(specs.values()):
        # value is a tuple (standard,min,max), only check floats, not strings (such as PE direction)
        if not isinstance(value[0], str) and (value[1] > value[0]) or (value[2] < value[0]):
            print(('bad spec file range:', value))
            sys.exit()

    print('\nspec file looks OK.\n')

    # read the DICOM file and extract the elements in specfile

    ds = dcm.read_file(dimg)

#    print('Spec file contains:')
#    for key, value in list(specs.items()):
#        print((key + '= ', value))

#    print('\nImage elements are:')
#    for key in list(specs.keys()):
#        print((key + '= ', eval('ds.' + key)))

    return_status = 0

    print('Results:\n')
    print('%30s %8s %8s %8s %8s %12s'
          % ('Element', 'Value', 'Expected', 'Max', 'Min', 'Status'))
    print('%30s %8s %8s %8s %8s %12s'
          % ('---------------------------', '--------', '--------', '--------', '--------', '------------'))

    for key, value in list(specs.items()):

        isfloat = False
        # handle special cases first
        if key == 'PixelSpacingX':
            ps = eval('ds.PixelSpacing')
            val = float(ps[1])
            isfloat = True
        elif key == 'PixelSpacingY':
            ps = eval('ds.PixelSpacing')
            val = float(ps[0])
            isfloat = True
        elif isinstance(value[0], str):
            val = eval('ds.' + key)
        else:
            val = float(eval('ds.' + key))
            isfloat = True

        if isfloat:
            if (val >= value[1]) and (val <= value[2]):
                status = "OK"
            else:
                status = "OutOfRange"
                return_status = -1
        else:
            if val == value[0]:
                status = "OK"
            else:
                status = "OutOfRange"
                return_status = -1

        if isfloat:
            print('%30s %8.2f %8.2f %8.2f %8.2f %12s'
                  % (key, val, value[0], value[1], value[2], status))
        else:
            print('%30s %8s %8s %8s %8s %12s'
                  % (key, val, value[0], value[1], value[2], status))

    if return_status == 0:
        print('PASS')
    else:
        print('FAIL')

    return return_status

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="protocol_check_dicom: check DICOM file with CSV spec file")
    parser.add_argument("image", type=str,
                        help="DICOM image to check.")
    parser.add_argument("specfile", type=str,
                        help="Specification file (CSV).")
    args = parser.parse_args()

    sys.exit(protocol_check_dicom(args.image, args.specfile))
