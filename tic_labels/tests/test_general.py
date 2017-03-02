# generalized test
# pytest test_general.py -v

import pytest
import os,sys
import labels
import nibabel as nib
relativeHome='../'
srcDir=relativeHome+'labels/'
datDir=relativeHome+'data/'

# you only need to change this array for all similar tests with the format:
#               functionName + inputFilename + arguments
# and the output can be stdout or file
# or you will have to change the testList's format
testItems=[\
# function      ,arguments                              ,output file    ,expected results
["stats.py"     ,"123.nii.gz -v --stats all"            ,""             ,"expected_stats_123_all.dat"]     ,\
["stats.py"     ,"123.nii.gz -v --stats volume com"     ,""             ,"expected_stats_123_vol_com.dat"] ,\
["stats.py"     ,"9mo.label.gwm.nii.gz -v"              ,""             ,"expected_stats_9mo.dat"]          ,\
["ellipsoid.py" ,"9mo.label.gwm.nii.gz -v"              ,""             ,"expected_ellipsoid_9mo.dat"]      ,\
["extract.py"   ,"9mo.label.gwm.nii.gz -x 1 2 3 --out 123.nii.gz"\
                                                        ,"123.nii.gz"   ,"expected_extract.nii.gz"]         ,\
["remove.py"    ,"123.nii.gz -r 2 --out 13.nii.gz"      ,"13.nii.gz"    ,"expected_remove.nii.gz"]          ,\
]

testList=list(map(lambda t:(srcDir+t[0]+" "+datDir+t[1],datDir+t[2],datDir+t[3]),testItems))

@pytest.mark.parametrize(\
                        ( "command_to_test","output_file","filename_expected"), testList)

def testCommandlineCall(capfd, command_to_test,output_file,filename_expected,):
    #may add another method to test on function call
    os.system(command_to_test)
    if output_file!=datDir: # the output is saved in nii format
        resout = nib.load(output_file).get_data()
        expected = nib.load(filename_expected).get_data()
        assert resout.all() == expected.all()
    else:                   # the output is in stdout
        resout, reserr = capfd.readouterr()
        expected = open(filename_expected, "r").read()
        assert resout == expected
#may add another method to test on function call
#def testFunctionCall(function_to_test,output,filename_expected,):
