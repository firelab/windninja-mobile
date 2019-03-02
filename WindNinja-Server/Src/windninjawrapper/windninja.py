import argparse
import logging
import datetime
import os

import logger
from config import CONFIG, MESSAGES
from model import Project, JobStatus
from gis import createDem, convertShpToJson, getLayerInfo, getRasterInfo, withinForecast
from wncli import execute_wncli
from queue import dequeue
from utility import zip_files

VERSION = "2019.02.21.1"

def main():
    logging.debug("windninja.main()")  #NOTE: THIS DEBUG STATEMENT WILL NEVER GET INTO THE LOG FILE BUT WILL OUTPUT TO STDOUT
    start = datetime.datetime.now()

    # argument parsing
    parser = argparse.ArgumentParser(description="WindNinja Server Wrapper")
    parser.add_argument("id", help="id of the windninja run")
    parser.add_argument("-l", "--log_level", choices=["debug", "info", "warn", "none"], default="none", help="Logging level")
    parser.add_argument("-p", "--pretty_print", action='store_true', help="Pretty print job file")

    #---------------------------------------------------------------------------------
    #IMPORTANT: if args are bad, process will exit without much in the way of logging 
    #   so when run from queue or web be sure to validate command line is correctly
    #   formatted...
    #TODO: create custome parser that logs command line errors to file
    #---------------------------------------------------------------------------------
    args = parser.parse_args()
    logging.debug(str(args))

    project = None
    status = JobStatus.failed
    msg = None

    try: 

        id = args.id.replace("-", "")
        project_path = os.path.join(CONFIG.JOBS_DIRECTORY, id)

        log_level = getattr(logging, args.log_level.upper(), 0)
        if log_level:
            logger.enable_file(project_path, log_level)

        #-----------------------------------------------------------------------
        #IMPORTANT:  FAILURES BEFORE THIS POINT WILL NOT BE LOGGED TO TEXT FILE
        #-----------------------------------------------------------------------

        logging.info("Begin - version {}".format(VERSION))
        logging.debug("project path: {}".format(project_path))

        project = Project(project_path)
        project.pretty_print = args.pretty_print
        project.openJob()
               
        if project is None or project.job is None or project.error is not None:
            logging.error("Exiting: Unable to open project file: {}".format(project.error))
            project = None
        elif project.job["status"] != JobStatus.new.name:
            logging.error("Exiting: Project is not NEW: status={}".format(project.job["status"]))
            project = None
        else:
            project.updateJob(JobStatus.executing.name, (logging.INFO, "Initializing WindNinja Run" ), True)

            # evaluate 'auto' forecast if necessary
            logging.debug("evaluate project forecast: {}".format(project.forecast))
            if project.forecast.lower() == "auto":
                evaluated_forecast = withinForecast(project.bbox)
                logging.debug("evaluated forecast for bbox: {}".format(evaluated_forecast))
                if evaluated_forecast:
                    project.forecast = evaluated_forecast
                    #TODO: should this new value be written back to job info
                    project.updateJob(None, (logging.INFO, "Auto Forecast Evaluated: {}".format(evaluated_forecast)), True)
                else:
                    #project.updateJob(None, (logging.ERROR, MESSAGES.BBOX_OUTSIDE_FORECASTS), True)
                    raise Exception(MESSAGES.BBOX_OUTSIDE_FORECASTS)


            # create the cli output folder
            wncli_folder = os.path.join(project_path, "wncli")
            os.makedirs(wncli_folder)
            
            result = createDem(project.bbox, wncli_folder)
            if result[0]:
                project.demPath = result[1]
                project.updateJob(None, (logging.INFO, "DEM created"), True)

                # execute the cli 
                override_args = {ptr.split(":")[0]: ptr.split(":")[1] for ptr in project.parameters.split(";")}
                #TODO: rethink "products" 
                output_shp = project.products.get("vector", False)
                output_asc = project.products.get("clustered", False)
                output_wx = project.products.get("weather", False)
                        
                result = execute_wncli(wncli_folder, override_args, project.demPath, project.forecast, output_shp, output_asc, output_wx)
                
                #result:
                # 0 : status [True | False]
                # 1 : output_folder | error message [string]
                # 2 : simulations [list of datetime]
                # 3 : windninja_shapefiles [list of string]
                # 4 : windninja_ascfiles [list of string]
                # 5 : weather_shapefiles [list of string]

                if result[0]:
                    project.updateJob(None, (logging.INFO, "WindNinjaCLI executed"), True)
                    results_folder = result[1]
                    
                    # add the simulation times/zone info
                    simulations = result[2]
                    simulations.sort()
                    
                    # initialize some variables used across products
                    wx_infos = wn_infos = None
                    wx_max_speed = wn_max_speed = 0

                    project.output = {
                        "simulations" : {
                            "times" : ["{:%Y%m%dT%H%M}".format(d) for d in simulations], 
                            "utcOffset" : "{:%z}".format(result[2][0])
                        }
                    }

                    # generate the desired output products

                    # weather results as geojson vectors
                    #TODO: even though the wx data is small (a few hundred points) if it was aggregated to 
                    #       a single file it might help with performance... and size could be reduced if
                    #       using a denormalized format - the geometry json is approx 1/2 the file size.
                    #       
                    if project.products.get("weather",False):
                        converted_weather = processShapefiles(results_folder, result[5], project.path, True, where="speed>0", zip_name="wx_geojson.zip")
                        if converted_weather[0]:
                            project.updateJob(None, (logging.INFO, "Weather converted to geojson"), True)
                            wx_infos = converted_weather[2]
                            wx_max_speed = converted_weather[3]
                            output = project.output["weather"] = {
                                "name": "Weather Json Vectors",
                                "type": "vector",
                                "format": "json",
                                "package": os.path.basename(converted_weather[4]),
                                "files": converted_weather[1],
                                "data": {
                                    "maxSpeed": {
                                       "overall": wx_max_speed
                                    }
                                }
                            }
                            for i in wx_infos:
                                name = i.replace("shp", "json")
                                output["data"]["maxSpeed"][name] = wx_infos[i]["max"]
                        else:
                            project.updateJob(None, (logging.ERROR, converted_weather[1]), True)

                    # windninja resutls as geojson vectors
                    if project.products.get("vector",False):
                        converted_windninja = processShapefiles(results_folder, result[3], project.path, True, zip_name="wn_geojson.zip")
                        if converted_windninja[0]:
                            project.updateJob(None, (logging.INFO, "Output converted to geojson"), True)
                            wn_infos = converted_windninja[2]
                            wn_max_speed = converted_windninja[3]
                            output = project.output["vector"] = {
                                "name": "WindNinja Json Vectors",
                                "type": "vector",
                                "format": "json",
                                "package": os.path.basename(converted_windninja[4]),
                                "files": converted_windninja[1],
                                "data": {
                                    "maxSpeed": {
                                        "overall": wn_max_speed
                                    }
                                }
                            }
                            for i in wn_infos:
                                name = i.replace("shp", "json")
                                output["data"]["maxSpeed"][name] = wn_infos[i]["max"]
                        else:
                            project.updateJob(None, (logging.ERROR, converted_windninja[1]), True)

                    # topofire tiles
                    #TODO: this one could be kicked off in a parrallel process as it doesn't rely on the WN output
                    #TODO: Tile fetch is surprisingly quick but could create a local cache that is auto built as requests come in.
                    if project.products.get("topofire", False):
                        from tilegrabber import grab_tiles
                        topofire_zip_file = grab_tiles(project.bbox, project.path, "topofire")
                        
                        if topofire_zip_file:
                            project.updateJob(None, (logging.INFO, "TopoFire tiles compiled"), True)

                            project.output["topofire"] = {
                                "name": "TopoFire Basemap",
                                "type": "basemap",
                                "format": "tiles",
                                "package": os.path.basename(topofire_zip_file),
                                "files": []
                            }
                        else:
                            project.updateJob(None, (logging.WARNING, "TopoFire tiles unavailable"), True)

                    # windninja results as tile packages
                    if project.products.get("raster", False):
                        from rastertilemaker import make_tiles_for_output
                        wn_shpfiles = result[3]

                        # calculate values if needed
                        if output_wx and not wx_infos:
                            wx_shpfiles = results[5]
                            converted = processShapefiles(results_folder, wx_shpfiles, project.path, False)
                            wx_max_speed = covnerted[3]

                        if not wn_infos:
                            converted = processShapefiles(results_folder,wn_shpfiles, project.path, False)
                            wn_infos = converted[2]
                            wn_max_speed = converted[3]

                        max_speed = wn_max_speed if (wn_max_speed > wx_max_speed) else wx_max_speed

                        #NOTE: weather points NOT drawn in tiles, but max speed maybe from weather ....
                        #TODO: should this return an error/status?
                        tile_zip = make_tiles_for_output(project.path, (results_folder, wn_shpfiles), (wn_infos, max_speed), project.forecast)
                        project.updateJob(None, (logging.INFO, "Output converted to raster tiles"), True)
                        
                        output = project.output["raster"] = {
                            "name": "WindNinja Raster Tiles",
                            "type": "raster",
                            "format": "tiles",
                            "package": tile_zip,
                            "files": [k.replace(".shp", "") for k in wn_infos.keys()],
                            "data": {
                                "maxSpeed": {
                                    "overall": max_speed
                                }
                            }
                        }

                        for i in wn_infos:
                            name = i.replace(".shp", "")
                            output["data"]["maxSpeed"][name] = wn_infos[i]["max"]

                    # windninja results as custom clustered format
                    if project.products.get("clustered", False):
                        from convolve import createClusters

                        # run calculation if not already done
                        if not wn_infos:
                            wn_infos = {}
                            for f in [a for a in result[4] if a.find("vel") > 0 ]:
                                wn_infos[f] = getRasterInfo(os.path.join(results_folder, f))
        
                            wn_max_speed = sorted(wn_infos.values(), key=lambda x: x["max"], reverse=True)[0]["max"]

                        #NOTE: assumes weather max will be covered if created
                        max_speed = wn_max_speed if (wn_max_speed > wx_max_speed) else wx_max_speed

                        #TODO: should this return a status/error
                        native_wkid = int(wn_infos.values()[0]["native_wkid"])
                        file_format = "json"
                        clustered_file, breakdown = createClusters(results_folder, project.path, "wn_clustered", native_wkid, separate=False, given_max_vel=max_speed, format=file_format)
                        project.updateJob(None, (logging.INFO, "Output converted to cluster"), True)

                        #TODO: zip file
                        zip_name="wn_clustered.zip"
                        zip_files(os.path.join(project.path, zip_name), [os.path.join(project.path, f) for f in clustered_file])

                        output = project.output["clustered"] = {
                            "name": "WindNinja Cluster Vectors",
                            "type": "cluster",
                            "format": file_format,
                            "baseUrl": "",
                            "package": zip_name,
                            "files": clustered_file,
                            "data":  {
                                "maxSpeed": {
                                    "overall": wn_max_speed
                                },
                                "speedBreaks": breakdown
                            }
                        }
                        for i in wn_infos:
                            name = i.replace("_vel.asc", "").replace(".shp", "")
                            output["data"]["maxSpeed"][name] = wn_infos[i]["max"]

                    # processing complete!
                    status = JobStatus.succeeded
                else:
                    project.updateJob(None, (logging.ERROR, result[1]), True)

            else:
                project.updateJob(None, (logging.ERROR, result[1]), True)

    except Exception as e:
        try: 
            msg = str(e).replace("\n", " ")
            if project is not None:
                project.updateJob(None, (logging.ERROR, msg), True)
            else:
                logging.error(msg)
        except: pass

    finish = datetime.datetime.now()
    delta = finish - start

    if project is not None:
        try:        
            msg = "Complete - total processing: {}".format(delta)
            project.updateJob(status.name, (logging.INFO, msg), True)
        except Exception as ex:
            logging.error("job update failed n failed:\t{}".format(str(ex)))

        try: project.sendEmail()
        except Exception as ex:
            logging.error("send notification failed:\t{}".format(str(ex)))

    #TODO: should this be a command line flag to skip or try
    try:
        dequeue(args.id)
        logging.info("Job dequeue")
    except Exception as ex:
        logging.error("job dequeue failed:\t{}".format(str(ex))) 

