JOBS_DIRECTORY = r"../../Data/job"
JOB_FILENAME = "job.json"
IN_DEM_PATH = r"../../Data/dem/windninja_dem.vrt" #if relative, relative to windninja.py 
OUT_DEM_FILENAME = "dem.tif"
QUEUE_DIRECTORY = r"../../Data/queue"

MAIL = {
    "fromAddr":"test@gmail.com",
    "server":"smtp.gmail.com:587",
    "user":"test@gmail.com",
    "pass": "password"
}

DEM_MIN_BOUNDING_GEOM_WKB = 'AQYAAAACAAAAAQMAAAABAAAALAAAAAzP03/zcVTAsEVGP3iLOEAQkrZ/e21UwDBEGcGKjThAuGkl4OlrVMCwAUvfbo44QCA5QkCZVlTAINIJobqgOEAobkXATUZUwBCSOd9lrzhA4CpDgC9FVMCARMLgg7A4QPAuYiAKM1TA4Ghd32nOOEBsZLf/GS9UwNDOvIAF2DhAtNokoK4tVMCwd9iggNs4QDjZ6N85KlTAkCOy4GvkOECgx/ZfOCRUwCCG874c9DhADFMaoGscVMBwh9qA9gw5QHTBy79QGFTAAKYYIOEeOUA8RzjgrRdUwIBaRx/nITlA3LC/H1O9UMCY6DLge2dGQMSaXKAbvVDAcAiCAB9oRkAwUNy/M79QwHA5az+fc0ZA6Fbpn1byUMDom9/feIhHQGi1U8Ac/VDAkIR8oOKYR0AoihFg2QBRwMhh+p/HnUdA4LQCIJAKUcAIhDDgS6pHQIjZJyAmD1HAEN5g4LutR0CEDFGgdRJRwHh957+rrkdApIH/vz9LUcB4nN4fMbpHQPgu4h9wTlHA8CYOALW6R0D0ALD/SMpXwFBauP+1sUhAIA1AgMfKV8BIPpgAvrFIQEBnMCDhxV7AQFuGgCeASEDsTk4A2S1fwHD6mQCzMUhAdHhJYJMuX8A4zfo/zDBIQMDU8Z/tLl/AcDFIf9QUSEDcy1HA7SNfwLj1zx9Ca0VAHAW0n/IZX8AARPQ/qThEQJyzHKA0F1/AYBTwnwIiRECQMb4fExdfwJhXu2BpIURAXHQR4E3uXsBYyO2/WnVDQKTvEoDYHF7AGDuun2IEQUCsG7LfDuRdwDhw75+Mn0BAIAnSP5TiXcDQxGYftp1AQCiH598Tm13AeOrpv45mQECw9N3/Io1YwGBXZAC+DTpAHCC4nwxbWMDgiuzfE9Y5QDTvxz91gFTAkKODHvqGOEAMz9N/83FUwLBFRj94izhAAQMAAAABAAAAHQAAACiuB8DRVWDAcCO7YKdbS0D83ay/z1RgwEh2AsAUXEtAIJXq34lUYMDQo1YfNVxLQA6nIcDIS2DA4P5jQFRzS0BclQRgeklgwIDT9t+2ektAqIYTgFZIYMDoggmheH9LQFD28h+7P2DACDi1PpajS0BgEO//rD9gwDivy/9jpEtASlENoEJAYMBI+a+fGPVLQA4wBmBXQGDAWGIpAAAATEBAwQWgXkFgwODQ9l8xB0xAMKgHQMCfYcBITr3fQ2lRQJRm3p8U2GHAJF+5Hy6DUUBSjAngyedhwFhAe+AAilFAOXvq3+eOY8C8egqg/9hRQDvk8N9ej2PACHiYfwDZUUAt9vJ/5vFjwKi6C8BmtFFAmrwWIFY8ZMCc2bu/PpVRQL/Hy1+KQmTA7Lbi38mRUUCgnByAw0dkwJCkFiDCjlFAD0rn39jGZMAgjh4gcDhRQFFA+B9Ux2TAgKvMfxk4UUCUKvhf1NpkwPiakD/YFVFAevvS/+x3ZcBA3qTgZORPQPrd1Z/JYWbAMCKI/xXLSUABAAAghWRmwEAp5p/aoklA4j8kYFhkZsCwmqiAsJ1JQJ/lBmD6Y2bAEHyfgK2bSUAorgfA0VVgwHAju2CnW0tA'

WN_CLI_DEFAULTS = {
        "num_threads": "2",
        "forecast_duration": "3",
        "vegetation": "grass",
        "time_zone": "auto-detect",
        "output_wind_height": "20.0",
        "units_output_wind_height": "ft",
        "output_speed_units": "mph",  
        "mesh_choice": "fine",
        "input_speed": "5",
        "input_speed_units": "mph",
        "input_wind_height": "20",
        "units_input_wind_height": "ft"
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

class MESSAGES:
    BBOX_OUTSIDE_DEM="Job domain is outside the supported DEM bounds"