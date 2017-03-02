#!/bin/bash
export dcmFlatDir="./dcmFlat"

export dcmConvertDir="../nifti"

export dcmConvertAll="dcmConvertAll.cfg"
export dcmConvert="dcmConvert.cfg"

export dcmReportInfo="dcmReport.info"

export dcmFiles1="*.DCM"
export dcmFiles2="*.IMA"
export dcmFiles3="*.dcm"

export dcmFormat="nii"
export dcmFormatExtension=".nii.gz"


dcm_source() {
    echo
    cmd="source ${IC_GIT_PATH}/scripts/dcm_functions.sh"
    echo $cmd
    $cmd
    echo
}


dcm_list() {
    echo 
    echo "dcm Enviroment Variables"
    echo
    echo "   dcmFlatDir    = " $dcmFlatDir
    echo "   dcmReportInfo = " $dcmReportInfo
    echo "   dcmConvertAll = " $dcmConvertAll
    echo "   dcmConvert    = " $dcmConvert
    echo "   dcmConvertDir = " $dcmConvertDir

    echo; 
    echo "dcm Functions"
    echo 

    declare -F | awk ' /declare -f dcm_/{print "   " $3} '

    echo;
}

dcm_mv_incoming(){

    mkdir -p $2/data/
    mv $1 $2/data/dicom

}


dcm_scan() {

    dcm_search_dir=${1-./}
    dcm_flat_dir=${2-$dcmFlatDir}
    dcm_convert_all=${3-$dcmConvertAll}
    dcm_report_info=${4-$dcmReportInfo}

    dcm_flatten       $dcm_search_dir
    dcm_report        $dcm_flat_dir $dcm_report_info
    dcm_parse_general $dcm_convert_all $dcm_report_info
}


dcm_auto() {

    startDir=$(pwd)

    dcm_scan $1

    dcm_convert $dcmConvertAll

    cd $dcmConvertDir
    dcm_clean

    cd $startDir

}

dcm_parse_general() {

    FUNCNAME=dcm_parse_general
    outFileName=${1-$dcmConvertAll}
    dcm_report_info=${2-$dcmReportInfo}

    echo
    echo ">>>>>>>>>>> ${FUNCNAME}: cat $dcmConvertAll ..."
    echo

    # Contents of dcmparse.sh
    # Eventually it should be integrated into this function
    #
    
     rm -rf ${outFileName}.tmp1 

     awk -v awkOutDir="$dcmConvertDir" \
         -v awkFormat="$dcmFormat" \
         -v awkExtension="$dcmFormatExtension" \
                'BEGIN { FS = " " } 
                { printf "%2d %s %s %s%s\n", $1, awkOutDir, awkFormat, $2, awkExtension }' \
		    $dcm_report_info > ${outFileName}.tmp1

     sed -i -e '/Phoenix/d'  ${outFileName}.tmp1  # Remove Phoenix from the list

     dcm_add_rs ${outFileName}.tmp1 | tee ${outFileName}

     rm -rf ${outFileName}.tmp1 

    echo
}

dcm_add_rs() {
     awk 'BEGIN { FS = " " } 
                { gsub( ".nii", sprintf("_rs%02d.nii", $1), $4);
                  printf("%2d %s %s %s\n", $1, $2, $3, $4) }'  $1
}

dcm_remove_rs() {
  sed -e 's#_rs[[:digit:]][[:digit:]]##' $1
}

dcm_remove_rs01() {
  sed -e 's#_rs01##' $1
}

dcm_parse_secret1_t1ax_thigh() {

#  echo " "
#  echo ">>>>>>>>>> Selecting T1 axial images of the thigh "
#  echo " "

  grep  'T1AXDBLEFTTHIGH' $1 > ${1}.tmp
  mv -f ${1}.tmp ${1}

  cat $1
 
#  echo ""
}

dcm_remove_dti_color_fa() {
  sed -e '/ed2d.*_rs05/d' $1
}

