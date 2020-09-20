#!/usr/bin/python3

import SimpleITK as sitk
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sys.argv  = ['', 
'/home/ludwig/Repositories/Study/KAP/code/GliomaInput/InputData/FLAIR.nii.gz', 
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

#ToDo: Remove this information
  logger.debug(image.GetSize())
  logger.debug(image.GetOrigin())
  logger.debug(image.GetSpacing())
  logger.debug(image.GetDirection())
  logger.debug(image.GetNumberOfComponentsPerPixel())
  logger.debug(image.GetDimension())
  logger.debug(image.GetPixelIDValue())
  logger.debug(image.GetPixelIDTypeAsString())

def remove_spatially_overlapping_voxels(csf_image, flair_image):
  #ToDo: implement
  return flair_image

if len(sys.argv) <= 3:
    print('Missing argument')
    quit()

flair_image = read_image(sys.argv[1])
csf_image = read_image(sys.argv[2])

debug_image_information(flair_image)
debug_image_information(csf_image)

non_overlapping_flair_image = remove_spatially_overlapping_voxels(csf_image, flair_image)

write_image(non_overlapping_flair_image, sys.argv[3])