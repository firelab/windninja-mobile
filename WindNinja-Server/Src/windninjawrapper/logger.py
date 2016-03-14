import datetime

FILE = None

DEBUG = True
VERBOSE = True
INFO = True
ERROR = True


def verbose(msg):
	if VERBOSE:
		print msg
		write("VERBOSE", msg)
	
def debug(msg):
	if DEBUG:
		print msg
		write("DEBUG", msg)

def error(e):
	print e
	write("ERROR", e)
	
def info(msg):
	print msg
	write("INFO", msg)

def write(t, m):
    try:
        if FILE is not None:
            date_time_stamp = datetime.datetime.now().isoformat()
            formatted_message = "{0} | {1} | {2}\n".format(date_time_stamp,	t, m)
            with open(FILE, "a") as log_file:
                log_file.write(formatted_message)
    except: pass