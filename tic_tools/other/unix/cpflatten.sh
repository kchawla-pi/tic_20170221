#!/bin/bash
#
# cpflatten.sh <dirName>  $(find . -name "t2w_n4.nii*" | grep segment )
#

cpDir="${1}"

if [ ! -d $cpDir ]; then
     mkdir -p $cpDir
fi


for x in "${@:2}"
do

#  Do two replacements with sed.
#
#       1) Replace first "./" if it is at the beginning of the name with "". 
#          This removes the relative path designation and prevents files 
#          from being renamed as hidden files
#       
#       2) Replace "/" with "_".   
#


y=$( echo "$x"  | sed  -e 's%^\.\/%%' -e 's%\/%_%g')
cmd=$( echo "cp -f ${x} ${cpDir}/${y}" )


#echo $x
#echo $y
#echo $cmd
#echo

$cmd

done