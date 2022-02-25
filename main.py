import pandas as pd

from src.processing_folders import setup_folders, generate_time_tree
from src.processing_photos import list_and_date_photos, separate_photos_whithout_date, generate_photos_new_path


def main():

    photo_lake, photo_storage, photo_storage_manually = setup_folders()

    df = list_and_date_photos(photo_lake=photo_lake)
    df_auto, df_manual = separate_photos_whithout_date(df)

    generate_time_tree(df_auto, df_manual, photo_storage)

    df_auto, df_manual = generate_photos_new_path(df_auto, df_manual, photo_storage)


if __name__ == "__main__":
    main()
