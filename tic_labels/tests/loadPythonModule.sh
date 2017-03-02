#!/bin/bash

# This script replaces the default behavior of "python -c command" so that some pre-defined modules can be loaded before running the command.

# Try:
#   python -c "print (math.pi)"
# you will get
#   NameError: name 'math' is not defined
# because "math" module is not loaded.

# Now type:
#   alias python='./loadPythonModule.sh'
# But it's recommanded to move loadPythonModule.sh to usr/local/bin so that it can be called everywhere:
#   sudo cp loadPythonModule.sh /usr/local/bin/
#   alias python='loadPythonModule.sh'
# Try:
#   python -c "print (math.pi)"
# now it prints 3.141592653589793 correctly.

# The alias command can be put into ~/.bash_profile (on Mac) or ~/.bashrc (on Linux) for autorun.

PYTHON_PATH=/Users/b2l/anaconda/bin/python  # replace the path with the result from command:
                                            #      which python
DEFAULT_LOAD="import math;" # add your default modules loading commands here.

#echo "Number of arguments:  "$#
if [ $# -eq 2 ] && [ "$1" == '-c' ];then # run python commands after loading pre-defined modules
    echo "*** load pre-defined modules before running commands. ***"
    echo
    DEFAULT_LOAD+=$2
    #echo $DEFAULT_LOAD
    $PYTHON_PATH -c "$DEFAULT_LOAD"
else
    $PYTHON_PATH $@     # run python command normally
fi
