#!/usr/bin/python3

import SimpleITK as sitk
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sys.argv  = ['', 
'/home/ludwig/Repositories/Study/KAP/code/GliomaInput/InputData/Tum_FLAIR.nii.gz', 
'/home/ludwig/Repositories/Study/KAP/code/GliomaInput/InputData/CSF.nii.gz',
'/home/ludwig/output.nii.gz']

#Reads a nifti file with the fiven filename
def read_image(fileName):
  reader = sitk.ImageFileReader()
  reader.SetImageIO("NiftiImageIO")
  reader.SetFileName(fileName)

  return reader.Execute()

#writes a nifti image to the specified output path
def write_image(image, output_path):
  writer = sitk.ImageFileWriter()
  writer.SetFileName(output_path)
  writer.SetImageIO("NiftiImageIO")
  writer.Execute(image)

#debugs image information
def debug_image_information(image):
  for k in image.GetMetaDataKeys():
    v = image.GetMetaData(k)
    logger.debug(f"{k} : {v}")
  logger.debug("--------------------------------")

#naive implementation to remove overlapping voxels of two nii images
def remove_spatially_overlapping_voxels(csf_image, flair_image):
  for x in range(flair_image.GetSize()[0]):
    for y in range(flair_image.GetSize()[1]):
      for z in range(flair_image.GetSize()[2]):

        flair_pixel = flair_image[x,y,z]
        csf_pixel = csf_image[x,y,z]
        
        #overlap
        if flair_pixel > 0 and csf_pixel > 0:
          logger.debug(f"found overlap at ({x},{y},{z}) because pixel value at flair is {flair_pixel} and at csf is {csf_pixel}")
          csf_image[x,y,z] = 0

  return csf_image

if len(sys.argv) <= 3:
    print("Missing argument")
    quit()

flair_image = read_image(sys.argv[1])
csf_image = read_image(sys.argv[2])

debug_image_information(flair_image)
debug_image_information(csf_image)

non_overlapping_csf_image = remove_spatially_overlapping_voxels(csf_image, flair_image)

write_image(non_overlapping_csf_image, sys.argv[3])