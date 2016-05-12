import datetime
import pytz

FILE = None

DEBUG_ENABLED = True
VERBOSE_ENABLED = True
INFO_ENABLED = True
ERROR_ENABLED = True

class LOG_LEVEL:
    DEBUG = "DEBUG"
    VERBOSE = "VERBOSE"
    INFO = "INFO"
    ERROR = "ERROR"

MESSAGE_TEMPLATE = "{} | {} | {}"

def log(msg, level):
    if level==LOG_LEVEL.DEBUG:
        return debug(msg)
    elif level==LOG_LEVEL.VERBOSE:
        return verbose(msg)
    elif level==LOG_LEVEL.INFO:
        return info(msg)
    elif level==LOG_LEVEL.ERROR:
        return error(msg)
    else:
        return None
   
def verbose(msg):
    if VERBOSE_ENABLED:
        return _write_formatted(LOG_LEVEL.VERBOSE, msg)
    else:
        return None
        
def debug(msg):
    if DEBUG_ENABLED:
        return _write_formatted(LOG_LEVEL.DEBUG, msg)
    else:
        return None
        
def error(e):
    if ERROR_ENABLED:
        return _write_formatted(LOG_LEVEL.ERROR, e)
    else:
        return None

def info(msg):
    if INFO_ENABLED:
        return _write_formatted(LOG_LEVEL.INFO, msg)
    else:
        return None

def _format_message(message, type):
    date_time_stamp = datetime.datetime.now(pytz.timezone('US/Mountain')).isoformat()
    formatted_message = MESSAGE_TEMPLATE.format(date_time_stamp, type.ljust(7), message)
    return formatted_message

def _write_formatted(t, m):
    formatted_message = _format_message(m, t)
    _write(formatted_message)
    return formatted_message
    
def _write(m):
    print(m)
    try:
        if FILE is not None:
            with open(FILE, "a") as log_file:
                log_file.write(m)
                log_file.write("\n")
    except: pass