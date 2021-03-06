import logging
import sys
import NiftiNibabel
import NiftiSimpleITK

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
  """
  Main routine structuring process
  """
  logger.info("starting voxel removal...")

  if len(sys.argv) <= 2:
      logger.error("Missing argument; 1: base path, 2: nifti impl (1: simpleITK, else: nibabel)")
      quit()

  base_path = sys.argv[1]
  ni = NiftiSimpleITK.NiftiSimpleITK() if sys.argv[2] == "1" else NiftiNibabel.NiftiNibabel()

  flair_image_path = base_path + "Tum_FLAIR.nii.gz"
  csf_image_path = base_path + "CSF.nii.gz"

  logger.info(f"reading Tum_FLAIR image...")
  flair_image = ni.read_image(f"{flair_image_path}")

  logger.info(f"reading CSF image...")
  csf_image = ni.read_image(csf_image_path)

  logger.info("remove overlapping voxels in CSF image...")
  non_overlapping_csf_image = ni.remove_overlapping_voxels(csf_image, flair_image)

  logger.info(f"overwrite CSF image at {csf_image_path}...")
  ni.write_image(non_overlapping_csf_image, csf_image_path)

  logger.info("done")

if __name__ == "__main__":
  main()