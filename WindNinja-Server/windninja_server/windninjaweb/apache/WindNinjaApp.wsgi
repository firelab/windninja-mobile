import sys
import os
import logging

#TODO: update
logging.basicConfig(stream=sys.stderr)

# initialize the flask application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "..", "..", ".."))

# handle wsgi startup
#NOTE: this is necessary to get the Apache config SetEnv values
# but might be able to use instance folder? http://flask.pocoo.org/docs/0.10/config/#instance-folders
def application(environ, start_response):
    for key in ['WNSERVER_CONFIG', 'AWS_SMTP_HOST', 'AWS_SMTP_KEY', 'AWS_SMTP_SECRET']:
        os.environ[key] = environ[key]

    from windninja_server.windninjaweb.app import app as _application
    return _application(environ, start_response)
