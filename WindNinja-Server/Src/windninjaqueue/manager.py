import sys
import time
import datetime
from operator import itemgetter
import subprocess
import signal

import windninjaconfig as wnconfig
import windninjaqueue.queue as wnqueue

VERBOSE = False
CANCEL = False
LOOP_PAUSE = wnconfig.Config.QUEUE["loop_interval"]
MAX_RUNNING_JOBS = wnconfig.Config.QUEUE["max_running_jobs"]
PYTHON_EXECUTABLE = wnconfig.Config.QUEUE["windninja_wrapper"]["executable"]
WN_WRAPPER = wnconfig.Config.QUEUE["windninja_wrapper"]["script"]
WN_WRAPPER_OPTIONS = wnconfig.Config.QUEUE["windninja_wrapper"]["options"]
DETACHED_PROCESS = 0x00000008


#NOTES: this is a simple 'max' processes queue manager - first in, first out based on "created" time 
# other possible enhancements short term:
# * user round robin
# * user priority
# * checks if processes are still running
# * CPU/RAM usage limits?  

def preexec_function():
    # set the signal to be ignored
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def write_stdout(s):
    sys.stdout.write("[{}]:{}\n".format(datetime.datetime.now().isoformat(), s))
    sys.stdout.flush()

def main_loop():

    # set the datastore for the queue
    wnqueue.set_Queue(wnconfig.Config.QUEUE["datastore"], False)

    # start the loop
    while not CANCEL:        
        try:
            time.sleep(LOOP_PAUSE)
        except KeyboardInterrupt:
            pass
        except InterruptedError:
            pass
        
        try:
            # get count of "current running jobs"
            current_running = len(wnqueue.find_items_by_status(wnqueue.QueueStatus.running))
            available_jobs = MAX_RUNNING_JOBS - current_running      

            # find pending jobs and sort by time created
            pending_jobs = wnqueue.find_items_by_status(wnqueue.QueueStatus.pending)
            pending_jobs.sort(key=itemgetter("created"))
            pending_job_count = len(pending_jobs)
            
            if VERBOSE:
                write_stdout("Jobs - running: {0} ; available: {1}; pending:{2}".format(current_running, available_jobs, pending_job_count))

            for job in pending_jobs:
                if (available_jobs > 0):
                    id=job["id"]
                    write_stdout("enqueue job: {}".format(id))
                    
                    args = [PYTHON_EXECUTABLE, WN_WRAPPER, id]
                    try: args += WN_WRAPPER_OPTIONS
                    except: pass
                    
                    #windows/linux have different "Detach" usage
                    try:
                        if sys.platform == "win32":
                            pid = subprocess.Popen(args, close_fds=True, creationflags=DETACHED_PROCESS ).pid
                        else:
                            pid = subprocess.Popen(args, close_fds=True, preexec_fn = preexec_function).pid
                    except Exception as pex:
                        write_stdout("job [{}] failed to start: {}".format(id, str(pex)))
                        wnqueue.update_queue_item_status(id, wnqueue.QueueStatus.failed, "ERROR:{}".format(str(pex)))
                        continue
                    
                    #TODO: how to handle status update fail?
                    wnqueue.update_queue_item_status(id, wnqueue.QueueStatus.running, "pid:{}".format(pid))
                    available_jobs -= 1
                    pending_job_count -= 1
                else: 
                    write_stdout("Running jobs filled - remaining: {0}".format(pending_job_count))
                    break
                    
        except Exception as loop_ex:
            write_stdout("Unhandled expection in main loop: {}".format(str(loop_ex)))