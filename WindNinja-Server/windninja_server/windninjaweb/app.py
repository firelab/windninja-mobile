import logging

from flask import Flask
from flask import got_request_exception

import windninja_server.windninjaconfig as wnconfig
import windninja_server.windninjaqueue.queue as wnqueue
import windninja_server.windninjaweb.filestore as wndb


def log_exception(sender, exception, **extra):
    logging.exception(exception)


app = Flask(__name__)
app.config.from_object(wnconfig.Config)

wndb.set_Store(app.config["DATASTORE"])
wnqueue.set_Queue(app.config["QUEUE"])

logging.info("Starting the windninjaserver application")
got_request_exception.connect(log_exception, app)
