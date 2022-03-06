
import os
import calendar
import numpy as np
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS


def process_photos(df_photo):

    df_photo = _extract_date_photos(df_photo)
    df_photo['manual_sort'] = df_photo['date'].map(lambda x: pd.isna(x))

    return df_photo


def generate_photos_new_path(df_auto, df_manual, photo_storage):

    df_auto['photo_year'] = df_auto['date'].dt.year
    df_auto['photo_month'] = df_auto['date'].dt.month
    df_auto['photo_month_name'] = df_auto['photo_month'].map(lambda x: calendar.month_abbr[x])

    df_auto['to_path'] = df_auto.apply(
        lambda x: os.path.join(photo_storage, str(x['photo_year']), x['photo_month_name']), axis=1)

    df_manual['to_path'] = [os.path.join(photo_storage, 'to_sort_manually/')] * len(df_manual)

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