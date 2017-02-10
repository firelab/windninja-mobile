"""
Services are RPC style methods for web application
"""
from flask import request, abort, make_response, url_for, render_template
from flask_restful import reqparse
from werkzeug import exceptions
import json
import time

from windninjaweb.app import app
import windninjaweb.models as wnmodels
import windninjaweb.filestore as wndb
import windninjaweb.utility as wnutil

# ----------------CONFIGURATION----------------
_register_parser = reqparse.RequestParser()
_register_parser.add_argument("name", type=str, required=True, help="Name is required", location=["values", "json"])
_register_parser.add_argument("email", type=str, required=True, help="Email is required", location=["values", "json"])
_register_parser.add_argument("model", type=str, required=True, help="Model is required", location=["values", "json"])
_register_parser.add_argument("platform", type=str, required=True, help="Platform is required", location=["values", "json"])
_register_parser.add_argument("version", type=str, required=True, help="Version is required", location=["values", "json"])
_register_parser.add_argument("deviceId", type=str, required=True, help="DeviceId is required", location=["values", "json"])

_confirm_parser = reqparse.RequestParser()
_confirm_parser.add_argument("code", type=str, required=True, help="code is required", location="args")
_confirm_parser.add_argument("f", type=str, default="", required=False, store_missing=True, help="format of the output: json | html", location="args")

#TODO: log email confirmation offline
_email_parameters = app.config.get("MAIL", None)
_confirmation_code_separator = ":"
_confirmation_delta_minutes = 10 

# ----------------PUBLIC SERVICE METHODS----------------
@app.route("/services/registration/register", methods=["POST"])
def register():
    """
    Registration handler
    """
    try:
        args = _register_parser.parse_args(request)
        
        # create a device to add to the account
        device = wnmodels.Device.create(args.deviceId, args.model, args.platform, args.version)

        #email is the account id
        id = email = args["email"]
        account = wndb.get_account(id)
        
        if not account:
            message = "Registration accepted; Account pending verification"

            account = wnmodels.Account.create(id, email, args["name"])
            account.devices.append(device)
            
            # check auto accept
            if _auto_accept_registration(account):
                account.status = wnmodels.AccountStatus.accepted
                message = "Account accepted via auto-registration"
            
            # save the new account
            wndb.save_account(account)
        
        elif not account.has_device(device):
            message = "Account exists, device added"

            account.devices.append(device)
            
            # save the new account
            wndb.save_account(account)

        else:
            message = "Account and device exist"
            
        account_state = wnmodels.AccountState.create(account, message)
        response = make_response(account_state.to_json(), 200)

        # send account verification 
        if account.status == wnmodels.AccountStatus.pending:
            _generate_registration_confirmation(account)

    except exceptions.HTTPException as hex:      
         response = make_response(json.dumps(hex.data), hex.code)
    except Exception as ex:
        #TODO: log
        #TODO: hide real message with generic?
        response = make_response("{{'message':'{}'}}".format(str(ex)), 500)
    
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/services/registration/confirm", methods=["GET"])
def confirm():
    """
    Registrtaion confirmation handler
    """
    args = None
    result = wnutil.Namespace()
    try:
        # get the request data
        args = _confirm_parser.parse_args(request)
        
        #----------------------------------------
        #ERROR HANDLER TESTING
        #raise Exception("Testing error handler")
        #----------------------------------------

        # validate the confirmation code
        valid, message, account = _validate_registration_confirmation(args.code)

        # handle the validation result
        if account and valid:

            # update account to accepted and return response
            account.status = wnmodels.AccountStatus .accepted
            success = wndb.save_account(account)
            if success: 
                result.code = 200
                result.data = wnmodels.AccountState.create(account, message="Account enabled")
                
            else:
                result.code = 500
                result.data = {"message": "unable to update account"}
        
        elif account and not valid:
            result.data = wnmodels.AccountState.create(account, message="Confirmation code is expired")
            result.code = 403 
            
            # send a new code
            try:
                _generate_registration_confirmation(account)
                result.data.message+="; A new code as been generated and sent"
            except:
                result.data.message+="; Error generating or sending new code"

        else:
            result.code = 400
            result.data = {"message": message}
        
    except exceptions.HTTPException as hex:
        result.code = hex.code
        result.data = hex.data
        args = args or wnutil.Namespace(request.args.to_dict())
        args.f = args.get("f") or request.args.get("f", "html")
            
    except Exception as ex:
        #TODO: log
        #TODO: hide real message with generic?
        result.code = 500
        result.data = {"message": str(ex)}
    
    # create the expected response format - content-type rules over f argument
    if ("application/json" in [x.strip() for x in request.headers.get("ContentType", "").split(";")]) or args.f == "json":
        try:
            json_string = result.data.to_json()
        except:
            json_string = json.dumps(result.data)
        response = make_response(json_string, result.code)
        response.headers["Content-Type"] = "application/json"
    else:
        response = render_template("confirm.html", result=result)
    
    return response

# ----------------PRIVATE SUPPORT METHODS----------------
def _auto_accept_registration(account):
    """
    Determines if an account's registration can be automatically accepted or must be confirmed.

    Returns boolean: True/False
    """
    settings = app.config.get("AUTO_REGISTER", {"mode": "NONE"})
    mode = settings.get("mode", "NONE").upper()
    
    if mode == "ALL":

        return True

    elif mode == "EMAILS":
        
        return wnutil.is_whitelisted(account.email, settings)

    else:
    
        return False

def _generate_registration_confirmation(account):
    """
    Generates a registerion code and sends email.
    """

    # create the code parts
    encoded_id = wnutil.encode(app.secret_key, account.id).decode()
    account_hash = account.generate_code()
    time_stamp = str(int(time.time()))

    # create the code and url
    code = _confirmation_code_separator.join([encoded_id, account_hash, time_stamp])
    url = url_for("confirm", _external=True, code=code, f="html")

    # send the email
    subject = "WindNinja Mobile - account verification"
    body = "Welcome to WindNinja Mobile! Please click the link below to complete your registration.\n\n\n{0}\n\n\nThis code is valid for {1} minutes.".format(url, _confirmation_delta_minutes)
    wnutil.send_email(_email_parameters.get("server", {}), account.email, _email_parameters.get("from_address", ""), subject, body)

def _validate_registration_confirmation(code):
    """
    Validates a registration code and returns the associated account.

    Returns a tuple: Valid, Message, Account
    """

    # parse the code into parts
    parts = code.split(_confirmation_code_separator)
    if len(parts) != 3:
        return False, "Invalid code", None
    try:
        id = wnutil.decode(app.secret_key, parts[0])
        hash = parts[1]
        time_stamp = int(parts[2])
    except:
        return False, "Code parsing failed", None

    # get the assocated account
    account = wndb.get_account(id)
    if not account: 
        return False, "Account not found", None

    # validate the account hash
    if not account.generate_code() == hash:
        return False, "Account mismatch", None

    # validate the time frame
    if (time_stamp+(_confirmation_delta_minutes*60) < time.time()):
        return False, "Code has expired", account
    
    # return success
    return True, "", account
