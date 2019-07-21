import unittest
import datetime
import dateutil
import tempfile
import os

import windninjaweb.models as wnmodels
import windninjaweb.filestore as wndb

from tests_models import MockModels

class TestFileStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # create a temp directory for the file store and initialize it
        cls._store = tempfile.TemporaryDirectory()
        wndb.set_Store(cls._store.name, initialize=True)

        # create the "exsiting files" in a manual way
        account_file =  "{}.json".format(MockModels.account_id)
        with open(os.path.join(wndb._directories["account"], account_file), "w") as f:
            f.write(MockModels.account_json)

        feedback_file = "{}.json".format(MockModels.feedback_id)
        with open(os.path.join(wndb._directories["feedback"], feedback_file), "w") as f:
            f.write(MockModels.feedback_json)

        job_dir = os.path.join(wndb._directories["job"], MockModels.job_id.replace("-", ""))
        os.makedirs(job_dir)
        with open(os.path.join(job_dir, wndb._job_file_name), "w") as f:
            f.write(MockModels.job_json)

    def test_get_job(self):
        actual = wndb.get_job(MockModels.job_id)
        MockModels.validate_job(self, actual)

        actual = wndb.get_job("THIS IS A BAD ID")
        self.assertIsNone(actual, msg="Actual job: not None")

    def test_save_job(self):
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
        self.assertTrue(actual, msg="Job save failed")

        file = os.path.join(wndb._directories["job"], (target.id.replace("-", "").lower()), wndb._job_file_name)
        self.assertTrue(os.path.exists(file), "Job file not found")
        with open(file, "r") as f:
            actual = f.read()

        expected = '{"account": "my@account.com", "email  ": "name@email.com", "id": "464c19a6-9441-4ef9-a095-809f297aadbf", "input": {"domain": {"xmax": 3.0, "xmin": 1.0, "ymax": 4.0, "ymin": 2.0}, "forecast": "FCST", "parameters": "param1:1;param2:2", "products": "prod1:true;prod2:false"}, "messages": ["This is a test message"], "name": "test job", "output": {"products": []}, "status": "new"}'
        self.assertEqual(expected, actual, msg="Account json string mismatch")

        # update it again to make sure the "existing file" works
        target.messages.append("this is a second message")
        actual = wndb.save_job(target)
        self.assertTrue(actual, msg="Second job save failed ")

    def test_get_account(self):
        actual = wndb.get_account(MockModels.account_id)
        MockModels.validate_account(self, actual)

        actual = wndb.get_account("THIS IS A BAD ID")
        self.assertIsNone(actual, msg="Actual account: not None")

    def test_save_account(self):
        target = wnmodels.Account()
        target.created_on = datetime.datetime(2016,1,2,3,4,5,6)
        target.email = "name@email.com"
        target.id = "my@account.com"
        target.name = "test account"
        target.status = wnmodels.AccountStatus.disabled
        target.devices.append(wnmodels.Device.create("ID01", "MD01", "ANDR", "5.0"))
        target.devices.append(wnmodels.Device.create("ID02", "MD02", "IOS", "9.0"))

        actual = wndb.save_account(target)
        self.assertTrue(actual, msg="Account save failed")

        file = os.path.join(wndb._directories["account"], "{}.json".format(target.id.lower()))
        self.assertTrue(os.path.exists(file), "Account file not found")
        with open(file, "r") as f:
            actual = f.read()

        expected = '{"createdOn": "2016-01-02T03:04:05.000006", "devices": [{"id": "ID01", "model": "MD01", "platform": "ANDR", "version": "5.0"}, {"id": "ID02", "model": "MD02", "platform": "IOS", "version": "9.0"}], "email": "name@email.com", "id": "my@account.com", "name": "test account", "status": "disabled"}'
        self.assertEqual(expected, actual, msg="Account json string mismatch")

    def test_get_feedback(self):
        actual = wndb.get_feedback(MockModels.feedback_id)
        MockModels.validate_feedback(self, actual)

        actual = wndb.get_feedback("THIS IS A BAD ID")
        self.assertIsNone(actual, msg="Actual feedback: not None")

    def test_save_feedback(self):
        target = wnmodels.Feedback()
        target.account = "my@account.com"
        target.comments = "this is a test"
        target.date_time_stamp = datetime.datetime(2016,1,2,3,4,5,6)
        target.id = "f3e82852-97d8-4e49-baf9-c933b6c1c020"

        actual = wndb.save_feedback(target)
        self.assertTrue(actual, msg="Feedback save failed")

        file = os.path.join(wndb._directories["feedback"], "{}.json".format(target.id.lower()))
        self.assertTrue(os.path.exists(file), "Feedback file not found")
        with open(file, "r") as f:
            actual = f.read()

        expected = '{"account": "my@account.com", "comments": "this is a test", "dateTimeStamp": "2016-01-02T03:04:05.000006", "id": "f3e82852-97d8-4e49-baf9-c933b6c1c020"}'
        self.assertEqual(expected, actual, msg="Feedback json string mismatch")

    @classmethod
    def tearDownClass(cls):
        cls._store.cleanup()


if __name__ == '__main__':
    unittest.main()
