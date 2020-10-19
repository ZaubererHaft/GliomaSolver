import Nifti as ni
import logging
import sys
import SimpleITK as sitk

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
 img = ni.read_image("/home/ludwig/Repositories/Study/KAP/GliomaInput/TGM_63patients/tgm001_preop/brats_seg.nii.gz")

 tum_flair = ni.extract_labels_to_new_image(img, [(1,1),(2,1),(4,1)])
 tum_c1 = ni.extract_labels_to_new_image(img, [(1,1),(4,4)])

 ni.write_image(tum_flair, "/home/ludwig/Repositories/Study/KAP/GliomaInput/TGM_63patients/tgm001_preop/tum_flair.nii.gz") 
 ni.write_image(tum_c1, "/home/ludwig/Repositories/Study/KAP/GliomaInput/TGM_63patients/tgm001_preop/tum_c1.nii.gz") 

 img = ni.read_image("/home/ludwig/Repositories/Study/KAP/GliomaInput/TGM_63patients/tgm001_preop/brats_fet.nii.gz")
 tum_fet = ni.keep_overlapping_voxels(img, tum_c1)
 ni.write_image(tum_fet, "/home/ludwig/Repositories/Study/KAP/GliomaInput/TGM_63patients/tgm001_preop/tum_fet.nii.gz") 

 #ToDo: rename

 return

if __name__ == "__main__":
    main()