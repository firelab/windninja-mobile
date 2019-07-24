import pytest
import datetime
import tempfile
import os

import windninjaweb.models as wnmodels
import windninjaweb.filestore as wndb

from .tests_models import MockModels, validate_job, validate_account, validate_feedback

@pytest.fixture
def filestore(tmpdir):
    # create a temp directory for the file store and initialize it
    filestore = tmpdir
    wndb.set_Store(filestore, initialize=True)

    # create the "exsiting files" in a manual way
    account_file =  f"{MockModels.account_id}.json"
    fh = filestore.join("account", account_file)
    fh.write(MockModels.account_json)

    feedback_file = f"{MockModels.feedback_id}.json"
    fh = filestore.join("feedback", feedback_file)
    fh.write(MockModels.feedback_json)

    job_dir = os.path.join("job", MockModels.job_id.replace("-", ""))
    fh = filestore.mkdir(job_dir).join(wndb._job_file_name)
    fh.write(MockModels.job_json)

    return filestore


def test_get_job(filestore):
    actual = wndb.get_job(MockModels.job_id)
    validate_job(actual)

    actual = wndb.get_job("THIS IS A BAD ID")
    assert actual is None, "Actual job: not None"


def test_save_job(filestore):
    target = wnmodels.Job()
    target.account = "my@account.com"
    target.email = "name@email.com"
    target.id = "464c19a6-9441-4ef9-a095-809f297aadbf"
    target.input = wnmodels.JobInput()
    target.input.domain = wnmodels.BBOX.create(1.0, 2.0, 3.0, 4.0)
    target.input.forecast = "FCST"
    target.input.parameters = "param1:1;param2:2"
    target.input.products = "prod1:true;prod2:false"
    target.messages.append("This is a test message")
    target.name = "test job"
    target.status = wnmodels.JobStatus.new

    actual = wndb.save_job(target)
    assert actual, "Job save failed"

    job_dir = target.id.replace("-", "").lower()
    fh = os.path.join(wndb._directories["job"], job_dir, wndb._job_file_name)
    assert os.path.exists(fh), "Job file not found"
    with open(fh, "r") as f:
        actual = f.read()

    expected = '{"account": "my@account.com", "email": "name@email.com", "id": "464c19a6-9441-4ef9-a095-809f297aadbf", "input": {"domain": {"xmax": 3.0, "xmin": 1.0, "ymax": 4.0, "ymin": 2.0}, "forecast": "FCST", "parameters": "param1:1;param2:2", "products": "prod1:true;prod2:false"}, "messages": ["This is a test message"], "name": "test job", "output": {"simulations": {}}, "status": "new"}'
    assert expected == actual, "Account json string mismatch"

    # update it again to make sure the "existing file" works
    target.messages.append("this is a second message")
    actual = wndb.save_job(target)
    assert actual, "Second job save failed "


def test_get_account(filestore):
    actual = wndb.get_account(MockModels.account_id)
    validate_account(actual)

    actual = wndb.get_account("THIS IS A BAD ID")
    assert actual is None, "Actual account: not None"


def test_save_account(filestore):
    target = wnmodels.Account()
    target.created_on = datetime.datetime(2016,1,2,3,4,5,6)
    target.email = "name@email.com"
    target.id = "my@account.com"
    target.name = "test account"
    target.status = wnmodels.AccountStatus.disabled
    target.devices.append(wnmodels.Device.create("ID01", "MD01", "ANDR", "5.0"))
    target.devices.append(wnmodels.Device.create("ID02", "MD02", "IOS", "9.0"))

    actual = wndb.save_account(target)
    assert actual, "Account save failed"

    name = target.id.lower()
    path = os.path.join(wndb._directories["account"], f"{name}.json")
    assert os.path.exists(path), "Account file not found"

    with open(path, "r") as f:
        actual = f.read()

    expected = '{"createdOn": "2016-01-02T03:04:05.000006", "devices": [{"id": "ID01", "model": "MD01", "platform": "ANDR", "version": "5.0"}, {"id": "ID02", "model": "MD02", "platform": "IOS", "version": "9.0"}], "email": "name@email.com", "id": "my@account.com", "name": "test account", "status": "disabled"}'
    assert expected == actual, "Account json string mismatch"


def test_get_feedback(filestore):
    actual = wndb.get_feedback(MockModels.feedback_id)
    validate_feedback(actual)

    actual = wndb.get_feedback("THIS IS A BAD ID")
    assert actual is None, "Actual feedback: not None"


def test_save_feedback(filestore):
    target = wnmodels.Feedback()
    target.account = "my@account.com"
    target.comments = "this is a test"
    target.date_time_stamp = datetime.datetime(2016,1,2,3,4,5,6)
    target.id = "f3e82852-97d8-4e49-baf9-c933b6c1c020"

    actual = wndb.save_feedback(target)
    assert actual, "Feedback save failed"

    name = target.id.lower()
    path = os.path.join(wndb._directories["feedback"], f"{name}.json")
    assert os.path.exists(path), "Feedback file not found"

    with open(path, "r") as f:
        actual = f.read()

    expected = '{"account": "my@account.com", "comments": "this is a test", "dateTimeStamp": "2016-01-02T03:04:05.000006", "id": "f3e82852-97d8-4e49-baf9-c933b6c1c020"}'
    assert expected == actual, "Feedback json string mismatch"