dcm_remove_localizers() {
  sed  -e '/localizer/Id'  -e '/LOC/Id' $1
}

dcm_flatten() {

    FUNCNAME=dcm_flatten
    dcm_search_dir=${1-./}
    dcm_flat_dir=${2-$dcmFlatDir}

    echo
    echo ">>>>>>>>>> ${FUNCNAME} : Finding all DCM files and creating hard links in $dcmFlatDir"
    echo

    if [ -d $dcm_flat_dir ]; then
	echo 'Old ' $dcm_flat_dir ' exists.  Deleting before relinking dicom files.'
        rm -rf ${dcm_flat_dir}
    fi

    mkdir -p $dcm_flat_dir

    dcm_flatten_core $dcm_flat_dir $(find -L $dcm_search_dir -name $dcmFiles1 -o -name $dcmFiles2 -o -name $dcmFiles3)
}








dcm_flatten_core() {

    dcm_flat_dir="${1}"

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

    cmd=$(echo "ln -f ${x} ${dcm_flat_dir}/${y}")
    
#    echo '======='
#    echo $x
#    echo $y
#    echo $cmd
#    echo '-------'
     eval "$cmd"
#    echo '======='

    done
}


dcm_report() {

    FUNCNAME=dcm_report
    dcm_flat_dir=${1-$dcmFlatDir}
    dcm_report_info=${2-$dcmReportInfo}

    echo
    echo ">>>>>>>>>> ${FUNCNAME}: Scanning DCM files and creating $dcmReportInfo"
    echo

    unpacksdcmdir -src $dcm_flat_dir -targ . -scanonly $dcm_report_info
}

dcm_delete_duplicates(){
    awk '!seen[$4]++' $1
}

dcm_convert() {
    FUNCNAME=dcm_convert
    startDir=$PWD

    echo
    echo ">>>>>>>>>>> ${FUNCNAME}: Convert files according to $1 ...."
    echo
    cat $1

    echo
    echo ">>>>>>>>>>> ${FUNCNAME}: Unpacking ..."

    unpacksdcmdir -src $dcmFlatDir -targ . -cfg $1 -generic


    echo
    echo ">>>>>>>>>>> ${FUNCNAME}: dcm2nii conversion of dti and topup directories ..."

    iwDtiDcm2Nii.sh $1

    # Clean all dicom directories to rename files.

    echo
    echo ">>>>>>>>>>> ${FUNCNAME}: Clean NIFTI directories ..."

    cd ${startDir}

    dcmConvertDir=$(awk '{print $2}' $1 | uniq )

    for ii in $dcmConvertDir; do 
	iiDir="${startDir}/${ii}"
	cd $iiDir
	dcm_nifti_clean; 
    done

    echo
}

dcm_reorient2std() {

outputDir=${1}

if [ ! -d "${outputDir}" ]; then
   mkdir -p ${outputDir}
fi

echo

for ii in "${@:2}"; do

    echo "fslreorient2std $ii ${outputDir}/$ii"
    ${FSLDIR}/bin/fslreorient2std $ii ${outputDir}/$ii

done

echo

}


dcm_nifti_clean() {

    rename nii-infodump.dat info *.dat
    rename nii.gz-infodump.dat info *.dat
    rm -f flf
}

dcm_clean() {
    
    rm -rf ${dcmConvertAll} ${dcmConvert}
    rm -rf dicomdir.sumfile  
    rm -rf unpack.log
}

dcm_group() {

   dcm_remove_rs $1 > ${1}.dcmgroup.step1

   awk 'BEGIN{FS = " "}
     
       {

       outFileName=$4

       if (last == outFileName)
	   {
	       count++;

	   }
       else
	   {
	       count = 1;
	       last = $4;
      	   }

       gsub( ".nii.gz", sprintf("_rs%02d.nii.gz", count), outFileName);

       printf("%2d %s %s %s\n", $1, $2, $3, outFileName);

       }'  ${1}.dcmgroup.step1

   rm ${1}.dcmgroup.step1

}


