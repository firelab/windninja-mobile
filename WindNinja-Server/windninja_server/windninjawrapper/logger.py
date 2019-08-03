import logging
import os

# create the console output at debug level
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(logging.Formatter("%(levelname)s\t%(filename)s\t%(message)s"))

logger = logging.getLogger()
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)

_FILE_NAME = "windninja.log"

PRETTY_PRINT_JOB = False


def enable_file(folder, level):
    fh = logging.FileHandler(os.path.join(folder, _FILE_NAME))
    fh.setLevel(level)
    fh.setFormatter(
        logging.Formatter("%(asctime)s\t%(levelname)s\t%(filename)s\t%(message)s")
    )

    logger.addHandler(fh)
