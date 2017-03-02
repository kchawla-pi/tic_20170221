#!/usr/bin/env bash
#
# TIC RedCap Link Setup
#

export TIC_REDCAP_LINK_PATH=${TIC_PATH}/tic_redcap_link/

export TIC_MODULES=${TIC_REDCAP_LINK_PATH}/redcap:${TIC_MODULES}
export PYTHONPATH=${TIC_REDCAP_LINK_PATH}/redcap:$PYTHONPATH

source $TIC_REDCAP_LINK_PATH/other/tic_redcap_link_aliases.sh