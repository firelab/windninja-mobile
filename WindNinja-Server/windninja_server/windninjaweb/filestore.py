import os
import glob
import logging
from datetime import datetime
import pytz

from . import models as wnmodels


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_directories = {
    "main": "",
    "account": "",
    "feedback": "",
    "job": "",
    "notification": "",
}


def set_Store(dir, initialize=False):
    global _directories

    # TODO: the names could be configurable? probably overkill since db will be more likely
    _directories["main"] = dir
    _directories["job"] = os.path.join(dir, "job")
    _directories["feedback"] = os.path.join(dir, "feedback")
    _directories["account"] = os.path.join(dir, "account")
    _directories["notification"] = os.path.join(dir, "notification")

    if initialize:
        for d in _directories:
            os.makedirs(_directories[d], exist_ok=True)


# ------------JOB-------------------
_job_file_name = "job.json"


def get_job(id):
    """Return a populated Job from the given id

    Args:
        id (str): Unique identifier of the job
    Returns:
        Job: populated Job for the id or None if the job was not found.
    """
    job_folder = id.replace("-", "").lower()
    path = os.path.join(_directories["job"], job_folder, _job_file_name)

    logger.debug("Job file: {}".format(path))
    json_string = read_file(path)
    if json_string is None:
        return

    job = wnmodels.Job.from_json(json_string)

    return job


def save_job(job):
    """Saves a Job to the file store.

    Job will be saved under the job directory under a directory named
    after the job id.

    Args:
        job (Job): Job to save
    Returns:
        bool: True if the Job was successfully saved.
    """
    if not job:
        return False

    json_string = job.to_json()

    root = _directories["job"]
    job_directory = job.id.replace("-", "").lower()
    job_folder = os.path.join(root, job_directory)
    logger.debug("Job folder: {}".format(job_folder))

    os.makedirs(job_folder, exist_ok=True)

    path = os.path.join(root, job_folder, _job_file_name)
    logger.debug("Job file: {}".format(path))

    with open(path, "w") as json_file:
        json_file.write(json_string)

    return True


# ------------ACCOUNT-------------------
def get_account(id):
    """Retrieve the Account associated with the id.

    Args:
        id: unique identifier of the account
    Returns:
        Account: populated Account object associated with the id or None
            if the account was not found.
    """
    name = id.lower()
    path = os.path.join(_directories["account"], "{}.json".format(name))
    logger.debug("Account file: {}".format(path))
    json_string = read_file(path)
    if json_string is None:
        return

    account = wnmodels.Account.from_json(json_string)

    return account


def save_account(account):
    """Saves the Account to the file store.

    If successful, the Account contents will be persisted to a
    file in the accounts directory in a file named after the account identifier.

    If the account is falsy, then this method is a no-op
    (i.e., if you pass in None, this function does nothing and returns False).

    Args:
        account (Account): populated Account object to save
    Returns:
        bool: Indicates the success of the save
    """
    if not account:
        return False

    json_string = account.to_json()

    name = account.id.lower()
    path = os.path.join(_directories["account"], "{}.json".format(name))
    logger.debug("Account file: {path}")

    with open(path, "w") as json_file:
        json_file.write(json_string)

    return True


# ------------FEEDBACK------------------
def get_feedback(id):
    """Return the content of the feedack file for the given job id.

    Args:
        id (str): identifier of the job
    Returns:
        Feedback: populated Feedback object from the contents of the found file
                  or None if there was no feedback.
    """
    name = id.lower()
    path = os.path.join(_directories["feedback"], "{}.json".format(name))
    logger.debug("Feedback file: {}".format(path))
    json_string = read_file(path)

    if json_string is None:
        return None

    feedback = wnmodels.Feedback.from_json(json_string)

    return feedback


def save_feedback(feedback):
    """Saves the job feedback to the file store.

    If successful, the Feedback contents will be persisted to a
    file in the feedbac directory in a file named after the job identifier.

    If feedback is falsy, then this method is a no-op
    (i.e., if you pass in None, this function does nothing and returns False).

    Args:
        feedback (Feedback): Feedback object to save to the file store
    Returns:
        bool: Inidicates success of the save operation
    """
    if not feedback:
        return False

    json_string = feedback.to_json()

    name = feedback.id.lower()
    path = os.path.join(_directories["feedback"], "{}.json".format(name))
    logger.debug("Feedback file: {}".format(path))

    with open(path, "w") as json_file:
        json_file.write(json_string)

    return True


# ------------NOTIFICATION--------------
def _get_notification_from_file(path):
    logger.debug("Notification file: {}".format(path))
    json_string = read_file(path)
    if json_string is None:
        return

    notification = wnmodels.Notification.from_json(json_string)
    return notification


def get_notification(id):
    """Return the content of the notification for the given notification id.

    Args:
        id (str): identifier of the notification
    Returns:
        Notification: populated Notification object from the contents of the found file
            or None if there was no notification found.
    """
    name = id.lower()
    path = os.path.join(_directories["notification"], "{}.json".format(name))
    return _get_notification_from_file(path)


def get_notifications(expired=False):
    """Returns a list of all known notifications

    Args:
        expired (bool): If true, then return all notifications. Else only return
            those that have not yet expired.
    Returns:
        list: Notifications found in the notifications directory
    """
    notifications = []
    # ASSUMPTION: times are UTC WITH PYTZ
    dt = datetime.max if expired else datetime.utcnow()
    date_filter = pytz.utc.localize(dt)
    logger.debug("Notification date filter: {}".format(date_filter.isoformat()))

    file_filter = os.path.join(_directories["notification"], "*.json")
    logger.debug("Notification file filter: {}".format(file_filter))

    files = glob.glob(file_filter)
    logger.debug("Notification count: {}".format(len(files)))

    for f in files:
        notification = _get_notification_from_file(f)
        try:
            if notification and notification.expires > date_filter:
                notifications.append(notification)
        except TypeError:
            logger.warn(
                "Notification expires date is not tz aware: id={}, expires:{}"
                .format(notification.id, notification.expires)
            )

    return notifications


def save_notification(notification):
    """Saves the notification to the file store.

    If successful, the Notification contents will be persisted to a
    file in the notification directory in a file named after the identifier.

    If feedback is falsy, then this method is a no-op
    (i.e., if you pass in None, this function does nothing and returns False).

    Args:
        notification (Notification): Notification object to save to the file store
    Returns:
        bool: Inidicates success of the save operation
    """
    if not notification:
        return False

    json_string = notification.to_json()

    path = os.path.join(_directories["notification"], "{}.json".format(notification.id.lower()))
    logger.debug("Notification file: {}".format(path))

    with open(path, "w") as json_file:
        json_file.write(json_string)

    return True


def read_file(path):
    """
    Attempt to read a file as a string.
    Args:
        path (str): location of the file to read
    Returns:
        str: string containing the contents of the file
        None: if file was not found
    """
    try:
        with open(path, "r") as json_file:
            json_string = json_file.read()
    except FileNotFoundError:
        logger.exception("{} not found.".format(path))
        return None

    return json_string
