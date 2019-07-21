import windninjaweb.models as wnmodels
import os
import glob
import json
import logging
from datetime import datetime
import pytz

_logger = logging.getLogger(__name__)

_directories = {
    "main" : "",
    "account" : "",
    "feedback" : "",
    "job" : "",
    "notification": ""
    }

def set_Store(dir, initialize=False):
    global _directories

    #TODO: the names could be configurable? probably overkill since db will be more likely
    _directories["main"]  = dir
    _directories["job"] = os.path.join(dir, "job")
    _directories["feedback"] = os.path.join(dir, "feedback")
    _directories["account"] = os.path.join(dir, "account")
    _directories["notification"] = os.path.join(dir, "notification")

    if initialize:
        for d in _directories:
            os.makedirs(_directories[d])

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

#------------NOTIFICATION--------------
def _get_notification_from_file(file):
    _logger.debug("Notification file: {}".format(file))

    try:
        with open(file, "r") as json_file:
            json_string = json_file.read()

    except FileNotFoundError as e:
        return None

    notification = wnmodels.Notification.from_json(json_string)
    return notification


def get_notification(id):
    file = os.path.join(_directories["notification"], "{}.json".format(id.lower()))
    return _get_notification_from_file(file)

def get_notifications(exprired=False):
    notifications = []
    #ASSUMPTION: times are UTC WITH PYTZ
    dt = datetime.max if exprired else datetime.utcnow()
    date_filter = pytz.utc.localize(dt)
    _logger.debug("Notification date filter: {}".format(date_filter.isoformat()))

    file_filter = os.path.join(_directories["notification"], "*.json")
    _logger.debug("Notification file filter: {}".format(file_filter))

    files = glob.glob(file_filter)
    _logger.debug("Notification count: {}".format(len(files)))

    for f in files:
        notification = _get_notification_from_file(f)
        try:
            if notification and notification.expires > date_filter:
                notifications.append(notification)
        except TypeError:
            _logger.warn("Notification expires date is not tz aware: id={}, expires:{}".format(notification.id, notification.expires))

    return notifications

def save_notification(notification):
    if not notification:
        return False

    json_string = notification.to_json()

    file = os.path.join(_directories["notification"], "{}.json".format(notification.id.lower()))
    _logger.debug("Notification file: {}".format(file))

    with open(file, "w") as json_file:
        json_file.write(json_string)

    return True
