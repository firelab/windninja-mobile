import uuid
import datetime
import dateutil.parser
import json
from enum import Enum
import logging
import hashlib

import windninjaweb.utility as wnutils

#TODO: Break into sub package 
#TODO: better names for "from_" methods ???
_logger = logging.getLogger(__name__)

#----------JOB----------------
class JobStatus(Enum):
    unknown = 0
    new = 1
    waiting = 2
    executing = 3
    succeeded = 4
    failed = 5
    timedout = 6
    cancelling = 7
    cancelled = 8
    deleting = 9
    deleted = 10

class JobMessageType(Enum):
    info = 1
    error = 2

class Product:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.format = ""
        self.baseurl = ""
        self.package = ""
        self.files = []
        #self.data = []
        self.data = {}

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return None

        #TODO: validate values
        obj = cls()
        obj.name = json_dict.get("name")
        obj.type= json_dict.get("type")
        obj.format = json_dict.get("format")
        obj.baseurl = json_dict.get("baseurl")
        obj.package = json_dict.get("package")
        obj.data = json_dict.get("data", {})

        for file in json_dict.get("files", []):
            obj.files.append(file)

        #for data in json_dict.get("data", []):
        #    obj.data.append(data)
        
        return obj

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):

        files = []
        for f in self.files:
            files.append(f)
        
        #data = []
        #for d in self.data:
        #    data.append(d)

        dict = {
            "name" : self.name,
            "type" : self.type,
            "format" : self.format,
            "baseurl" : self.baseurl,
            "package" : self.package,
            "files" : files,
            #"data" : data,
            "data" : self.data,
            }

        return dict

class BBOX:
    def __init__(self):
        self.xmin = 0.0
        self.ymin = 0.0
        self.xmax = 0.0
        self.ymax = 0.0

    @classmethod
    def create(cls, xmin, ymin, xmax, ymax):
        obj = cls()
        obj.xmin = xmin
        obj.ymin = ymin
        obj.xmax = xmax
        obj.ymax = ymax
        return obj

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return None

        obj = cls()
        #TODO: validate values
        obj.xmin = json_dict.get("xmin")
        obj.ymin = json_dict.get("ymin")
        obj.xmax = json_dict.get("xmax")
        obj.ymax = json_dict.get("ymax")
        return obj

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):
        dict = {
            "xmin" : self.xmin,
            "ymin" : self.ymin,
            "xmax" : self.xmax,
            "ymax" : self.ymax
            }
        return dict

class JobInput: 
    def __init__(self):
        self.domain = BBOX()
        self.forecast = ""
        self.parameters = ""
        self.products = ""

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return None

        obj = cls()

        #TODO: validate values
        obj.domain = BBOX.from_dict(json_dict.get("domain", {}))
        obj.forecast = json_dict.get("forecast")
        obj.parameters = json_dict.get("parameters")
        obj.products = json_dict.get("products")

        return obj
    
    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):
        dict = {
            "domain" : self.domain.to_dict(),
            "forecast" : self.forecast,
            "parameters" : self.parameters,
            "products" : self.products
            }
        return dict

class JobOutput: 
    def __init__(self):
        self.products = {}
        self.simulations = {}

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return None

        obj = cls()

        for k in json_dict:
            if k == "simulations":
                obj.simulations = json_dict.get("simulations")
            else:
                obj.products[k] = Product.from_dict(json_dict[k])

        #products = json_dict.get("products", {})
        #for product in products:
        #    obj.products.append(Product.from_dict(product))

        return obj

    def updateBaseUrls(self, url):
        for product in self.products:
            self.products[product].baseurl = url

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for tests to sort... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):
        #list = []
        #for p in self.products:
        #    list.append(p.to_dict())

        dict = {
        #    "products" : list
            "simulations": self.simulations
        }

        for p in self.products:
            dict[p] = self.products[p].to_dict()

        return dict

