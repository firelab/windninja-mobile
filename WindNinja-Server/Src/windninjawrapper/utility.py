import logger
import subprocess

def executeShellProcess(command, working_directory):
    logger.verbose("Shell command:{}".format(command))
    proc = subprocess.Popen(command, shell=True, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(None)
    logger.verbose("Shell process result: {0}\r\n{1}\r\n{2}".format(proc.returncode, out, err))
    if proc.returncode == 0:
        result = (True, out)
    else:
        result = (False, err)

    return result
