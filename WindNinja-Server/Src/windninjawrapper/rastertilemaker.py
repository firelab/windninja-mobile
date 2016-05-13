#!/usr/bin/env python
import inspect
import json
from math import pi,cos,sin,tan,log,exp,atan,radians
from subprocess import call
import os
from Queue import Queue
import sys
import threading
import zipfile

from osgeo import ogr,osr
import mapnik

from config import CONFIG
import logger


DEG_TO_RAD = pi / 180
RAD_TO_DEG = 180 / pi
SUPERDIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory 
ONE = os.path.join(SUPERDIR,"assets", "1.png")
TWO = os.path.join(SUPERDIR,"assets","2.png")
THREE = os.path.join(SUPERDIR,"assets","3.png")
FOUR = os.path.join(SUPERDIR,"assets","4.png")
FIVE = os.path.join(SUPERDIR,"assets","5.png")
ONE_BIG = os.path.join(SUPERDIR,"assets","1_big.png")
TWO_BIG = os.path.join(SUPERDIR,"assets","2_big.png")
THREE_BIG = os.path.join(SUPERDIR,"assets","3_big.png")
FOUR_BIG = os.path.join(SUPERDIR,"assets","4_big.png")
FIVE_BIG = os.path.join(SUPERDIR,"assets","5_big.png")
# Default number of rendering threads to spawn, should be roughly equal to number of CPU cores available
NUM_THREADS = CONFIG.TILE_RASTER_MAX_THREADS
SIZE_X = 256
SIZE_Y = 256

def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - log(tan(lat_rad) + (1 / cos(lat_rad))) / pi) / 2.0 * n)
  return (xtile, ytile, zoom)

def tiles4BBox(domain, levels):
        tiles = {}
        for level in levels:
                tileset = []
                tile_min = deg2num(domain[3],domain[0], level)
                tile_max = deg2num(domain[1],domain[2], level)
                logger.debug("tile min:\t{0}\tmax:\t{1}".format(tile_min, tile_max))
                for x in range(tile_min[0], tile_max[0] + 1):
                        for y in range(tile_min[1], tile_max[1] + 1):
                                tile = (x, y, level)
                                tileset.append(tile)
                        tiles[str(level)] = tileset
        return tiles

def minmax(a,b,c):
        a = max(a,b)
        a = min(a,c)
        return a

def zipdir(path, zip):
        for root, dirs, files in os.walk(path):
                for file in files:
                        f = os.path.join(root,file).replace(path,"")
                        zip.write(os.path.join(root,file),arcname=f)

def getLayerInfo(shp_file):
        layer_info = {"min_speed":-1, "max_speed":-1, "extents": {}, "native_wkid": ""}

        driver = ogr.GetDriverByName('ESRI Shapefile')
        data_source = driver.Open(shp_file, 0)
        layer = data_source.GetLayer()
                
        # get the extent and transform
        native_srs = layer.GetSpatialRef()
        native_extent = layer.GetExtent()
        layer_info["native_wkid"] = native_srs.GetAuthorityCode(None)
        layer_info["extents"][native_srs.GetAuthorityCode(None)] = {"xmin": native_extent[0], "ymin":native_extent[2], "xmax":native_extent[1], "ymax":native_extent[3], "proj4string": native_srs.ExportToProj4()}

        # Lon/Lat WGS84
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)
        point1 = ogr.Geometry(ogr.wkbPoint)
        point1.AddPoint(native_extent[0], native_extent[2])
        multipoint.AddGeometry(point1)
        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(native_extent[1], native_extent[3])
        multipoint.AddGeometry(point2)
        
        target_srs = osr.SpatialReference()
        target_srs.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(native_srs, target_srs)
        multipoint.Transform(transform)

        layer_info["extents"]["4326"] = {
                        "xmin": multipoint.GetGeometryRef(0).GetPoint(0)[0], 
                        "ymin":multipoint.GetGeometryRef(0).GetPoint(0)[1], 
                        "xmax":multipoint.GetGeometryRef(1).GetPoint(0)[0], 
                        "ymax":multipoint.GetGeometryRef(1).GetPoint(0)[1],
                        "proj4string": target_srs.ExportToProj4()
                        }

        # WebMercator 3857
        target_srs = osr.SpatialReference()
        target_srs.ImportFromEPSG(3857)
        input_srs = osr.SpatialReference()
        input_srs.ImportFromEPSG(4326)
        transform = osr.CoordinateTransformation(input_srs, target_srs)
        multipoint.Transform(transform)
        layer_info["extents"]["3857"] = {
                        "xmin": multipoint.GetGeometryRef(0).GetPoint(0)[0], 
                        "ymin":multipoint.GetGeometryRef(0).GetPoint(0)[1], 
                        "xmax":multipoint.GetGeometryRef(1).GetPoint(0)[0], 
                        "ymax":multipoint.GetGeometryRef(1).GetPoint(0)[1],
                        "proj4string": target_srs.ExportToProj4()
                        }

        # Get the min/max wind speed
        sql = "SELECT MIN(speed), MAX(speed) FROM '{0}'".format(layer.GetName())
        query = data_source.ExecuteSQL(sql)
        feature = query.GetFeature(0)
        layer_info["min_speed"] = feature.GetField("MIN_speed")
        layer_info["max_speed"] = feature.GetField("MAX_speed")

        return layer_info

