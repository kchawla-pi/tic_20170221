tic_protocol_check
==================

protocol_check_dicom.py: protocol checker for DICOM images

This program reads a CSV file containing a list of DICOM elements, with expected values and ranges, 
and compares those values to the values in the header of a DICOM image.  The CSV file should be 
created as a copy of "template.csv" and then edited as desired.  Lines can be removed for elements
that you are not interested in checking. Lines can be added by looking in _dicom_dict.py to 
determine the proper spelling of elements (at the end of the row).  These dictionaries were copied 
from pydicom, which is used to read the DICOM file.

The file siemens_private_dict.py contains additional Siemens private elements, but is not complete.

(A checker for Nifti files may get developed as protocol_check_nifti.py)

Usage
-----

   $ python protocol_check_dicom.py 000001.DCM specfile.csv     (or make it executable and call it directly)


Example contents of specfile.csv::

        Element_name,               Expected_value,    min,     max
        Rows,                                  128,     64,     320
        RepetitionTime,                      100.0,   95.0,   110.0
        EchoTime,                              8.0,    6.0,    10.0
        SliceThickness,                        5.0,    3.0,     8.0
        FlipAngle,                              15,     10,      20
        NumberOfAverages,                        2,      2,       2
        PixelBandwidth,                        120,    100,     150
        InPlanePhaseEncodingDirection,         COL,    COL,     COL
        PixelSpacingX,                       0.729,    0.6,     1.0
        PixelSpacingY,                       0.729,    0.6,     1.0


Output::

                             Element    Value Expected      Max      Min       Status

         --------------------------- -------- -------- -------- -------- ------------
                                Rows   288.00   128.00    64.00   320.00           OK
                           FlipAngle    15.00    15.00    10.00    20.00           OK
                      SliceThickness     4.00     5.00     3.00     8.00           OK
                      PixelBandwidth   130.00   120.00   100.00   150.00           OK
                    NumberOfAverages     2.00     2.00     2.00     2.00           OK
                       PixelSpacingY     0.73     0.73     0.60     1.00           OK
                      RepetitionTime    26.96   100.00    95.00   110.00   OutOfRange
                            EchoTime     8.32     8.00     6.00    10.00           OK
                       PixelSpacingX     0.73     0.73     0.60     1.00           OK
       InPlanePhaseEncodingDirection      COL      COL      COL      COL           OK

