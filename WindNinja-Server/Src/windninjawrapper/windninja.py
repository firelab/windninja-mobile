import argparse
import datetime
import pytz
import os
import json
import math
import subprocess
import smtplib
import base64
from string import Template
from email.mime.text import MIMEText

from osgeo import gdal, osr, ogr
import ogr2ogr
from tilegrabber import grab_tiles
from rastertilemaker import make_tiles_for_output

import config
import logger

VERSION = "2016.05.10.1"

class Project:
    def __init__(self, path):
        self.path = path
        self.jobFile = os.path.join(path, config.JOB_FILENAME)
        logger.verbose("job json path: {0}".format(self.jobFile))
        self.job = None
        self.demPath = None
        self.forecast = "UCAR-GFS-GLOBAL-0.5-DEG"
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
            msg['From'] = config.MAIL["fromAddr"]
            msg['To'] = self.job['email']

            s = smtplib.SMTP(config.MAIL["server"])
            s.ehlo()
            if config.MAIL["user"] and config.MAIL["pass"]:
                logger.verbose("server requires login")  
                s.starttls()
                s.ehlo()
                s.login(config.MAIL["user"], config.MAIL["pass"])
            logger.verbose("attempting to send notification text: {}".format(msg.as_string()))
            s.sendmail(config.MAIL["fromAddr"], self.job['email'].split(','), msg.as_string())
            s.close()

#--------------------------------------------
# 2.7 version of the queue functions 
import glob

_directories = {
    "queue" : config.QUEUE_DIRECTORY
    }

def dequeue(id):
    item = _find_item(id)
    if item is None:
        raise KeyError("Item with id {} not found in queue".format(id))

    #More complex keep file with 'status'
    update_queue_item_status(id, "complete")

def update_queue_item_status(id, status, data=None):
    if type(status) is not str:
        raise TypeError("Status is not of type <QueueStatus>")
    
    try:
        existing_file = _find_item(id)
        base = os.path.splitext(existing_file)[0]
        new_file = "{0}.{1}".format(base, status)
        os.rename(existing_file, new_file)
        
        if data:
            with open(new_file, "at") as f:
                f.write(data)
                f.write("\n")

    except AttributeError:
        raise KeyError("Item with id {} not found in queue".format(id))

    except OSError:
        raise Exception("Queue update error") 

    except Exception:
        raise Exception("Queue update error") 

def _find_item(id):
    name_pattern = "{}.*".format(id)
    file_pattern = os.path.join(_directories["queue"], name_pattern)
    try:
        return  glob.glob(file_pattern)[0]
    except IndexError as iex:
        return None
#--------------------------------------------

def withinDEM(bbox):

    #dem minimum bounding geometry
    wkb = base64.b64decode(config.DEM_MIN_BOUNDING_GEOM_WKB)
    dem_mbg = ogr.CreateGeometryFromWkb(wkb)
    
    #polygon from job bounding box 
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(bbox[0], bbox[1])
    ring.AddPoint(bbox[0], bbox[3])
    ring.AddPoint(bbox[2], bbox[3])
    ring.AddPoint(bbox[2], bbox[1])
    ring.AddPoint(bbox[0], bbox[1])
    polygon = ogr.Geometry(ogr.wkbPolygon)
    polygon.AddGeometry(ring)
    
    return polygon.Within(dem_mbg)

def utmZone(x, y):
    '''Return the EPSG code for a given latitude and longitude'''
    # Southern hemisphere
    if (y < 0):
        base = 32700
    # Northern hemisphere
    else:
        base = 32600
    # Get standard zone
    epsg = base + int(math.floor((x + 186) / 6))
    # 180 is in 60
    if (x == 180):
        epsg = base + 60
    # Take care of Norway
    elif y >= 56.0 and y < 64.0 and x >= 3.0 and x < 12.0:
        epsg = base + 32
    # Take care of Svalbard
    elif y >= 72.0 and y < 84.0:
        if x >= 0.0 and x < 9.0:
            epsg = base + 31
        elif x >= 9.0 and x < 21.0:
            epsg = base + 33
        elif (x >= 21.0 and x < 33.0):
            epsg = base + 35
        elif (x >= 33.0 and x < 42.0):
            epsg = base + 37
    return epsg

