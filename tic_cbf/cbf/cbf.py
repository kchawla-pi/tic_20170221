#!/usr/bin/env python

"""

"""
import os
import argparse
import numpy
import nibabel
import nilearn


def get_mask(nii_mask):

    if nii_mask == None:
        mask = 1
    else:
        mask = nii_mask.get_data()

    return mask



def clpairs_to_pwi(nii_cl, nii_mask=None):
    nii_cl = nibabel.load(nii_cl)
    cl = nii_cl.get_data()

    if nii_mask == None:
        mask = numpy.ones( cl.shape[0:3] )
    else:
        mask = nii_mask.get_data()

    if cl.shape[0:3] == mask.shape[0:3]:
        pwi = (cl[:,:,:,0::2] - cl[:,:,:,1::2]) * mask[:,:,:,numpy.newaxis]
    else:
        pwi=[]
        print('Error message')

    return pwi

def read_m0(m0_filename):
    nii_m0 = nibabel.load(m0_filename)
    return nii_m0.get_data(), nii_m0.get_header()

def calc_pwi_stats(pwi, mask=None):

    pwi_mean = numpy.mean(pwi, axis=(0,1,2))
    pwi_std  = numpy.std(pwi, axis=(0,1,2))

    pwi_global_mean = numpy.mean(pwi)
    pwi_global_std  = numpy.std(pwi)

    return pwi_mean, pwi_std, pwi_global_mean, pwi_global_std

def std_volume_filter():
    pass

#
# Main Function
#

