from flask import Flask
import windninjaconfig as wnconfig
import windninjaweb.filestore as wndb
import windninjaqueue.queue as wnqueue

app = Flask(__name__)
app.config.from_object(wnconfig.Config)

import windninjaweb.views
import windninjaweb.api
import windninjaweb.services

wndb.set_Store(app.config["DATASTORE"], False)
wnqueue.set_Queue(app.config["QUEUE"], False)

# global expection logging
import logging

logging.info('Starting the windninjaserver application')

def log_exception(sender, exception, **extra):
    logging.exception(exception)

from flask import got_request_exception
got_request_exception.connect(log_exception, app)
