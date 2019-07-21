import sys
import time
import datetime
from operator import itemgetter
import signal
import windninjaqueue.windninja as wn
import windninjaqueue.queue as wnqueue

VERBOSE = False
CANCEL = False
LOOP_PAUSE = 5
MAX_RUNNING_JOBS = 5

#NOTES: this is a simple 'max' processes queue manager - first in, first out based on "created" time
# other possible enhancements short term:
# * user round robin
# * user priority
# * checks if processes are still running
# * CPU/RAM usage limits?

def write_stdout(s):
    sys.stdout.write("[{}]:{}\n".format(datetime.datetime.now().isoformat(), s))
    sys.stdout.flush()

def main_loop(config):

    #initialize configuration
    global LOOP_PAUSE
    LOOP_PAUSE = config.get("loop_interval", LOOP_PAUSE)
    global MAX_RUNNING_JOBS
    MAX_RUNNING_JOBS = config.get("max_running_jobs", MAX_RUNNING_JOBS)

    wn.PYTHON_EXECUTABLE = config["windninja_wrapper"]["executable"]
    wn.WN_WRAPPER= config["windninja_wrapper"]["script"]
    wn.WN_WRAPPER_OPTIONS = config["windninja_wrapper"]["options"]

    wnqueue.set_Queue(config)

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

                    status, pid, message = wn.start_job(id)
                    wnqueue.update_queue_item_status(id, status, message)

                    if (status == wnqueue.QueueStatus.running):
                        available_jobs -= 1
                        pending_job_count -= 1
                    else:
                        write_stdout("job [{}] failed to start: {}".format(id, message))

                else:
                    write_stdout("Running jobs filled - remaining: {0}".format(pending_job_count))
                    break

        except Exception as loop_ex:
            write_stdout("Unhandled expection in main loop: {}".format(str(loop_ex)))
