JOBS_DIRECTORY = r"../../Data/job"
JOB_FILENAME = "job.json"
DEM_PATH = r"../../Data/dem/windninja_dem.vrt"
DEM_FILENAME = "dem.tif"
QUEUE_DIRECTORY = r"../../Data/queue"

MAIL = {
    "fromAddr":"test@gmail.com",
    "server":"smtp.gmail.com:587",
    "user":"test@gmail.com",
    "pass": "password"
}

WN_CLI_PATH = r"/usr/local/bin/WindNinja_cli"
WN_CLI_ARGS_DA = (
									"--elevation_file $elevation_file "
									"--mesh_choice $mesh_choice "
									"--num_threads $num_threads "
									"--vegetation $vegetation "
									"--time_zone $time_zone "
									"--initialization_method $initialization_method "
									"--input_speed $input_speed "
									"--input_speed_unit $input_wind_height "
									"--input_wind_height $input_wind_height "
									"--units_input_wind_height $units_input_wind_height  "
									"--output_speed_units $output_speed_units "
									"--output_wind_height $output_wind_height "
									"--units_output_wind_height $units_output_wind_height "
									"--write_shapefile_output $write_shapefile_output "
									"--write_wx_model_shapefile_output $write_wx_model_shapefile_output "
									"--write_goog_output false"
									)

WN_CLI_ARGS_WX = (
									"--elevation_file $elevation_file "
									"--mesh_choice $mesh_choice "
									"--num_threads $num_threads "
									"--vegetation $vegetation "
									"--time_zone $time_zone "
									"--initialization_method $initialization_method "
									"--wx_model_type $wx_model_type "
									"--forecast_duration $forecast_duration "
									"--output_speed_units $output_speed_units "
									"--output_wind_height $output_wind_height "
									"--units_output_wind_height $units_output_wind_height "
									"--write_shapefile_output $write_shapefile_output "
									"--write_wx_model_shapefile_output $write_wx_model_shapefile_output "
									"--write_goog_output false"
									)
TILE_GRAB_URL_TEMPLATES = {
		"topofire": "http://topofire.dbs.umt.edu/topomap/relief/{0}/{1}/{2}.jpg"
	}
TILE_GRAB_FILE_TEMPLATE = "{0}.jpg"
TILE_GRAB_MIN_LEVEL = 1
TILE_GRAB_MAX_LEVEL = 15
TILE_RASTER_FILE_NAME = "tiles"
TILE_RASTER_ZIP_NAME = "tiles.zip"
