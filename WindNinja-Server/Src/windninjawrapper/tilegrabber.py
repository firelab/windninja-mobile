import math
import urllib2
import os
import zipfile
from config import CONFIG
import logger

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile, zoom)

def tiles4BBox(domain, levels):
	tiles = {}
	logger.debug("DOMAIN: " + str(domain))
	logger.debug("LEVELS: " + str(levels))
	for level in levels:
		tileset = []
		logger.debug("LEVEL : " + str(level))
		#NOTE: using TOP-LEVEL as orign (GOOGLE/OSM/ETC) switch to BOTTOM-LEFT if
		#using strict TMS
		#tile_min = deg2num(domain["ymax"],domain["xmin"], level)
		#tile_max = deg2num(domain["ymin"],domain["xmax"], level)
		tile_min = deg2num(domain[3],domain[0], level)
		tile_max = deg2num(domain[1],domain[2], level)
		logger.debug("TILE MIN: " + str(tile_min) + ", TILE MAX: " + str(tile_max))
		for x in range(tile_min[0], tile_max[0] + 1):
			for y in range(tile_min[1], tile_max[1] + 1):
				logger.debug("X, Y: " + str(x) + ", " + str(y))
				tile = (x, y, level)
				tileset.append(tile)
		tiles[str(level)] = tileset
	return tiles

def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            f = os.path.join(root,file).replace(path,"")
            logger.debug("FILE: " + str(f))
            zip.write(os.path.join(root,file),arcname=f)
            
def grab_tiles(domain,output_dir,map_type):
	base_folder = os.path.join(output_dir,map_type)
	logger.debug(base_folder)
	url_template = CONFIG.TILE_GRAB_URL_TEMPLATES[map_type]
	
	#TODO 
	file_template = CONFIG.TILE_GRAB_FILE_TEMPLATE 
	min_level = CONFIG.TILE_GRAB_MIN_LEVEL
	max_level = CONFIG.TILE_GRAB_MAX_LEVEL
	zip_file_name = os.path.join(output_dir,"{0}.zip".format(map_type))
	logger.debug(zip_file_name)

	tiles = tiles4BBox(domain, range(min_level, max_level))
	logger.debug(str(tiles) + " " + str(len(tiles)))

	for level in tiles.keys():
		logger.debug(level)
		tileset = tiles[level]
		logger.debug(tileset)

		for tile in tileset:
			url = url_template.format(tile[2], tile[0], tile[1])		
			logger.debug(url)
			folder = os.path.join(base_folder, str(tile[2]), str(tile[0]))
			logger.debug(folder)
			file_name = file_template.format(tile[1])
			file = os.path.join(base_folder, str(tile[2]), str(tile[0]), file_name)
			logger.debug(folder)

			try:
				response = urllib2.urlopen(url)

				if not os.path.exists(folder):
					os.makedirs(folder)

				with open(file, "wb") as f:
					f.write(response.read())

			except urllib2.URLError, e:
				logger.error("failed to fetch: {0}".format(url))
				continue
	
	#zip folder
	logger.info("ZIP INFO: " + str(zip_file_name) + ", " + str(base_folder))
	zipf = zipfile.ZipFile(zip_file_name, 'w')
	zipdir(base_folder, zipf)
	zipf.close()

	return os.path.basename(zip_file_name)