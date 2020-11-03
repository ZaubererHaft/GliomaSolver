import SimpleITK as sitk
import numpy as np
import logging
import os.path
from sklearn.preprocessing import MinMaxScaler

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
  Writes a nifti image to the specified output path.
  """
  writer = sitk.ImageFileWriter()
  writer.SetFileName(output_path)
  writer.SetImageIO("NiftiImageIO")
  writer.Execute(image)

def create_image(array, image_information):
  """
  Creates an image with an array and a parent image to get all transfrom information.
  """
  img_corr = sitk.GetImageFromArray(array)
  img_corr.CopyInformation(image_information)
  img_corr = set_xyz_units(img_corr, "2")
  return img_corr

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

  return create_image(seg_new, image)

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

def clear_background_intensity(image):
  """
  Sets the voxels relativ to the top left voxel (0,0,0) to zero
  """
  voxel = image[0,0,0]

  logger.info("clear background voxel intensities...")
  
  for x in range(image.GetSize()[0]):
    for y in range(image.GetSize()[1]):
      for z in range(image.GetSize()[2]):

        pixel = image[x,y,z]
        
        if pixel <= voxel:
          image[x,y,z] = 0

  logger.info(f"intensity clearance complete")
  return image


def normalize_image(image):
  """
  Normalizes a nifti image and sets all voxels to values between [0,1]
  """
  img_npy = sitk.GetArrayFromImage(image)

  x = image.GetSize()[0]
  y = image.GetSize()[1]
  z = image.GetSize()[2]

  img_npy = img_npy.reshape((x*y, z))

  scaler = MinMaxScaler()
  scaler = scaler.fit(img_npy)
  img_npy = scaler.transform(img_npy)
  img_npy = img_npy.reshape((z, y, x))

  return create_image(img_npy, image)

def correct_xyz_units_if_necessary(image):
  value = None

  if image.HasMetaDataKey("xyzt_units"):
    value = image.GetMetaData("xyzt_units")

  if not value or value != "\x02":
    logger.warning(f"xyzt_tag is not set correcting to x02")
    image = set_xyz_units(image, "\x02")
  else:
    logger.info(f"xyzt_tag is set correctly to x02")

  return image

def set_xyz_units(image, value):
  image.SetMetaData('xyzt_units', value)
  return image

def log_image_information(image):
  """
  Debugs image information, more specific: header data of the nifti image
  """
  for k in image.GetMetaDataKeys():
    v = image.GetMetaData(k)
    logger.info(f"{k} : {v}")

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