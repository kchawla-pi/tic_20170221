#!/usr/bin/env python3

"""
Use morphsnakes to grow selected points in a image to produce a labels images.
"""

import nibabel as nib
import numpy as np
from matplotlib import pyplot as ppl
import argparse
import pandas as pd
from skimage.morphology import convex_hull_image, binary_dilation, binary_erosion
from tools import morphsnakes


# for morphsnakes
def circle_levelset(shape, center, sqradius):
    """Build a binary function with a circle as the 0.5-levelset."""
    grid = np.mgrid[list(map(slice, shape))].T - center
    phi = sqradius - np.sqrt(np.sum(grid.T**2, 0))
    u = np.float_(phi > 0)
    return u

def grow_labels(img,pts):
    # img can be a filename or a 2D array, returns a 2D nparray

    if isinstance(img,str):
        # load the image - display the first image in the dataset
        img = nib.load(img)
        imgvol = img.get_data()
        shp = imgvol.shape
        if len(shp)==2:
            imgdata = imgvol[:, :]
        elif len(shp) == 3:
            imgdata = imgvol[:, :, 0]
        elif len(shp) == 4:
            imgdata = imgvol[:, :, 0, 0]
        elif len(shp) == 5:
            imgdata = imgvol[:, :, 0, 0, 0]
    else:
        imgdata = img

    # imgdata = np.rot90(np.flipud(imgdata),3)  # should really use the affine transforms in header

    masksum = np.zeros((shp[0],shp[1],1),dtype=int)

    for ptnum,pt in enumerate(pts):
        # Morphological ACWE. Initialization of the level-set.
        macwe = morphsnakes.MorphACWE(imgdata, smoothing=0, lambda1=20, lambda2=1)
        macwe.levelset = circle_levelset(imgdata.shape, pt, 2)

        numiter = 20
        print('Snaking #%d at (%d,%d) intensity= %f'% (ptnum,pt[0],pt[1],imgdata[pt[0],pt[1]]))

        # Iterate.
        for i in range(numiter):
            macwe.step()

        # use convex_hull to get it a bit more 'rounded' and then dilate
        # mask = convex_hull_image(macwe.levelset)
        mask = macwe.levelset
        mask = binary_dilation(mask)

        masksum[:,:,0] = masksum[:,:,0] + mask*(ptnum + 1)

    # dilate a bit

    print('dir(masksum):',dir(masksum))

    return masksum

def xnii(xy,shp):
    # xy is an (x,y) tuple, shp is the shape of the array
    newxy = (shp[0]-xy[1], xy[0])
    return newxy


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Use morphsnakes to grow selected points into a labels image.")
    parser.add_argument("img", type=str,
                        help="Nifti image filename")
    parser.add_argument("pts", type=str,
                        help="List of points in CSV file.")
    args = parser.parse_args()

    img = nib.load(args.img)
    imgdata = img.get_data()
    shp = imgdata.shape

    ptdf = pd.read_csv(args.pts)
    mypts = ptdf.to_records(index=False)
    # pts = [(80,83),(63,85), (71,92)]
    # pts = [(83,80),(85,63), (92,71)]
    niipts = []
    for x,y in mypts:      # convert to Nifti coords
        # niipts.append(xnii((x, y), shp))
        niipts.append((x, y))
    mylabels = grow_labels(args.img,niipts)


    nibmask = nib.Nifti1Image(mylabels, img.affine, img.header)
    nib.save(nibmask,'mylabels.nii.gz')

    fig = ppl.figure()
#    ppl.imshow(np.flipud(np.rot90(imgdata[:,:,0,0],3)), cmap=ppl.cm.gray, interpolation='bicubic', origin='lower')
#     ppl.imshow(imgdata[:,:,0,0], cmap=ppl.cm.gray, interpolation='bicubic', origin='lower')
    ppl.imshow(mylabels, cmap=ppl.cm.gray, alpha = 0.3, interpolation='bicubic', origin='lower')
    ppl.show()

