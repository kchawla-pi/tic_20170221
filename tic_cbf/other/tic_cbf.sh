# TIC_CBF
export TIC_CBF_PATH=$TIC_PATH/tic_cbf/''  # Add path information here
export TIC_CBF_PYTHONPATH=${TIC_CBF_PATH}/cbf

export PYTHONPATH=${TIC_CBF_PATH}:$PYTHONPATH

alias  tic_cbf='python ${TIC_CBF_PYTHONPATH}/cbf.py'
alias  tic_cbf_nipype='python ${TIC_CBF_PYTHONPATH}/cbf_nipype.py'


