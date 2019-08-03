import os
from config import CONFIG

# --------------------------------------------
# 2.7 version of the queue functions
import glob

_directories = {"queue": CONFIG.QUEUE_DIRECTORY}


def dequeue(id):
    item = _find_item(id)
    if item is None:
        raise KeyError("Item with id {} not found in queue".format(id))

    # More complex keep file with 'status'
    update_queue_item_status(id, "complete")


def update_queue_item_status(id, status, data=None):
    if type(status) is not str:
        raise TypeError("Status is not of type <QueueStatus>")

    try:
        existing_file = _find_item(id)
        base = os.path.splitext(existing_file)[0]
        new_file = "{0}.{1}".format(base, status)
        os.rename(existing_file, new_file)

        if data:
            with open(new_file, "at") as f:
                f.write(data)
                f.write("\n")

    except AttributeError:
        raise KeyError("Item with id {} not found in queue".format(id))

    except OSError:
        raise Exception("Queue update error")

    except Exception:
        raise Exception("Queue update error")


def _find_item(id):
    name_pattern = "{}.*".format(id)
    file_pattern = os.path.join(_directories["queue"], name_pattern)

    try:
        return glob.glob(file_pattern)[0]
    except IndexError as iex:
        return None


# --------------------------------------------
