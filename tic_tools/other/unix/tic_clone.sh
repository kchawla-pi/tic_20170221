#!/bin/bash
#
# This file will clone repositories from GitHub to run TIC.
#
#
# git clone https://github.com/bkraft4257/tic_tools

#
#
#

TIC_REPOSITORY_PATH=${1-$PWD}
TIC_TOOLS_PATH=${TIC_REPOSITORY_PATH}/tic_tools/

TIC_SETUP_PATH=$HOME/.tic

cd $TIC_REPOSITORY_PATH

# TIC Modules hosted by bkraft4257

for ii in tic_cbf tic_freesurfer tic_labels tic_redcap_link; do
    [ -d $TIC_REPOSITORY_PATH/${ii} ] || git clone https://github.com/bkraft4257/${ii}
    echo
done

# TIC modules hosted by crhamilt

for ii in tic_protocol_check; do
    [ -d $TIC_REPOSITORY_PATH/${ii} ] || git clone https://github.com/crhamilt/${ii}
    echo
done

source  $TIC_TOOLS_PATH/other/unix/tic_initial_setup.sh
