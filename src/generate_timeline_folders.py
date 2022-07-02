
import calendar
import shutil
import logging
import os
from tqdm import tqdm

import pandas as pd

from src.conf import FOLDER, fileToIgnore
from src.preprocessing import extract_date_photos

logger = logging.getLogger('logger')


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


def check_old_folders(destination_path):

    try:
        df_locations = pd.read_csv(os.path.join(FOLDER, 'locations.csv'), sep=';')
    except:
        logger.info('No locations.csv file found')
        return None

    df_locations['start_date (YYYY-MM-DD)'] = pd.to_datetime(df_locations['start_date (YYYY-MM-DD)'])
    df_locations['end_date (YYYY-MM-DD)'] = pd.to_datetime(df_locations['end_date (YYYY-MM-DD)'])

    check_if_folders_exist(df_locations, destination_path)
    identify_photos_to_move(df_locations, destination_path)
    create_folder_and_transfer_photos(df_locations)


def identify_photos_to_move(df_locations, destination_path):

    df_locations['end_year'] = df_locations['end_date (YYYY-MM-DD)'].dt.year
    df_locations['year_to_explore'] = df_locations.apply(lambda x: list(range(x['start_year'], x['end_year'] + 1, 1)),
                                                         axis=1)
    df_locations['photos_to_mv'] = df_locations.apply(
        lambda x: _get_photos_to_move_path(x['year_to_explore'], x['start_date (YYYY-MM-DD)'], x['end_date (YYYY-MM-DD)'], destination_path),
        axis=1)

    return df_locations


def check_if_folders_exist(df_locations, destination_path):

    # check if folder name to find if it has already been created
    df_locations['start_year'] = df_locations['start_date (YYYY-MM-DD)'].dt.year
    df_locations['start_month'] = df_locations['start_date (YYYY-MM-DD)'].dt.month
    df_locations['start_month_name'] = df_locations['start_month'].map(lambda x: calendar.month_abbr[x])
    df_locations['folder_to_find'] = df_locations.apply(lambda x: os.path.join(destination_path, str(x['start_year']),
                                                                               '{0:02d}_{1}_{2}'.format(
                                                                                   x['start_month'],
                                                                                   x['start_month_name'],
                                                                                   x['locations'])), axis=1)
    df_locations['is_created'] = df_locations['folder_to_find'].map(lambda x: os.path.exists(x))
    df_locations = df_locations[~df_locations['is_created']]

    return df_locations


def _get_photos_to_move_path(list_year, start_date, end_date, destination_path):
    df_photos_to_mv = pd.DataFrame()
    list_files = []

    for year in list_year:
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(destination_path, str(year))):
            list_files += [os.path.join(dirpath, file) for file in filenames if file not in fileToIgnore]

    df_photos_to_mv['from_path'] = list_files
    df_photos_to_mv = extract_date_photos(df_photos_to_mv)
    df_photos_to_mv['date'] = pd.to_datetime(df_photos_to_mv['date'])
    df_photos_to_mv['is_kept'] = df_photos_to_mv['date'].map(lambda x: start_date <= x <= end_date)
    df_photos_to_mv = df_photos_to_mv[df_photos_to_mv['is_kept']]

    return df_photos_to_mv['from_path'].tolist()


def create_folder_and_transfer_photos(df_locations):
    for folder_to_create, list_photos in zip(df_locations['folder_to_find'], df_locations['photos_to_mv']):
        os.makedirs(folder_to_create, exist_ok=True)
        for photos_path in tqdm(list_photos):
            to_path = os.path.join(folder_to_create, os.path.basename(photos_path))
            shutil.move(photos_path, to_path)