from flask import Flask
import windninjaconfig as wnconfig
import windninjaweb.filestore as wndb
import windninjaqueue.queue as wnqueue

app = Flask(__name__)
app.config.from_object(wnconfig.Config)

#if not app.debug:
#    import logging
#    h = logging.StreamHandler()
#    h.setLevel(logging.DEBUG)
#    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#    h.setFormatter(formatter)
#    
#    logger = logging.getLogger("windninjaweb.models")
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(h)
#
#    logger = logging.getLogger("windninjaweb.filestore")
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(h)

import windninjaweb.views
import windninjaweb.api
import windninjaweb.services

wndb.set_Store(app.config["DATASTORE"], False)
wnqueue.set_Queue(app.config["QUEUE"]["datastore"], False)