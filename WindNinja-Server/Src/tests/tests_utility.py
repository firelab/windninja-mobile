import unittest
import os
import windninjaweb.utility as wnutils

class TestUtility(unittest.TestCase):
    mail = {"server": {"address": "smtp.gmail.com:587", "password": "@dmin4dev", "user": "gcs4windninja@gmail.com"},  "from_address": "windninja@yourdatasmarter.com"}
    auto_register = {"domains": ["fs.fed.us", "yourdatasmarter.com"], "emails":["someone@gmail.com", "me@gmail.com"]}

    @classmethod
    def setUpClass(cls):
        pass

    def test_send_email(self):
        to_addresses = "fspataro@yourdatasmarter.com"
        body = "This is a unit test email"
        subject = "WindNinja Server UnitTest"
        wnutils.send_email(TestUtility.mail["server"], to_addresses, TestUtility.mail["from_address"], subject, body)
       
    def test_is_whitelisted(self):
        
        valid_domain_email = "me@yourdatasmarter.com"
        valid_email = "me@gmail.com"
        invalid_email = "not_me@gmail.com"

        # populated whitelist
        whitelist = TestUtility.auto_register
        self.assertTrue(wnutils.is_whitelisted(valid_domain_email, whitelist), msg="Valid domain failed")
        self.assertTrue(wnutils.is_whitelisted(valid_email, whitelist), msg="Valid email failed")
        self.assertFalse(wnutils.is_whitelisted(invalid_email, whitelist), msg="Invalid email accepted")

        # empty whitelist
        whitelist = {}
        self.assertFalse(wnutils.is_whitelisted(valid_domain_email, whitelist), msg="Valid domain accepted with empty whitelist")
        self.assertFalse(wnutils.is_whitelisted(valid_email, whitelist), msg="Valid email accepted with empty whitelist")
        self.assertFalse(wnutils.is_whitelisted(invalid_email, whitelist), msg="Invalid email accepted with empty whitelist")
    
    def test_validate(self):

        target = wnutils.validate
        message = "Incorrect value: {}"
        
        value = "a"
        self.assertTrue(target(value, str, message), "Validate incorrectly failed")

        value = ""
        self.assertRaisesRegex(ValueError, message.format(value), target, value, str, message)

        value = 1
        self.assertRaisesRegex(TypeError, message.format(type(value)), target, value, str, message)

    def test_encode_decode(self):
        key =  b'.\x87\xa4m9\xbd)_\x07\x08{\xf4\xf8qY^\x81\x9f3\xb4U\xca|\x12'
        value = "me@mail.com"
        encoded = wnutils.encode(key, value)
        decoded = wnutils.decode(key, encoded)

        self.assertEqual(value, decoded, "Incorrect decoded value")

    @classmethod
    def tearDownClass(cls):
        pass

if __name__ == '__main__':
    unittest.main()
