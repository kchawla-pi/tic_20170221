#!/usr/bin/env bash

export TIC_REDCAP_LINK_PATH='/Users/bkraft/PycharmProjects/tic_redcap_link'  # Add path information here
export TIC_REDCAP_LINK_PYTHONPATH=${TIC_REDCAP_LINK_PATH}/redcap_link

export PYTHONPATH=${TIC_REDCAP_LINK_PYTHONPATH}:$PYTHONPATH

alias  redcap_upload='python3 ${TIC_REDCAP_LINK_PYTHONPATH}/redcap_upload.py' 