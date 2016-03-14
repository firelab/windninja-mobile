import sys
import os
import logging

#TODO: update
#logging.basicConfig(stream=sys.stderr)

# initialize the flask application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "..", ".."))
print(sys.path)
#sys.path.insert(0,"/srv/WindNinjaServer/App/")


# handle wsgi startup
#NOTE: this is necessary to get the Apache config SetEnv values
# but might be able to use instance folder? http://flask.pocoo.org/docs/0.10/config/#instance-folders
def application(environ, start_response):
    os.environ['WNSERVER_CONFIG'] = environ['WNSERVER_CONFIG']
    
    from windninjaweb.app import app as _application
    return _application(environ, start_response)