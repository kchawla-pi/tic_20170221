#!/usr/bin/env python

"""

"""
from __future__ import division
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import sys
import numpy as np
from numpy import linalg
from random import random

import nibabel as nb
import pandas as pd
import scipy.ndimage as ndimage
import argparse

from scipy.ndimage.morphology import binary_erosion, binary_dilation, binary_opening

import labels
import _utilities as util
import scipy.stats as stats


# https://github.com/minillinim/ellipsoid/blob/master/ellipsoid.py

class EllipsoidTool:
    """Some stuff for playing with ellipsoids"""
    def __init__(self): pass
    
    def getMinVolEllipse(self, P=None, tolerance=0.01):
        """ Find the minimum volume ellipsoid which holds all the points
        
        Based on work by Nima Moshtagh
        http://www.mathworks.com/matlabcentral/fileexchange/9542
        and also by looking at:
        http://cctbx.sourceforge.net/current/python/scitbx.math.minimum_covering_ellipsoid.html
        Which is based on the first reference anyway!
        
        Here, P is a numpy array of N dimensional points like this:
        P = [[x,y,z,...], <-- one point per line
             [x,y,z,...],
             [x,y,z,...]]
        
        Returns:
        (center, radii, rotation)
        
        """
        (N, d) = np.shape(P)
        d = float(d)
    
        # Q will be our working array
        Q = np.vstack([np.copy(P.T), np.ones(N)]) 
        QT = Q.T
        
        # initializations
        err = 1.0 + tolerance
        u = (1.0 / N) * np.ones(N)

        # Khachiyan Algorithm
        while err > tolerance:
            V = np.dot(Q, np.dot(np.diag(u), QT))
            M = np.diag(np.dot(QT , np.dot(linalg.inv(V), Q)))    # M the diagonal vector of an NxN matrix
            j = np.argmax(M)
            maximum = M[j]
            step_size = (maximum - d - 1.0) / ((d + 1.0) * (maximum - 1.0))
            new_u = (1.0 - step_size) * u
            new_u[j] += step_size
            err = np.linalg.norm(new_u - u)
            u = new_u

        # center of the ellipse 
        center = np.dot(P.T, u)
    
        # the A matrix for the ellipse
        A = linalg.inv(
                       np.dot(P.T, np.dot(np.diag(u), P)) - 
                       np.array([[a * b for b in center] for a in center])
                       ) / d
                       
        # Get the values we'd like to return
        U, s, rotation = linalg.svd(A)
        radii = 1.0/np.sqrt(s)
        
        return (center, radii, rotation)

    def getEllipsoidVolume(self, radii):
        """Calculate the volume of the blob"""
        return 4./3.*np.pi*radii[0]*radii[1]*radii[2]

    def getEllipsoidFA(self, radii):
        """Calculate the Fractional Anisotropy of the blob"""
        mean_radii = np.mean(radii)
        diff_radii = radii-mean_radii
        return  np.sqrt( 3./2. ) * np.sqrt( np.sum(np.dot( diff_radii, diff_radii)) / np.dot( radii, radii )  )


    def plotEllipsoid(self, center, radii, rotation, ax=None, plotAxes=False, cageColor='b', cageAlpha=0.2):
        """Plot an ellipsoid"""
        make_ax = ax == None
        if make_ax:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            
        u = np.linspace(0.0, 2.0 * np.pi, 100)
        v = np.linspace(0.0, np.pi, 100)
        
        # cartesian coordinates that correspond to the spherical angles:
        x = radii[0] * np.outer(np.cos(u), np.sin(v))
        y = radii[1] * np.outer(np.sin(u), np.sin(v))
        z = radii[2] * np.outer(np.ones_like(u), np.cos(v))
        # rotate accordingly
        for i in range(len(x)):
            for j in range(len(x)):
                [x[i,j],y[i,j],z[i,j]] = np.dot([x[i,j],y[i,j],z[i,j]], rotation) + center
    
        if plotAxes:
            # make some purdy axes
            axes = np.array([[radii[0],0.0,0.0],
                             [0.0,radii[1],0.0],
                             [0.0,0.0,radii[2]]])
            # rotate accordingly
            for i in range(len(axes)):
                axes[i] = np.dot(axes[i], rotation)
    
    
            # plot axes
            for p in axes:
                X3 = np.linspace(-p[0], p[0], 100) + center[0]
                Y3 = np.linspace(-p[1], p[1], 100) + center[1]
                Z3 = np.linspace(-p[2], p[2], 100) + center[2]
                ax.plot(X3, Y3, Z3, color=cageColor)
    
        # plot ellipsoid
        ax.plot_wireframe(x, y, z,  rstride=4, cstride=4, color=cageColor, alpha=cageAlpha)
        
        if make_ax:
            plt.show()
            plt.close(fig)
            del fig


