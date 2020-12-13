import AbstractNifti
import numpy as np
import logging
from sklearn.preprocessing import MinMaxScaler
import nibabel as nib

class NiftiNibabel(AbstractNifti.Nifti):
  logger = logging.getLogger(__name__)

  def read_image(self, fileName):
    return nib.load(fileName)

  def write_image(self, image, output_path):
    nib.save(image, output_path)

  def create_image(self, array, reference_image):
    return nib.Nifti1Image(array, reference_image.affine, reference_image.header)

  def create_image_by(self, image, reference_image):
    return self.create_image(image.get_fdata(), reference_image)

  def extract_labels_to_new_image (self, image, targets):
    img_npy = image.get_fdata()
    seg_new = np.zeros_like(img_npy)

    for i in range(len(targets)):
      (src_label,target_label) = targets[i] 
      seg_new[img_npy == src_label] = target_label

    return self.create_image(seg_new, image)

  def keep_overlapping_voxels(self, image_a, image_b):
    kept = 0
    image_data_a = image_a.get_fdata()
    image_data_b = image_b.get_fdata()

    for x in range(image_b.header.get_data_shape()[0]):
      for y in range(image_b.header.get_data_shape()[1]):
        for z in range(image_b.header.get_data_shape()[2]):

            pixel_b = image_data_b[x,y,z]
            pixel_a = image_data_a[x,y,z]
          
            if pixel_b <= 0 or pixel_a <= 0:
              image_data_a[x,y,z] = 0
            else:
              kept += 1
              self.logger.debug(f"keep voxel at ({x},{y},{z}) because pixel value at A is {pixel_a} and at B is {pixel_b}")

    self.logger.info(f"kept {kept} unmatching voxels")
    return self.create_image(image_data_a, image_a)

  def remove_overlapping_voxels(self, image_a, image_b):
    removed = 0

    image_data_a = image_a.get_fdata()
    image_data_b = image_b.get_fdata()

    for x in range(image_b.header.get_data_shape()[0]):
        for y in range(image_b.header.get_data_shape()[1]):
          for z in range(image_b.header.get_data_shape()[2]):

            pixel_b = image_data_b[x,y,z]
            pixel_a = image_data_a[x,y,z]
          
            if pixel_b > 0 and pixel_a > 0:
              self.logger.debug(f"found overlap at ({x},{y},{z}) because pixel value at A is {pixel_a} and at B is {pixel_b}")
              image_data_a[x,y,z] = 0
              removed += 1

    self.logger.info(f"removed {removed} overlapping voxels")
    return self.create_image(image_data_a, image_a)

  def clear_background_intensity(self, image):
    image_data = image.get_fdata()
    voxel = image_data[0,0,0]

    self.logger.info("clear background voxel intensities...")
    
    for x in range(image.header.get_data_shape()[0]):
        for y in range(image.header.get_data_shape()[1]):
          for z in range(image.header.get_data_shape()[2]):

            pixel = image_data[x,y,z]
          
            if pixel <= voxel:
              image_data[x,y,z] = 0

    self.logger.info(f"intensity clearance complete")
    return self.create_image(image_data, image)


  def normalize_image(self, image):
    x = image.header.get_data_shape()[0]
    y = image.header.get_data_shape()[1]
    z = image.header.get_data_shape()[2]

    image_data = image.get_fdata()
    image_data = image_data.reshape((x*y, z))

    scaler = MinMaxScaler()
    scaler = scaler.fit(image_data)
    image_data = scaler.transform(image_data)
    image_data = image_data.reshape((x, y, z))

    return self.create_image(image_data, image)

  def create_metadata_report(self, img_1, img_2):
    k1s = img_1.header
    k2s = img_2.header

    set_k1 = set(k1s)
    set_k2 = set(k2s)

    in_1_and_two = set_k1 & set_k2
    only_in_1 = set_k1 - set_k2
    only_in_2 = set_k2 - set_k1

    l1 = []
    l2 = []
    l3 = []

    for k in in_1_and_two:
      val1 = img_1.header[k]
      val2 = img_2.header[k]

      if(np.all(val1 != val2)):
        l1.append((k, val1, val2))

    for k in only_in_1:
      l2.append((k, img_1.header[k]))

    for k in only_in_2:
      l3.append((k,img_2.header[k]))

    return (l1, l2, l3)
