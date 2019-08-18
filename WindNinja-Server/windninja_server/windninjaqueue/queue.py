import os
import glob
import logging

from .enums import QueueMode, QueueStatus

# TODO: move queue to database (could be easy enough to simply pull queue from JOB status once Job is database)
# TODO: create QueueException

wn = None  # NOTE: needed for conditional import of start_job function
_mode = QueueMode.disabled
_directories = {"queue": ""}


def set_Queue(config, initialize=False):
    global _directories
    _directories["queue"] = config["datastore"]

    global _mode
    _mode = QueueMode[config.get("mode", "disabled")]

    if _mode == QueueMode.immediate:
        global wn
        import windninjaqueue.windninja as wn

        wn.PYTHON_EXECUTABLE = config["windninja_wrapper"]["executable"]
        wn.WN_WRAPPER = config["windninja_wrapper"]["script"]
        wn.WN_WRAPPER_OPTIONS = config["windninja_wrapper"]["options"]

    if initialize:
        os.makedirs(_directories["queue"])


def enqueue(id, reset_existing=False):
    if _mode == QueueMode.disabled:
        return

    name = "{0}.{1}".format(id, QueueStatus.pending.name)
    file = os.path.join(_directories["queue"], name)

    if _find_item(id) is None:
        try:
            open(file, "x").close()
        except FileExistsError:
            raise KeyError("Item with id {} already exists in queue".format(id))
    elif reset_existing:
        update_queue_item_status(id, QueueStatus.pending)
    else:
        raise KeyError("Item with id {} already exists in queue".format(id))

    # start job if in immediate mode
    if _mode == QueueMode.immediate:
        logging.debug("immediate queue start")
        try:
            status, pid, message = wn.start_job(id)
            logging.debug(
                "start results status={} pid={} message={}".format(status, pid, message)
            )
        except Exception as ex:
            status = QueueStatus.failed
            message = "ERROR:{}".format(str(ex))

        # TODO: handle race condition here with wrapper...
        update_queue_item_status(id, status, message)

        if status == QueueStatus.failed:
            raise Exception(message)


def dequeue(id, **kwargs):
    # just skip out if disabled
    if _mode == QueueMode.disabled:
        return

    item = _find_item(id)
    if item is None:
        raise KeyError("Item with id {} not found in queue".format(id))

    update_queue_item_status(id, QueueStatus.complete, **kwargs)


def update_queue_item_status(id, status, data=None):
    if _mode == QueueMode.disabled:
        return

    if type(status) is not QueueStatus:
        raise TypeError("Status is not of type <QueueStatus>")

    try:
        existing_file = _find_item(id)
        if existing_file is None:
            raise KeyError("Item with id {} not found in queue".format(id))

        base = os.path.splitext(existing_file)[0]
        new_file = "{0}.{1}".format(base, status.name)
        os.rename(existing_file, new_file)

        if data:
            with open(new_file, "at") as f:
                f.write(data)
                f.write("\n")

    except AttributeError:
        raise KeyError("Item with id {} not found in queue".format(id))

    except OSError as osex:
        raise Exception("Queue update os error\n{}\n".format(str(osex)), data)


def find_items_by_status(status):
    # get the files by status pattern
    name_pattern = "*.{}".format(status.name)
    file_pattern = os.path.join(_directories["queue"], name_pattern)
    files = glob.glob(file_pattern)

    # return a dictionary with id and created time
    return [
        {
            "id": os.path.splitext(os.path.basename(item))[0],
            "created": os.path.getctime(item),
        }
        for item in files
    ]


def _find_item(id):
    name_pattern = "{}.*".format(id)
    file_pattern = os.path.join(_directories["queue"], name_pattern)
    try:
        return glob.glob(file_pattern)[0]
    except IndexError:
        return None
