import SimpleITK as sitk
import numpy as np
import logging
import os.path

logger = logging.getLogger(__name__)

def read_image(fileName):
  """
  Reads a nifti file with the given filename
  """
  reader = sitk.ImageFileReader()
  reader.SetImageIO("NiftiImageIO")
  reader.SetFileName(fileName)

  return reader.Execute()

def write_image(image, output_path):
  """
  Writes a nifti image to the specified output path
  """
  writer = sitk.ImageFileWriter()
  writer.SetFileName(output_path)
  writer.SetImageIO("NiftiImageIO")
  writer.Execute(image)

def extract_labels_to_new_image (image, targets):
 """
 Extracts one to many labels and stores it into a new image.
 """
 img_npy = sitk.GetArrayFromImage(image)
 uniques = np.unique(img_npy)
 seg_new = np.zeros_like(img_npy)

 for i in range(len(targets)):
    (src_label,target_label) = targets[i] 
    seg_new[img_npy == src_label] = target_label

 img_corr = sitk.GetImageFromArray(seg_new)
 img_corr.CopyInformation(image)

 return img_corr

def keep_overlapping_voxels(image_a, image_b):
  """
  Compares two images and uses image b as a blend mask.
  """
  kept = 0

  for x in range(image_b.GetSize()[0]):
    for y in range(image_b.GetSize()[1]):
      for z in range(image_b.GetSize()[2]):

        pixel_b = image_b[x,y,z]
        pixel_a = image_a[x,y,z]
        
        if pixel_b <= 0 or pixel_a <= 0:
          image_a[x,y,z] = 0
        else:
          kept += 1
          logger.debug(f"keep voxel at ({x},{y},{z}) because pixel value at A is {pixel_a} and at B is {pixel_b}")

  logger.info(f"kept {kept} unmatching voxels")
  return image_a

def remove_spatially_overlapping_voxels(image_a, image_b):
  """
  Removes all voxels at A if they are set set and at there is a non empty voxel at B at the same index.
  """
  removed = 0

  for x in range(image_b.GetSize()[0]):
    for y in range(image_b.GetSize()[1]):
      for z in range(image_b.GetSize()[2]):

        pixel_b = image_b[x,y,z]
        pixel_a = image_a[x,y,z]
        
        if pixel_b > 0 and pixel_a > 0:
          logger.debug(f"found overlap at ({x},{y},{z}) because pixel value at A is {pixel_a} and at B is {pixel_b}")
          image_a[x,y,z] = 0
          removed += 1

  logger.info(f"removed {removed} overlapping voxels")
  return image_a

def debug_image_information(image):
  """
  Debugs image information, more specific: header data of the nifti image
  """
  for k in image.GetMetaDataKeys():
    v = image.GetMetaData(k)
    logger.debug(f"{k} : {v}")

def create_backup_if_necessary(image, original_image_path):
  """
  Writes a backup image as the new image overwrites the original one
  """
  backup_path = ""
  if original_image_path.endswith(".nii"):
    backup_path = original_image_path.replace(".nii", "") + "_backup.nii"
  elif original_image_path.endswith(".nii.gz"):
    backup_path = original_image_path.replace(".nii.gz", "") + "_backup.nii.gz"
  else:
    backup_path = original_image_path + "_backup.nii.gz"
    
  logger.debug(f"check if backup is available on {backup_path}...")

  if os.path.isfile(backup_path):
    logger.info("backup already exists, skipping step")
  else:
    logger.info("no CSF backup found, creating one...")
    write_image(image, backup_path)