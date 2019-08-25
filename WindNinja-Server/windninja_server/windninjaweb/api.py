import os
import logging

from flask import abort, url_for, send_from_directory, jsonify
from flask_restful import Resource, reqparse, fields, marshal

import windninja_server.windninjaweb.models as wnmodels
import windninja_server.windninjaweb.filestore as wndb
import windninja_server.windninjaqueue.queue as wnqueue
import windninja_server.windninjaweb.utility as wnutil
import windninja_server.windninjaconfig as wnconfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
_email_parameters = wnconfig.Config.MAIL


def error_response(code, message):
    response = jsonify({"message": message})
    response.status_code = code
    return response


# controllers
class EnumField(fields.Raw):
    def format(self, value):
        return value.name


class JobController(Resource):
    def __init__(self):
        # post request parsing
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "name",
            type=str,
            required=True,
            help="Job name is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "xmin",
            type=float,
            required=True,
            help="Job xmin is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "ymin",
            type=float,
            required=True,
            help="Job ymin is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "xmax",
            type=float,
            required=True,
            help="Job xmax is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "ymax",
            type=float,
            required=True,
            help="Job ymax is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "parameters",
            type=str,
            required=True,
            help="Job parameters is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "forecast",
            type=str,
            required=True,
            help="Job forecast is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "email", type=str, default="", location=["json", "values"]
        )
        self.reqparse.add_argument(
            "account",
            type=str,
            required=True,
            help="Job account is required",
            location=["json", "values"],
        )
        self.reqparse.add_argument(
            "products",
            type=str,
            required=True,
            help="Job products is required",
            location=["json", "values"],
        )

        super(JobController, self).__init__()

    def get(self, id):

        # get the job
        job = wndb.get_job(id)
        if job:

            # update product urls if complete
            if job.status == wnmodels.JobStatus.succeeded:
                url = url_for(
                    "output", _external=True, job=job.id.replace("-", ""), id=""
                )
                job.output.updateBaseUrls(url)

            return job.to_dict()
        else:
            abort(404)

    def post(self):
        args = self.reqparse.parse_args()
        job = wnmodels.Job.create(args)
        success = wndb.save_job(job)

        if success:
            try:
                wnqueue.enqueue(job.id)
            except Exception as ex:
                job.status = wnmodels.JobStatus.failed
                job.add_message(str(ex), wnmodels.JobMessageType.error)
                wndb.save_job(job)

            return job.to_dict()
        else:
            abort(500)


class AccountController(Resource):
    def __init__(self):
        # serialiation specification (mostly defined in the .json() function now.
        device_fields = {
            "id": fields.String(),
            "model": fields.String(),
            "platform": fields.String(),
            "version": fields.String(),
        }

        self.account_fields = {
            "id": fields.String(attribute="id"),
            "email": fields.String(attribute="email"),
            "name": fields.String(attribute="name"),
            "status": EnumField(attribute="status"),
            "createdOn": fields.DateTime(dt_format="iso8601", attribute="created_on"),
            "devices": fields.List(fields.Nested(device_fields), attribute="devices"),
        }

        super(AccountController, self).__init__()

    def get(self, id):

        account = wndb.get_account(id)

        if account:
            return marshal(account, self.account_fields)
        else:
            abort(404)


class NotificationListController(Resource):
    def __init__(self):

        super(NotificationListController, self).__init__()

    def get(self):

        notifications = wndb.get_notifications(exprired=False)

        if notifications is None:
            return []
        else:
            notifications_list = [n.to_dict() for n in notifications]
            return notifications_list


class NotificationController(Resource):
    def __init__(self):

        super(NotificationController, self).__init__()

    def get(self, id):
        notification = wndb.get_notification(id)

        if notification:
            return notification.to_dict()
        else:
            abort(404)


class FeedbackController(Resource):
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument(
            "account",
            type=str,
            required=True,
            help="Account is required",
            location=["values", "json"],
        )
        self.post_parser.add_argument(
            "comments",
            type=str,
            required=True,
            help="Comments is required",
            location=["values", "json"],
        )

        self.feedback_fields = {
            "id": fields.String(attribute="id"),
            "account": fields.String(attribute="account"),
            "dateTimeStamp": fields.DateTime(
                dt_format="iso8601", attribute="date_time_stamp"
            ),
            "comments": fields.String(attribute="comments"),
        }

    def post(self):
        args = self.post_parser.parse_args()
        feedback = wnmodels.Feedback.create(args)
        success = wndb.save_feedback(feedback)

        if success:
            try:
                # send the email
                subject = "WindNinja Mobile - Feedback"
                body = feedback.to_email_body()
                wnutil.send_email(
                    _email_parameters.get("server", {}),
                    _email_parameters.get("support_address", ""),
                    _email_parameters.get("from_address", ""),
                    subject,
                    body,
                )
            except Exception:
                # return error_response(500, str(ex))
                logger.exception(f"Feedback from {feedback.account} failed")

            return marshal(feedback, self.feedback_fields)
        else:
            abort(500)


class OutputController(Resource):
    def get(self, job, id):
        job = job.replace("-", "")
        return send_from_directory(os.path.join(wndb._directories["job"], job), id)


# /api/job/23becdaadf7c4ec2993497261e63d813
# /api/account/test@gmail.com
