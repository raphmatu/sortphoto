
import os
import calendar
import subprocess
from pathlib import Path
from tqdm import tqdm

FOLDER = os.path.join(str(Path(__file__).parents[1]))


def transfer_photos(df_auto, df_manual):

    for df in [df_auto, df_manual]:

        for from_path, to_path in tqdm(zip(df['from_path'], df['to_path']), total=len(df)):
            cmd = ['cp', '-r', from_path, to_path]
            subprocess.run(cmd)


def generate_time_tree(df_auto, photo_storage):

    df_auto['photo_year'] = df_auto['date'].dt.year
    df_auto['photo_month'] = df_auto['date'].dt.month
    df_auto['photo_month_name'] = df_auto['photo_month'].map(lambda x: calendar.month_abbr[x])

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


def setup_folders():

    photo_lake = os.path.join(FOLDER, 'sample')
    photo_storage = os.path.join(FOLDER, 'photo_storage')
    photo_storage_manually = os.path.join(FOLDER, 'need_manual_sorting')

    return photo_lake, photo_storage, photo_storage_manually