def createDem(bbox, project_path):
    '''Create a dem based on a bounding box'''
    
    if not withinDEM(bbox):
        return False, config.MESSAGES.BBOX_OUTSIDE_DEM
    
    center = [bbox[2] + ((bbox[0] - bbox[2]) / 2), bbox[3] + ((bbox[1] - bbox[3]) / 2)]
    logger.verbose("dem center: {0}".format(center))
    
    utm = utmZone(center[0], center[1])
    src_srs = osr.SpatialReference()
    dst_srs = osr.SpatialReference()
    src_srs.ImportFromEPSG(4326)
    dst_srs.ImportFromEPSG(utm)
    ct = osr.CoordinateTransformation(src_srs, dst_srs)
    logger.verbose("using utm zone: {0}".format(utm))

    window = [0,0,0,0]
    x = bbox[0]
    y = bbox[1]
    x, y, z = ct.TransformPoint(x, y)
    window[0] = x
    window[1] = y
    x = bbox[2]
    y = bbox[3]
    x, y, z = ct.TransformPoint(x, y)
    window[2] = x
    window[3] = y

    input_dem_path = os.path.abspath(config.IN_DEM_PATH)
    logger.verbose("input dem path: {}".format(input_dem_path))

    output_dem_path = os.path.join(project_path, config.OUT_DEM_FILENAME)
    output_dem_path = os.path.abspath(output_dem_path)
    logger.verbose("output dem path: {0}".format(output_dem_path))
        
    command = 'gdalwarp -tr 85 85 -t_srs epsg:%d -te %d %d %d %d %s %s -overwrite' % (utm, window[0], window[1], window[2], window[3], input_dem_path, output_dem_path)
    
    result = executeShellProcess(command, project_path)
    if result[0]:
        result = (True, output_dem_path)
    
    return result

def executeWNCLI(project): 

    #TODO: split parameters into dictionary during open job + serialize correctly in write job
    #TODO: validate parameters and values
    
    # defaults
    cli = config.WN_CLI_DEFAULTS.copy()
    
    # overrides
    overide_args = project.parameters.split(";")
    for a in overide_args:
        parts = a.split(":")
        cli[parts[0]] = parts[1]

    # mandatory
    cli["initialization_method"] = "domainAverageInitialization" if (project.forecast == "NONE") else "wxModelInitialization"
    cli["elevation_file"] = project.demPath
    cli["wx_model_type"] = project.forecast
    cli["write_shapefile_output"] = "true"
    cli["write_wx_model_shapefile_output"] = "true"
    
    # create the correct command line template
    if project.forecast == "NONE":
        cli_template = Template("{0} {1}".format(config.WN_CLI_PATH, config.WN_CLI_ARGS_DA))
    else:
        cli_template = Template("{0} {1}".format(config.WN_CLI_PATH, config.WN_CLI_ARGS_WX))

    # execute the command
    command = cli_template.substitute(cli)
    shell_result = executeShellProcess(command, project.path)

    # process results
    if (shell_result[0]):
        
        # construct the output folder path
        folder_name = "{0}-{1}".format(project.forecast, os.path.basename(project.demPath))
        output_folder = os.path.join(project.path, folder_name)
        logger.verbose("Output Folder: {0}".format(output_folder))
        time_folder = os.listdir(output_folder)[0]
        time_folder = os.path.join(output_folder, time_folder)
        logger.verbose("Time folder: {0}".format(time_folder))

        # collect the output shapefiles
        all_shapefiles = [f for f in os.listdir(time_folder) if f.endswith(".shp")]
       
        weather_shapefiles = []
        windninja_shapefiles = []
       
        #NOTE: WindNinja outputs file times in Time Zone of the extent.  
        #   for now, return all the results until we can determine the time zone for comparison 
        for shp in all_shapefiles:
            parts = os.path.splitext(shp)[0].split("_") 
            if shp.startswith(project.forecast):
                weather_shapefiles.append(shp)
            else:
                windninja_shapefiles.append(shp)
               
        # filter out any "past" results and forecasts
        #current_datetime = datetime.datetime.now()
        #current_datetime = datetime.datetime(current_datetime.year, current_datetime.month, current_datetime.day, current_datetime.hour)
        #for shp in all_shapefiles:
        #    parts = os.path.splitext(shp)[0].split("_") 
        #    if shp.startswith(project.forecast):
        #        parts_len = len(parts)
        #        hour = parts[parts_len - 1]
        #        date = parts[parts_len - 2][-10:]
        #        list = weather_shapefiles
        #    else:
        #        hour = parts[2]
        #        date = parts[1]
        #        list = windninja_shapefiles
        #   
        #    shapefile_datetime = datetime.datetime.strptime("{0}T{1}".format(date, hour), "%m-%d-%YT%H%M")
        #    if (shapefile_datetime >= current_datetime):
        #        list.append(shp)

        logger.verbose("WindNinja output files: {0}".format(windninja_shapefiles))
        logger.verbose("Weather output files: {0}".format(weather_shapefiles))
        if len(windninja_shapefiles) == 0 or len(weather_shapefiles)==0:
            result = (False, "WindNinjaCLI did not produce outputs for the job parameters")
        else:
            result = (True, time_folder, windninja_shapefiles, weather_shapefiles)    

    else:
        # pass error result back
        result = shell_result

    return result

