import logging
import sys
import os.path
import NiftiNibabel
import NiftiSimpleITK

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("starting image normalization...")

    if len(sys.argv) <= 2:
       logger.error("Missing argument; 1: base path, 2: nifti impl (1: simpleITK, else: nibabel)")
       quit()

    prefix = ".nii.gz"
    base_path = sys.argv[1]
    ni = NiftiSimpleITK.NiftiSimpleITK() if sys.argv[2] == "1" else NiftiNibabel.NiftiNibabel()

    logger.info("normalize Tum_FET image...")
    img = ni.read_image(f"{base_path}Tum_FET{prefix}")
    img = ni.normalize_image(img)
    ni.write_image(img, f"{base_path}Tum_FET{prefix}")

    logger.info("now set background intensity to zero and correct meta data if necessary...")
    for component in os.listdir(base_path):     
        join = f"{base_path}{component}"
        if os.path.isfile(join):

            logger.info(f"remove background intensity of {component}...")
            img = ni.read_image(join)
            img = ni.clear_background_intensity(img)

            logger.info(f"normalizing complete")
            ni.write_image(img, join)

    logger.info("done")
    
if __name__ == "__main__":
    main()