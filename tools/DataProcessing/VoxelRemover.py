import SimpleITK as sitk
import os.path
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Reads a nifti file with the given filename
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

#writes a backup image as the new image overwrites the original one
def create_backup_if_necessary(image, original_image_path):
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

#simple implementation to remove overlapping voxels of two nii images
def remove_spatially_overlapping_voxels(csf_image, flair_image):

  removed = 0

  for x in range(flair_image.GetSize()[0]):
    for y in range(flair_image.GetSize()[1]):
      for z in range(flair_image.GetSize()[2]):

        flair_pixel = flair_image[x,y,z]
        csf_pixel = csf_image[x,y,z]
        
        if flair_pixel > 0 and csf_pixel > 0:
          logger.debug(f"found overlap at ({x},{y},{z}) because pixel value at FLAIR is {flair_pixel} and at CSF is {csf_pixel}")
          csf_image[x,y,z] = 0
          removed += 1

  logger.info(f"removed {removed} overlapping voxels")
  return csf_image


#main routine structuring process
def main():
  logger.info("starting voxel removal...")

  if len(sys.argv) <= 2:
      logger.error("Missing argument; 1: FLAIR image, 2: CSF image, 3: output file")
      quit()

  flair_image_path = sys.argv[1]
  csf_image_path = sys.argv[2]

  logger.info(f"reading FLAIR image {flair_image_path}...")
  flair_image = read_image(flair_image_path)
  debug_image_information(flair_image)

  logger.info(f"reading CSF image {csf_image_path}...")
  csf_image = read_image(csf_image_path)
  debug_image_information(csf_image)

  create_backup_if_necessary(csf_image, csf_image_path)

  logger.info("remove overlapping voxels in CSF image...")
  non_overlapping_csf_image = remove_spatially_overlapping_voxels(csf_image, flair_image)

  logger.info(f"overwrite CSF image at {csf_image_path}...")
  write_image(non_overlapping_csf_image, csf_image_path)

  logger.info("done")

if __name__ == "__main__":
    main()