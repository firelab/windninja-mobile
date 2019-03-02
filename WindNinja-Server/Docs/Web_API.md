# WindNinja Mobile - Server API

## ENDPOINTS

### JOB

GET /api/job/[string:id]
* returns 200 when matched with job details as JSON
* returns 404 when not matched with error as JSON 

POST /api/job
* QUERY STRING PARAMETERS:
  * __name__ string, required - user defined, descriptive name of the job
  * __xmin__ float, required - domain bounding box minimum x coordinate (longitude) in decimal degrees WGS84
  * __ymin__ float, required - domain bounding box minimum y coordinate (latitude) in decimal degrees WGS84
  * __xmax__ float, required - domain bounding box maximum x coordinate (longitude) in decimal degrees WGS84
  * __ymax__ float, required - domain bounding box maximum y coordinate (latitude) in decimal degrees WGS84
  * __parameters__ string, required - WindNinja model parameters as semi-colon (;) delimited list of colon (:) delimited key value pairs (see WindNinja CLI parameters). Required parameters are forecast_duration, vegetation, and mesh_choice. Others can be overriden from the embedded defaults.  Some are locked down for performance reasons. 
  * __forecast__ string, required - forecast to be used in the model runs (see WindNinja CLI parameters). Supports 'AUTO' to pick a specifically aligned forecast for the domain extent.
  * __email__ string, optional - email address to send job notifications 
  * __account__ string, required - id of registered account with the WindNinja Mobile system
  * __products__ JSON, required - output types to generate as semi-colon (;) delimited list of colon (:) delimited key value pairs 
    
    * __vector__ = GeoJson files of the WindNinja output . One file for each time simulation
    * __raster__ = Mapnik generated tileset based on the WindNinja output shapefiles. One tileset for each time simulation, all packaged in a zip file. __NOTE__: this product type may go away in the future.
    * __topofire__ = Basemap tileset for the job domain extracted from the UofM TopoFire tile service
    * __geopdf__ = Not implemented as of yet, placeholder for future development
    * __clustered__ = This is a custom csv-like generated format of raw numerical data. The file contains "scaled" levels of detail. The format is parse-able by any client but was designed specifically for the WindNinja Mobile application for download size and rendering speed.
    * __weather__ = GeoJson files of the large scale weather data downloaded and input to the WindNinja CLI for the job domain. One file for each time simulation
      
* returns 200 when job is successfully saved and queued and returns the details as JSON (see structure below)
* returns 200 when job is successfully saved but queueing fails and returns the details as JSON (see structure below)
* returns 400 when required parameters are missing as JSON message
* returns 500 when job saving faults or other error

### ACCOUNT

GET /api/account/[string:id]
* returns 200 when matched with account details as JSON (see structure below)
* returns 404 when not matched with error as JSON 
	
### FEEDBACK 

POST /api/feedback
* BODY JSON: 
	* {"account":[string:id],"comments":[string]}
* returns 200 when feedback is successfully queued and returns the feedback details as JSON (see structure below)
* returns 400 when required parameters are missing as JSON message
* returns 500 when feedback queueing faults with error as JSON

### NOTIFICATIONS
	
GET /api/notification
* returns 200 with list of notifications as JSON (see structure below)
* returns 500 when if any error with error as JSON
	
GET	/api/notification/[string:id]
* return 200 when matched with notification as JSON (see structure below)
* returns 404 when not matched with error as JSON 
* returns 500 when if any error with error as JSON
	
### OUTPUT

