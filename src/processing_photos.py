
import os
import numpy as np
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS


def generate_photos_new_path(df_auto, df_manual, photo_storage):

    df_auto['to_path'] = df_auto.apply(
        lambda x: os.path.join(photo_storage, str(x['photo_year']), x['photo_month_name']), axis=1)

    manual_sort_path = os.path.join(photo_storage, 'to_sort_manually/')
    df_manual['to_path'] = [manual_sort_path] * len(df_manual)

    return df_auto, df_manual


def separate_photos_whithout_date(df):
    df['manual_sort'] = df['date'].map(lambda x: pd.isna(x))
    df_auto = df[~df['manual_sort']].reset_index(drop=True)
    df_manual = df[df['manual_sort']].reset_index(drop=True)

    return df_auto, df_manual


def list_and_date_photos(photo_lake):

    list_photos_path = _get_photos_path(directory=photo_lake)
    df_photo_metadata = pd.DataFrame()
    df_photo_metadata['from_path'] = list_photos_path

    list_photos_date = []

    for photo_path in df_photo_metadata['from_path']:
        image = Image.open(photo_path)
        exifdata = image.getexif()
        if exifdata:
            photo_date = _get_oldest_date_from_exif_data(exifdata=exifdata)
            list_photos_date.append(photo_date)
        else:
            print(photo_path)
            list_photos_date.append(np.nan)

    df_photo_metadata['date'] = list_photos_date

    return df_photo_metadata


def _get_photos_path(directory):
    list_photos_path = []

    list_photo = os.listdir(directory)
    for photo in list_photo:
        list_photos_path.append(os.path.join(directory, photo))

    return list_photos_path


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