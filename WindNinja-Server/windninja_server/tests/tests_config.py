import unittest
import tempfile
import os


class TestConfig(unittest.TestCase):
    # yaml_string = "---\ndatastore: C:/WindNinjaServer/Data\nauto_register:\n    mode: EMAIL\n    domains: \n        - fs.fed.us\n        - yourdatasmarter.com\n    emails:\n        - someone@mail.com\n        - me@mail.com\nmail:\n    server:\n        address: smtp.mail.com:587\n        password: 'pwd4mail'\n        user: admin_account@mail.com\n    from_address: from_account@mail.com\n"
    yaml_string = "auto_register:\n  domains:\n  - fs.fed.us\n  - yourdatasmarter.com\n  emails:\n  - someone@mail.com\n  - me@mail.com\n  mode: EMAILS\ndatastore: C:/WindNinjaServer/Data\nmail:\n  from_address: from_account@mail.com\n  server:\n    address: smtp.mail.com:587\n    password: 'pwd4mail'\n    user: admin_account@mail.com\nqueue:\n  datastore: C:/WindNinjaServer/Data/Queue\n  loop_interval: 5\n  max_running_jobs: 5\n  python_executable: C:/python.exe\n  windninja_wrapper: C:/WindNinjaServer/windninja.py\n"

    @classmethod
    def setUpClass(cls):
        # create a temp file to read
        cls._config_file = tempfile.NamedTemporaryFile(delete=False, mode="w")
        cls._config_file.file.write(cls.yaml_string)
        cls._config_file.file.close()
        os.environ["WNWEB_CONFIG"] = cls._config_file.name

    def test_config(self):
        import windninjaconfig as wnconfig

        self.assertEqual(
            wnconfig.Config.DATASTORE,
            "C:/WindNinjaServer/Data",
            msg="Incorrect DATASTORE value",
        )

        self.assertIsNotNone(wnconfig.Config.MAIL, msg="MAIL is None")
        self.assertIsNotNone(wnconfig.Config.MAIL["server"], msg="MAIL server is None")
        self.assertEqual(
            wnconfig.Config.MAIL["server"]["address"],
            "smtp.mail.com:587",
            msg="Incorrect MAIL server address value",
        )
        self.assertEqual(
            wnconfig.Config.MAIL["server"]["user"],
            "admin_account@mail.com",
            msg="Incorrect MAIL server user value",
        )
        self.assertEqual(
            wnconfig.Config.MAIL["server"]["password"],
            "pwd4mail",
            msg="Incorrect MAIL server password value",
        )
        self.assertEqual(
            wnconfig.Config.MAIL["from_address"],
            "from_account@mail.com",
            msg="Incorrect MAIL from address value",
        )

        self.assertIsNotNone(wnconfig.Config.AUTO_REGISTER, msg="AUTO_REGISTER is None")
        self.assertIn(
            wnconfig.Config.AUTO_REGISTER["mode"],
            ["ALL", "EMAILS", "NONE"],
            msg="Invalid AUTO_REGISTER mode value",
        )
        self.assertIsNotNone(
            wnconfig.Config.AUTO_REGISTER["domains"],
            msg="AUTO_REGISTER domains is None",
        )
        self.assertCountEqual(
            wnconfig.Config.AUTO_REGISTER["domains"],
            ["fs.fed.us", "yourdatasmarter.com"],
            msg="Mismatched AUTO_REGISTER domains list",
        )
        self.assertIsNotNone(
            wnconfig.Config.AUTO_REGISTER["emails"], msg="AUTO_REGISTER emails is None"
        )
        self.assertCountEqual(
            wnconfig.Config.AUTO_REGISTER["emails"],
            ["someone@mail.com", "me@mail.com"],
            msg="Mismatched AUTO_REGISTER emails list",
        )

        self.assertIsNotNone(wnconfig.Config.QUEUE, "QUEUE is None")
        self.assertEqual(
            wnconfig.Config.QUEUE["datastore"],
            "C:/WindNinjaServer/Data/Queue",
            "Invalid QUEUE datastore value",
        )
        self.assertEqual(
            wnconfig.Config.QUEUE["max_running_jobs"],
            5,
            "Invalid QUEUE max_running_jobs value",
        )
        self.assertEqual(
            wnconfig.Config.QUEUE["loop_interval"],
            5,
            "Invalid QUEUE loop_interval value",
        )
        self.assertEqual(
            wnconfig.Config.QUEUE["python_executable"],
            "C:/python.exe",
            "Invalid QUEUE python_executable value",
        )
        self.assertEqual(
            wnconfig.Config.QUEUE["windninja_wrapper"],
            "C:/WindNinjaServer/windninja.py",
            "Invalid QUEUE windninja_wrapper value",
        )

    @classmethod
    def tearDownClass(cls):
        os.remove(cls._config_file.name)


if __name__ == "__main__":
    unittest.main
