import Nifti as ni
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("starting image normalization...")

    if len(sys.argv) <= 1:
        logger.error("Missing argument; 1: base path")
        quit()

    prefix = ".nii.gz"
    base_path = sys.argv[1]

    logger.info("normalize FET image...")
    img = ni.read_image(f"{base_path}FET{prefix}")
    img = ni.normalize_image(img)
    ni.write_image(img, f"{base_path}FET{prefix}")

    logger.info("remove background intensity of WM...")
    img = ni.read_image(f"{base_path}WM{prefix}")
    img = ni.clear_background_intensity(img)
    ni.write_image(img, f"{base_path}WM{prefix}")

    logger.info("remove background intensity of GM...")
    img = ni.read_image(f"{base_path}GM{prefix}")
    img = ni.clear_background_intensity(img)
    ni.write_image(img, f"{base_path}GM{prefix}")

    logger.info("done")
    
if __name__ == "__main__":
    main()