def executeShellProcess(command, working_directory):
    logger.verbose("Shell command:{}".format(command))
    proc = subprocess.Popen(command, shell=True, cwd=working_directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate(None)
    logger.verbose("Shell process result: {0}\r\n{1}\r\n{2}".format(proc.returncode, out, err))
    if proc.returncode == 0:
        result = (True, out)
    else:
        result = (False, err)

    return result

def convertShpToJson(shapefiles, out_folder):
    result = (True, [])
    converted = result[1]
    try:
        for shp in shapefiles[1]:
            in_file = os.path.join(shapefiles[0], shp)
            out_file = os.path.join(out_folder, "{0}.{1}".format(os.path.splitext(shp)[0], "json"))
            logger.debug("Converting {0} to {1}".format(in_file, out_file))
            conversion = ogr2ogr.main(["", "-f", "geojson", "-t_srs", "epsg:3857", out_file, in_file])
            
            if not conversion:
                result = (False, "SHP to GEOJSON conversion failed: {0}".format(shp))
                break
            else:
                converted.append(os.path.split(out_file)[1])

    except Exception as e:
        msg = str(e).replace("\n", " ")
        result = (False, msg)

    return result

def main():
    logger.debug("windninja.main()")  #NOTE: THIS DEBUG STATEMENT WILL NEVER GET INTO THE LOG FILE BUT WILL OUTPUT TO STDOUT
    start = datetime.datetime.now()

    # argument parsing
    parser = argparse.ArgumentParser(description="WindNinja Server Wrapper")
    parser.add_argument("id", help="id of the windninja run")
    parser.add_argument("-v", "--verbose", action='store_true', help="Print processing statements")
    parser.add_argument("-d", "--debug", action='store_true', help="Print processing statements")
    parser.add_argument("-i", "--info", action='store_true', help="Print processing statements")
    #parser.add_argument("-e", "--error", action='store_true', help="Print processing statements")
    args = parser.parse_args()
    logger.debug(str(args))
    
    # set runtime configuration
    logger.VERBOSE_ENABLED = args.verbose
    logger.DEBUG_ENABLED = args.debug
    logger.INFO_ENABLED = args.info
    #logger.ERROR_ENABLED = args.error

    project = None
    status = "failed"
    msg = None

    try: 

        id = args.id.replace("-", "")

        project_path = os.path.join(config.JOBS_DIRECTORY, id)
        logger.FILE = os.path.join(project_path, "log.txt")
        logger.info("Begin - version {0}".format(VERSION))
        logger.verbose("project path: {0}".format(project_path))
                
        project = Project(project_path)
        project.openJob()
        if project.job["status"] != "new":
            logger.error("Exiting: Project is not NEW: status={0}".format(project.job["status"]))
            project = None
        else:
            project.updateJob("Executing", ("Initializing WindNinja Run", logger.LOG_LEVEL.INFO), True)
                
            result = createDem(project.bbox, project.path)
            if result[0]:
                project.demPath = result[1]
                
                project.updateJob(None, ("DEM created", logger.LOG_LEVEL.INFO), True)
            
                result = executeWNCLI(project)
                if result[0]:
                    project.updateJob(None, ("WindNinjaCLI executed", logger.LOG_LEVEL.INFO), True)            
                    
                    # generate the desired output products
                    project.output = {}

                    # json vectors
                    if project.products.has_key("vector") and project.products["vector"]:
                        converted_windninja = convertShpToJson((result[1], result[2]), project.path)
                        converted_weather = convertShpToJson((result[1], result[3]), project.path)
                        if converted_windninja[0] and converted_weather[0]:
                            project.updateJob(None, ("Output converted to geojson", logger.LOG_LEVEL.INFO), True)
                            #TODO create zip package
                            
                            project.output["windninja_vectors_json"] = {
                                "name": "WindNinja Json Vectors",
                                "type": "vector",
                                "format": "json",
                                "package": "",
                                "files": converted_windninja[1]
                            }

                            project.output["weather_vectores_json"] = {
                                "name": "Weather Json Vectors",
                                "type": "vector",
                                "format": "json",
                                "package": "",
                                "files": converted_weather[1]
                            }
                            
                        else:
                            if not converted_windninja[0]:
                                project.updateJob(None, (converted_windninja[1], logger.LOG_LEVEL.ERROR), True)
                            if not converted_weather[0]:
                                project.updateJob(None, (converted_weather[1], logger.LOG_LEVEL.ERROR), True)
                    
                    # topofire tiles
                    #TODO: this one could be kicked off in a parrallel process as it doesn't rely on the WN output
                    if project.products.has_key("topofire") and project.products["topofire"]:
                        topofire_zip_file = grab_tiles(project.bbox, project.path, "topofire")
                        project.updateJob(None, ("TopoFire tiles compiled", logger.LOG_LEVEL.INFO), True)
                        
                        project.output["topofire_basemap_tiles"] = {
                            "name": "TopoFire Basemap",
                            "type": "basemap",
                            "format": "tiles",
                            "package": topofire_zip_file,
                            "files": []
                        }

                    if project.products.has_key("raster") and project.products["raster"]:
                        tile_zip,layer_info = make_tiles_for_output(project.path, (result[1], result[2], result[3]), project.forecast)
                        project.updateJob(None, ("Output converted to raster tiles", logger.LOG_LEVEL.INFO), True)
                        
                        prd = project.output["windninja_raster_tiles"] = {
                            "name": "WindNinja Raster Tiles",
                            "type": "raster",
                            "format": "tiles",
                            "package": tile_zip,
                            "files": [],
                            "data": []
                        }

                        for layer in layer_info.keys():
                            info = layer_info[layer]
                            name = os.path.splitext(layer)[0]
                            prd["files"].append(name)
                            prd["data"].append("{0}:{1}".format(name, info["max_speed"]))

                    status = "succeeded"
                else:
                    project.updateJob(None, (result[1], logger.LOG_LEVEL.ERROR), True)

            else:
                project.updateJob(None, (result[1], logger.LOG_LEVEL.ERROR), True)

    except Exception as e:
        try: 
            msg = str(e).replace("\n", " ")
            if project is not None:
                project.updateJob(None, (msg, logger.LOG_LEVEL.ERROR), True)
            else:
                logger.error(msg)
        except: pass
             
    finish = datetime.datetime.now()
    delta = finish - start
    
    if project is not None:
        try:        
            msg = "Complete - total processing: {0}".format(delta)
            project.updateJob(status, (msg, logger.LOG_LEVEL.INFO), True)
        except Exception as ex:
            logger.error("job update failed n failed:\t{}".format(str(ex)))
    
        try: project.sendEmail()
        except Exception as ex:
            logger.error("send notification failed:\t{}".format(str(ex)))
    
    #if msg is not None:
    #    logger.info(msg)
    
    try:
        dequeue(args.id)
        logger.info("Job dueued")
    except Exception as ex:
        logger.error("job dequeue failed:\t{}".format(str(ex))) 
    
if __name__ == "__main__":
    logger.debug("windninja run as main") #NOTE: THIS DEBUG STATEMENT WILL NEVER GET INTO THE LOG FILE BUT WILL OUTPUT TO STDOUT
    main() 