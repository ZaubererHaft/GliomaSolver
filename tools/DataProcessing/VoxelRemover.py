import Nifti as ni
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
  """
  Main routine structuring process
  """
  logger.info("starting voxel removal...")

  if len(sys.argv) <= 1:
      logger.error("Missing argument; 1: base path")
      quit()

  base_path = sys.argv[1]
  
  flair_image_path = base_path + "Tum_FLAIR.nii.gz"
  csf_image_path = base_path + "CSF.nii.gz"

  logger.info(f"reading Tum_FLAIR image...")
  flair_image = ni.read_image(f"{flair_image_path}")
  ni.debug_image_information(flair_image)

  logger.info(f"reading CSF image...")
  csf_image = ni.read_image(csf_image_path)
  ni.debug_image_information(csf_image)

  logger.info("remove overlapping voxels in CSF image...")
  non_overlapping_csf_image = ni.remove_spatially_overlapping_voxels(csf_image, flair_image)

  logger.info(f"overwrite CSF image at {csf_image_path}...")
  ni.write_image(non_overlapping_csf_image, csf_image_path)

  logger.info("done")

if __name__ == "__main__":
    main()