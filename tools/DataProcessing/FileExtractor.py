import Nifti as ni
import logging
import sys
import SimpleITK as sitk
import os.path

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

base_path = "/home/ludwig/Repositories/Study/KAP/GliomaInput/TGM_63patients/tgm001_preop/"
prefix = ".nii.gz"

def main():
 seg_file = base_path + "brats_seg" + prefix
 fet_file = base_path + "brats_fet" + prefix

 logger.info(f"read segmentation file {seg_file}...")
 img = ni.read_image(seg_file)

 logger.info(f"extract TUM_FLAIR and TUM_C1 image...")
 tum_flair = ni.extract_labels_to_new_image(img, [(1,1),(2,1),(4,1)])
 tum_c1 = ni.extract_labels_to_new_image(img, [(1,1),(4,4)])

 ni.write_image(tum_flair, base_path + "Tum_FLAIR"  + prefix) 
 ni.write_image(tum_c1, base_path + "Tum_T1c"  + prefix) 

 logger.info(f"read FET image...")
 img = ni.read_image(fet_file)
 logger.info(f"extract TUM_FET image...")
 tum_fet = ni.keep_overlapping_voxels(img, tum_c1)
 ni.write_image(tum_fet, base_path + "Tum_FET"  + prefix) 

 logger.info(f"renaming tissue files...")
 rename("brats_fet", "FET")
 rename("brats_fla", "FLAIR")
 rename("brats_t1c", "CSF")
 rename("brats_t1c_csf", "T1c")
 rename("brats_t1c_gm", "GM")
 rename("brats_t1c_wm", "WM")

 logger.info(f"delete old files...")
 os.remove(seg_file)
 os.remove(base_path + "brats_tissues" + prefix)

 logger.info(f"done")
 return

def rename(old, new):
 os.rename(base_path + old + prefix, base_path + new  + prefix)
 
if __name__ == "__main__":
    main()