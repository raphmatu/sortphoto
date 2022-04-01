
import os
import logging

from src.processing_folders import setup_folders, generate_time_tree, transfer_photos, list_and_identify_files, \
                                   process_files
from src.processing_photos import generate_photos_new_path
from src.utils import setup_logger

logger = logging.getLogger('logger')


def main():

    logger = setup_logger()
    fileBucket, photo_storage = setup_folders()

    if os.path.exists(fileBucket):
        df = list_and_identify_files(fileBucket=fileBucket)
        df_auto, df_manual = process_files(df)
        df_auto, df_manual = generate_photos_new_path(df_auto, df_manual, photo_storage)

        generate_time_tree(df_auto, photo_storage)
        transfer_photos(df_auto, df_manual)

    else:
        logger.info('"fileBucket" folder can not be found. Please create one')


if __name__ == "__main__":
    main()
