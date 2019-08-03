import pytest

import os
import smtplib
import windninjaweb.utility as wnutils


MAIL = {
    "server": {
        "address": "smtp.gmail.com:587",
        "password": "@dmin4dev",
        "user": "gcs4windninja@gmail.com",
    },
    "from_address": "windninja@yourdatasmarter.com",
}

AUTO_REGISTER = {
    "domains": ["fs.fed.us", "yourdatasmarter.com"],
    "emails": ["someone@gmail.com", "me@gmail.com"],
}


def test_send_email(mocker):
    mock_smtp = mocker.patch("smtplib.SMTP")

    to_addresses = "fspataro@yourdatasmarter.com"
    body = "This is a unit test email"
    subject = "WindNinja Server UnitTest"

    expected_msg = 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\nSubject: WindNinja Server UnitTest\nFrom: windninja@yourdatasmarter.com\nTo: fspataro@yourdatasmarter.com\n\nThis is a unit test email'

    smtp = wnutils.send_email(
        MAIL["server"], to_addresses, MAIL["from_address"], subject, body
    )

    smtp.sendmail.assert_called_with(MAIL["from_address"], [to_addresses], expected_msg)


def test_is_whitelisted():

    valid_domain_email = "me@yourdatasmarter.com"
    valid_email = "me@gmail.com"
    invalid_email = "not_me@gmail.com"

    # populated whitelist
    whitelist = AUTO_REGISTER
    assert wnutils.is_whitelisted(valid_domain_email, whitelist), "Valid domain failed"
    assert wnutils.is_whitelisted(valid_email, whitelist), "Valid email failed"
    assert not wnutils.is_whitelisted(
        invalid_email, whitelist
    ), "Invalid email accepted"

    # empty whitelist
    whitelist = {}
    assert not wnutils.is_whitelisted(
        valid_domain_email, whitelist
    ), "Valid domain accepted with empty whitelist"
    assert not wnutils.is_whitelisted(
        valid_email, whitelist
    ), "Valid email accepted with empty whitelist"
    assert not wnutils.is_whitelisted(
        invalid_email, whitelist
    ), "Invalid email accepted with empty whitelist"


def test_validate():
    message = "Incorrect value: {}"

    assert wnutils.validate("a", str, message), "Validate incorrectly failed"

    with pytest.raises(ValueError) as excinfo:
        wnutils.validate("", str, message)

    assert message.format("") == str(excinfo.value)

    with pytest.raises(TypeError) as excinfo:
        wnutils.validate(1, str, message)

    assert message.format(type(1)) == str(excinfo.value)


def test_encode_decode():
    key = b".\x87\xa4m9\xbd)_\x07\x08{\xf4\xf8qY^\x81\x9f3\xb4U\xca|\x12"
    value = "me@mail.com"
    encoded = wnutils.encode(key, value)
    decoded = wnutils.decode(key, encoded)

    assert value == decoded, "Value decoded incorrectly"
