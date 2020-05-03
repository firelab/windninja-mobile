import sys
import time
import datetime
from operator import itemgetter
import subprocess

import windninjaqueue.windninja as wn
import windninjaqueue.queue as wnqueue

VERBOSE = False
CANCEL = False
LOOP_PAUSE = 5
MAX_RUNNING_JOBS = 5
# horrible way to do this, but we need to track how many threads are in use
threads_in_use = 0

# NOTES: this is a simple 'max' processes queue manager - first in, first out based on "created" time
# other possible enhancements short term:
# * user round robin
# * user priority
# * checks if processes are still running
# * CPU/RAM usage limits?


def write_stdout(s):
    sys.stdout.write("[{}]:{}\n".format(datetime.datetime.now().isoformat(), s))
    sys.stdout.flush()


def main_loop(config):

    # initialize configuration
    global LOOP_PAUSE
    LOOP_PAUSE = config.get("loop_interval", LOOP_PAUSE)
    global MAX_RUNNING_JOBS
    MAX_RUNNING_JOBS = config.get("max_running_jobs", MAX_RUNNING_JOBS)

    wn.PYTHON_EXECUTABLE = config["windninja_wrapper"]["executable"]
    wn.WN_WRAPPER = config["windninja_wrapper"]["script"]
    wn.WN_WRAPPER_OPTIONS = config["windninja_wrapper"]["options"]

    wnqueue.set_Queue(config)

    max_threads = 8
    threads_in_use = 0
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
            current_running = len(
                wnqueue.find_items_by_status(wnqueue.QueueStatus.running)
            )

            # find pending jobs and sort by time created
            pending_jobs = wnqueue.find_items_by_status(wnqueue.QueueStatus.pending)
            pending_jobs.sort(key=itemgetter("created"))
            pending_job_count = len(pending_jobs)
            available_cores = """mpstat -P ALL | cut -d" " -f10 | tail -n 8 | awk '$1 < 0.25 { print }' | sort -n | wc -l"""

            if VERBOSE:
                write_stdout(
                    "Jobs - running jobs: {0} ; available cores: {1}; pending jobs:{2}".format(
                        current_running, available_cores, pending_job_count
                    )
                )

            for job in pending_jobs:
                if threads_in_use < max_threads:
                    id = job["id"]
                    write_stdout("enqueue job: {}".format(id))
                    available_cores = subprocess.check_output(available_cores, shell=True)
                    if pending_job_count >= available_cores:
                        nthreads = 1
                    elif pending_job_count == 1:
                        nthreads = available_cores
                    else:
                        nthreads = available_cores / pending_job_count

                    status, pid, message = wn.start_job(id, num_threads=nthreads)
                    wnqueue.update_queue_item_status(id, status, message)

                    if status == wnqueue.QueueStatus.running:
                        pending_job_count -= 1
                    else:
                        write_stdout("job [{}] failed to start: {}".format(id, message))

                else:
                    write_stdout(
                        "Running jobs filled - remaining: {0}".format(pending_job_count)
                    )
                    break

        except Exception as loop_ex:
            write_stdout("Unhandled expection in main loop: {}".format(str(loop_ex)))