class GoogleProjection:
    def __init__(self,levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = SIZE_X
        for d in range(0,levels):
            e = c / 2
            self.Bc.append(c / 360.0)
            self.Cc.append(c / (2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2
                
    def fromLLtoPixel(self,ll,zoom):
         d = self.zc[zoom]
         e = round(d[0] + ll[0] * self.Bc[zoom])
         f = minmax(sin(DEG_TO_RAD * ll[1]),-0.9999,0.9999)
         g = round(d[1] + 0.5 * log((1 + f) / (1 - f)) * -self.Cc[zoom])
         return (e,g)
     
    def fromPixelToLL(self,px,zoom):
         e = self.zc[zoom]
         f = (px[0] - e[0]) / self.Bc[zoom]
         g = (px[1] - e[1]) / -self.Cc[zoom]
         h = RAD_TO_DEG * (2 * atan(exp(g)) - 0.5 * pi)
         return (f,h)

class RenderThread:
    def __init__(self, tile_dir, data_file, proj4string, max_speed, q, printLock, maxZoom):
        self.tile_dir = tile_dir
        self.q = q
        self.m = mapnik.Map(SIZE_X,SIZE_Y)

        one = max_speed/5      # 6
        two = str(one*2)       # 8
        three = str(one*3)     # 10
        four = str(4*one)      # 12
        one = str(one)
        
        
        self.printLock = printLock       
        # Load style XML

        # NOTE:
        # Buffer_size = 2048 prevents cutting off arrow markers during draw.
        # Draws entire map then cuts the image into tiles.
        xml = """<?xml version="1.0" encoding="utf-8"?>
        <!DOCTYPE Map[]>
        <Map srs="+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0.0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over" background-color="#00000000" buffer-size="2048" maximum-extent="-20037508.34,-20037508.34,20037508.34,20037508.34">

        <Parameters>
          <Parameter name="bounds">-180,-85.0511,180,85.0511</Parameter>
          <Parameter name="center">0,0,2</Parameter>
          <Parameter name="format">png</Parameter>
          <Parameter name="minzoom">0</Parameter>
          <Parameter name="maxzoom">22</Parameter>
          <Parameter name="name"><![CDATA[PowerAwesome]]></Parameter>
          <Parameter name="description"><![CDATA[PowerAwesomeDescription]]></Parameter>
        </Parameters>


        <Style name="PowerAwesomeID" filter-mode="first" >
          <Rule>
            <MinScaleDenominator>12500</MinScaleDenominator>
            <Filter>([speed] &gt;= {high}) and ([speed] &lt; {v_high})</Filter>
            <PointSymbolizer file='{orange}' allow-overlap="false" transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>12500</MaxScaleDenominator>
            <MinScaleDenominator>5000</MinScaleDenominator>
            <Filter>([speed] &gt;= {high}) and ([speed] &lt; {v_high})</Filter>
            <PointSymbolizer file='{orange}' allow-overlap="true" transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>5000</MaxScaleDenominator>
            <Filter>([speed] &gt;= {high}) and ([speed] &lt; {v_high})</Filter>
            <PointSymbolizer file='{orange}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MinScaleDenominator>12500</MinScaleDenominator>
            <Filter>([speed] &gt;= {med}) and ([speed] &lt; {high})</Filter>
            <PointSymbolizer file='{yellow}' allow-overlap="false" transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>12500</MaxScaleDenominator>
            <MinScaleDenominator>5000</MinScaleDenominator>
            <Filter>([speed] &gt;= {med}) and ([speed] &lt; {high})</Filter>
            <PointSymbolizer file='{yellow}' allow-overlap="true" transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>5000</MaxScaleDenominator>
            <Filter>([speed] &gt;= {med}) and ([speed] &lt; {high})</Filter>
            <PointSymbolizer file='{yellow}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MinScaleDenominator>12500</MinScaleDenominator>
            <Filter>([speed] &gt;= {low}) and ([speed] &lt; {med})</Filter>
            <PointSymbolizer file='{green}' allow-overlap="false" transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>12500</MaxScaleDenominator>
            <MinScaleDenominator>5000</MinScaleDenominator>
            <Filter>([speed] &gt;= {low}) and ([speed] &lt; {med})</Filter>
            <PointSymbolizer file='{green}' allow-overlap="true" transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>5000</MaxScaleDenominator>
            <Filter>([speed] &gt;= {low}) and ([speed] &lt; {med})</Filter>
            <PointSymbolizer file='{green}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MinScaleDenominator>12500</MinScaleDenominator>
            <Filter>([speed] &gt; {v_high})</Filter>
            <PointSymbolizer allow-overlap="false" file='{red}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>12500</MaxScaleDenominator>
            <MinScaleDenominator>5000</MinScaleDenominator>
            <Filter>([speed] &gt; {v_high})</Filter>
            <PointSymbolizer allow-overlap="true" file='{red}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>5000</MaxScaleDenominator>
            <Filter>([speed] &gt; {v_high})</Filter>
            <PointSymbolizer file='{red}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MinScaleDenominator>12500</MinScaleDenominator>
            <Filter>([speed] &lt; {low})</Filter>
            <PointSymbolizer allow-overlap="false" file='{blue}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>12500</MaxScaleDenominator>
            <MinScaleDenominator>5000</MinScaleDenominator>
            <Filter>([speed] &lt; {low})</Filter>
            <PointSymbolizer allow-overlap="true" file='{blue}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>5000</MaxScaleDenominator>
            <Filter>([speed] &lt; {low})</Filter>
            <PointSymbolizer file='{blue}' transform="rotate([QGIS_dir])" />
          </Rule>
          <Rule>
            <MinScaleDenominator>12500</MinScaleDenominator>
            <PointSymbolizer allow-overlap="false" />
          </Rule>
          <Rule>
            <MaxScaleDenominator>12500</MaxScaleDenominator>
            <MinScaleDenominator>5000</MinScaleDenominator>
            <PointSymbolizer allow-overlap="true" />
          </Rule>
        </Style>
        <Layer name="PowerAwesomeID"
          srs='{proj}'>
            <StyleName>PowerAwesomeID</StyleName>
            <Datasource>
               <Parameter name="file"><![CDATA[{data}]]></Parameter>
               <Parameter name="type"><![CDATA[shape]]></Parameter>
            </Datasource>
          </Layer>

        </Map>""".format(data=data_file,proj=proj4string,low=one,med=two,high=three,v_high=four,blue=ONE,green=TWO,yellow=THREE,orange=FOUR,red=FIVE)

        logger.debug(xml)

        mapnik.load_map_from_string(self.m, xml, True)
        #mapnik.load_map(self.m, mapfile, True)

        # Obtain <Map> projection
        self.prj = mapnik.Projection(self.m.srs)
        # Projects between tile pixel co-ordinates and LatLong (EPSG:4326)
        self.tileproj = GoogleProjection(maxZoom + 1)


    def render_tile(self, tile_uri, x, y, z):

        # Calculate pixel positions of bottom-left & top-right
        p0 = (x * SIZE_X, (y + 1) * SIZE_X)
        p1 = ((x + 1) * SIZE_Y, y * SIZE_Y)

        # Convert to LatLong (EPSG:4326)
        l0 = self.tileproj.fromPixelToLL(p0, z)
        l1 = self.tileproj.fromPixelToLL(p1, z)

        # Convert to map projection (e.g.  mercator co-ords EPSG:900913)
        c0 = self.prj.forward(mapnik.Coord(l0[0],l0[1]))
        c1 = self.prj.forward(mapnik.Coord(l1[0],l1[1]))

        # Bounding box for the tile
        if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
            bbox = mapnik.Box2d(c0.x,c0.y, c1.x,c1.y)
        else:
            bbox = mapnik.Envelope(c0.x,c0.y, c1.x,c1.y)
        render_size = SIZE_X
        self.m.resize(render_size, render_size)
        self.m.zoom_to_box(bbox)
        if(self.m.buffer_size < render_size / 2):
            self.m.buffer_size = render_size / 2

        # Render image with default Agg renderer
        im = mapnik.Image(render_size, render_size)
        mapnik.render(self.m, im)
        
        im.save(tile_uri, 'png256')


    def loop(self):
        while True:
            #Fetch a tile from the queue and render it
            r = self.q.get()
            if (r == None):
                self.q.task_done()
                break
            else:
                (name, tile_uri, x, y, z) = r

            exists = ""
            if os.path.isfile(tile_uri):
                exists = "exists"
            else:
                self.render_tile(tile_uri, x, y, z)
            bytes = os.stat(tile_uri)[6]
            empty = ''
            if bytes == 103:
                empty = " Empty Tile "
            self.printLock.acquire()
            logger.debug("{} : {} {} {} {} {}".format(name, z, x, y, exists, empty))
            self.printLock.release()
            self.q.task_done()

def render_tiles(bbox, data_file, proj4string, max_speed, tile_dir, minZoom=1,maxZoom=18, name="unknown", num_threads=NUM_THREADS, tms_scheme=False):
        logger.verbose("render_tiles({} {} {} {} {} {})".format(bbox, data_file, tile_dir, minZoom, maxZoom, name))

        # Launch rendering threads
        queue = Queue(32)
        printLock = threading.Lock()
        renderers = {}
        for i in range(num_threads):
                renderer = RenderThread(tile_dir, data_file, proj4string, max_speed, queue, printLock, maxZoom)
                render_thread = threading.Thread(target=renderer.loop)
                render_thread.start()
                renderers[i] = render_thread

        if not os.path.isdir(tile_dir):
                os.makedirs(tile_dir)

        gprj = GoogleProjection(maxZoom + 1) 
        ll0 = (bbox[0],bbox[3])
        ll1 = (bbox[2],bbox[1])

        for z in range(minZoom,maxZoom + 1):
                px0 = gprj.fromLLtoPixel(ll0,z)
                px1 = gprj.fromLLtoPixel(ll1,z)
                logger.debug("\nZOOOOOOOOM: {}".format(z))
                logger.debug("PX 0: {}".format(px0))
                logger.debug("PX 1: {}".format(px1))
                logger.debug("BBOX: {}".format(bbox))
                for x in range(int(px0[0] / (SIZE_X * 1.0)),int(px1[0] / (SIZE_Y * 1.0)) + 1):
                        # Validate x co-ordinate
                        if (x < 0) or (x >= 2 ** z):
                                continue
                
                        # check if we have directories in place
                        zoom = "%s" % z
                        str_x = "%s" % x
                        zx_dir = os.path.join(tile_dir, zoom, str_x)
                        if not os.path.isdir(zx_dir):
                                os.makedirs(zx_dir)

                        for y in range(int(px0[1] / (SIZE_X * 1.0)),int(px1[1] / (SIZE_Y * 1.0)) + 1):
                                # Validate x co-ordinate
                                if (y < 0) or (y >= 2 ** z):
                                        continue
                                # flip y to match OSGEO TMS spec
                                if tms_scheme:
                                        str_y = "%s" % ((2 ** z - 1) - y)
                                else:
                                        str_y = "%s" % y
                
                                tile_uri = os.path.join(tile_dir,zoom ,str_x,'{0}.png'.format(str_y))
                                # Submit tile to be rendered into the queue
                                t = (name, tile_uri, x, y, z)
                                try:
                                        queue.put(t)
                                except KeyboardInterrupt:
                                        raise SystemExit("Ctrl-c detected, exiting...")

        # Signal render threads to exit by sending empty request to queue
        for i in range(num_threads):
                        queue.put(None)
        # wait for pending rendering jobs to complete
        queue.join()
        for i in range(num_threads):
                        renderers[i].join()

def make_tiles_for_output(dir, wn_results, forecast):
        logger.verbose("make_tiles_for_output({} {} {})".format(dir, wn_results, forecast))
        output_dir = wn_results[0]
        results = wn_results[1]
        layer_info_array = {}

        # Iterate through runs to get GLOBAL maximum speed
        max_speed = 0.
        for res in results:
                file_path = os.path.join(output_dir,res)
                layer_info = getLayerInfo(file_path)
                max_speed = max(max_speed,layer_info['max_speed'])

        for res in results:
                k = res.rfind("_")
                time = res[:k]
                time = time.replace("dem_","")
                name = res.split(".")[0]
                tile_dir = os.path.join(dir, CONFIG.TILE_RASTER_FILE_NAME, name)
                if not os.path.exists(tile_dir):
                        os.makedirs(tile_dir)

                file_path = os.path.join(output_dir,res)
                layer_info = getLayerInfo(file_path)
                logger.debug("LAYER INFO: {}".format(layer_info))
                ext = layer_info['extents']['4326']
                bbox = (ext['xmin'],ext['ymin'],ext['xmax'],ext['ymax'])
                proj4string = layer_info['extents'][layer_info["native_wkid"]]["proj4string"]
                logger.debug("Proj4String: {}".format(proj4string))
                layer_info['max_speed'] = max_speed
                layer_info_array[res] = layer_info
                render_tiles(bbox, file_path, proj4string, max_speed, tile_dir, CONFIG.TILE_RASTER_MIN_LEVEL, CONFIG.TILE_RASTER_MAX_LEVEL, "WindNinja")
        zipf = zipfile.ZipFile(str(os.path.join(dir, CONFIG.TILE_RASTER_ZIP_NAME)), 'w')
        zipdir(os.path.join(dir, CONFIG.TILE_RASTER_FILE_NAME), zipf)
        zipf.close()

        return CONFIG.TILE_RASTER_ZIP_NAME,layer_info_array