class Job ():
    def __init__(self):
        self.id = ""
        self.name = ""
        self.account = ""
        self.email = ""
        self.status = JobStatus.unknown
        self.messages = []
        self.output = JobOutput()
        self.input = JobInput()
        
    @classmethod
    def create(cls, initializer):
        # initializer can be flattened to structured
        job = cls()
        job.id = str(uuid.uuid4())
        job.status = JobStatus.new
        job.add_message("job created", JobMessageType.info)

        dict = initializer or {}
        job.account = dict.get("account", "")
        job.email = dict.get("email", "")
        job.name = dict.get("name", "")

        dict = dict.get("input", dict)
        job.input.forecast = dict.get("forecast", "")
        job.input.parameters = dict.get("parameters", "")
        job.input.products = dict.get("products", "")

        job.input.domain = BBOX.from_dict(dict.get("domain", dict))

        return job

    @classmethod
    def from_json(cls, json_string):
        _logger.debug(json_string)
        
        json_dict = json.loads(json_string)
        return cls.from_dict(json_dict)
        
    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return None

        obj = cls()
        # TODO which of these items MUST be found or generate an error?
        
        #REQUIRED
        # TODO: check required values for something other than empty string
        obj.id = json_dict["id"]
        obj.name = json_dict["name"]
        obj.status = JobStatus[json_dict["status"].lower()]    
        obj.account = json_dict["account"]
        
        #OPTIONAL
        obj.email = json_dict.get("email")
        for message in json_dict.get("messages", []):
            obj.messages.append(message)

        obj.input = JobInput.from_dict(json_dict.get("input"))
        obj.output = JobOutput.from_dict(json_dict.get("output"))

        return obj

    def add_message(self, message, type):
        #TODO: keep formatting in sync with web and queue projects that might also add messages... or sync all "models" into a module.
        formatted = "{0} | {1} | {2}".format(datetime.datetime.utcnow().isoformat(), type.name, message)
        self.messages.append(formatted)

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):
        list = []
        for m in self.messages:
            list.append(m)

        dict = {
            "id" : self.id,
            "name" : self.name,
            "account" : self.account,
            "email" : self.email,
            "status" : self.status.name,
            "input" : None if self.input is None else self.input.to_dict(),
            "output" : None if self.output is None else self.output.to_dict(),
            "messages": list
            }
        return dict

#----------FEEDBACK----------------
class Feedback:
    def __init__(self):
        self.id = ""
        self.account = ""
        self.date_time_stamp = None
        self.comments = ""

    @classmethod
    def create(cls, initializer):
        feedback = cls()
        feedback.id = str(uuid.uuid4())
        feedback.date_time_stamp = datetime.datetime.utcnow()
        
        #required so throw an error if not found in initialier
        feedback.account = initializer["account"]
        feedback.comments = initializer["comments"]

        return feedback

    @classmethod
    def from_json(cls, json_string):
        _logger.debug(json_string)
        
        json_dict = json.loads(json_string)
        return cls.from_dict(json_dict)

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return

        obj = cls()
        # TODO which of these items MUST be found or generate an error?
        
        #REQUIRED
        # TODO: check required values for something other than empty string
        obj.id = json_dict["id"]
        obj.account = json_dict["account"]
        obj.date_time_stamp = dateutil.parser.parse(json_dict["dateTimeStamp"])
        obj.comments = json_dict["comments"]

        return obj

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):
        dict = {
            "id" : self.id,
            "account" : self.account,
            "dateTimeStamp" : self.date_time_stamp.isoformat(),
            "comments" : self.comments
            }
        return dict
        
    def to_email_body(self):
        template = "ID:{}\nACCOUNT:{}\nDATE:{}\nCOMMENTS:\n{}"
        return template.format(self.id, self.account, self.date_time_stamp.isoformat(), self.comments)

