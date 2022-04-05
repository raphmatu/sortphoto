
import os
import parser
import logging

from src.processing_folders import setup_folders, generate_time_tree, transfer_photos, list_and_identify_files, \
                                   process_files
from src.processing_photos import generate_photos_new_path
from src.utils import setup_logger

logger = logging.getLogger('logger')


def main(source_path, destination_path):

    logger = setup_logger()
    fileBucket, photo_storage = setup_folders(source_path, destination_path)

    if os.path.exists(fileBucket):
        df = list_and_identify_files(fileBucket=fileBucket)
        df_auto, df_manual = process_files(df)
        df_auto, df_manual = generate_photos_new_path(df_auto, df_manual, photo_storage)

        generate_time_tree(df_auto, photo_storage)
        transfer_photos(df_auto, df_manual)

    else:
        logger.info('"fileBucket" folder can not be found. Please create one')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--source_path', required=False, type=str,
                        help="Indicate the path to the folder containing all the documents to sort")

    parser.add_argument('--destination_path', required=False, type=str,
                        help="Indicate the path to the folder when the sorted files will be moved")

    execution_args = vars(parser.parse_args())
    main(source_path=execution_args['source_path'], destination_path=execution_args['destination_path'])
