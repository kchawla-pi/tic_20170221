#!/bin/bash
#
# lnflatten.sh <dirName>  $(find . -name "t2w_n4.nii*" | grep segment )
#

lnDir="${1}"

if [ ! -d $lnDir ]; then
     mkdir -p $lnDir
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



cmd=$( echo "ln -f ${x} ${lnDir}/${y}" )


#echo $x
#echo $y
#echo $cmd
#echo

$cmd

done