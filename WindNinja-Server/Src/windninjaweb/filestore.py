import windninjaweb.models as wnmodels
import os
import json
import logging

_logger = logging.getLogger(__name__)

_directories = {
    "main" : "", 
    "account" : "",
    "feedback" : "",
    "job" : ""
    }

def set_Store(dir, initialize):
    global _directories
    _directories["main"]  = dir
    _directories["job"] = os.path.join(dir, "job")
    _directories["feedback"] = os.path.join(dir, "feedback")
    _directories["account"] = os.path.join(dir, "account")

    if initialize:
        os.makedirs(_directories["job"])
        os.makedirs(_directories["feedback"])
        os.makedirs(_directories["account"])
     

#------------JOB-------------------
_job_file_name = "job.json"

def get_job(id):
    job_folder = id.replace("-", "").lower()
    file = os.path.join(_directories["job"], job_folder, _job_file_name)
    _logger.debug("Job file: {}".format(file))
    
    try:
    
        with open(file, "r") as json_file:
            json_string = json_file.read()

    except FileNotFoundError as e:
        return None

    job = wnmodels.Job.from_json(json_string)   
    return job

def save_job(job):
    if not job:
        return False

    json_string = job.to_json()

    job_folder = os.path.join(_directories["job"], job.id.replace("-", "").lower())
    _logger.debug("Job folder: {}".format(job_folder))
    
    try:
        os.mkdir(job_folder)
    except FileExistsError:
        pass

    file = os.path.join(_directories["job"], job_folder, _job_file_name)
    _logger.debug("Job file: {}".format(file))
    
    with open(file, "w") as json_file:
        json_file.write(json_string)

    return True

#------------ACCOUNT-------------------
def get_account(id):
    file = os.path.join(_directories["account"], "{}.json".format(id.lower()))
    _logger.debug("Account file: {}".format(file))

    try:
    
        with open(file, "r") as json_file:
            json_string = json_file.read()

    except FileNotFoundError as e:
        return None

    account = wnmodels.Account.from_json(json_string)   
    return account

def save_account(account):
    if not account:
        return False

    json_string = account.to_json()

    file = os.path.join(_directories["account"], "{}.json".format(account.id.lower()))
    _logger.debug("Account file: {}".format(file))
    
    with open(file, "w") as json_file:
        json_file.write(json_string)

    return True

#------------FEEDBACK------------------
def get_feedback(id):
    file = os.path.join(_directories["feedback"], "{}.json".format(id.lower()))
    _logger.debug("Feedback file: {}".format(file))
    
    try:
    
        with open(file, "r") as json_file:
            json_string = json_file.read()

    except FileNotFoundError as e:
        return None

    feedback = wnmodels.Feedback.from_json(json_string)   
    return feedback

def save_feedback(feedback):
    if not feedback:
        return False

    json_string = feedback.to_json()

    file = os.path.join(_directories["feedback"], "{}.json".format(feedback.id.lower()))
    _logger.debug("Feedback file: {}".format(file))

    with open(file, "w") as json_file:
        json_file.write(json_string)

    return True