if __name__ == "__main__":

    ## Parsing Arguments
    #
    #

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='cbf')

    parser.add_argument("in_cl",             help="CL pairs NIFTI image" )
    parser.add_argument("in_m0",             help="M0 NIFTI image" )
    parser.add_argument("--mask",            help="mask", default = None )
    parser.add_argument("--working_dir",     help="Working directory (default=cwd)", default = os.getcwd() )
    parser.add_argument("--mask",            help="mask", default = None )
    parser.add_argument("--out_basename",    help="Output basename" )
    parser.add_argument("--scale",           help="scale", default=1, type=float )
    parser.add_argument("--std_criterion",   help="Standard Deviation criterion (default=2.25)", default=2.25,
                            type=float )
    parser.add_argument("-v","--verbose",    help="Verbose flag",      action="store_true", default=False )


    inArgs = parser.parse_args()


    m0, m0_header = read_m0(inArgs.m0)
    mask = get_mask(inArgs.mask)

    pwi = clpairs_to_pwi(inArgs.in_cl, inArgs.mask)
    pwi_mean, pwi_std, pwi_global_mean, pwi_global_std = calc_pwi_stats(pwi, inArgs.mask)

    nibabel.save( nibabel.Nifti1Image( pwi, None, m0_header ), 'pwi.nii.gz' )
    nibabel.save( nibabel.Nifti1Image( numpy.mean(pwi, axis=3), None, m0_header ), 'mean.pwi.nii.gz' )
    nibabel.save( nibabel.Nifti1Image( numpy.std(pwi, axis=3), None, m0_header ), 'std.pwi.nii.gz' )



    # """
    #
    # echo "perfusion filtering"
    #
    # if (1) then
    # fslmaths  $CBF_dir/$series_name:r:r_perfsub_org.nii.gz -mul $CBF_dir/ref_vol_brain_mask.nii.gz $CBF_dir/$series_name:r:r_perfsub_org_brain.nii.gz
    # fslsplit  $CBF_dir/$series_name:r:r_perfsub_org.nii.gz $CBF_dir/tmp/perfsub_org
    #
    # #
    # # Calculate Perf Mean and Standard Deviation for each individual PWI image
    # #
    #
    # foreach perfsubfile ( $CBF_dir/tmp/perfsub_org*.nii.gz)
    #   fslstats $perfsubfile -M >> $CBF_dir/mean_perf.txt
    #   fslstats $perfsubfile -S >> $CBF_dir/std_perf.txt
    # end
    #
    # # Calculate total number of perusion volumes
    # set total_perf_volumes = `wc -l $CBF_dir/mean_perf.txt | awk '{print $1}' `
    #
    #
    # echo "mean check"
    #
    # # Calculate global standard deviation
    # set std = `awk '{sum+=$1; sumsq+=$1*$1} END {print sqrt(sumsq/NR - (sum/NR)**2)}' $CBF_dir/mean_perf.txt`
    #
    # # Calculate global perfusion mean
    # set perf_mean = `awk '{sum+=$1} END {print (sum/NR)}' $CBF_dir/mean_perf.txt`
    #
    #
    # # Calculate acceptable limits +/- 2.5 Standard deviations
    # cat -n $CBF_dir/mean_perf.txt | awk '{if ($2<('$perf_mean'+(2.5*'$std'))) print $0}' | awk '{if ($2>('$perf_mean'-(2.5*'$std'))) print $1-1, $2}' > $CBF_dir/mean_keep_volumes.txt
    # echo "set size ratio 0.167; set term png size 747,167 ; set out '$CBF_dir/mean_perf.png'; plot '$CBF_dir/mean_perf.txt' using 1 with lines;" | gnuplot
    #
    # endif
    #
    # # Standard Deviation Check
    # echo "std check"
    #
    # if (1) then
    # set std_std = `awk '{sum+=$1; sumsq+=$1*$1} END {print sqrt(sumsq/NR - (sum/NR)**2)}' $CBF_dir/std_perf.txt`
    # set std_mean = `awk '{sum+=$1} END {print (sum/NR)}' $CBF_dir/std_perf.txt`
    #
    #
    # echo "set size ratio 0.167; set term png size 747,167 ; set out '$CBF_dir/std_perf.png'; plot '$CBF_dir/std_perf.txt' using 1 with lines;" | gnuplot
    #
    #
    #
    # set std_criterion = 2.25
    #
    # cat -n $CBF_dir/std_perf.txt | awk '{if ($2<('$std_mean'+('$std_criterion'*'$std_std'))) print $1-1, $2}' > $CBF_dir/std_keep_volumes.txt
    # cat $CBF_dir/mean_keep_volumes.txt $CBF_dir/std_keep_volumes.txt | sort -n | awk '{print $1}' | uniq -d > $CBF_dir/keep_volumes.txt
    #
    #
    # echo "generating filtered perfusion series"
    #
    #
    # set std_kept_volumes =  `wc -l $CBF_dir/std_keep_volumes.txt | awk '{print $1}'`
    # set mean_kept_volumes =  `wc -l $CBF_dir/mean_keep_volumes.txt | awk '{print $1}'`
    #
    # set kept_volumes = `wc -l $CBF_dir/keep_volumes.txt | awk '{print $1}'`
    #
    # set keep_files = `awk '{print "'$CBF_dir'/tmp/perfsub_org*0" $1 ".nii.gz"}' $CBF_dir/keep_volumes.txt`
    # fslmerge -t  $CBF_dir/$series_name:r:r_perfsub_filt.nii.gz $keep_files
    #
    # endif
    #
    # #
    # # Over filter check
    # #
    #
    #
    # echo "overfiltering check"
    #
    # set overfiltering_criterion = 2
    # set stable = `awk 'BEGIN {max=0;min=100000}{if ( max <= $1) max=$1; if ( min >= $1) min=$1} END {print (log(max-min) < '$overfiltering_criterion')}' $CBF_dir/std_perf.txt`
    #
    #
    #
    # #############################################
    #
    # echo "making CBF Volume"
    #
    # if (1) then
    # #set cbf_scale = "./cbf_scale_factors.nii.gz"
    # set cbf_scale = -10  # This has been arbitrarily set. I am using a negative number because Control/Label pairs have been swapped in my data set.
    #
    # fslmaths $CBF_dir/$series_name:r:r_perfsub_org.nii.gz -Tmean -mul $cbf_scale -mul 3.0  $CBF_dir/$series_name:r:r_cbf.nii.gz -odt float
    # fslmaths $CBF_dir/$series_name:r:r_perfsub_filt.nii.gz  -Tmean -mul $cbf_scale -mul 3.0  $CBF_dir/$series_name:r:r_cbf_filt.nii.gz -odt float
    # endif
    #
    #
    # #############################################
    #
    # echo "mask CBF Images"
    #
    # set global_CBF_org = `fslstats  $CBF_dir/$series_name:r:r_cbf.nii.gz -k $CBF_dir/ref_vol_brain_mask.nii.gz -M`
    # set global_CBF_filt = `fslstats $CBF_dir/$series_name:r:r_cbf_filt.nii.gz -k $CBF_dir/ref_vol_brain_mask.nii.gz -M`
    # @ filtered_volumes = $total_perf_volumes - $kept_volumes
    # @ std_filtered_volumes = $total_perf_volumes - $std_kept_volumes
    # @ mean_filtered_volumes = $total_perf_volumes - $mean_kept_volumes
    #
    # #Mask CBF
    # fslmaths $CBF_dir/$series_name:r:r_cbf.nii.gz -mul $CBF_dir/ref_vol_brain_mask.nii.gz $CBF_dir/$series_name:r:r_cbf_brain.nii.gz
    # fslmaths $CBF_dir/$series_name:r:r_cbf_filt.nii.gz -mul $CBF_dir/ref_vol_brain_mask.nii.gz  $CBF_dir/$series_name:r:r_cbf_filt_brain.nii.gz
    # fslmaths $CBF_dir/$series_name:r:r_cbf.nii.gz -sub $CBF_dir/$series_name:r:r_cbf_filt.nii.gz  $CBF_dir/discarded_cbf.nii.gz
    #
    #
    # #############################################
    #
    # echo== 1 ) then
    #   cp $CBF_dir/$series_name:r:r_cbf_brain.nii.gz $CBF_dir/$series_name:r:r_cbf_brain_incl.nii.gz
    #   set include_file = $CBF_dir/$series_name:r:r_cbf_brain_incl.nii.gz
    #   set include_global_cbf = $global_CBF_org
    #   set stable_text = "original"
    #   set filtered_volumes = " 0 "
    #   set std_filtered_volumes = " 0 "
    #   set mean_filtered_volumes = " 0 "
    # else
    #   cp $CBF_dir/$series_name:r:r_carded_cbf_hcs.png
    # slicer $CBF_dir/scalp.nii.gz -s 2 -i 0 200 -A 896 $CBF_dir/scalp_h.png
    #
    #
    # #Generate report
    # echo '<html>' > $CBF_dir/cbf_report.html
    # echo '<hr><p><b>'$series4d'</b><br>' >> $CBF_dir/cbf_report.html
    # #global CBF
    # echo '<hr><p><bMG BORDER=0 SRC="std_perf.png">' >> $CBF_dir/cbf_report.html
    # #images
    # echo '<hr><p>Brain Extracted CBF (sagittal, coronal, horizontal)<p><IMG BORDER=0 SRC="cbf_brain_hcs.png"><p>' >> $CBF_dir/cbf_report.html
    # echo '<p>Brain Extracted CBF (horizontal sections)<p><IMG BORDER=0 SRC="cbf_brain_h.png"><p>' >> $CBF_dir/cbf_report.h
    #
    # """
