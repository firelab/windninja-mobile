import logging

from flask import Flask
from flask import got_request_exception
from flask_restful import Api

import windninja_server.windninjaconfig as wnconfig
import windninja_server.windninjaqueue.queue as wnqueue
import windninja_server.windninjaweb.filestore as wndb
import windninja_server.windninjaweb.api as wnapi
from windninja_server.windninjaweb.services import registration_blueprint


def log_exception(sender, exception, **extra):
    logging.exception(exception)

# configure_app
app = Flask(__name__)
app.config.from_object(wnconfig.Config)

wndb.set_Store(app.config["DATASTORE"])
wnqueue.set_Queue(app.config["QUEUE"])

logging.info("Starting the windninjaserver application")
got_request_exception.connect(log_exception, app)


# register_main_endpoints
api = Api(app)
api.add_resource(wnapi.JobController, "/api/job", endpoint="jobs")
api.add_resource(wnapi.JobController, "/api/job/<string:id>", endpoint="job")
api.add_resource(wnapi.AccountController, "/api/account/<string:id>", endpoint="account")
api.add_resource(wnapi.FeedbackController, "/api/feedback", endpoint="feedback")
api.add_resource(
    wnapi.NotificationListController,
    "/api/notification",
    endpoint="notifications"
)
api.add_resource(
    wnapi.NotificationController,
    "/api/notification/<string:id>",
    endpoint="notification"
)
api.add_resource(
    wnapi.OutputController,
    "/output/<string:job>/<string:id>",
    endpoint="output"
)

# register_service_endpoints
app.register_blueprint(registration_blueprint)

application = app
