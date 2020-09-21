import SimpleITK as sitk
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
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

#simple implementation to remove overlapping voxels of two nii images
def remove_spatially_overlapping_voxels(csf_image, flair_image):
  for x in range(flair_image.GetSize()[0]):
    for y in range(flair_image.GetSize()[1]):
      for z in range(flair_image.GetSize()[2]):

        flair_pixel = flair_image[x,y,z]
        csf_pixel = csf_image[x,y,z]
        
        if flair_pixel > 0 and csf_pixel > 0:
          logger.debug(f"found overlap at ({x},{y},{z}) because pixel value at flair is {flair_pixel} and at csf is {csf_pixel}")
          csf_image[x,y,z] = 0

  return csf_image

#main routine structuring process
def main():
  logger.info("starting voxel deletion...")

  if len(sys.argv) <= 3:
      logger.error("Missing argument; 1: flair image, 2: csf image, 3: output file")
      quit()

  logger.info(f"reading FLAIR image {sys.argv[1]}...")
  flair_image = read_image(sys.argv[1])
  debug_image_information(flair_image)

  logger.info(f"reading CSF image {sys.argv[2]}...")
  csf_image = read_image(sys.argv[2])
  debug_image_information(csf_image)

  logger.info("remove overlapping voxels in CSF image...")
  non_overlapping_csf_image = remove_spatially_overlapping_voxels(csf_image, flair_image)

  logger.info(f"writing CSF image to {sys.argv[3]}...")
  write_image(non_overlapping_csf_image, sys.argv[3])

  logger.info("done")

if __name__ == "__main__":
    main()