#!/usr/bin/env bash

alias cdtic='cd $TIC_PATH; lsreport_function'
alias cdstudies='cd $STUDIES_PATH; lsreport_function'
alias cdtemplates='cd $TEMPLATES_PATH; lsreport_function'

alias cdixi='cd $TEMPLATE_IXI; lsreport_function'
alias cdinia='cd $TEMPLATE_INIA19; lsreport_function'
alias cdmni='cd $TEMPLATE_MNI; lsreport_function'

alias cdsd='cd $SUBJECTS_DIR; lsreport_function'

alias  fsvinia='fslview $TEMPLATE_INIA19/inia19_rhesus_macaque/inia19_e_T1wFullImage.nii.gz $TEMPLATE_INIA19/inia19_rhesus_macaque/inia19-NeuroMaps.nii.gz:colormap=lut:lut=$TEMPLATE_INIA19/inia19-NeuroMaps.txt &'

alias  fsvfsl='fslview $FSL_DIR/data/standard/MNI152_T1_1mm_brain.nii.gz &'
alias  fsvixi='fslview $TEMPLATE_IXI/ixiTemplate2_e_T1wFullImage.nii.gz &'

alias cda='echo; echo $PWD; cd $(pwd -P); echo $PWD; echo; ls; echo'

alias redcm='source $TIC_TOOLS_PATH/other/unix/dcm_functions.sh'
alias retic='source $TIC_TOOLS_PATH/other/unix/tic_aliases.sh'


alias ag='alias | grep'
alias hg='history | grep '
alias eg='env | grep '
alias lg='ls | grep '

alias lsp='echo; echo $PATH | tr ":" "\n" | cat -n | sort -n -r; echo'          # Enumerates path
alias lspp='echo; echo $PYTHONPATH | tr ":" "\n" | cat -n | sort -n -r; echo'   # Enumerates Python Path
alias lssd='echo; echo $SUBJECTS_DIR; echo'

alias l1='ls -1d'
alias lld='ld -ld'
alias llr='ls -lrt'
alias lls='ls -lrS'

alias frv='freeview'
alias fsv='fslview'
alias fsvall='fslview_all_function'

alias lsreport='lsreport_function'

alias lnflatten='${TIC_TOOLS_PATH}/other/unix/lnflatten.sh'
alias cpflatten='${TIC_TOOLS_PATH}/other/unix/cpflatten.sh'

alias tic_reorient2std='${TIC_TOOLS_PATH}/other/unix/tic_reorient2std.sh ../../reorient *.gz'
alias tic_path='echo; echo $TIC_PATH; echo'

# Aliases to TIC Python functions

alias tic_cumsum_nii='$TIC_TOOLS_PYTHONPATH/cumsum_nii.py'
alias tic_sort_nii='$TIC_TOOLS_PYTHONPATH/sort_nii.py'
alias tic_extract_b0='$TIC_TOOLS_PYTHONPATH/extract_b0.py'
alias tic_extract_volumes='$TIC_TOOLS_PYTHONPATH/extract_volumes.py'
alias tic_plot_overlay='$TIC_TOOLS_PYTHONPATH/plot_overlay.py'
alias tic_ants_ct='$TIC_TOOLS_PYTHONPATH/ants_ct.py'
alias tic_ants_lct='$TIC_TOOLS_PYTHONPATH/ants_lct.py'

