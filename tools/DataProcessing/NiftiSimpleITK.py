import AbstractNifti
import SimpleITK as sitk
import numpy as np
import logging
from sklearn.preprocessing import MinMaxScaler

class NiftiSimpleITK(AbstractNifti.Nifti):
  logger = logging.getLogger(__name__)

  def read_image(self, fileName):
    reader = sitk.ImageFileReader()
    reader.SetImageIO("NiftiImageIO")
    reader.SetFileName(fileName)

    return reader.Execute()

  def write_image(self, image, output_path):
    writer = sitk.ImageFileWriter()
    writer.SetFileName(output_path)
    writer.SetImageIO("NiftiImageIO")
    writer.Execute(image)

  def create_image(self, array, image_information):
    img_corr = sitk.GetImageFromArray(array)
    img_corr.CopyInformation(image_information)
    return img_corr

  def create_image_by(self, image, reference_image):
    return self.create_image(sitk.GetArrayFromImage(image), reference_image)

  def extract_labels_to_new_image (self, image, targets):
    img_npy = sitk.GetArrayFromImage(image)
    uniques = np.unique(img_npy)
    seg_new = np.zeros_like(img_npy)

    for i in range(len(targets)):
      (src_label,target_label) = targets[i] 
      seg_new[img_npy == src_label] = target_label

    return self.create_image(seg_new, image)

  def keep_overlapping_voxels(self, image_a, image_b):
    kept = 0

    for x in range(image_b.GetSize()[0]):
      for y in range(image_b.GetSize()[1]):
        for z in range(image_b.GetSize()[2]):

          pixel_b = image_b[x,y,z]
          pixel_a = image_a[x,y,z]
          
          if pixel_b <= 0 or pixel_a <= 0:
            image_a[x,y,z] = 0
          else:
            kept += 1
            self.logger.debug(f"keep voxel at ({x},{y},{z}) because pixel value at A is {pixel_a} and at B is {pixel_b}")

    self.logger.info(f"kept {kept} unmatching voxels")
    return image_a

  def remove_overlapping_voxels(self, image_a, image_b):
    removed = 0

    for x in range(image_b.GetSize()[0]):
      for y in range(image_b.GetSize()[1]):
        for z in range(image_b.GetSize()[2]):

          pixel_b = image_b[x,y,z]
          pixel_a = image_a[x,y,z]
          
          if pixel_b > 0 and pixel_a > 0:
            self.logger.debug(f"found overlap at ({x},{y},{z}) because pixel value at A is {pixel_a} and at B is {pixel_b}")
            image_a[x,y,z] = 0
            removed += 1

    self.logger.info(f"removed {removed} overlapping voxels")
    return image_a

  def clear_background_intensity(self, image):
    voxel = image[0,0,0]

    self.logger.info("clear background voxel intensities...")
    
    for x in range(image.GetSize()[0]):
      for y in range(image.GetSize()[1]):
        for z in range(image.GetSize()[2]):

          pixel = image[x,y,z]
          
          if pixel <= voxel:
            image[x,y,z] = 0

    self.logger.info(f"intensity clearance complete")
    return image


  def normalize_image(self, image):
    img_npy = sitk.GetArrayFromImage(image)

    x = image.GetSize()[0]
    y = image.GetSize()[1]
    z = image.GetSize()[2]

    img_npy = img_npy.reshape((x*y, z))

    scaler = MinMaxScaler()
    scaler = scaler.fit(img_npy)
    img_npy = scaler.transform(img_npy)
    img_npy = img_npy.reshape((z, y, x))

    return self.create_image(img_npy, image)

  def create_metadata_report(self, img_1, img_2):
    k1s = img_1.GetMetaDataKeys()
    k2s = img_2.GetMetaDataKeys()

    set_k1 = set(k1s)
    set_k2 = set(k2s)

    in_1_and_two = set_k1 & set_k2
    only_in_1 = set_k1 - set_k2
    only_in_2 = set_k2 - set_k1

    l1 = []
    l2 = []
    l3 = []

    for k in in_1_and_two:
      val1 = img_1.GetMetaData(k)
      val2 = img_2.GetMetaData(k)

      if(val1 != val2):
        l1.append((k, val1, val2))

    for k in only_in_1:
      l2.append((k, img_1.GetMetaData(k)))

    for k in only_in_2:
      l3.append((k, img_2.GetMetaData(k)))

    return (l1, l2, l3)
