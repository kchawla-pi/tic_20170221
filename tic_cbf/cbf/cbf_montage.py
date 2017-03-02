#!/usr/bin/env python

"""
Hello-

MRIcroGL has a full scripting language, you can see examples here
  http://www.mccauslandcenter.sc.edu/mricrogl/about

You can have MRIcroGL run these scripts when it launches, and this allows other programs to control MRIcroGL (for
example having Matlab batch a large set of images). In particular, with Matlab you would use the "system" function to
launch MRIcroGL. There are two methods:

1.) If you place a text file named 'startup.gls' in MRIcroGL's script folder it will run this script when the program
launches.

2.) You can pass the name of a script file to MRIcroGL at launch, for example "MRIcroGL ~/myDir/myScript.gls". This
will cause MRIcroGL to run the specified script.

  a.) A very useful function for these scripts is the "quit;" command. Put this in the last line of your script and
  MRIcroGL will shut down once it has completed running your script. This is useful if you want to save a batch of
  bitmaps and do not want any user interaction. However, be aware that if a user opens and runs a script from the
  graphical user interface with a "quit" the program will shut down as soon as it is done. In particular, if you make
  a "startup.gls" script with "quit" in it and do not delete this file after it is executed users will not be able to
   run MRIcroGL graphically: whenever it is launched it will auotmatically run the startup script and then quit.

3.) Be aware that with OSX the script and application files are both hidden in the application package, and in
general OSX is more finicky about running items (the interface may give you a warning). In any case, with OSX you would
 call the script like this "~/osx/MRIcroGL.app/contents/MacOS/MRIcroGL ~/osx/MRIcroGL.app/script/basic.gls "
	reply
"""
import os
import argparse
import numpy
import nibabel
import nilearn
import subprocess


command = ['/Applications/MRIcroGL/MRIcroGL.app/Contents/MacOS/MRIcroGL',
           '/Users/bkraft/PycharmProjects/tic_cbf/cbf/cbf_montage.gls']



DEVNULL = open(os.devnull, 'wb')
pipe = subprocess.Popen(command, stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)

print(2+2)