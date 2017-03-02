echo
echo " --- Measure label -----------------------"
echo

stats.py 9mo.label.gwm.nii.gz -v

echo
echo " --- Measure minimum bounding ellipsoid -----------------------"
echo

ellipsoid.py 9mo.label.gwm.nii.gz -v

echo
echo " --- Extract label -----------------------"
echo

extract.py 9mo.label.gwm.nii.gz -x 1 2 3 --out 123.nii.gz
stats.py 123.nii.gz -v

echo
echo " --- Remove label -----------------------"
echo

remove.py 123.nii.gz -r 2 --out 13.nii.gz
stats.py 13.nii.gz -v 

