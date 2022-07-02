
import argparse

from src.preprocessing import extract_information_from_files
from src.transfer_files import transfer_photos
from src.generate_timeline_folders import generate_time_tree, check_old_folders
from src.setup import setup_logger, setup_folders


def main(source_path, destination_path):

    #source_path = "R://Raph//Perso//photos_iphone_20220606"
    #destination_path = "E://Raph//Photos_chronologie"

    setup_logger()
    source_path, destination_path = setup_folders(source_path, destination_path)

    df_auto, df_manual = extract_information_from_files(source_path, destination_path)
    check_old_folders(destination_path)
    generate_time_tree(df_auto, destination_path)
    transfer_photos(df_auto, df_manual)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('--source_path', required=False, type=str,
                        help="Indicate the path to the folder containing all the documents to sort")

    parser.add_argument('--destination_path', required=False, type=str,
                        help="Indicate the path to the folder when the sorted files will be moved")

    execution_args = vars(parser.parse_args())
    main(source_path=execution_args['source_path'], destination_path=execution_args['destination_path'])
