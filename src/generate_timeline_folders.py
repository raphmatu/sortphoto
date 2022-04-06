
import os


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