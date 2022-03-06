
import sys
import logging


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