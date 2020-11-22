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

    if len(sys.argv) <= 2:
        logger.error("Missing argument; 1: reference image path 1, 2: base path")
        quit()

    logger.info("starting header comparison...")

    reference_path = sys.argv[1]
    global path
    path = sys.argv[2]

    reference_img = nib.load(reference_path)

    prefix = ".nii.gz"
    seg_file = path + "brats_seg" + prefix
    fet_file = path + "brats_fet" + prefix

    seg_img = nib.load(seg_file)
    fet_img = nib.load(fet_file)

    logger.info(f"extracting Tum_FLAIR and Tum_T1c...")

    tum_flair = extract_labels_to_new_image(seg_img, [(1,1),(2,1),(4,1)])
    tum_c1 = extract_labels_to_new_image(seg_img, [(1,4),(4,1)])

    clipped_img = nib.Nifti1Image(tum_flair, reference_img.affine, reference_img.header)
    nib.save(clipped_img, path + "Tum_FLAIR" + prefix)

    clipped_img = nib.Nifti1Image(tum_c1, reference_img.affine, reference_img.header)
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

    clipped_img = nib.Nifti1Image(fet_data, reference_img.affine, reference_img.header)
    nib.save(clipped_img, path + "Tum_FET" + prefix)
    
    logger.info("rename tissue files...")

    rename("brats_fet", "FET")
    rename("brats_fla", "FLAIR")
    rename("brats_t1c", "T1c")
    rename("brats_t1c_csf", "CSF")
    rename("brats_t1c_gm", "GM")
    rename("brats_t1c_wm", "WM")

    logger.info("cleanup...")

    os.remove(path + "brats_seg" + prefix)
    os.remove(path + "brats_tissues" + prefix)

    logger.info("fix header...")
    for component in os.listdir(path):     
       join = f"{path}{component}"

       if os.path.isfile(join):
            img = nib.load(join)
            data = img.get_fdata()
            
            clipped_img = nib.Nifti1Image(data, reference_img.affine, reference_img.header)
            nib.save(clipped_img, join)

    
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

    clipped_img = nib.Nifti1Image(csf_data, reference_img.affine, reference_img.header)
    nib.save(clipped_img, path + "CSF" + prefix)
    logger.info(f"kept {kept} unmatching voxels")

    wm_img = nib.load(path + "WM" + prefix)
    wm_data = wm_img.get_fdata()
    wm_voxel = wm_data[0,0,0]

    logger.info("clear background in WM")
    for x in range(wm_img.header.get_data_shape()[0]):
        for y in range(wm_img.header.get_data_shape()[1]):
            for z in range(wm_img.header.get_data_shape()[2]):

                pixel = wm_data[x,y,z]
            
                if pixel <= wm_voxel:
                    wm_data[x,y,z] = 0

    clipped_img = nib.Nifti1Image(wm_data, reference_img.affine, reference_img.header)
    nib.save(clipped_img, path + "WM" + prefix)

    gm_img = nib.load(path + "GM" + prefix)
    gm_data = gm_img.get_fdata()
    gm_voxel = gm_data[0,0,0]

    logger.info("clear background in GM")
    for x in range(gm_img.header.get_data_shape()[0]):
        for y in range(gm_img.header.get_data_shape()[1]):
            for z in range(gm_img.header.get_data_shape()[2]):

                pixel = gm_data[x,y,z]
            
                if pixel <= gm_voxel:
                    gm_data[x,y,z] = 0

    clipped_img = nib.Nifti1Image(gm_data, reference_img.affine, reference_img.header)
    nib.save(clipped_img, path + "GM" + prefix)
    
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