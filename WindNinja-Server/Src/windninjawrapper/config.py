import os
import yaml

#print("job wrapper config initalization...")
#print(os.path.dirname(os.path.abspath(__file__)))

class CONFIG:
    JOBS_DIRECTORY = ""
    JOB_FILENAME = ""
    IN_DEM_PATH = "" 
    OUT_DEM_FILENAME = ""
    QUEUE_DIRECTORY = ""
    MAIL = {}
    DEM_MIN_BOUNDING_GEOM_WKB = ""
    WN_CLI_DEFAULTS = {}
    WN_CLI_PATH = ""
    WN_CLI_ARGS_DA = ""
    WN_CLI_ARGS_WX = ""
    TILE_GRAB_URL_TEMPLATES = {}
    TILE_GRAB_FILE_TEMPLATE = ""
    TILE_GRAB_MIN_LEVEL = -1
    TILE_GRAB_MAX_LEVEL = -1
    TILE_RASTER_FILE_NAME = ""
    TILE_RASTER_ZIP_NAME = ""
    TILE_RASTER_MAX_THREADS = 1
    TILE_RASTER_MIN_LEVEL = -1
    TILE_RASTER_MAX_LEVEL = -1

class MESSAGES:
    BBOX_OUTSIDE_DEM=""
    
try:
    __config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "windninjawrapper.config.yaml")  #os.environ["WNSERVER_CONFIG"]
    print(__config_file)
    with open(__config_file, "r") as f:
        overrides = yaml.safe_load(f)
    
    CONFIG.JOBS_DIRECTORY = os.path.abspath(overrides["job_wrapper"]["job_datastore"])
    CONFIG.JOB_FILENAME = overrides["job_wrapper"]["job_filename"]
    CONFIG.IN_DEM_PATH = overrides["job_wrapper"]["in_dem_path"]
    CONFIG.OUT_DEM_FILENAME = overrides["job_wrapper"]["out_dem_filename"]
    CONFIG.QUEUE_DIRECTORY = os.path.abspath(overrides["job_wrapper"]["queue_datastore"])
    CONFIG.MAIL = overrides["mail"]
    CONFIG.DEM_MIN_BOUNDING_GEOM_WKB = overrides["job_wrapper"]["dem_min_bounding_geom_wkb"]
    CONFIG.WN_CLI_DEFAULTS = overrides["job_wrapper"]["wn_cli"]["defaults"]
    CONFIG.WN_CLI_PATH = overrides["job_wrapper"]["wn_cli"]["path"]
    CONFIG.WN_CLI_ARGS_DA = " ".join(overrides["job_wrapper"]["wn_cli"]["args_da"])
    CONFIG.WN_CLI_ARGS_WX = " ".join(overrides["job_wrapper"]["wn_cli"]["args_wx"])
    CONFIG.TILE_GRAB_URL_TEMPLATES = overrides["job_wrapper"]["tile_grabber"]["urls"]
    CONFIG.TILE_GRAB_FILE_TEMPLATE = overrides["job_wrapper"]["tile_grabber"]["file_template"]
    CONFIG.TILE_GRAB_MIN_LEVEL = overrides["job_wrapper"]["tile_grabber"]["min_level"]
    CONFIG.TILE_GRAB_MAX_LEVEL = overrides["job_wrapper"]["tile_grabber"]["max_level"]
    CONFIG.TILE_RASTER_FILE_NAME = overrides["job_wrapper"]["tile_maker"]["file_name"]
    CONFIG.TILE_RASTER_ZIP_NAME = overrides["job_wrapper"]["tile_maker"]["zip_name"]
    CONFIG.TILE_RASTER_MAX_THREADS = overrides["job_wrapper"]["tile_maker"]["max_threads"]
    CONFIG.TILE_RASTER_MIN_LEVEL = overrides["job_wrapper"]["tile_maker"]["min_level"]
    CONFIG.TILE_RASTER_MAX_LEVEL = overrides["job_wrapper"]["tile_maker"]["max_level"]
    
    
    MESSAGES.BBOX_OUTSIDE_DEM = overrides["job_wrapper"]["messages"]["bbox_outside_dem"]
    
except Exception as ex:
    print("config loading failed: {}".format(str(ex)))


#print("job wrapper config initalized!")
#print(CONFIG.JOBS_DIRECTORY)