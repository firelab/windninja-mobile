import sys
import subprocess
import logging
import signal
from windninjaqueue.enums import QueueStatus

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
PYTHON_EXECUTABLE = "python"
WN_WRAPPER = "windninjawrapper/windninja.py"
WN_WRAPPER_OPTIONS = []


def preexec_function():
    # set the signal to be ignored
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def start_job(id, **kwargs):

    wn_args = [PYTHON_EXECUTABLE, WN_WRAPPER, id]
    try:
        wn_args += WN_WRAPPER_OPTIONS
    except Exception:
        pass

    if len(kwargs) > 0:
        wn_args += ['--' + key + '=' + value for key, value in kwargs]

    logging.debug("start job args: {}".format(wn_args))
    # windows/linux have different "Detach" usage
    status = QueueStatus.running
    message = ""
    pid = None

    try:
        if sys.platform == "win32":
            # NOTE in testing on WIN10 in 'immediate' mode this setup will fail on the gdalwarp... ??? maybe missing environment variable?
            logging.debug("full new process group")
            pid = subprocess.Popen(
                wn_args, close_fds=True, creationflags=CREATE_NEW_PROCESS_GROUP
            ).pid
            # pid = subprocess.Popen(args, close_fds=True, creationflags=DETACHED_PROCESS ).pid
            # pid = subprocess.Popen(args).pid
        else:
            pid = subprocess.Popen(
                wn_args, close_fds=True, preexec_fn=preexec_function
            ).pid

        message = "pid:{}".format(pid)
        logging.debug("job start success: {}".format(message))

    except Exception as ex:
        status = QueueStatus.failed
        # TODO: get full trace info
        message = "ERROR:{}".format(str(ex))
        logging.debug("job start failed: {}".format(message))

    return status, pid, message
