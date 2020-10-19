import SimpleITK as sitk
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