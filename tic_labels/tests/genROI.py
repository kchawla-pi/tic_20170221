#!/usr/bin/env python
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import nibabel as nib


def randrange(n, vmin, vmax):
    return (vmax - vmin)*np.random.rand(n) + vmin

def genROI(center1,radius1,shape1,center2,radius2,shape2,showImg):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    data=[]
    nPts=[]
    boxEdge=200
    pts=np.zeros([boxEdge,boxEdge,boxEdge])
    
    com=np.array([0,0,0])
    #generate coordinates of points
    for c, m, center,radius,shape in [('r', 'o',center1, radius1,shape1), ('b', '^',center2,radius2,shape2)]:
        
        xr = range(center[0]-int(radius/2),center[0]+int(radius/2+0.5))
        yr = range(center[1]-int(radius/2),center[1]+int(radius/2+0.5))
        zr = range(center[2]-int(radius/2),center[2]+int(radius/2+0.5))
        xs,ys,zs=np.meshgrid(xr,yr,zr)
        region=np.zeros([boxEdge,boxEdge,boxEdge])
        for i in xr:
            for j in yr:
                for k in zr:
                    if not pts[i,j,k]:
                        if (shape=='sphere' and round(((i-center[0])**2+(j-center[1])**2+(k-center[2])**2)**0.5)<=radius/2) or shape=='cube':
                            com+=[i,j,k]
                            pts[i,j,k]=1
                            region[i,j,k]=1
        nPts.append(np.sum(region))
        coords=np.nonzero(region)
        ax.scatter(coords[0],coords[1],coords[2], c=c, marker=m)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.title('%d and %d points in each regions. But they may overlap.'%(nPts[0],nPts[1]))
    if showImg:
        plt.show()

    totalPts=int(np.sum(pts[pts>0]))
    com=np.round(com/totalPts)
    print ('There should be %d points'%totalPts)
    print ('com should be',com)
    niiImg = nib.Nifti1Image(pts, affine=np.eye(4))
    nib.save(niiImg, 'test3Dcubes.nii.gz')
    return totalPts,com

if __name__=="__main__":
    centers=np.random.randint(20,size=(2,3))+90
    radius=np.random.randint(10,size=(2))+10
    shape=np.random.choice(['cube','sphere'],2,replace=False)
    genROI(centers[0],radius[0],shape[0],centers[1],radius[1],shape[1],1)
