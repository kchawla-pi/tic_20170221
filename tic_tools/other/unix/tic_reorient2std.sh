#!/bin/bash

outputDir="${1}"

if [ ! -d "${outputDir}" ]; then
   mkdir -p ${outputDir}
fi

echo

for ii in "${@:2}"; do

    cmd="fslreorient2std $ii ${outputDir}/$ii"   
    echo $cmd;
    $cmd;

done

echo