GET /output/[string:job]/[string:id]
* returns 200 with specific content (JSON, ZIP, etc) when matched
* returns 404 when not matched with error as JSON {"message": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again."}
* returns 500 when if any error with error as JSON

## JSON STRUCTURES

#### 400 Required parameter missing

    {
        "message": {
            "name": "[Endpoint parameter name] is required"
        }
    }

#### 404 Resource not found/item id not matched

    {
        "message": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again."
    }

#### 200 Job Details

    {
        "output": {
            "products": [
                {
                    "baseUrl": "http://windninja.wfmrda.org/output/23becdaadf7c4ec2993497261e63d813/",
                    "package": "tiles.zip",
                    "type": "raster",
                    "format": "tiles",
                    "files": [
                        "dem_12-15-2015_1700_29m",
                        "dem_12-15-2015_1400_29m",
                        "dem_12-15-2015_2300_29m",
                        "dem_12-15-2015_2000_29m"
                    ],
                    "name": "WindNinja Raster Tiles",
                    "data": [
                        "dem_12-15-2015_1700_29m:24.722978",
                        "dem_12-15-2015_1400_29m:27.903006",
                        "dem_12-15-2015_2300_29m:16.501172",
                        "dem_12-15-2015_2000_29m:21.656377"
                    ]
                },
                {
                    "baseUrl": "http://windninja.wfmrda.org/output/23becdaadf7c4ec2993497261e63d813/",
                    "package": "topofire.zip",
                    "type": "basemap",
                    "format": "tiles",
                    "files": [],
                    "name": "TopoFire Basemap",
                    "data": []
                },
                {
                    "baseUrl": "http://windninja.wfmrda.org/output/23becdaadf7c4ec2993497261e63d813/",
                    "package": "",
                    "type": "vector",
                    "format": "json",
                    "files": [
                        "UCAR-NAM-CONUS-12-KM-12-15-2015_1400.json",
                        "UCAR-NAM-CONUS-12-KM-12-15-2015_1700.json",
                        "UCAR-NAM-CONUS-12-KM-12-15-2015_2000.json",
                        "UCAR-NAM-CONUS-12-KM-12-15-2015_2300.json"
                    ],
                    "name": "Weather Json Vectors",
                    "data": []
                },
                {
                    "baseUrl": "http://windninja.wfmrda.org/output/23becdaadf7c4ec2993497261e63d813/",
                    "package": "",
                    "type": "vector",
                    "format": "json",
                    "files": [
                        "dem_12-15-2015_1400_29m.json",
                        "dem_12-15-2015_1700_29m.json",
                        "dem_12-15-2015_2000_29m.json",
                        "dem_12-15-2015_2300_29m.json"
                    ],
                    "name": "WindNinja Json Vectors",
                    "data": []
                }
            ]
        },
        "account": "test@yourdatasmarter.com",
        "messages": [
            "2015-02-27T16:48:45.2949952-07:00 | INFO | job created",
            "2015-02-27T16:48:46.251000-07:00 | INFO | Initializing WindNinja Run",
            "2015-02-27T16:48:46.370000-07:00 | INFO | DEM created",
            "2015-02-27T16:49:01.439000-07:00 | INFO | WindNinjaCLI executed",
            "2015-02-27T16:49:19.481000-07:00 | INFO | Output converted to geojson",
            "2015-02-27T16:49:19.527000-07:00 | INFO | Complete - total processing: 0:00:33.474000",
            "2015-12-15T11:24:12.802000-07:00 | INFO | Initializing WindNinja Run",
            "2015-12-15T11:24:12.935000-07:00 | INFO | DEM created",
            "2015-12-15T11:24:21.444000-07:00 | INFO | WindNinjaCLI executed",
            "2015-12-15T11:24:47.399000-07:00 | INFO | Output converted to geojson",
            "2015-12-15T11:24:49.941000-07:00 | INFO | TopoFire tiles compiled",
            "2015-12-15T11:25:10.774000-07:00 | INFO | Output converted to raster tiles",
            "2015-12-15T11:29:22.910000-07:00 | INFO | Initializing WindNinja Run",
            "2015-12-15T11:29:23.003000-07:00 | INFO | DEM created",
            "2015-12-15T11:29:29.823000-07:00 | INFO | WindNinjaCLI executed",
            "2015-12-15T11:29:56.014000-07:00 | INFO | Output converted to geojson",
            "2015-12-15T11:29:58.313000-07:00 | INFO | TopoFire tiles compiled",
            "2015-12-15T11:30:22.230000-07:00 | INFO | Output converted to raster tiles",
            "2015-12-15T11:30:25.061000-07:00 | INFO | Complete - total processing: 0:00:59.454000"
        ],
        "status": "succeeded",
        "email": "",
        "id": "23becdaa-df7c-4ec2-9934-97261e63d813",
        "input": {
            "parameters": "forecast_duration:12;vegetation:trees;mesh_choice:fine",
            "domain": {
                "ymax": 47.038565315467025,
                "ymin": 46.99526210560205,
                "xmax": -113.97925790543299,
                "xmin": -114.0235465406869
            },
            "products": "vector:true;raster:true;topofire:true;geopdf:false",
            "forecast": "UCAR-NAM-CONUS-12-KM"
        },
        "name": "Point Six (test)"
    }

#### 200 Account Details
    {
        "devices": [
            {
                "platform": "Android",
                "version": "5.1",
                "id": "123",
                "model": "XT1254"
            },
            {
                "platform": "iOS",
                "version": "9.3.4",
                "id": "456",
                "model": "iPad3,2"
            }
        ],
        "status": "accepted",
        "email": "me@work.com",
        "id": "me@work.com",
        "createdOn": "2016-05-20T22:33:50.306919",
        "name": "Iam A User"
    }
#### 200 Notification Details

    {
        "id": "23becdaa-df7c-4ec2-9934-97261e63d813",
        "expires" : "2015-12-15T11:30:25.061000-07:00",
        "message" : "This is an announcement about the WindNinja Mobile system"
    }
