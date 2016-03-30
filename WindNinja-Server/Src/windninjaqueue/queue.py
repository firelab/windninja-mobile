import os
import glob
from enum import Enum

#TODO: move queue to database (could be easy enough to simply pull queue from JOB status once Job is database)

_directories = {
    "queue" : ""
    }

class QueueStatus(Enum):
    unknown = 0
    pending = 1
    running = 2
    complete = 3
    failed = 4

#TODO: create QueueException

def set_Queue(dir, initialize):
    global _directories
    _directories["queue"]  = dir
    
    if initialize:
        os.makedirs(_directories["queue"])
        
def enqueue(id, reset_existing=False):
    name = "{0}.{1}".format(id, QueueStatus.pending.name)
    file = os.path.join(_directories["queue"], name)

    if (_find_item(id) is None):
        try:
            open(file, "x").close()
        except FileExistsError:
            raise KeyError("Item with id {} already exists in queue".format(id))
    elif reset_existing:
        update_queue_item_status(id, QueueStatus.pending)
    else:
        raise KeyError("Item with id {} already exists in queue".format(id))

def dequeue(id):
    item = _find_item(id)
    if item is None:
        raise KeyError("Item with id {} not found in queue".format(id))
        
    update_queue_item_status(id, QueueStatus.complete)

def update_queue_item_status(id, status, data=None):
    if type(status) is not QueueStatus:
        raise TypeError("Status is not of type <QueueStatus>")
    
    try:
        existing_file = _find_item(id)
        base = os.path.splitext(existing_file)[0]
        new_file = "{0}.{1}".format(base, status.name)
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

def find_items_by_status(status):
    # get the files by status pattern
    name_pattern = "*.{}".format(status.name)
    file_pattern = os.path.join(_directories["queue"], name_pattern)
    files = glob.glob(file_pattern)

    # return a dictionary with id and created time
    return [{"id":os.path.splitext(os.path.basename(item))[0], "created":os.path.getctime(item)} for item in files]

def _find_item(id):
    name_pattern = "{}.*".format(id)
    file_pattern = os.path.join(_directories["queue"], name_pattern)
    try:
        return  glob.glob(file_pattern)[0]
    except IndexError as iex:
        return None
