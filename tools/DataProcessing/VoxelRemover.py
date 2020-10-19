import Nifti as ni
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def remove_spatially_overlapping_voxels(csf_image, flair_image):
  """
  Simple implementation to remove overlapping voxels of two nii images
  """
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

def main():
  """
  Main routine structuring process
  """
  logger.info("starting voxel removal...")

  if len(sys.argv) <= 2:
      logger.error("Missing argument; 1: FLAIR image, 2: CSF image, 3: output file")
      quit()

  flair_image_path = sys.argv[1]
  csf_image_path = sys.argv[2]

  logger.info(f"reading FLAIR image {flair_image_path}...")
  flair_image = ni.read_image(flair_image_path)
  ni.debug_image_information(flair_image)

  logger.info(f"reading CSF image {csf_image_path}...")
  csf_image = ni.read_image(csf_image_path)
  ni.debug_image_information(csf_image)

  #backup only for testing purposes
  #ni.create_backup_if_necessary(csf_image, csf_image_path)

  logger.info("remove overlapping voxels in CSF image...")
  non_overlapping_csf_image = remove_spatially_overlapping_voxels(csf_image, flair_image)

  logger.info(f"overwrite CSF image at {csf_image_path}...")
  ni.write_image(non_overlapping_csf_image, csf_image_path)

  logger.info("done")

if __name__ == "__main__":
    main()