def processShapefiles(results_folder, shpfiles, project_path, convertToGeoJson, where=None, zip_name=""):
    zip_package = None
    geoJson = None

    if convertToGeoJson:
        converted = convertShpToJson((results_folder, shpfiles), project_path, where)
        if converted[0]:
            geoJson = converted[1]
            
            if zip_name:
                zip_package = os.path.join(project_path, zip_name)
                zip_files(zip_package, [os.path.join(project_path, f) for f in geoJson])

        else:
            # exit and return error
            return converted

    # determine the max speed
    infos = {}
    for f in shpfiles:
        infos[f] = getLayerInfo(os.path.join(results_folder, f), "speed")
        
    max_speed = sorted(infos.values(), key=lambda x: x["max"], reverse=True)[0]["max"]

    return (True, geoJson, infos, max_speed, zip_package)

if __name__ == "__main__":
    logging.debug("windninja run as main") #NOTE: THIS DEBUG STATEMENT WILL NEVER GET INTO THE LOG FILE BUT WILL OUTPUT TO STDOUT
    main() 
    
    #shpfiles = ['WX_20171020T1800.shp', 'WX_20171020T1900.shp', 'WX_20171020T2000.shp', 'WX_20171020T2100.shp', 'WX_20171020T1600.shp', 'WX_20171020T2200.shp', 'WX_20171020T1700.shp']
    #results_folder = r"T:\temp\wn_examples\filestore\job\1a111111111111111111111111111111\wncli\results"
    #f = shpfiles[0]
    #i = getLayerInfo(os.path.join(results_folder, f), "speed")
