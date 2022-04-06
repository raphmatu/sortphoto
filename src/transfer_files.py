
import logging
import shutil

from tqdm import tqdm

logger = logging.getLogger('logger')


def transfer_photos(df_auto, df_manual):

    for df in [df_auto, df_manual]:

        for from_path, to_path in tqdm(zip(df['from_path'], df['to_path']), total=len(df)):
            shutil.copy(from_path, to_path)

    sorted_files = len(df_auto)
    unsorted_files = len(df_manual)
    total_files = sorted_files + unsorted_files
    logger.info('{}/{} files have been successfully sorted'.format(sorted_files, total_files))
    logger.info('{}/{} files need to be sorted manually'.format(unsorted_files, total_files))