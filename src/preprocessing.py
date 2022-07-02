
import calendar
import logging
import os

from src.conf import FOLDER

import numpy as np
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS
from tqdm import tqdm

from src.conf import dictFormat, fileToIgnore

logger = logging.getLogger('logger')


def extract_information_from_files(source_path, destination_path):
    """
    This function executes several main steps :
    - list all available files in source path directory
    - identify photos, videos and unknown files among them
    - generate destination path for the photos to be transfered
    :param source_path: directory containing photos to be sorted
    :param destination_path: directory containing sorted photos
    :return:
    """

    df_photo, df_video, df_unknown = list_and_identify_files(source_path)
    df_photo = extract_date_photos(df_photo)
    df_photo['manual_sort'] = df_photo['date'].map(lambda x: pd.isna(x))

    # TODO: Implement video sorting script
    # df_video = process_video(df_video=df_video)

    df_auto, df_manual = separate_unsortable_files(df_photo, df_video, df_unknown)
    df_auto, df_manual = generate_photos_new_path(df_auto, df_manual, destination_path)

    return df_auto, df_manual


def list_and_identify_files(source_path):
    """
    List, identify and separate files as photos, videos or unknown type. It returns 3 differents dataframe according to
    the file type
    :param source_path:
    :return:
    """
    df = _get_filepath(directory=source_path)
    df['filetype'] = df['from_path'].map(lambda x: _return_video_or_photo(x))

    df_photo = df[df['filetype'] == 'photo'].reset_index(drop=True)
    df_video = df[df['filetype'] == 'video'].reset_index(drop=True)
    df_unknown = df[df['filetype'] == 'unknown_filetype'].reset_index(drop=True)

    return df_photo, df_video, df_unknown


def separate_unsortable_files(df_photo, df_video, df_unknown):
    """
    This function separates photos and videos (TBI) in two dataframe : auto and manual.
    auto dataframe contains photos that can be automatically sorted
    manual dataframe contains photos that will need to be sorted manually
    :param df_photo:
    :param df_video:
    :param df_unknown:
    :return:
    """

    df_photo_manual = df_photo[df_photo['manual_sort']].reset_index(drop=True)
    df_photo_auto = df_photo[~df_photo['manual_sort']].reset_index(drop=True)
    df_video = df_video.reset_index(drop=True)

    #df_video_manual = df_video[~df_video['manual_sort']].reset_index(drop=True)
    #df_video_auto = df_video[df_video['manual_sort']].reset_index(drop=True)

    df_manual = pd.concat([df_unknown, df_photo_manual, df_video])
    df_auto = df_photo_auto.copy()

    return df_auto, df_manual


def generate_photos_new_path(df_auto, df_manual, photo_storage):
    """
    Generates the destination path for each photos according to the date and the location file
    :param df_auto:
    :param df_manual:
    :param photo_storage:
    :return:
    """

    df_auto['photo_year'] = df_auto['date'].dt.year
    df_auto['photo_month'] = df_auto['date'].dt.month
    df_auto['photo_month_name'] = df_auto['photo_month'].map(lambda x: calendar.month_abbr[x])
    df_auto['photo_month_name'] = df_auto.apply(lambda x: '{0:02d}_{1}'.format(x['photo_month'], x['photo_month_name']), axis=1)

    df_auto['to_path'] = df_auto.apply(
        lambda x: os.path.join(photo_storage, str(x['photo_year']), x['photo_month_name']), axis=1)

    df_manual['to_path'] = [os.path.join(photo_storage, 'to_sort_manually')] * len(df_manual)

    df_auto = _synchronize_folders_from_location_file(df_auto)

    return df_auto, df_manual


