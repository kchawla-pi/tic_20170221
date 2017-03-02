#!/usr/bin/env python3
# coding: utf-8
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Plots several overlay images using nilearn.plot_stat_map.

http://nilearn.github.io/modules/generated/nilearn.plotting.plot_stat_map.html

"""
from __future__ import division

import os
import sys
import argparse
from nilearn import plotting, image
from scipy.interpolate import interp1d
import numpy
from matplotlib import cm



#
# bipolar() copied from https://gist.github.com/endolith/2879736
#
# Copyright 2012 endolith at gmail com
# Copyright 2009 Ged Ridgway at gmail com
# Translation and modification of
# http://www.mathworks.com/matlabcentral/fileexchange/26026-bipolar-colormap
# Based on Manja Lehmann's hand-crafted colormap for cortical visualisation
#

def redblue_bipolar(lutsize=256, n=0.333, interp='linear'):
    """
    Bipolar hot/cold colormap, with neutral central color.

    This colormap is meant for visualizing diverging data; positive
    and negative deviations from a central value.  It is similar to a
    blackbody colormap for positive values, but with a complementary
    "cold" colormap for negative values.

    Parameters
    ----------
    lutsize : int
        The number of elements in the colormap lookup table. (Default is 256.)
    n : float
        The gray value for the neutral middle of the colormap.  (Default is
        1/3.)
        The colormap goes from cyan-blue-neutral-red-yellow if neutral
        is < 0.5, and from blue-cyan-neutral-yellow-red if neutral > 0.5.
        For shaded 3D surfaces, an `n` near 0.5 is better, because it
        minimizes luminance changes that would otherwise obscure shading cues
        for determining 3D structure.
        For 2D heat maps, an `n` near the 0 or 1 extremes is better, for
        maximizing luminance change and showing details of the data.
    interp : str or int, optional
        Specifies the type of interpolation.
        ('linear', 'nearest', 'zero', 'slinear', 'quadratic, 'cubic')
        or as an integer specifying the order of the spline interpolator
        to use. Default is 'linear'.  See `scipy.interpolate.interp1d`.

    Returns
    -------
    out : matplotlib.colors.LinearSegmentedColormap
        The resulting colormap object

    Notes
    -----
    If neutral is exactly 0.5, then a map which yields a linear increase in
    intensity when converted to grayscale is produced. This colormap should
    also be reasonably good
    for colorblind viewers, as it avoids green and is predominantly based on
    the purple-yellow pairing which is easily discriminated by the two common
    types of colorblindness. [2]_

    Examples
    --------
    # >>> from mpl_toolkits.mplot3d import Axes3D
    # >>> from matplotlib import cm
    # >>> import matplotlib.pyplot as plt
    # >>> import numpy as np
    # >>> fig = plt.figure()
    # >>> ax = fig.gca(projection='3d')
    # >>> x = y = np.arange(-4, 4, 0.15)
    # >>> x, y = np.meshgrid(x, y)
    # >>> z = (1- x/2 + x**5 + y**3)*exp(-x**2-y**2)
    # >>> surf = ax.plot_surface(x, y, z, rstride=1, cstride=1, linewidth=0.1,
    # >>>                        vmax=abs(z).max(), vmin=-abs(z).max())
    # >>> fig.colorbar(surf)
    # >>> plt.show()
    # >>> set_cmap(bipolar(201))
    # >>> waitforbuttonpress()
    # >>> set_cmap(bipolar(201, 0.1)) # dark gray as neutral
    # >>> waitforbuttonpress()
    # >>> set_cmap(bipolar(201, 0.9)) # light gray as neutral
    # >>> waitforbuttonpress()
    # >>> set_cmap(bipolar(201, 0.5)) # grayscale-friendly colormap

    References
    ----------
    .. [1] Lehmann Manja, Crutch SJ, Ridgway GR et al. "Cortical thickness
        and voxel-based morphometry in posterior cortical atrophy and typical
        Alzheimer's disease", Neurobiology of Aging, 2009,
        doi:10.1016/j.neurobiolaging.2009.08.017
    .. [2] Brewer, Cynthia A., "Guidelines for Selecting Colors for
        Diverging Schemes on Maps", The Cartographic Journal, Volume 33,
        Number 2, December 1996, pp. 79-86(8)
        http://www.ingentaconnect.com/content/maney/caj/1996/00000033/00000002/art00002
    """
    if n < 0.5:
        if not interp:
            interp = 'linear'  # seems to work well with dark neutral colors  cyan-blue-dark-red-yellow

        _data = (
            (0, 1, 1),  # cyan
            (0, 0, 1),  # blue
            (n, n, n),  # dark neutral
            (1, 0, 0),  # red
            (1, 1, 0),  # yellow
        )
    elif n >= 0.5:
        if not interp:
            interp = 'cubic'  # seems to work better with bright neutral colors blue-cyan-light-yellow-red
            # produces bright yellow or cyan rings otherwise

        _data = (
            (0, 0, 1),  # blue
            (0, 1, 1),  # cyan
            (n, n, n),  # light neutral
            (1, 1, 0),  # yellow
            (1, 0, 0),  # red
        )
    else:
        raise ValueError('n must be 0.0 < n < 1.0')

    xi = numpy.linspace(0, 1, numpy.array(_data).shape[0])
    cm_interp = interp1d(xi, _data, axis=0, kind=interp)
    xnew = numpy.linspace(0, 1, lutsize)
    ynew = cm_interp(xnew)

    # No form of interpolation works without this, but that means the interpolations are not working right.
    ynew = numpy.clip(ynew, 0, 1)

    return cm.colors.LinearSegmentedColormap.from_list('redblue_bipolar', ynew, lutsize)


# ======================================================================================================================
# region Main Function
#

def plot_overlay_ortho(background, overlay, xyz_direction, ncuts, out_dir=os.getcwd(),  cmap='redblue', **kwargs):
    """ Creates a nCut png images from the NIFTI image """

    # Create output directory if it doesn't exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)


    output_file  = os.path.abspath( os.path.join(out_dir, 'overlay_{0}'.format(xyz_direction) + '.png'))

    if cmap is 'redblue':
        cmap = redblue_bipolar()

    elif cmap is 'hot':
        cmap = redblue_bipolar()

    elif cmap is 'jet':
        cmap = redblue_bipolar()

    else:
        cmap = redblue_bipolar()


    plotting.plot_stat_map(overlay, bg_img=background, cmap=cmap,
                           display_mode=xyz_direction, cut_coords=(0,0,0),
                           output_file=output_file,
                           **kwargs
                           )

#endregion


# ======================================================================================================================
# region Main Function
#

def plot_overlay_xyz(background, overlay, xyz_direction, cut_coords, out_dir=os.getcwd(), cmap='redblue', **kwargs):
    """ Creates a nCut png images from the NIFTI image """

    # Create output directory if it doesn't exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Loop over cuts and create background image

#    if len(cut_coords) == 1:
    cuts = plotting.find_cut_slices(image.load_img(background), direction=xyz_direction,
                                      n_cuts=cut_coords, spacing='auto')
#    else:
#        cuts = cut_coords

    for ii,jj in enumerate(cuts):

        output_file  = os.path.abspath( os.path.join(out_dir, 'overlay_{0}_{1:03}'.format(xyz_direction, ii) + '.png'))

        plotting.plot_stat_map(overlay, bg_img=background, cmap=redblue_bipolar(),
                               display_mode=xyz_direction, cut_coords=[jj],
                               output_file=output_file,
                               **kwargs
                               )

#endregion

# ======================================================================================================================
# region Main Function
#

def main():
    """Parameters:

    bg_img : Niimg-like object
        The background image that the ROI/mask will be plotted on top of. If nothing is specified, the MNI152
        template will be used. To turn off background image, just pass “bg_img=False”.

    overlay: Niimg-like object
       The statistical map image

    cut_coords : None, a tuple of floats, or an integer
        The MNI coordinates of the point where the cut is performed If display_mode is ‘ortho’,
        this should be a 3-tuple: (x, y, z) For display_mode == ‘x’, ‘y’, or ‘z’, then these are the coordinates of
        each cut in the corresponding direction. If None is given, the cuts is calculated automaticaly.
        If display_mode is ‘x’, ‘y’ or ‘z’, cut_coords can be an integer, in which case it specifies the
        number of cuts to perform

    output_file : string, or None, optional
        The name of an image file to export the plot to. Valid extensions are .png, .pdf, .svg. If output_file is
        not None, the plot is saved to a file, and the display is closed.

    display_mode : {‘ortho’, ‘x’, ‘y’, ‘z’, ‘yx’, ‘xz’, ‘yz’}
        Choose the direction of the cuts: ‘x’ - sagittal,  ‘y’ - coronal, ‘z’ - axial,
        ‘ortho’ - three cuts are performed in orthogonal directions.

    colorbar : boolean, optional
        If True, display a colorbar on the right of the plots.

    figure : integer or matplotlib figure, optional
        Matplotlib figure used or its number. If None is given, a new figure is created.

    axes : matplotlib axes or 4 tuple of float: (xmin, ymin, width, height), optional
        The axes, or the coordinates, in matplotlib figure space, of the axes used to display the plot. If None,
        the complete figure is used.

    title : string, optional
        The title displayed on the figure.

    threshold : a number, None, or ‘auto’
        If None is given, the image is not thresholded. If a number is given, it is used to threshold the image:
        values below the threshold (in absolute value) are plotted as transparent. If auto is given, the threshold
        is determined magically by analysis of the image.

    annotate : boolean, optional
        If annotate is True, positions and left/right annotation are added to the plot.

    draw_cross : boolean, optional
        If draw_cross is True, a cross is drawn on the plot to indicate the cut plosition.

    black_bg : boolean, optional
        If True, the background of the image is set to be black. If you wish to save figures with a black background,
        you will need to pass “facecolor=’k’, edgecolor=’k’” to matplotlib.pyplot.savefig.

    cmap : matplotlib colormap, optional
        The colormap for specified image. The ccolormap must be symmetrical.

    symmetric_cbar : boolean or ‘auto’, optional, default ‘auto’
        Specifies whether the colorbar should range from -vmax to vmax or from vmin to vmax. Setting to ‘auto’
        will select the latter if the range of the whole image is either positive or negative. Note: The colormap
        will always be set to range from -vmax to vmax.

    dim : float, ‘auto’ (by default), optional
        Dimming factor applied to background image. By default, automatic heuristics are applied based upon the
        background image intensity. Accepted float values, where a typical scan is -1 to 1 (-1 = increase constrast;
        1 = decrease contrast), but larger values can be used for a more pronounced effect. 0 means no dimming.

    vmax : float
        Upper bound for plotting, passed to matplotlib.pyplot.imshow


    Examples:

        tic_plot_overlay brainmask.mgz --bg_img FLAIR.mgz --display_mode ortho   --colorbar --black_bg --threshold .2


    Limitations:

        Colormap is bipolar only.  It needs to be able to be changed.


"""

    usage = "usage: %prog [options] arg1 arg2"

    parser = argparse.ArgumentParser(prog='plot_overlay')


    parser.add_argument('overlay', help="Overlay Image")
    parser.add_argument('--bg_img', help="Background Image")

    parser.add_argument('--out_dir', help="Output directory (./)", default=os.getcwd() )
    parser.add_argument('--display_mode', help="Direction", choices=['x','y','z', 'ortho'], default='z')

#    parser.add_argument('--cut_coords', help="Number of slices", nargs='*', type=int, default=[1])
    parser.add_argument('--nslices', help="Number of slices (5)", type=int, default=5)

    parser.add_argument('--colorbar', help='If True, display a colorbar on the right of the plots (False).',
                        action="store_true", default=False )

    parser.add_argument('--symmetric_cbar', help=('Specifies whether the colorbar should range from -vmax to vmax or'
                                                  'from vmin to vmax. Setting to auto will select the latter if the'
                                                  'range of the whole image is either positive or negative. Note:'
                                                  'The colormap will always be set to range from -vmax to vmax.'
                                                  '(False)'),
                        action="store_true", default=False )

    parser.add_argument('--cmap', help=('Selects colormap for overlay image from a set list. Currently, only colormap '
                                        'supported is the redblue diverging colormap. Other colormaps are expected '
                                        'to be added in the future. (redblue)'), default='redblue_bipolar', choices=['redblue'] )

    parser.add_argument('--annotate',
                        help= ('If annotate is True, positions and left/right '
                               'annotation is added to the plot. (false)'),
                        action="store_true", default=False)

    parser.add_argument('--draw_cross', help= ('If draw_cross is True, a cross is drawn on the plot to '
                                               'indicate the cut plosition. (false)'),
                        action="store_true", default=False)

    parser.add_argument('--alpha', help='Alpha of overlay image (0.8)', type=float, default=.8)

    parser.add_argument('--vmax', help='Upper bound for plotting, passed to matplotlib.pyplot.imshow',
                        type=float, default=None)

    parser.add_argument('--dim', help=('Dimming factor applied to background image. By default, automatic heuristics'
                                       'are applied based upon the background image intensity. Accepted float values,'
                                       'where a typical scan is -1 to 1 (-1 = increase constrast; '
                                       '1 = decrease contrast), but larger values can be used for a more pronounced'
                                       'effect. 0 means no dimming. (0)'),
                        type=float, default=0)

    parser.add_argument('--threshold', help=('If None is given, the image is not thresholded. '
                                             'If a number is given, it is used to threshold the image: '
                                             'values below the threshold (in absolute value) '
                                             'are plotted as transparent. If auto is given, the threshold '
                                             'is determined magically by analysis of the image. (None)'),
                        default=None)

    parser.add_argument('--black_bg', help=('If True, the background of the image is set to be black.'
                                            'If you wish to save figures with a black background,'
                                            'you will need to pass facecolor=k, edgecolor=k to '
                                            'matplotlib.pyplot.savefig. (False)'),
                        action="store_true", default=False)

    parser.add_argument('-v', '--verbose', help='If True, display a colorbar on the right of the plots. (false)',
                        action="store_true", default=False )

    inArgs = parser.parse_args()

    if inArgs.verbose:
        print(inArgs.verbose)

    # Setting the threshold like this is necessary to avoid a bug in nilearn.plot_stat_map

    if inArgs.threshold=='auto' or inArgs.threshold==None:
        threshold=inArgs.threshold
    else:
        threshold = float(inArgs.threshold)



    if 'ortho' in inArgs.display_mode:

        # Ortho plots a single ortho slice at the center of the volume
        plot_overlay_ortho(inArgs.bg_img, inArgs.overlay, inArgs.display_mode, inArgs.nslices, alpha=inArgs.alpha,
                           threshold=threshold,
                           colorbar=inArgs.colorbar, out_dir=inArgs.out_dir,
                           black_bg=inArgs.black_bg,
                           annotate=inArgs.annotate,
                           vmax=inArgs.vmax,
                           dim=inArgs.dim,
                           cmap=inArgs.cmap,
                           symmetric_cbar=inArgs.symmetric_cbar,
                           draw_cross=inArgs.draw_cross)

    else:

        # Plots a series of slices
        plot_overlay_xyz(inArgs.bg_img, inArgs.overlay, inArgs.display_mode, inArgs.nslices, alpha = inArgs.alpha,
                         threshold=threshold,
                         colorbar=inArgs.colorbar, out_dir=inArgs.out_dir,
                         black_bg=inArgs.black_bg,
                         annotate=inArgs.annotate,
                         vmax=inArgs.vmax,
                         dim=inArgs.dim,
                         cmap=inArgs.cmap,
                         symmetric_cbar=inArgs.symmetric_cbar,
                         draw_cross=inArgs.draw_cross)


#endregion

if __name__ == "__main__":
    sys.exit(main())

