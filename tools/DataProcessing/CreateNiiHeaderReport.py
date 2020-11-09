from logging import log
import Nifti as ni
import logging
import sys
import os.path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():

   # if len(sys.argv) <= 2:
   #    logger.error("Missing argument; 1: nifti path 1, 2: nifti path 2")
   #    quit()

    logger.info("starting header comparison...")

    path_1 = "/home/ludwig/Repositories/Study/KAP/GliomaInput/19P_HavingResults/rec006_pre/" #sys.argv[1]
    path_2 = "/home/ludwig/Repositories/Study/KAP/GliomaInput/TGM_63patients/tgm001_preop/" #sys.argv[2]

    for component in os.listdir(path_1):     
        join_1 = f"{path_1}{component}"
        join_2 = f"{path_2}{component}"


        if os.path.isfile(join_1):

            logger.info(f"comparing {join_1} with {join_2}...")

            img_1 = ni.read_image(join_1)
            img_2 = ni.read_image(join_2)

            (l1, l2, l3) = ni.create_metadata_report(img_1, img_2)

            if len(l1) > 0:
                logger.info(f"differing values in {join_1} and {join_2}:")
                logger.info(f"format: (key, val img_1, val img_2")
                print_arr(l1)

            if len(l2) > 0:
                logger.info(f"keys and values only in {join_1}:")
                print_arr(l2)

            if len(l3) > 0:
                logger.info(f"keys and values only in {join_2}:")
                print_arr(l3)

            if len(l1) + len(l2) +len(l3) <= 0:
                logger.info("no meta data differ")

            #img = ni.copy_meta_data(img_1, img_2)
            #img_2 = ni.correct_xyz_units_if_necessary(img_2)
            
            print("")
            #ni.write_image(img, join_2)


    logger.info("done")

def print_arr(arr):
    arr = sorted(arr)
    for line in arr:
        logger.info(f"{line}")

if __name__ == "__main__":
    main()