def extract_date_photos(df_photo):
    """
    This function opens each photo and extract the oldest date found in metadata. It returns the 'df_photo' dataframe
    with one more column containing the photo oldest date.
    :param df_photo: dataframe containing 1 column 'from_path' with all files paths
    :return:
    """

    list_photos_date = []

    logger.info('Start date extraction from photos...')

    for photo_path in tqdm(df_photo['from_path']):
        try:
            image = Image.open(photo_path)
        except:
            list_photos_date.append(np.nan)
            continue

        exifdata = image.getexif()
        if exifdata:
            photo_date = _get_oldest_date_from_exif_data(exifdata=exifdata)
            list_photos_date.append(photo_date)
        else:
            list_photos_date.append(np.nan)

    df_photo['date'] = list_photos_date

    return df_photo


def _get_oldest_date_from_exif_data(exifdata):
    date_tag = {
        306: 'DateTime',
        36867: 'DateTimeOriginal',
        36868: 'DateTimeDigitized'
    }

    list_date = {}
    for tag_id in exifdata:
        if tag_id in date_tag.keys():

            tag = TAGS[tag_id]
            date_photo = exifdata.get(tag_id)

            # decode bytes
            if isinstance(date_photo, bytes):
                date_photo = date_photo.decode()

            list_date[tag] = date_photo

    list_date = {k: v for k, v in list_date.items() if v != "0000:00:00 00:00:00"}
    earliest_date = _get_oldest_date(list_date)
    return earliest_date


def _get_oldest_date(list_date):

    df_dates = pd.DataFrame(list_date.values(), columns=['date'])
    df_dates['date'] = pd.to_datetime(df_dates['date'], format="%Y:%m:%d %H:%M:%S")
    earliest_date = df_dates['date'].min()

    return earliest_date


def _get_filepath(directory):
    """
    List all files paths from directory arg and return a dataframe with 1 column 'from_path' containing all of them
    :param str directory:
    :return:
    """

    df = pd.DataFrame()
    list_files = []
    for (dirpath, dirnames, filenames) in os.walk(directory):
        list_files += [os.path.join(dirpath, file) for file in filenames if file not in fileToIgnore]

    df['from_path'] = list_files

    logger.info('{} files found. Start processing...'.format(len(list_files)))

    return df


def _return_video_or_photo(filepath):
    """
    Check the extension of each file and classify them as photo, video or unknown
    :param str filepath:
    :return:
    """

    extension = os.path.splitext(filepath)[1]
    extension_upper = extension.upper()

    for filetype in dictFormat.keys():
        if extension_upper in dictFormat[filetype]:
            return filetype

    return 'unknown_filetype'


def _synchronize_folders_from_location_file(df_auto):
    """
    Identify locations from locations.csv file and modify destination folder file path if needed
    :param df_auto:
    :return:
    """

    try:
        df_locations = pd.read_csv(os.path.join(FOLDER, 'locations.csv'), sep=';')
    except:
        logger.info('No locations.csv file found')
        return df_auto

    df_locations['start_date (YYYY-MM-DD)'] = pd.to_datetime(df_locations['start_date (YYYY-MM-DD)'])
    df_locations['end_date (YYYY-MM-DD)'] = pd.to_datetime(df_locations['end_date (YYYY-MM-DD)'])

    df_auto['location'] = df_auto['date'].map(lambda x: _extract_location(x, df_locations))
    df_auto['to_path'] = df_auto.apply(lambda x: _add_location_to_path(x['to_path'], x['location']), axis=1)
    df_auto['photo_month_name'] = df_auto.apply(lambda x: _add_location_to_path(x['photo_month_name'], x['location']), axis=1)

    return df_auto


def _extract_location(date, df):
    df_time_window = df[(df['start_date (YYYY-MM-DD)'] < date) & (df['end_date (YYYY-MM-DD)'] > date)].reset_index()

    if len(df_time_window) > 1:
        logger.info('Several dates are overlapping')
        exit()
    elif len(df_time_window) == 0:
        return np.nan

    return df_time_window['locations'].item()


def _add_location_to_path(path, location):
    if not pd.isna(location):
        new_path = '{}_{}'.format(path, location)
        return new_path
    return path




