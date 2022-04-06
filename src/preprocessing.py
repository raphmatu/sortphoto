
import calendar
import logging
import os


import numpy as np
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS


from src.conf import dictFormat, fileToIgnore

logger = logging.getLogger('logger')


def extract_information_from_files(source_path, destination_path):

    df_photo, df_video, df_unknown = list_and_identify_files(source_path)
    df_photo = process_photos(df_photo=df_photo)

    # TODO : Implement video sorting script
    # df_video = process_video(df_video=df_video)

    df_auto, df_manual = separate_unsortable_files(df_photo, df_video, df_unknown)
    df_auto, df_manual = generate_photos_new_path(df_auto, df_manual, destination_path)

    return df_auto, df_manual


def list_and_identify_files(source_path):
    df = _get_filepath(directory=source_path)
    df['filetype'] = df['from_path'].map(lambda x: _return_video_or_photo(x))

    df_photo = df[df['filetype'] == 'photo'].reset_index(drop=True)
    df_video = df[df['filetype'] == 'video'].reset_index(drop=True)
    df_unknown = df[df['filetype'] == 'unknown_filetype'].reset_index(drop=True)

    return df_photo, df_video, df_unknown


def process_photos(df_photo):

    df_photo = _extract_date_photos(df_photo)
    df_photo['manual_sort'] = df_photo['date'].map(lambda x: pd.isna(x))

    return df_photo


def separate_unsortable_files(df_photo, df_video, df_unknown):

    df_photo_manual = df_photo[df_photo['manual_sort']].reset_index(drop=True)
    df_photo_auto = df_photo[~df_photo['manual_sort']].reset_index(drop=True)
    df_video = df_video.reset_index(drop=True)

    #df_video_manual = df_video[~df_video['manual_sort']].reset_index(drop=True)
    #df_video_auto = df_video[df_video['manual_sort']].reset_index(drop=True)

    df_manual = pd.concat([df_unknown, df_photo_manual, df_video])
    df_auto = df_photo_auto.copy()

    return df_auto, df_manual


def generate_photos_new_path(df_auto, df_manual, photo_storage):

    df_auto['photo_year'] = df_auto['date'].dt.year
    df_auto['photo_month'] = df_auto['date'].dt.month
    df_auto['photo_month_name'] = df_auto['photo_month'].map(lambda x: calendar.month_abbr[x])
    df_auto['photo_month_name'] = df_auto.apply(lambda x: '{0:02d}_{1}'.format(x['photo_month'], x['photo_month_name']), axis=1)

    df_auto['to_path'] = df_auto.apply(
        lambda x: os.path.join(photo_storage, str(x['photo_year']), x['photo_month_name']), axis=1)

    df_manual['to_path'] = [os.path.join(photo_storage, 'to_sort_manually')] * len(df_manual)

    return df_auto, df_manual


def _extract_date_photos(df_photo):

    list_photos_date = []

    for photo_path in df_photo['from_path']:
        image = Image.open(photo_path)
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

    earliest_date = _get_oldest_date(list_date)
    return earliest_date


def _get_oldest_date(list_date):
    df_dates = pd.DataFrame(list_date.values(), columns=['date'])
    df_dates['date'] = pd.to_datetime(df_dates['date'], format="%Y:%m:%d %H:%M:%S")
    earliest_date = df_dates['date'].min()

    return earliest_date


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



