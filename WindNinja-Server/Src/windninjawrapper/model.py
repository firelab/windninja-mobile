import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from config import CONFIG
import logging

class Project:
    def __init__(self, path):
        self.error = None
        self.pretty_print = False
        self.path = path
        self.jobFile = os.path.join(path, CONFIG.JOB_FILENAME)
        logging.debug("job json path: {0}".format(self.jobFile))
        self.job = None
        self.demPath = None
        self.forecast = "NOMADS-NAM-CONUS-12-KM"
        self.parameters = "duration:12;vegetation:grass"
        self.domain = []
        self.products = {"vector":True, "raster":False, "topofire":True, "geopdf":False, "clustered": False, "weather": False}
        self.email = None
        self.output = {}
        
    def openJob(self):
        try:
            with open(self.jobFile, "r") as json_file:
                json_string = json_file.read()
                logging.debug("Job file string:\n{}".format(json_string))
        except IOError as oe:
            self.error = "I/O error({0}): {1}".format(oe.errno, oe.strerror)
            return

        try:
            self.job = json.loads(json_string)
            logging.debug("Job: {}".format(self.job))
        except ValueError as je:
            self.error = "Json.loads Error: {}".format(je.message)
            return

        if self.job.has_key("input"):
            # get the forecast name
            if self.job["input"].has_key("forecast"):
                self.forecast = self.job["input"]["forecast"]
            else:
                self.job["input"]["forecast"] = self.forecast
            
            # get the windninja parameters
            if self.job["input"].has_key("parameters"):
                self.parameters = self.job["input"]["parameters"]
            else:
                self.job["input"]["parameters"] = self.parameters

            #parse products: semi-colon delimited key:value pairs where key is the product name and value is boolean to generate
            if self.job["input"].has_key("products"):
                self.products = {}
                truelist = ("yes", "true", "t", "1")
                products = self.job["input"]["products"].split(";")
                for p in products:
                    pairs = p.split(":")
                    value = pairs[1].lower() in truelist
                    self.products[pairs[0].lower()] = value

            else:
                # the default back onto the job
                self.job["input"]["products"] = ""
                for p in selft.products.iterkeys():
                    self.products += "{0}:{1};".format(p, products[p])
            
            #parse the domain values into box
            if (self.job["input"].has_key("domain") and self.job["input"]["domain"].has_key("xmin") and self.job["input"]["domain"].has_key("ymin") and self.job["input"]["domain"].has_key("xmax") and self.job["input"]["domain"].has_key("ymax")):
                self.bbox = [self.job["input"]["domain"]["xmin"],self.job["input"]["domain"]["ymin"],self.job["input"]["domain"]["xmax"],self.job["input"]["domain"]["ymax"]]
            else:
                raise ValueError("Job does not contain a valid domain bound box")


    def updateJob(self, status, message_tuple, write):
        
        if self.job is None:
            return

        if status is not None:
            self.job["status"] = status

        if message_tuple is not None:
            if not self.job.has_key("messages"):
                self.job["messages"] = []

            logging.log(*message_tuple)

            #TODO: keep formatting in sync with web and queue projects that might also add messages... or sync all "models" into a module.
            formatted_message = "{} | {} | {}".format(datetime.now().isoformat(), logging.getLevelName(message_tuple[0]), message_tuple[1])
            self.job["messages"].append(formatted_message)

        if self.output is not None:
            self.job["output"] = self.output
            #if self.version >= 1.1:
                #self.job["output"]["products"] = self.output
            #else:
                # products is just list
                #self.job["output"] =  {"products": self.output.values()}
                # raster data is list of strings: 'name:max_speed'

        logging.debug("Job: {}".format(self.job))

        if write:
            pretty = 2 if self.pretty_print else None
            with open(self.jobFile, "w") as json_file:
                json_file.write(json.dumps(self.job, indent=pretty))

    def sendEmail(self):
        if self.job['email'] and self.job['email'].strip():
            msg = MIMEText("Your run '{}' has been completed.\nStatus: {}".format(self.job['name'], self.job["status"]))
            msg['Subject'] = 'WindNinja Run Complete'
            msg['From'] = CONFIG.MAIL["from_address"]
            msg['To'] = self.job['email']

            s = smtplib.SMTP(CONFIG.MAIL["server"]["address"])
            s.ehlo()
            if CONFIG.MAIL["server"]["user"] and CONFIG.MAIL["server"]["password"]:
                logging.debug("server requires login")  
                s.starttls()
                s.ehlo()
                s.login(CONFIG.MAIL["server"]["user"], CONFIG.MAIL["server"]["password"])
            logging.debug("attempting to send notification text: {}".format(msg.as_string()))
            s.sendmail(CONFIG.MAIL["from_address"], self.job['email'].split(','), msg.as_string())
            s.close()
