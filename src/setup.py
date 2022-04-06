
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger('logger')

FOLDER = os.path.join(str(Path(__file__).parents[1]))


def setup_logger():

    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    console_logger = logging.StreamHandler(sys.stdout)
    console_logger.setLevel(logging.INFO)
    console_logger.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s',
                                                  datefmt='%Y-%m-%d %H:%M:%S'))
    logger = logging.getLogger('logger')
    logger.addHandler(console_logger)
    logger.setLevel(logging.INFO)

    return logger


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