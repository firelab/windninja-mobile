import sys
import os
import time
import tempfile
import glob

#job_dir = r"/home/wnadmin/WindNinjaServer/Data/job"
job_dir = r"/srv/WindNinjaServer/Data/job"
sleep_time = 15

#--------------------------------------------
# 2.7 version of the queue functions 
_directories = {
    "queue" : r"/srv/WindNinjaServer/Data/queue"
    }

def dequeue(id):
    item = _find_item(id)
    if item is None:
        raise KeyError("Item with id {} not found in queue".format(id))

    #Simpler 'remove file' alogrithm 
    #try:
    #    file = item
    #    os.remove(file)
    #except OSError as oex:
    #    raise Exception("Failed to remove queue item {}".format(id))

    #More complex keep file with 'status'
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
        return  glob.glob(file_pattern)[0]
    except IndexError as iex:
        return None

#--------------------------------------------
current_pid = os.getpid()
id = sys.argv[1] if len(sys.argv) > 1 else "testid"

file_path = os.path.join(job_dir, "{}.{}.wn".format(current_pid, int(time.time())))
f = open(file_path, "w")

f.write("[{0}] python:{1}\n".format(current_pid, sys.executable))
f.write("[{0}] version:{1}\n".format(current_pid, sys.version))
f.write("[{0}] running windninja job - id: {1}\n".format(current_pid,id))

time.sleep(sleep_time)
f.write("[{0}] doing job stuff {1}\n".format(current_pid, time.time()))

time.sleep(sleep_time)
try:
    dequeue(id)
    f.write("[{0}] dequeue success...\n".format(current_pid))
except:
    f.write("[{0}] dequeue failed...\n".format(current_pid))
    
f.write("[{0}] job complete...\n".format(current_pid))
f.close()