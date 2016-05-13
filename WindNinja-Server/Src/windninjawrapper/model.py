import os
import json
import smtplib
from email.mime.text import MIMEText
from config import CONFIG
import logger

class Project:
    def __init__(self, path):
        self.path = path
        self.jobFile = os.path.join(path, CONFIG.JOB_FILENAME)
        logger.verbose("job json path: {0}".format(self.jobFile))
        self.job = None
        self.demPath = None
        self.forecast = "NOMADS-NAM-CONUS-12-KM"
        self.parameters = "duration:12;vegetation:grass"
        self.domain = []
        self.products = {"vector":True, "raster":False, "topofire":True, "geopdf":False}
        self.email = None
        self.output = {}
        
    def openJob(self):
        with open(self.jobFile, "r") as json_file:
            json_string = json_file.read()
            logger.debug(json_string)
    
        self.job = json.loads(json_string)
        logger.debug(self.job)
        
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
            
            formatted_message = logger.log(*message_tuple)
            if formatted_message:
                self.job["messages"].append(formatted_message)
            
            
        if self.output is not None:
            self.job["output"] = {"products": self.output.values()}

        logger.debug(self.job)

        if write:
            pretty = 2 if logger.DEBUG_ENABLED else None
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
                logger.verbose("server requires login")  
                s.starttls()
                s.ehlo()
                s.login(CONFIG.MAIL["server"]["user"], CONFIG.MAIL["server"]["password"])
            logger.verbose("attempting to send notification text: {}".format(msg.as_string()))
            s.sendmail(CONFIG.MAIL["from_address"], self.job['email'].split(','), msg.as_string())
            s.close()
