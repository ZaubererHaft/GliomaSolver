import logging
import sys
import os.path
import nibabel as nib
import numpy as np
from sklearn.preprocessing import MinMaxScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

path = None

def main():

    if len(sys.argv) <= 1:
        logger.error("Missing argument; 1:  base path")
        quit()

    logger.info("starting image processing...")

    global path
    path = sys.argv[1]

    prefix = ".nii.gz"
    seg_file = path + "brats_seg" + prefix
    fet_file = path + "brats_fet" + prefix

    seg_img = nib.load(seg_file)
    fet_img = nib.load(fet_file)

    logger.info(f"extracting Tum_FLAIR and Tum_T1c...")

    tum_flair = extract_labels_to_new_image(seg_img, [(1,1),(2,1),(4,1)])
    tum_c1 = extract_labels_to_new_image(seg_img, [(1,4),(4,1)])

    clipped_img = nib.Nifti1Image(tum_flair, seg_img.affine, seg_img.header)
    nib.save(clipped_img, path + "Tum_FLAIR" + prefix)

    clipped_img = nib.Nifti1Image(tum_c1, seg_img.affine, seg_img.header)
    nib.save(clipped_img, path + "Tum_T1c" + prefix)

    fet_data = fet_img.get_fdata()
    kept = 0

    logger.info(f"extracting Tum_FET by intersecting FET and Tum_T1c...")
    for x in range(fet_img.header.get_data_shape()[0]):
        for y in range(fet_img.header.get_data_shape()[1]):
            for z in range(fet_img.header.get_data_shape()[2]):

                pixel_b = tum_c1[x,y,z]
                pixel_a = fet_data[x,y,z]
        
                if pixel_b <= 0 or pixel_a <= 0:
                    fet_data[x,y,z] = 0
                else:
                    kept += 1
    logger.info(f"kept {kept} unmatching voxels")

    logger.info("normalize Tum_FET...")
    x = fet_img.header.get_data_shape()[0]
    y = fet_img.header.get_data_shape()[1]
    z = fet_img.header.get_data_shape()[2]
    fet_data = fet_data.reshape((x*y, z))

    scaler = MinMaxScaler()
    scaler = scaler.fit(fet_data)
    fet_data = scaler.transform(fet_data)
    fet_data = fet_data.reshape((x, y, z))

    clipped_img = nib.Nifti1Image(fet_data, seg_img.affine, seg_img.header)
    nib.save(clipped_img, path + "Tum_FET" + prefix)

    logger.info("extract patient anatomy...")

    tissue_img = nib.load(path + "brats_tissues" + prefix)
    csf_data = extract_labels_to_new_image(tissue_img, [(1,1)])
    clipped_img = nib.Nifti1Image(csf_data, tissue_img.affine, tissue_img.header)
    nib.save(clipped_img, path + "CSF" + prefix)

    gm_data = extract_labels_to_new_image(tissue_img, [(2,1)])
    clipped_img = nib.Nifti1Image(gm_data, tissue_img.affine, tissue_img.header)
    nib.save(clipped_img, path + "GM" + prefix)

    wm_data = extract_labels_to_new_image(tissue_img, [(3,1)])
    clipped_img = nib.Nifti1Image(wm_data, tissue_img.affine, tissue_img.header)
    nib.save(clipped_img, path + "WM" + prefix)

    logger.info("rename tissue files...")

    rename("brats_fet", "FET")
    rename("brats_fla", "FLAIR")
    rename("brats_t1c", "T1c")

    logger.info("cleanup...")

    os.remove(path + "brats_seg" + prefix)
    os.remove(path + "brats_tissues" + prefix)
    os.remove(path + "brats_t1c_csf" + prefix)
    os.remove(path + "brats_t1c_gm" + prefix)
    os.remove(path + "brats_t1c_wm" + prefix)


    logger.info("remove voxels in CSF image overlapping with the Tum_FLAIR image and clear intensity...")

    csf_img = nib.load(path + "CSF" + prefix)
    csf_data = csf_img.get_fdata()
    csf_voxel = csf_data[0,0,0]

    removed = 0
    for x in range(csf_img.header.get_data_shape()[0]):
        for y in range(csf_img.header.get_data_shape()[1]):
            for z in range(csf_img.header.get_data_shape()[2]):

                pixel_b = csf_data[x,y,z]
                pixel_a = tum_flair[x,y,z]

                if pixel_b <= csf_voxel:
                    csf_data[x,y,z] = 0
                elif pixel_b > 0 and pixel_a > 0:
                    csf_data[x,y,z] = 0
                    removed += 1

    clipped_img = nib.Nifti1Image(csf_data, csf_img.affine, csf_img.header)
    nib.save(clipped_img, path + "CSF" + prefix)
    logger.info(f"removed {removed} voxels")
    
    logger.info("done")
    
def rename(old, new):
    os.rename(path + old + ".nii.gz", path + new  + ".nii.gz")

def extract_labels_to_new_image (image, targets):
  """
  Extracts one to many labels and stores it into a new image.
  """
  img_npy = image.get_fdata()
  seg_new = np.zeros_like(img_npy)

  for i in range(len(targets)):
    (src_label,target_label) = targets[i] 
    seg_new[img_npy == src_label] = target_label

  return seg_new

if __name__ == "__main__":
    main()