#
# Main Function
#

if __name__ == "__main__":

     ## Parsing Arguments
     #
     #

     usage = "usage: %prog [options] arg1 arg2"

     parser = argparse.ArgumentParser(prog='ellipsoid')

     parser.add_argument("in_nii",    help="Label NIFTI filename ")
     parser.add_argument("--out",    help="Label NIFTI filename ", default=None)

     parser.add_argument("--labels",        help="Label indices to analyze", type=int, nargs="*", default = None )
     parser.add_argument("--sort",          help="Label indices to analyze", type=str, default = 'label' )

     parser.add_argument("--stats",                help="Stats to report (default=All)", type=str, nargs="*", default=None)

     parser.add_argument("-d","--display",  help="Display Results", action="store_true", default=False )
     parser.add_argument("-v","--verbose",  help="Verbose flag",      action="store_true", default=False )
     parser.add_argument("--verbose_nlines", help="Number of lines to display (default=10)",     default=10 )

     parser.add_argument("--debug",         help="Debug flag",      action="store_true", default=False )

     inArgs = parser.parse_args()


     if inArgs.debug:

         print("inArgs.in_nii   = " +  inArgs.in_nii + '\n')
         print("inArgs.debug     = " +  str(inArgs.debug))
         print("inArgs.verbose   = " +  str(inArgs.verbose))


     label_nii    = labels.read_nifti_file( inArgs.in_nii, 'Label file does not exist' )
     label_array  = label_nii.get_data()

     labels = labels.get_labels( inArgs.labels, label_array)

     df_stats  = pd.DataFrame(columns=('label', 'com_x', 'com_y', 'com_z', 
                                       'label_volume', 'ellipsoid_volume',
                                       'center_x', 'center_y', 'center_z',
                                       'r1', 'r2', 'r3', 'fa' ))
     if inArgs.stats is not None:
         stats_list = inArgs.stats
     else:
         stats_list = list(df_stats.columns.values)

     if inArgs.verbose:
         jj=0
         pd.set_option('expand_frame_repr', False)

     for ii in labels:

         mask = label_array == ii 

         label_volume = int(np.sum(  mask  ))         
         com_x, com_y, com_z = np.round( ndimage.measurements.center_of_mass(mask), 0)

         mask_where = np.where( mask )

         P        = np.asarray( zip( mask_where[0].tolist(), mask_where[1].tolist(), mask_where[2].tolist()))

         try:
             ET = EllipsoidTool()
             (center, radii, rotation) = ET.getMinVolEllipse( P, .01)                 

             ellipsoid_volume = ET.getEllipsoidVolume(radii)
             ellipsoid_fa     = ET.getEllipsoidFA(radii)

         except:
             center           = radii        = [np.nan]*3
             ellipsoid_volume = ellipsoid_fa = np.nan

         df_stats.loc[ len(df_stats) ] = [ ii, com_x, com_y, com_z, 
                                           label_volume, ellipsoid_volume,
                                           center[0], center[1], center[2],
                                           radii[0], radii[1], radii[2], ellipsoid_fa ]

         if inArgs.verbose:
             if jj==(inArgs.verbose_nlines-1):
                 print(' ')
                 df_verbose =  df_stats.tail(inArgs.verbose_nlines) 
                 print (df_verbose[ stats_list].to_string(formatters={'label_volume':'{:,.0f}'.format,'ellipsoid_volume':'{:,.3f}'.format,
                                                        'com_x':'{:,.2f}'.format,'com_y':'{:,.2f}'.format, 'com_z':'{:,.2f}'.format,
                                                        'center_x':'{:,.2f}'.format,'center_y':'{:,.2f}'.format, 'center_z':'{:,.2f}'.format,
                                                        'r1':'{:,.2f}'.format,'r2':'{:,.2f}'.format, 'r3':'{:,.2f}'.format, 'fa':'{:,.3f}'.format }) )

                 jj = 0
             else:
                 jj += 1

         
     if inArgs.verbose:
         print('\n\n')
         print (df_stats[stats_list])
         print('\n')

     if not inArgs.out == None:
         df_stats[ stats_list ].to_csv(inArgs.out, index=False ) 
