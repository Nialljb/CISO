import os
import numpy as np
np.set_printoptions(precision=4, suppress=True)
import nibabel as nib

def pixSize():
    data_path = '/flywheel/v0/input/axi'
    for filepath in data_path.rglob('*.nii.gz'):
        studyBrainReference = str(filepath)
        print("studyBrainReference is: ", studyBrainReference)
        n1_img = nib.load(studyBrainReference)
        n1_img

        pix = (n1_img.header['pixdim'])
        pixdim = pix[1]
        # scaleFactor = pixdim[0] * pixdim[1] * pixdim[2]
        # print(scaleFactor)
    
    return pixdim
