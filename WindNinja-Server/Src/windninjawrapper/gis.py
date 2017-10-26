import base64
import logging
import math
import os

from osgeo import gdal, osr, ogr
import ogr2ogr

from config import CONFIG, MESSAGES
from utility import execute_shell_process


def withinDEM(bbox):

    #dem minimum bounding geometry
    wkb = base64.b64decode(CONFIG.DEM_MIN_BOUNDING_GEOM_WKB)
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
        return False, MESSAGES.BBOX_OUTSIDE_DEM
    
    center = [bbox[2] + ((bbox[0] - bbox[2]) / 2), bbox[3] + ((bbox[1] - bbox[3]) / 2)]
    logging.debug("dem center: {0}".format(center))
    
    utm = utmZone(center[0], center[1])
    src_srs = osr.SpatialReference()
    dst_srs = osr.SpatialReference()
    src_srs.ImportFromEPSG(4326)
    dst_srs.ImportFromEPSG(utm)
    ct = osr.CoordinateTransformation(src_srs, dst_srs)
    logging.debug("using utm zone: {0}".format(utm))

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

    input_dem_path = os.path.abspath(CONFIG.IN_DEM_PATH)
    logging.debug("input dem path: {}".format(input_dem_path))
    
    output_dem_path = os.path.join(project_path, CONFIG.OUT_DEM_FILENAME)
    output_dem_path = os.path.abspath(output_dem_path)
    logging.debug("output dem path: {0}".format(output_dem_path))
    
    #TODO: convert to gdal.warp in v2
    command = 'gdalwarp -tr 85 85 -t_srs epsg:%d -te %d %d %d %d %s %s -overwrite' % (utm, window[0], window[1], window[2], window[3], input_dem_path, output_dem_path)
    result = execute_shell_process(command, project_path)
    if result[0]:
        result = (True, output_dem_path)
    
    return result

def convertShpToJson(shapefiles, out_folder, where=None):
    result = (True, [])
    converted = result[1]
    params = ["", "-f", "geojson", "-t_srs", "epsg:3857"]
    
    if where:
        params.append("-where")
        params.append(where)

    try:
        for shp in shapefiles[1]:
            in_file = os.path.join(shapefiles[0], shp)
            
            #Remove any . characters from the output name
            out_file = os.path.join(out_folder, "{0}.{1}".format(os.path.splitext(shp)[0].replace(".", ""), "json"))
            logging.debug("Converting {0} to {1}".format(in_file, out_file))
            args = params + [out_file, in_file]
            conversion = ogr2ogr.main(args)
            
            if not conversion:
                result = (False, "SHP to GEOJSON conversion failed: {0}".format(shp))
                break
            else:
                converted.append(os.path.split(out_file)[1])

    except Exception as e:
        msg = str(e).replace("\n", " ")
        result = (False, msg)

    return result

def getLayerInfo(file, field):
    info = {"min":-1, "max":-1, "extents": {}, "native_wkid": ""}
        
    data_source = ogr.Open(file, 0)
    layer = data_source.GetLayer()
                
    # get the extent and transform
    sr = layer.GetSpatialRef()
    wkid = sr.GetAuthorityCode(None)
    info["native_wkid"] = wkid

    envelope = layer.GetExtent()
    extent = {
        "xmin": envelope[0],
        "ymin":envelope[2],
        "xmax":envelope[1],
        "ymax":envelope[3],
        "proj4string": sr.ExportToProj4()
    }
    info["extents"][wkid] = extent

    projected_wkids = [4326, 3857]
    if wkid in projected_wkids:
        projected_wkids.remove(wkid)

    projected_extents = convertExtents(extent, projected_wkids)
    info["extents"].update(projected_extents)
    
    # Get the min/max wind speed
    sql = "SELECT MIN({0}), MAX({0}) FROM \"{1}\"".format(field, layer.GetName())
    query = data_source.ExecuteSQL(sql)
    feature = query.GetFeature(0)
    info["min"] = feature.GetField("MIN_{}".format(field))
    info["max"] = feature.GetField("MAX_{}".format(field))

    return info

def getRasterInfo(file):
    info = {"min":-1, "max":-1, "extents": {}, "native_wkid": ""}

    raster = gdal.Open(file)
    band1 = raster.GetRasterBand(1)
    stats = band1.GetStatistics(False, True)

    info["min"] = stats[0]
    info["max"] = stats[1]

    prj = raster.GetProjectionRef()
    sr = osr.SpatialReference(prj)
    wkid = sr.GetAuthorityCode(None)
    info["native_wkid"] = wkid

    ulx, xres, xskew, uly, yskew, yres  = raster.GetGeoTransform()
    lry = uly + (raster.RasterYSize * yres)
    lrx = ulx + (raster.RasterXSize * xres)

    extent = {
        "xmin":lrx if (lrx<ulx) else ulx, 
        "ymin":lry if (lry<uly) else uly, 
        "xmax":ulx if (ulx>lrx) else lrx, 
        "ymax":uly if (uly>lry) else lry, 
        "proj4string": sr.ExportToProj4()
    }
    info["extents"][wkid] = extent

    projected_wkids = [4326, 3857]
    if wkid in projected_wkids:
        projected_wkids.remove(wkid)
    
    projected_extents = convertExtents(extent, projected_wkids)
    info["extents"].update(projected_extents)

    return info

def convertExtents(extent, wkids):
    extents = {}

    native_srs = osr.SpatialReference()
    native_srs.ImportFromProj4(extent["proj4string"])

    for wkid in wkids:
        multipoint = ogr.Geometry(ogr.wkbMultiPoint)
        point1 = ogr.Geometry(ogr.wkbPoint)
        point1.AddPoint(extent["xmin"], extent["ymin"])
        multipoint.AddGeometry(point1)
        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(extent["xmax"], extent["ymax"])
        multipoint.AddGeometry(point2)
        
        target_srs = osr.SpatialReference()
        target_srs.ImportFromEPSG(wkid)
        transform = osr.CoordinateTransformation(native_srs, target_srs)
        multipoint.Transform(transform)

        extents[wkid] = {
            "xmin": multipoint.GetGeometryRef(0).GetPoint(0)[0], 
            "ymin":multipoint.GetGeometryRef(0).GetPoint(0)[1], 
            "xmax":multipoint.GetGeometryRef(1).GetPoint(0)[0], 
            "ymax":multipoint.GetGeometryRef(1).GetPoint(0)[1],
            "proj4string": target_srs.ExportToProj4()
        }

    return extents
