#!/usr/bin/python3

import SimpleITK as sitk
import sys


sys.argv  = ['', '/home/ludwig/Repositories/Study/KAP/code/GliomaInput/InputData/T1c.nii.gz']

if len(sys.argv) <= 1:
    print('Missing argument')
    quit()

inputData = sys.argv[1]

reader = sitk.ImageFileReader()
reader.SetImageIO("NiftiImageIO")
reader.SetFileName(inputData)
image = reader.Execute()

#toto: remove nonzero voxels

writer = sitk.ImageFileWriter()
writer.SetFileName('/home/ludwig/my_output.nii.gz')
writer.SetImageIO("NiftiImageIO")
writer.Execute(image)