# WindNinja Mobile Server Side System

The server side system consists of:
 - a web API based on Flask (Python 3) via Apache & MOD_WSGI
 - a queue manager (Python 3) managed by Supervisor
 - a data store of json files
 - a WindNinja CLI wrapper script (Python 2) with GDAL/OGR and Mapnik utilities

### Version 
2016.05.13

### Installation

Global installs
```s
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-pip
sudo apt-get install python3-pip
sudo apt-get install python-dev
```

#### APACHE
```s
sudo apt-get install apache2
```

#### MOD_WSGI
15.x:
```s
sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmod wsgi
```

14.x (default mod-wsgi package is v3.4 but has thread error, get latest version from pip)

Disable the existing wsgi module if enabled (wsgi.conf and wsgi.load files are listed in the mods-enabled directry):
```s
ls /etc/apache2/mods-enabled
sudo a2dismod wsgi
```
Install updated version
```s
sudo apt-get install apache2-dev
sudo pip3 install mod_wsgi
sudo mod_wsgi-express install-module
```
The last command will install the .so file AND output the text content for .load (first line) and .conf (second line).  These files are NOT yet created.  Create them and add the text from the output.
```s
sudo nano /etc/apache2/mods-available/wsgi_express.load
	LoadModule ….
sudo nano /etc/apache2/mods-available/wsgi_express.conf
	WSGIPythonHome ….

sudo a2enmod wsgi_express
sudo service apache2 restart
```

#### SUPERVISOR
NOTE: supervisor is Python 2.x only

15.x:  TODO

14.x (apt-get doesn't install latest version, using pip and manual setup). The files listed below are pulled from the stock apt-get supervisor package. 
```s
sudo pip install supervisor
sudo mkdir /etc/supervisor
sudo mkdir /etc/supervisor/conf.d
sudo mkdir /etc/default/supervisor
sudo mkdir /var/log/supervisor
sudo cp supervisord.conf /etc/supervisor/supervisord.conf
sudo cp supervisor.default /etc/default/supervisor
sudo cp supervisor.init /etc/init.d/supervisor 
sudo chmod 755 /etc/init.d/supervisor
```

Start the supervisor service 
```s
sudo service supervisor start
```
Configur supervisor auto start on boot:
```s
sudo update-rc.d supervisor defaults
```


#### PYTHON MODULES
Python2:
```s
sudo pip install pytz
sudo pip install pyyaml
sudo pip install dateutil
sudo pip install enum34
sudo pip install numpy
```
Python3:
```s
sudo pip3 install flask
sudo pip3 install flask-restful
sudo pip3 install pyyaml
sudo pip3 install blinker
```
#### MAPNIK (python2 only?)
```s
sudo  apt-get python-mapnik
```

#### WindNinja Mobile Server
```s
git clone [git-repo-url]
```
Perform the following edits in the local repo before deploy

Config files:
- Copy and rename the two .config.yaml files (remove 'template' from name)
- Use absolute paths for safety
- SMTP configuratin values
- Performance values: job count, threads, etc
- Auto register settings
- remove comments

Digital Elevation Model files:  
- These files are two big to load to the GitHub repo.  
- Copy these files to the local repo Data/dem folder.  
- Edit the "min bounding geometry" setting in the config if not using AK and CONUS

Edit WindNinjaApp.conf 
- Edit server name and alias 
- Edit paths to wsgi app if necessary
- NOTE: this file is directly under git control but these edits do not need to be commited to GitHub (can use assume-nochange)
- TODO: create a 'template' for this file and commit that to GitHub

```s
sudo python3 Src/deploy.py all -d /srv/WindNinjaServer
sudo chmod 777 -R /srv/WindWindServer/Data
sudo mkdir /var/log/WindNinjaServer
sudo a2ensite WindNinjaApp
sudo service apache2 reload
sudo supervisorctl -c /etc/supervisor/supervisord.conf
>>>reload
>>>status
>>>quit
```

On the web server, AWS information and credentials are needed to access the SMTP server.
Add them as environment variables:
```
export AWS_SMTP_HOST=..
export AWS_SMTP_KEY=..
export AWS_SMTP_SECRET=...
```

#### WINDNINJA
Follow build steps: https://github.com/firelab/windninja/wiki/Building-WindNinja-on-Linux. Except 'Build GDAL' step needs to include python:

```s
sudo apt-get install build-essential python-all-dev
wget http://download.osgeo.org/gdal/1.11.1/gdal-1.11.1.tar.gz
tar xvfz gdal-1.11.1.tar.gz
cd gdal-1.11.1 && ./configure --with-python
make && sudo make install
sudo ldconfig
```

#### EMAIL
```s
sudo apt-get install sendmail
```

#### Helpful commands 
```s
apachectl -V  [apache version]
sudo a2enmod wsgi-express
sudo a2dismod wsgi-express

sudo a2ensite WindNinjaApp
sudo a2dissite WindNinjaApp

sudo truncate -s0 /var/log/apache2/error.log
sudo truncate -s0 /var/log/supervisor/supervisord.log
sudo truncate -s0 /var/log/WindNinjaServer/wnqueue.log

sudo supervisorctl -c /etc/supervisor/supervisord.conf
	supervisorctl> start wnqueue
	supervisorctl> stop wnqueue
	supervisorctl> reload wnqueue

sudo ./WindNinjaServer/Src/deploy.py [all, app, data, config, apache, supervisor] -d /srv/WindNinjaServer
```

#### Testing System
Verify queue manager & job wrapper
- Drop the job queue file into the queue stroe 
```s
cp Data/job/1a1111111111111111111111111111/1a1111111111111111111111111111.pending Data/queue
```
- If file extension should change to .running, if the manager picks it up.  It will change to .complete or .fail depending on the result 
- Check the job folder for artificats being created
- Check the wnqueue log file for manager issues 
    - /var/log/WindNinjaServer/wnqueue.log
- Truncate the queue log with:
```s
sudo truncate -s0 /var/log/WindNinjaServer/wnqueue.log 
```
- Review the job log file and job json
    - Data/job/1a1111111111111111111111111111/log.txt
    - Data/job/1a1111111111111111111111111111/job.json
- Clean up the job to run again
```s
Data/job/1a1111111111111111111111111111/clean-job.sh
rm Data/queue/1a1111111111111111111111111111.complete 
```

