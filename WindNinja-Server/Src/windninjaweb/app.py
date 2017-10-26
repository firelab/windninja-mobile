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