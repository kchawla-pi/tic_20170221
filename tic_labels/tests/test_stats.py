import sys
import subprocess
import numpy as np

relativeHome='../'
srcDir=relativeHome+'labels/'

#outDir=relativeHome+'output/'

sys.path.insert(0,'.')
sys.path.insert(0,relativeHome)
sys.path.insert(0,srcDir)

from labels import *
from genROI import *
import stats

class TestLabelClass:
    def test_stats(capsys):
        centers=np.random.randint(20,size=(2,3))+90
        radius=np.random.randint(20,size=(2))+10
        shape=np.random.choice(['cube','sphere'],2,replace=False)
        expectedV,expectedCOM = genROI(centers[0],radius[0],shape[0],centers[1],radius[1],shape[1],1)
        proc=subprocess.run(['../labels/stats.py', 'test3Dcubes.nii.gz', '-v','--stats','volume','com'],stdout=subprocess.PIPE)
        outputBuff=proc.stdout.decode("utf-8")
        lines=outputBuff.split('\n')[1:]

        for line in lines:
            if line!='':
                results=line.split(' ')
                results=list(filter(None, results))
                runV=results[2]
                runCOM=results[3:6]
                runV=float(runV)

                assert expectedV==float(runV)
                assert np.array_equal(list(map(lambda v:float(v),runCOM)),expectedCOM)

