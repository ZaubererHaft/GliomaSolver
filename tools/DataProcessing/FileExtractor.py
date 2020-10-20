import Nifti as ni
import logging
import sys
import os.path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

base_path = ""
prefix = ".nii.gz"

def main():
 logger.info("starting file extraction...")

 if len(sys.argv) <= 1:
    logger.error("Missing argument; 1: Base Path to patient folder")
    quit()

 global base_path
 base_path = sys.argv[1]

 seg_file = base_path + "brats_seg" + prefix
 fet_file = base_path + "brats_fet" + prefix
 tissue_file = base_path + "brats_tissues" + prefix

 logger.info(f"read segmentation file {seg_file}...")
 seg_img = ni.read_image(seg_file)

 logger.info(f"extract TUM_FLAIR and TUM_C1 image...")
 tum_c1 = extract_and_write_flair_c1(seg_img)

 logger.info(f"read FET image...")
 fet_img = ni.read_image(fet_file)

 logger.info(f"extract TUM_FET image...")
 extract_and_write_fet_image(fet_img, tum_c1)

 logger.info(f"renaming tissue files...")
 rename_tissues_files()

 logger.info(f"delete old files...")
 cleanup([seg_file, tissue_file])

 logger.info(f"done")
 return

def extract_and_write_flair_c1(segmentation_image):
 """
 Extracts the Tum_FLAIR and Tum_C1 images and writes them to the disk.
 """
 tum_flair = ni.extract_labels_to_new_image(segmentation_image, [(1,1),(2,1),(4,1)])
 tum_c1 = ni.extract_labels_to_new_image(segmentation_image, [(1,1),(4,4)])

 ni.write_image(tum_flair, base_path + "Tum_FLAIR"  + prefix) 
 ni.write_image(tum_c1, base_path + "Tum_T1c"  + prefix) 

 return tum_c1

def extract_and_write_fet_image(fet_image, tum_c1):
 """
 Extracts the Tum_FET image with the FET and Tum_C1 image and writes it to the disk.
 """
 tum_fet = ni.keep_overlapping_voxels(fet_image, tum_c1)
 ni.write_image(tum_fet, base_path + "Tum_FET"  + prefix) 

def rename_tissues_files():
 """
 Renames the tissues files to the solver convention
 """
 rename("brats_fet", "FET")
 rename("brats_fla", "FLAIR")
 rename("brats_t1c", "T1c")
 rename("brats_t1c_csf", "CSF")
 rename("brats_t1c_gm", "GM")
 rename("brats_t1c_wm", "WM")

def rename(old, new):
 os.rename(base_path + old + prefix, base_path + new  + prefix)

def cleanup(files):
 for file in files:
    os.remove(file)
 
if __name__ == "__main__":
    main()