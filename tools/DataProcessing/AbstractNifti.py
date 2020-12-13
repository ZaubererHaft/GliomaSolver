import os.path
from abc import ABC, abstractmethod

class Nifti(ABC):

    @abstractmethod
    def read_image(self, fileName):
        """
        Reads a nifti file with the given filename
        """
        return

    @abstractmethod
    def write_image(self, image, output_path):
        """
        Writes a nifti image to the specified output path.
        """
        return 

    @abstractmethod
    def create_image(self, array, reference_image):
        """
        Creates an image with an array and a parent image to get all transfrom information.
        """
        return

    @abstractmethod
    def create_image_by(self, image, reference_image):
        """
        Creates a new image by using the raw data of the first image and the meta data and affine of the reference image.
        """
        return

    @abstractmethod
    def extract_labels_to_new_image (self, image, targets):
        """
        Extracts one to many labels and stores it into a new image.
        """
        return 

    @abstractmethod
    def keep_overlapping_voxels(self, image_a, image_b):
        """
        Compares two images and uses image b as a blend mask.
        """
        return
        
    @abstractmethod
    def remove_overlapping_voxels(self, image_a, image_b):
        """
        Removes all voxels at A if they are set and if there is a non empty voxel at B at the same index.
        """
        return
        
    @abstractmethod
    def clear_background_intensity(self, image):
        """
        Sets the voxels relativ to the top left voxel (0,0,0) to zero
        """
        return 
        
    @abstractmethod
    def normalize_image(self, image):
        """
        Normalizes a nifti image and sets all voxels to values between [0,1]
        """
        return
        
    @abstractmethod
    def create_metadata_report(self, img_1, img_2):
        """
        Creates a triple containing the differences between the header files of the two images.
        """
        
    def create_backup_if_necessary(self, image, original_image_path):
        """
        Writes a backup image as the new image overwrites the original one
        """
        backup_path = ""
        if original_image_path.endswith(".nii"):
            backup_path = original_image_path.replace(".nii", "") + "_backup.nii"
        elif original_image_path.endswith(".nii.gz"):
            backup_path = original_image_path.replace(".nii.gz", "") + "_backup.nii.gz"
        else:
            backup_path = original_image_path + "_backup.nii.gz"
            
        if not os.path.isfile(backup_path):
            self.write_image(image, backup_path)