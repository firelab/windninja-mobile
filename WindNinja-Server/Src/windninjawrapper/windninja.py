import argparse
import datetime
import os
from string import Template

import logger
from config import CONFIG
from queue import dequeue
from model import Project
from utility import executeShellProcess
from gis import createDem, convertShpToJson
#from tilegrabber import grab_tiles
#from rastertilemaker import make_tiles_for_output
import convolve
import re
import pytz


VERSION = "2016.05.10.1"

def executeWNCLI(project): 

    #TODO: split parameters into dictionary during open job + serialize correctly in write job
    #TODO: validate parameters and values
    
    # defaults
    cli = CONFIG.WN_CLI_DEFAULTS.copy()
    
    # overrides
    overide_args = project.parameters.split(";")
    for a in overide_args:
        parts = a.split(":")
        cli[parts[0]] = parts[1]

    # mandatory
    cli["initialization_method"] = "domainAverageInitialization" if (project.forecast == "NONE") else "wxModelInitialization"
    cli["elevation_file"] = project.demPath
    cli["wx_model_type"] = project.forecast

    #if vector or raster (is true)
    if project.products.get("vector",False) or project.products.get("raster",False):
        cli["write_shapefile_output"] = "true"
    else:
        cli["write_shapefile_output"] = "false"

    # if vector or raster or clustered is true
    if project.products.get("weather",False):
        cli["write_wx_model_shapefile_output"] = "true"
    else:
        cli["write_wx_model_shapefile_output"] = "false"

    # if clustered is true
    if project.products.get("clustered",False):
        cli["write_ascii_output"] = "true"
    else:
        cli["write_ascii_output"] = "false"

    # create the correct command line template
    if project.forecast == "NONE":
        cli_template = Template("{0} {1}".format(CONFIG.WN_CLI_PATH, CONFIG.WN_CLI_ARGS_DA))
    else:
        cli_template = Template("{0} {1}".format(CONFIG.WN_CLI_PATH, CONFIG.WN_CLI_ARGS_WX))

    # execute the command
    command = cli_template.substitute(cli)
    shell_result = executeShellProcess(command, project.path)

    # parse the timezone from the shell logs
    try:
        re_pattern = "Run \d*: Simulation time is \d*-[A-Za-z]*-\d* \d*:\d*:\d* [A-Z]{3}"
        line = re.search(re_pattern,shell_result[1]).group()
        timezone = line[-3:]
    except:
        # If we fail to parse a timezone abbreviation 
        # use this default value instead
        # (this value is currently mapped to MDT)
        timezone = "NA"

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
        windninja_asciifiles = [f for f in os.listdir(time_folder) if f.endswith(".asc")]
       
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
        if (len(windninja_shapefiles) == 0 and len(windninja_asciifiles) == 0) or len(weather_shapefiles)==0:
            result = (False, "WindNinjaCLI did not produce outputs for the job parameters")
        else:
            result = (True, time_folder, windninja_shapefiles, weather_shapefiles, timezone)   

    else:
        # pass error result back
        result = shell_result

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
    #parser.add_argument("-w", "--warn", action='store_true', help="Print processing statements")
    args = parser.parse_args()
    logger.debug(str(args))
    
    # set runtime configuration
    logger.VERBOSE_ENABLED = args.verbose
    logger.DEBUG_ENABLED = args.debug
    logger.INFO_ENABLED = args.info
    #logger.ERROR_ENABLED = args.error
    #logger.WARNING_ENABLED = args.warn

    project = None
    status = "failed"
    msg = None

    try: 

        id = args.id.replace("-", "")

        project_path = os.path.join(CONFIG.JOBS_DIRECTORY, id)
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

                    #json weather
                    if project.products.get("weather",False):
                        converted_weather = convertShpToJson((result[1], result[3]), project.path)
                        if converted_weather[0]:
                            project.updateJob(None, ("Weather converted to geojson", logger.LOG_LEVEL.INFO), True)
                            #TODO create zip package
                            
                            project.output["weather_vectores_json"] = {
                                "name": "Weather Json Vectors",
                                "type": "vector",
                                "format": "json",
                                "package": "",
                                "files": converted_weather[1]
                            }
                            
                        else:
                            if not converted_weather[0]:
                                project.updateJob(None, (converted_weather[1], logger.LOG_LEVEL.ERROR), True)


                    # json vectors
                    if project.products.get("vector",False):
                        converted_windninja = convertShpToJson((result[1], result[2]), project.path)
                        if converted_windninja[0]:
                            project.updateJob(None, ("Output converted to geojson", logger.LOG_LEVEL.INFO), True)
                            #TODO create zip package
                            
                            project.output["windninja_vectors_json"] = {
                                "name": "WindNinja Json Vectors",
                                "type": "vector",
                                "format": "json",
                                "package": "",
                                "files": converted_windninja[1]
                            }
                            
                        else:
                            if not converted_windninja[0]:
                                project.updateJob(None, (converted_windninja[1], logger.LOG_LEVEL.ERROR), True)
                    
                    # topofire tiles
                    #TODO: this one could be kicked off in a parrallel process as it doesn't rely on the WN output
                    if project.products.has_key("topofire") and project.products["topofire"]:
                        topofire_zip_file = grab_tiles(project.bbox, project.path, "topofire")
                        
                        if topofire_zip_file:
                            project.updateJob(None, ("TopoFire tiles compiled", logger.LOG_LEVEL.INFO), True)
                        
                            project.output["topofire_basemap_tiles"] = {
                                "name": "TopoFire Basemap",
                                "type": "basemap",
                                "format": "tiles",
                                "package": topofire_zip_file,
                                "files": []
                            }
                        else:
                            project.updateJob(None, ("TopoFire tiles unavailable", logger.LOG_LEVEL.WARNING), True)

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

                    if project.products.has_key("clustered") and project.products["clustered"]:
                        folder_name = "{0}-{1}".format(project.forecast, os.path.basename(project.demPath))
                        output_folder = os.path.join(project.path, folder_name)
                        time_folder = os.listdir(output_folder)[0]
                        time_folder = os.path.join(output_folder, time_folder)
                        file_name,vel_range = convolve.createClusters(time_folder,write_path=project.path,name="clustered",timezone=result[4],separate=False)

                        project.output["clustered"] = {
                            "name": "WindNinja Cluster Vectors",
                            "type": "cluster",
                            "format": "csv",
                            "baseUrl": "",
                            "package": "",
                            "files": file_name,
                            "data":  vel_range # rounded to 2 decimal places                            
                        }


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
        
    try:
        dequeue(args.id)
        logger.info("Job dueued")
    except Exception as ex:
        logger.error("job dequeue failed:\t{}".format(str(ex))) 
    
if __name__ == "__main__":
    logger.debug("windninja run as main") #NOTE: THIS DEBUG STATEMENT WILL NEVER GET INTO THE LOG FILE BUT WILL OUTPUT TO STDOUT
    main() 
