#!/usr/bin/env bash

# The following two lines should be placed your .tic directory in your tic.sh 
# setup file. 

# export TIC_TOOLS_PATH=$TIC_PATH/tic_tools/''  # Add path information here
# source $TIC_TOOLS_PATH/tic_bashrc_setup.sh


export TIC_TOOLS_PYTHONPATH=${TIC_TOOLS_PATH}/tools
export PYTHONPATH=${TIC_TOOLS_PATH}:${TIC_TOOLS_PYTHONPATH}:$PYTHONPATH

source $TIC_TOOLS_PATH/other/unix/dcm_functions.sh
source $TIC_TOOLS_PATH/other/unix/tic_aliases.sh
source $TIC_TOOLS_PATH/other/unix/tic_functions.sh

export PATH=$TIC_TOOLS_PATH/other/unix/:$PATH
