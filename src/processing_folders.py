
import os
import logging
import shutil
import pandas as pd
from tqdm import tqdm
from pathlib import Path

from src.conf import dictFormat, fileToIgnore
from src.processing_photos import process_photos

logger = logging.getLogger('logger')
FOLDER = os.path.join(str(Path(__file__).parents[1]))


def process_files(df):

    df_photo = df[df['filetype'] == 'photo'].reset_index(drop=True)
    df_video = df[df['filetype'] == 'video'].reset_index(drop=True)
    df_unknown = df[df['filetype'] == 'unknown_filetype'].reset_index(drop=True)

    df_photo = process_photos(df_photo=df_photo)

    # TODO : Implement video sorting script
    # df_video = process_video(df_video=df_video)

    df_auto, df_manual = separate_unsortable_files(df_photo, df_video, df_unknown)

    return df_auto, df_manual


def separate_unsortable_files(df_photo, df_video, df_unknown):

    df_photo_manual = df_photo[df_photo['manual_sort']].reset_index(drop=True)
    df_photo_auto = df_photo[~df_photo['manual_sort']].reset_index(drop=True)
    df_video = df_video.reset_index(drop=True)

    #df_video_manual = df_video[~df_video['manual_sort']].reset_index(drop=True)
    #df_video_auto = df_video[df_video['manual_sort']].reset_index(drop=True)

    df_manual = pd.concat([df_unknown, df_photo_manual, df_video])
    df_auto = df_photo_auto.copy()

    return df_auto, df_manual


def transfer_photos(df_auto, df_manual):

    for df in [df_auto, df_manual]:

        for from_path, to_path in tqdm(zip(df['from_path'], df['to_path']), total=len(df)):
            shutil.copy(from_path, to_path)

    sorted_files = len(df_auto)
    unsorted_files = len(df_manual)
    total_files = sorted_files + unsorted_files
    logger.info('{}/{} files have been successfully sorted'.format(sorted_files, total_files))
    logger.info('{}/{} files need to be sorted manually'.format(unsorted_files, total_files))


def generate_time_tree(df_auto, photo_storage):

    df_photo_metadata_auto_grouped = df_auto.groupby('photo_year')['photo_month_name']\
                                            .agg(lambda x: list(set(x)))\
                                            .reset_index()

    for year, list_months in zip(df_photo_metadata_auto_grouped['photo_year'],
                                 df_photo_metadata_auto_grouped['photo_month_name']):
        year_folder_path = os.path.join(photo_storage, str(year))
        os.makedirs(year_folder_path, exist_ok=True)

        for month in list_months:
            month_folder_path = os.path.join(photo_storage, str(year), month + '/')
            os.makedirs(month_folder_path, exist_ok=True)

    os.makedirs(os.path.join(photo_storage, 'to_sort_manually'), exist_ok=True)


def list_and_identify_files(fileBucket):

    df = _get_filepath(directory=fileBucket)
    df['filetype'] = df['from_path'].map(lambda x: _return_video_or_photo(x))

    return df


def _get_filepath(directory):

    df = pd.DataFrame()
    list_files = []
    for (dirpath, dirnames, filenames) in os.walk(directory):
        list_files += [os.path.join(dirpath, file) for file in filenames if file not in fileToIgnore]

    df['from_path'] = list_files

    logger.info('{} files found. Start processing...'.format(len(list_files)))

    return df


def _return_video_or_photo(filepath):

    extension = os.path.splitext(filepath)[1]
    extension_upper = extension.upper()

    for filetype in dictFormat.keys():
        if extension_upper in dictFormat[filetype]:
            return filetype

    return 'unknown_filetype'


def setup_folders(source_path=None, destination_path=None):

    if not source_path:
        source_path = os.path.join(FOLDER, 'fileBucket')

    if not destination_path:
        destination_path = os.path.join(FOLDER, 'sorted_photos')
        os.makedirs(destination_path, exist_ok=True)

    if source_path:
        if not os.path.exists(source_path):
            logger.info('{} can not be found')
            exit()

    if destination_path:
        if not os.path.exists(destination_path):
            logger.info('{} can not be found')
            exit()

    return source_path, destination_path
