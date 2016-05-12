import json
import os
from flask import abort, url_for, send_from_directory
from flask_restful import Api, Resource, reqparse, fields, marshal

from windninjaweb.app import app
import windninjaweb.models as wnmodels
import windninjaweb.filestore as wndb
import windninjaqueue.queue as wnqueue
import windninjaweb.utility as wnutil

_email_parameters = app.config.get("MAIL", None)

# controllers
class EnumField(fields.Raw):
    def format(self, value):
        return value.name

class JobController(Resource):
    
    def __init__(self):
        # post request parsing
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("name", type=str, required=True, help="Job name is required", location="values")
        self.reqparse.add_argument("xmin", type=float, required=True, help="Job xmin is required", location="values")
        self.reqparse.add_argument("ymin", type=float, required=True, help="Job ymin is required", location="values")
        self.reqparse.add_argument("xmax", type=float, required=True, help="Job xmax is required", location="values")
        self.reqparse.add_argument("ymax", type=float, required=True, help="Job ymax is required", location="values")
        self.reqparse.add_argument("parameters", type=str, required=True, help="Job parameters is required", location="values")
        self.reqparse.add_argument("forecast", type=str, required=True, help="Job forecast is required", location="values")
        self.reqparse.add_argument("email", type=str, default="", location="values")
        self.reqparse.add_argument("account", type=str, required=True, help="Job account is required", location="values")
        self.reqparse.add_argument("products", type=str, required=True, help="Job products is required", location="values")
        
        # job serialiation specification (mostly defined in the .json() function of job now.
        bbox_fields = {
            "xmin": fields.Float(),
            "ymin": fields.Float(),
            "xmax": fields.Float(),
            "ymax": fields.Float(),
        }

        product_fields = {
            "name" : fields.String(attribute="name"),
            "type" : fields.String(attribute="type"),
            "format" : fields.String(attribute="format"),
            "baseUrl" : fields.String(attribute="baseurl"),
            "package" : fields.String(attribute="package"),
            "files" : fields.List(fields.String(), attribute="files"),
            "data" : fields.List(fields.String(), attribute="data"),
        }

        job_input_fields = {
            "domain" : fields.Nested(bbox_fields, attribute="domain"),
            "forecast" : fields.String(attribute="forecast"),
            "parameters" : fields.String(attribute="parameters"),
            "products" :fields.String(attribute="products")
        }

        job_output_fields = {
            "products": fields.List(fields.Nested(product_fields), attribute="products")
        }

        self.job_fields =  {
            "name" : fields.String(attribute="name"),
            "email" : fields.String(attribute= "email"),
            "id"  : fields.String(attribute="id"),
            "status" : EnumField(attribute='status'),
            "messages" : fields.List(fields.String, attribute='messages'),
            "output" : fields.Nested(job_output_fields, attribute="output"),
            "input" : fields.Nested(job_input_fields,  attribute="input"),
            "account" : fields.String(attribute="account")
        }

        super(JobController, self).__init__()

    def get(self, id):
        
        # get the job
        job = wndb.get_job(id)
        if job:

            # update product urls if complete
            if job.status == wnmodels.JobStatus.succeeded:
                url = url_for("output", _external=True, job=job.id.replace("-",""), id="")
                for product in job.output.products:
                    product.baseurl = url
                    
            return marshal(job, self.job_fields)
        else:
            abort(404)

    def post(self):
        args = self.reqparse.parse_args()
        job = wnmodels.Job.create(args)
        success = wndb.save_job(job)

        if success:
            wnqueue.enqueue(job.id)
            return marshal(job, self.job_fields)
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

        self.account_fields =  {
            "id"  : fields.String(attribute="id"),
            "email" : fields.String(attribute= "email"),
            "name" : fields.String(attribute="name"),
            "status" : EnumField(attribute='status'),
            "createdOn" : fields.DateTime(dt_format="iso8601", attribute="created_on"),
            "devices" : fields.List(fields.Nested(device_fields), attribute="devices")
        }

        super(AccountController, self).__init__()

    def get(self, id):
        
        account = wndb.get_account(id)
        
        if account:
            return marshal(account, self.account_fields)
        else:
            abort(404)

class FeedbackController(Resource):
    
    def __init__(self):
        self.post_parser = reqparse.RequestParser()
        self.post_parser.add_argument("account", type=str, required=True, help="Account is required", location=["values", "json"])
        self.post_parser.add_argument("comments", type=str, required=True, help="Comments is required", location=["values", "json"])

        self.feedback_fields = {
            "id" : fields.String(attribute="id"),
            "account" : fields.String(attribute="account"),
            "dateTimeStamp" : fields.DateTime(dt_format="iso8601", attribute="date_time_stamp"),
            "comments" : fields.String(attribute="comments")
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
                wnutil.send_email(_email_parameters.get("server", {}), 
                    _email_parameters.get("support_address", ""), 
                    _email_parameters.get("from_address", ""), 
                    subject, body)
            except:
                pass
        
        
            return marshal(feedback, self.feedback_fields)
        else:
            abort(500)

class OutputController(Resource):
    def get(self, job, id):
        job = job.replace("-", "")
        return send_from_directory(os.path.join(wndb._directories["job"], job), id)

api = Api(app)
api.add_resource(JobController, "/api/job", endpoint="jobs" )
api.add_resource(JobController, "/api/job/<string:id>", endpoint="job")
api.add_resource(AccountController, "/api/account/<string:id>", endpoint="account")
api.add_resource(FeedbackController, "/api/feedback", endpoint="feedback")
api.add_resource(OutputController, "/output/<string:job>/<string:id>", endpoint="output")

#/api/job/7cd8759fe49f49749efd43748b40419c
#/api/account/fred.spataro@gmail.com
