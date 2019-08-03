"""
Utility methods and classes for the project
"""
import smtplib
import base64
from email.mime.text import MIMEText


class Namespace(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def send_email(server, to_addresses, from_address, subject, body):
    """
    Send email using setting defined in 'server'

    Returns:
        SMTP: SMTP object used to send the email. Primarily for unit testing.
    """

    # NOTE: from address does not appear to 'reset' from the gmail account used
    # TODO: implement other SMTP providers or non-SMTP variations

    # create the message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_addresses

    # connect to server and send
    s = smtplib.SMTP(server["address"])
    s.ehlo()
    if server["user"] and server["password"]:
        s.starttls()
        s.ehlo()
        s.login(server["user"], server["password"])
    s.sendmail(from_address, to_addresses.split(","), msg.as_string())
    s.close()

    return s


def is_whitelisted(email, whitelist):
    """
    Determines if an email address/domian is in the whitelist

    Returns boolean: True/False
    """
    whitelisted = email in (whitelist.get("emails", []) or [])
    if not whitelisted:
        domain = email.split("@")[-1]
        whitelisted = domain in (whitelist.get("domains", []) or [])
    return whitelisted


# TODO: better name? or move to "models" as it's really specific to those attributes
def validate(value, value_type, message):
    """
    Validates a value is not "falsey" and of the correct type.

    Returns boolean or raises error
    """
    if not value:
        raise ValueError(message.format(value))

    if not type(value) is value_type:
        raise TypeError(message.format(type(value)))

    return True


def encode(key, clear):
    """
    A very simple obfuscation encoding function
    --- key is btyes i.e. from os.urandom(24)

    Returns: byte string
    """
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + key_c) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode("utf-8"))


def decode(key, enc):
    """
    Decoding function for a very simple obfuscation encoding function
    --- key is btyes i.e. from os.urandom(24)

    Returns: string
    """
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode("utf-8")
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - key_c) % 256)
        dec.append(dec_c)
    return "".join(dec)
