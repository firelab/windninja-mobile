import logging
import os
import subprocess
import zipfile

def execute_shell_process(command, working_directory, env=None):
    logging.debug("Shell command:{}".format(command))
    logging.debug("Environ: {}".format(env))

    custom_env = os.environ.copy()
    if (env):
        custom_env.update(env)

    proc = subprocess.Popen(command, shell=True, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=custom_env)
    out, err = proc.communicate(None)
    logging.debug("Shell process result:{0}Return Code:{1}{0}StdOut:{2}{0}StdErr:{3}".format(os.linesep, proc.returncode, out, err))
    if proc.returncode == 0:
        result = (True, out)
    else:
        result = (False, err)
    return result

def zip_files(archive_path, files):
    zipf = zipfile.ZipFile(archive_path, "w",  zipfile.ZIP_DEFLATED)
    logging.info("Zip archive opened: {}".format(archive_path))
    for file in files:
        rel_file = os.path.basename(file)
        logging.debug("zipping file: {}".format(rel_file))
        zipf.write(file,arcname=rel_file)
    zipf.close()

def zip_dir(archive_path, dir_path):
    zipf = zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED)
    logging.info("Zip archive opened: {}".format(archive_path))
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            abs_file = os.path.join(root,file) 
            rel_file = abs_file.replace(dir_path,"")
            logging.debug("zipping file: {}".format(rel_file))
            zipf.write(abs_file,arcname=rel_file)
    zipf.close()