#----------NOTIFICATION------------
class Notification:
    def __init__(self):
        self.id = ""
        self.message = ""
        self.expires = None

    @classmethod
    def create(cls, initializer):
        notification = cls()
        notification.id = str(uuid.uuid4())
        
        #required so throw an error if not found in initialier
        notification.expires = initializer["expires"]
        notification.message = initializer["message"]
        
        return notification

    @classmethod
    def from_json(cls, json_string):
        _logger.debug(json_string)
        
        json_dict = json.loads(json_string)
        return cls.from_dict(json_dict)

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return

        obj = cls()
        # TODO which of these items MUST be found or generate an error?
        
        #REQUIRED
        # TODO: check required values for something other than empty string
        obj.id = json_dict["id"]
        obj.message = json_dict["message"]
        obj.expires = dateutil.parser.parse(json_dict["expires"])
        
        return obj

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):
        dict = {
            "id" : self.id,
            "message" : self.message,
            "expires" : self.expires.isoformat() if self.expires else datetime.datetime.max,
        }
        return dict

#----------ACCOUNT----------------
class AccountStatus(Enum):
    unknown = 0
    pending = 1
    accepted = 2
    disabled = 3

class Device:
    def __init__(self):
        self.id = ""
        self.model = ""
        self.platform = ""
        self.version = ""

    @classmethod
    def create(cls, id, model, platform, version):
        
        # validate requirements
        wnutils.validate(id, str, "Invalid device id: {}")
        wnutils.validate(model, str, "Invalid device model: {}")
        wnutils.validate(platform, str, "Invalid device platform: {}")
        wnutils.validate(version, str, "Invalid device version: {}")         

        obj = cls()
        obj.id = id
        obj.model = model
        obj.platform = platform
        obj.version = version
        return obj

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return

        obj = cls.create(json_dict["id"], json_dict["model"], 
                         json_dict["platform"],  json_dict["version"])

        return obj

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):
        dict = {
            "id" : self.id,
            "model" : self.model,
            "platform" : self.platform,
            "version" : self.version
            }
        return dict

class Account:
    _code_template = "{0}&{1}"

    def __init__(self):
        self.id = ""
        self.email = ""
        self.name = ""
        self.created_on = None
        self.status = AccountStatus.unknown
        self.devices = []

    @classmethod
    def create(cls, id, email, name):
        account = cls()

        account.id = id
        account.email = email
        account.name = name
        account.status = AccountStatus.pending
        account.created_on = datetime.datetime.utcnow()

        return account

    @classmethod
    def from_json(cls, json_string):
        _logger.debug(json_string)
        
        json_dict = json.loads(json_string)
        return cls.from_dict(json_dict)

    @classmethod
    def from_dict(cls, json_dict):
        if not json_dict:
            return

        obj = cls()
        # TODO which of these items MUST be found or generate an error?
        
        #REQUIRED
        # TODO: check required values for something other than empty string
        obj.id = json_dict["id"]
        obj.email = json_dict["email"]
        obj.name = json_dict["name"]
        obj.status = AccountStatus[json_dict["status"].lower()]    
        obj.created_on = dateutil.parser.parse(json_dict["createdOn"])
        
        for device in json_dict.get("devices", []):
            obj.devices.append(Device.from_dict(device))

        return obj
    
    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):

        list = []
        for d in self.devices:
            list.append(d.to_dict())

        dict = {
            "id" : self.id,
            "email" : self.email,
            "name" : self.name,
            "createdOn" : self.created_on.isoformat(),
            "status" : self.status.name,
            "devices" : list
            }

        return dict

    def generate_code(self):
        encoded = Account._code_template.format(self.created_on.isoformat(), self.id).encode("utf-8")
        hash = hashlib.sha256(encoded)
        return hash.hexdigest()

    def has_device(self, device):
        for d in self.devices:
            if d.id == device.id:
                return True

        return False

class AccountState:
    def __init__(self):
        self.account = ""
        self.status = AccountStatus.unknown
        self.message = ""

    @classmethod
    def create(cls, account, message = ""):
        state = cls()
        state.account = account.id
        state.status = account.status
        state.message = message
        return state

    def to_json(self):
        dict = self.to_dict()

        #TODO: sorting seems like a waste but tests fail without a known string represtatntion 
        # Maybe set module flags for these... 
        return json.dumps(dict, sort_keys=True)

    def to_dict(self):

        list = []
        
        dict = {
            "account" : self.account,
            "accountStatus" : self.status.name,
            "message" : self.message
            }

        return dict