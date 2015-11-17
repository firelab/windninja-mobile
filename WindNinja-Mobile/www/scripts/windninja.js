// Variables
var _DEBUG = false
	, _includeDemo = true
	, configDir
	, config = {}
	, isIOS7 = false
	, map
	, mapView
	, sketch
	, longPress
	, gpsSource
	, gpsLayer
	, sketchSource
	, sketchLayer
	, sketchPolyFeature
	, sketchLineFeature
	, sketchFeatures = []
	, sketchCoordinates = []
	, mapProj
	, latLonProj
	, baseMaps = []
	, mapLayers = []
	, gpsLayer
	, clusterDistance = 12
	, ninjaRun
	, domainName
	, startPixel
	, holdPromise
	, connection
	, dataDir
	, cacheDir
	, serverURL = 'http://carto.yourdatasmarter.com/USFS/WindNinja/'
	, dataURL
	, eRegex = /[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?/
	, oRegex = /(dem_(\d{2}-\d{2}-\d{4})_(\d{4})_\d{1,3}[a-z]{1})/
	, fRegex = /((?:(?:UCAR|NOMADS)-(?:NAM|HRRR)-(?:CONUS|ALASKA)-(?:\d{1,2}(?:\.\d{1,2})?-KM|DEG))-(\d{2}-\d{2}-\d{4})_(\d{4}))/
	, dRegex = /(domain)/
	, rRegex = /(relief)/
	, rasRegex = /(tiles)/
	, guidRegex = /[\da-zA-Z]{8}-([\da-zA-Z]{4}-){3}[\da-zA-Z]{12}/
	, demoJob = {
		"status": "Created",
		"output": {
			"products": [
			{
				"name": "Weather Json Vectors",
				"type": "vector",
				"format": "json",
				"baseUrl": "",
				"package": "",
				"files": [
					"UCAR-NAM-CONUS-12-KM-02-27-2015_1700.json",
					"UCAR-NAM-CONUS-12-KM-02-27-2015_2000.json",
					"UCAR-NAM-CONUS-12-KM-02-27-2015_2300.json",
					"UCAR-NAM-CONUS-12-KM-02-28-2015_0200.json"
				],
				"data": null
			},
			{
				"name": "TopoFire Basemap",
				"type": "basemap",
				"format": "tiles",
				"baseUrl": "",
				"package": "relief.zip",
				"files": [],
				"data": null
			},
			{
				"name": "WindNinja Raster Tiles",
				"type": "raster",
				"format": "tiles",
				"baseUrl": "",
				"package": "tiles.zip",
				"files": [
					"dem_02-27-2015_1700_29m",
					"dem_02-27-2015_2000_29m",
					"dem_02-27-2015_2300_29m",
					"dem_02-28-2015_0200_29m"
				],
				"data": [
					"dem_02-27-2015_1700_29m:24.84",
					"dem_02-27-2015_2000_29m:33.59",
					"dem_02-27-2015_2300_29m:29.96",
					"dem_02-28-2015_0200_29m:24.87"
				]
			},
			{
				"name": "WindNinja Json Vectors",
				"type": "vector",
				"format": "json",
				"baseUrl": "",
				"package": "",
				"files": [
					"dem_02-27-2015_1700_29m.json",
					"dem_02-27-2015_2000_29m.json",
					"dem_02-27-2015_2300_29m.json",
					"dem_02-28-2015_0200_29m.json"
				],
				"data": null
			}
			]
		},
		"messages": [],
		"id": "23becdaa-df7c-4ec2-9934-97261e63d813",
		"name": "Point Six (test)",
		"input": {
			"domain": {
				"xmin": -114.0235465406869,
				"ymin": 46.99526210560205,
				"ymax": 47.038565315467025,
				"xmax": -113.97925790543299
			},
			"parameters": "forecast_duration:12;vegetation:trees;mesh_choice:fine",
			"products": "vector:true;raster:true;topofire:true;geopdf:false",
			"forecast": "UCAR-NAM-CONUS-12-KM"
		}
	};

// Initialize UI
$(document).ready(initUI);
// Device listeners
$(document).on('deviceready', _onDeviceReady);
$(document).on('offline', _onOffilne);
$(document).on('online', _onOnline);

// Cordova Device ready
function _onDeviceReady() {
	// Fix for iOS 7 and the statusbar overlaying the webview
	if (device.platform === 'iOS' && (parseFloat(device.version) >= 7)) {
		isIOS7 = true;
		StatusBar.overlaysWebView(false);
		StatusBar.styleDefault();
		StatusBar.backgroundColorByName('lightGray');

		var btm = ($(20).toEm() + 3.25)
		$('#foot').css({ 'bottom': btm + 'em' });

		// Reset our map size to account for the statusbar
		setmapsize();
	}

	// Initialze cache directory (offilne map tiles), and initialize our map
	window.resolveLocalFileSystemURL(cordova.file.cacheDirectory, function (directoryEntry) {
		directoryEntry.getDirectory('tilesCache', { create: true, exclusive: false }, function (dir) {
			console.info('tiles cache directory created/set.');
			cacheDir = dir;
			_initMap();
			// Start GPS location
			_onGPSOn();
		}, fail);
	}, fail);

	// Initialize data directory (where run data is stored), and load any existing runs
	window.resolveLocalFileSystemURL(cordova.file.dataDirectory, function (directoryEntry) {
		configDir = directoryEntry;

		_loadConfig().always(function () {
			console.info('config loaded, initializing run data directory');
			directoryEntry.getDirectory('runs', { create: true, exclusive: false }, function (dir) {
				console.info('run data directory created/set.');
				dataDir = dir;
				WindNinjaRun.prototype.__dir = dataDir.nativeURL;
				// is a demo run included?
				if (_includeDemo) {
					console.info('including demo run');
					// Initialize demo run
					dataDir.getDirectory('23becdaa-df7c-4ec2-9934-97261e63d813', { create: true, exclusive: false }, function (testDir) {
						testDir.getFile("job.json", { create: true, exclusive: false }, function (file) {
							file.createWriter(function (fileWriter) {
								var blob = new Blob([JSON.stringify(demoJob)], { type: 'application/json' });
								fileWriter.write(blob);

								// Initialize run list
								_initRunList();
							});
						});
					}, fail);
				} else {
					// Initialize run list
					_initRunList();
				}
			}, fail);
		});
	}, fail);
}
// Loss of network connection
function _onOffilne() {
	connection = false;
	$('#createRun').button('disable').attr({ 'disabled': 'disabled' });
	$('[data-online=true]').each(function () { $(this).attr({ 'disabled': 'disabled' }); });
	navigator.notification.alert('Network Connection lost', null, 'Network Status', 'Ok');
}
// Reacquire network connection
function _onOnline() {
	connection = true;
	$('#createRun').button('enable').removeAttr('disabled');
	$('[data-online=true]').each(function () { $(this).removeAttr('disabled'); });
}
// Load config file
function _loadConfig() {
	return $.ajax({
		url: configDir.nativeURL + 'config.json',
		dataType: 'json',
		method: 'GET'
	}).done(function (configData) {
		console.info('config loaded successfully');
		config = configData;
	}).fail(function () {
		console.info('config not found or corrupt, setting defaults');
		config = {
			"Name": "",
			"Email": "",
			"Phone": "",
			"Outputs": {
				"vector": true,
				"raster": true,
				"topo": true,
				"googl": false,
				"geopdf": false,
				"weather": true
			},
			"Device": device.model,
			"Platform": device.platform,
			"Version": device.version,
			"Registered": false,
			"RegistrationID": undefined
		};
		// Open welcome & settings pages
		$('#welcome').popup('open');
		$('#pnl_Settings').panel('open');
	}).always(function () {
		// bind config properties to the proper UI elements
		$('#userName').val(config.Name);
		$('#userEmail').val(config.Email);
		var parts = config.Phone.split('@');
		$('#userPhone').val(parts[0]);
		$('#provider').val(parts[1]).selectmenu('refresh');
		for (var type in config.Outputs) {
			if (config.Outputs.hasOwnProperty(type) && config.Outputs[type])
				$('#' + type + 'Output').prop('checked', true).flipswitch('refresh');
		}

		if (config.Email) {
			$('#email').prop('disabled', false).flipswitch('enable');
		} else {
			$('#email').prop({ 'checked': false, 'disabled': true }).flipswitch('disable').flipswitch('refresh');
		}

		if (config.Phone && config.Phone.indexOf('@') == 10) {
			$('#text').prop('disabled', false).flipswitch('enable');
		} else {
			$('#text').prop({ 'checked': false, 'disabled': true }).flipswitch('disable').flipswitch('refresh');
		}

		_enableRegister();
	});
}
// Save config file
function _saveConfig(alert) {
	// Save UI elements to the config object
	config.Name = $('#userName').val();
	config.Email = $('#userEmail').val();
	config.Phone = $('#userPhone').val().replace(/\D/g, '') + '@' + $('#provider').val();
	config.Outputs = {
		"vector": $('#vectorOutput').prop('checked'),
		"raster": $('#rasterOutput').prop('checked'),
		"topo": $('#topoOutput').prop('checked'),
		"googl": $('#googlOutput').prop('checked'),
		"geopdf": $('#geopdfOutput').prop('checked'),
		"weather": true
	};
	config.Device = device.model;
	config.Platform = device.platform;
	config.Version = device.version;

	if (config.Email) {
		$('#email').prop('disabled', false).flipswitch('enable');
	} else {
		$('#email').prop({ 'checked': false, 'disabled': true }).flipswitch('disable').flipswitch('refresh');
	}

	if (config.Phone.indexOf('@') == 10) {
		$('#text').prop('disabled', false).flipswitch('enable');
	} else {
		$('#text').prop({ 'checked': false, 'disabled': true }).flipswitch('disable').flipswitch('refresh');
	}

	console.info(config);

	configDir.getFile('config.json', { create: true, exclusive: false }, function (file) {
		file.createWriter(function (fileWriter) {
			var blob = new Blob([JSON.stringify(config)], { type: 'application/json' });
			fileWriter.write(blob);
			if (alert)
				navigator.notification.alert('Settings Saved.', null, 'Settings');
		}, fail);
	});
}
// Check if the 'Register' button should be enabled
function _enableRegister() {
	if (config.Registered) {
		$('#register').prop('disabled', true).button('disable').button('refresh');
		$('#sbmtFeedback').prop('disabled', false).button('enable').button('refresh');
		return
	}

	if ($('#userName').val() !== '' && $('#userEmail').val() !== '') {
		$('#register').prop('disabled', false).button('enable').button('refresh');
	}
	return
}
// Register device for support and feedback
function _registerInstall() {
	var registration = {
		"name": config.Name,
		"email": config.Email,
		"device": config.Device,
		"platform": config.Platform,
		"version": config.Version
	};

	$.ajax({
		url: serverURL + 'api/register',
		method: 'POST',
		contentType: 'application/json',
		dataType: 'json',
		data: JSON.stringify(registration)
	}).done(function (data) {
		console.log(data);
		config.RegistrationID = data.id;
		config.Registered = true;
		_saveConfig(false);
		$('#sbmtFeedback').button('enable').button('refresh');
		navigator.notification.alert('Thank you for registering your install of WindNinja Mobile.');
	}).fail(function () {
		config.RegistrationID = null;
		config.Registered = false;
		_saveConfig(false);
		navigator.notification.alert('Error trying to register WindNinja Mobile. Please try again shortly.');
	});
}
// Submit feedback
function _submitFeedback(feedback) {
	var data = {
		'registerId': config.RegistrationID,
		'comments': feedback
	};
	$.ajax({
		url: serverURL + 'api/feedback',
		method: 'POST',
		contentType: 'application/json',
		dataType: 'json',
		data: JSON.stringify(data)
	}).done(function (data) {
		navigator.notification.alert('Your feedback has been submitted.', null, 'Feedback');
	}).fail(function () {
		navigator.notification.alert('Error submitting feedback. Please try again shortly.');
	});
}
// Initialize map objects
function _initMap() {
	console.info('cache directory initialized, creating and configuring map objects.');
	// Set map projections
	mapProj = ol.proj.get('EPSG:3857'); // Web-Mercator
	latLonProj = ol.proj.get('EPSG:4326'); // Lat/Lon
	var center = ol.proj.transform([-98.579404, 39.828127], latLonProj, mapProj);
	var size = ol.extent.getWidth(mapProj.getExtent()) / 256;
	var resolutions = new Array();
	var matrixIds = new Array();

	for (var z = 0; z < 14; z++) {
		resolutions[z] = size / Math.pow(2, z);
		matrixIds[z] = z;
	}
	baseMaps = [];

	/*
	 * Basemaps
	 */
	// Shaded Relief (shared by all online basemaps)
	var shadow = new ol.layer.Tile({
		source: new ol.source.WMTS({
			url: "http://basemap.nationalmap.gov/arcgis/rest/services/USGSShadedReliefOnly/MapServer/WMTS/",
			layer: '0',
			matrixSet: 'EPSG:3857',
			format: 'image/png',
			projection: mapProj,
			tileGrid: new ol.tilegrid.WMTS({
				origin: ol.extent.getTopLeft(mapProj.getExtent()),
				resolutions: resolutions,
				matrixIds: matrixIds
			}),
			style: 'default',
			wrapX: true
		})
	})
	// OSM
	baseMaps.push(new ol.layer.Group({
		id: 'osm',
		visible: true,
		preload: Infinity,
		layers: [
			//shadow,
			new ol.layer.Tile({
				source: new ol.source.OSM({
					url: 'http://{a-c}.tile.opencyclemap.org/landscape/{z}/{x}/{y}.png'
				})
			})
		]
	}));
	// Satellite
	baseMaps.push(new ol.layer.Group({
		id: 'sat',
		visible: false,
		preload: Infinity,
		layers: [
			//shadow,
			new ol.layer.Tile({
				source: new ol.source.MapQuest({
					layer: 'sat'
				})
			})
		]
	}));
	// TopoFire
	baseMaps.push(new ol.layer.Group({
		id: 'topofire',
		visible: false,
		layers: [
			//shadow,
			new ol.layer.Tile({
				source: new ol.source.OSM({
					url: 'http://topofire.dbs.umt.edu/topomap/relief/{z}/{x}/{y}.jpg',
					crossOrigin: 'anonymous'
				})
			})
		]
	}));
	// Local TopoFire Tiles (must be downloaded with each run - cached locally)
	baseMaps.push(new ol.layer.Tile({
		id: 'local',
		visible: false,
		source: new ol.source.XYZ({
			url: cacheDir.nativeURL + 'TopoFire/{z}/{x}/{y}.jpg'
		})
	}));

	/*
	 * Layers
	 */
	// GPS layer
	gpsSource = new ol.source.Vector();
	gpsLayer = new ol.layer.Vector({
		source: gpsSource,
		style: new ol.style.Style({
			image: new ol.style.Icon({
				src: 'css/images/gps.png'
			})
		})
	});
	// GeoMac (Current Fires & Perimeters)
	mapLayers.push(new ol.layer.Image({
		name: 'geomac',
		id: 'geomac',
		visible: false,
		source: new ol.source.ImageWMS({
			url: 'http://wildfire.cr.usgs.gov/ArcGIS/services/geomac_dyn/MapServer/WMSServer',
			params: { 'LAYERS': '26,25' }, //Current Fires(26), Current Fire Perimeters(25)
			crossOrigin: 'anonymous'
		})
	}));
	// MODIS
	mapLayers.push(new ol.layer.Tile({
		name: 'modis',
		id: 'modis',
		visible: false,
		source: new ol.source.TileWMS({
			url: 'http://activefiremaps.fs.fed.us/cgi-bin/mapserv.exe',
			params: {
				'map': 'conus.map',
				'LAYERS': 'Last 24 hour fire detections,Last 12 hour fire detections,Current Large incidents',
				'VERSION': '1.1.0'
			}
		})
	}));
	// Sketch layer
	sketchSource = new ol.source.Vector();
	sketchLayer = new ol.layer.Vector({
		source: sketchSource,
		style: new ol.style.Style({
			fill: new ol.style.Fill({
				color: [255, 0, 0, 0.5]
			}),
			stroke: new ol.style.Stroke({
				color: [255, 0, 0, 1],
				width: 2
			})
		})
	});

	// View
	mapView = new ol.View({
		center: center,
		projection: mapProj,
		zoom: 5,
		maxZoom: 17,
		minZoom: 3
	});
	// Map
	map = new ol.Map({
		layers: baseMaps,
		target: 'map',
		view: mapView,
		zoom: 10,
		controls: [new ol.control.Rotate(), new ol.control.Zoom()]
	});

	var l = mapLayers.length;
	for (var i = 0; i < l; ++i) {
		map.addLayer(mapLayers[i]);
	}

	// Custom Interactions
	sketch = new ol.interaction.Pointer({
		handleDownEvent: function (evt) {
			sketchLineFeature = new ol.Feature(new ol.geom.LineString([]));
			sketchSource.addFeature(sketchLineFeature);
			sketchFeatures.push(sketchLineFeature);
			sketchLineFeature.getGeometry().setCoordinates(sketchCoordinates);
			return true;
		},
		handleDragEvent: function (evt) {
			sketchCoordinates.push(evt.coordinate);
			sketchFeatures[0].getGeometry().setCoordinates(sketchCoordinates);
			return true;
		},
		handleUpEvent: function (evt) {
			sketchPolyFeature = new ol.Feature(new ol.geom.Polygon([sketchCoordinates]));
			// Remove the linestring
			sketchSource.removeFeature(sketchLineFeature);
			sketchSource.addFeature(sketchPolyFeature);
			return true;
		}
	});
	longPress = new ol.interaction.Pointer({
		handleDownEvent: function (evt) {
			clearTimeout(holdPromise);
			startPixel = evt.pixel;
			holdPromise = setTimeout(function () {
				// Vibrate to notify that the action is complete
				navigator.vibrate(50);

				// Set our center location for the run and center the map on it
				mapView.setCenter(evt.coordinate);

				// Open the panel to create run
				$('#request-panel').panel('open');
			}, 750, false);
		},
		handleDragEvent: function (evt) {
			clearTimeout(holdPromise);
			startPixel = undefined;
		},
		handleUpEvent: function (evt) {
			if (startPixel) {
				var pixel = evt.pixel;
				var deltaX = Math.abs(startPixel[0] - pixel[0]);
				var deltaY = Math.abs(startPixel[1] - pixel[1]);
				if (deltaX + deltaY > 6) {
					clearTimeout(holdPromise);
					startPixel = undefined;
				}
			}
		}
	});

	//add GPS button to 'zoom' controls (have to add this here because UI initialization has already occured)
	$('div.ol-zoom.ol-unselectable.ol-control').append($('<button id="btn_GPS" title="GPS" />').on('click', function () {
		_onGPSOn();
		//if ($(this).hasClass('on')) {
		//	_onGPSOff();
		//} else {
		//	_onGPSOn();
		//}
	}).addClass('off'));
}
// Remove map sketch layer
function _removeSketch() {
	map.removeLayer(sketchLayer);
	map.removeInteraction(sketch);
}
// Clean map sketch layer
function _cleanSketch() {
	if (sketchSource.getFeatures().length > 0) {
		sketchSource.clear();
	}
	sketchLineFeature = undefined;
	sketchPolyFeature = undefined;
	sketchCoordinates = [];
	sketchFeatures = [];
}
// Initialize Runs list
function _initRunList() {
	console.info('initializing run list.');
	$('#loadRun').button('disable').removeAttr('disabled');
	var dir = dataDir.nativeURL;
	var directoryReader = dataDir.createReader();
	var select = $('#runSelect');
	var defs = [];

	select.empty();
	directoryReader.readEntries(function (entries) {
		$.each(entries, function (i, entry) {
			if (entry.isDirectory && entry.name !== 'Documents') {
				var def = $.Deferred();
				var url = dir + entry.name + '/' + 'job.json';
				defs.push(def.promise());

				$.ajax({
					url: url,
					dataType: 'json'
				}).done(function (job) {
					var opt = $('<option />')
						.val(job.id)
						.text(job.name);

					select.append(opt);

					console.log(job.name + ' added to run list');

					def.resolve();
				}).fail(function (err) {
					def.reject([err.statusText]);
				});
			}
		});

		$.when.apply($, defs).done(function () {
			select.selectmenu('refresh').prop('selectedIndex', 0);
			if (select.length > 0) {
				select.selectmenu('enable').removeAttr('disbled').selectmenu('refresh');
				initRun();
			}
			else {
				select.selectmenu('disable').attr({ 'disbled': 'disabled' }).selectmenu('refresh');
			}
		}).fail(function (err) {
			fail(new Error(err).stack);
		});
	});
}
// Initialize UI elements and handlers
function initUI() {
	console.info('document loaded, initializing UI.');
	// Setup UI elements and event handlers

	// buttons first
	// Footer Buttons
	$('#btn_layers').button({
		icon: 'grid',
		iconpos: 'left',
		mini: true
	}).on('click', function () {
		console.info('#btn_layers.onClick');
		$(this).parent().toggleClass('ui-btn-on');
		$('#pnl_layers').panel('toggle');

	});
	$('#btn_draw').on('click', function () {
		console.group('#btn_draw.onClick');
		$('#draw').hide();
		$('#sketch').show();
		_cleanSketch();
		map.addLayer(sketchLayer);
		map.addInteraction(sketch);
		console.groupEnd();
	});
	$('#btn_submit').on('click', function () {
		console.group('#btn_submit.onClick');
		$('#draw').show();
		$('#sketch').hide();
		_removeSketch();
		$('#request-panel').panel('open');
		console.groupEnd();
	});
	$('#btn_cancel').on('click', function () {
		_removeSketch();
		$('#sketch').hide();
		$('#draw').show();
	});
	$('#btn_run-opts').button({
		icon: 'bullets',
		iconpos: 'right',
		mini: true,
		disabled: true
	}).on('click', function () {
		console.info('#btn_run-opts.onClick');
		$('#pnl_run-opts').panel('toggle');
	});
	// run options panel buttons
	$('#btn_time').button({ mini: true }).on('click', function () {
		console.info('#btn_time.onClick');
		$(this).parent().toggleClass('ui-btn-on');

		if ($('#btn_legend').parent().hasClass('ui-btn-on')) {
			$('#btn_legend').parent().removeClass('ui-btn-on');
			$('#pnl_legend').popup('close').on('popupafterclose', function (evt, ui) {
				if ($('#btn_time').parent().hasClass('ui-btn-on')) {
					$('#pnl_time').popup('open');
				}
				$('#pnl_legend').unbind('popupafterclose');
			});
		} else {
			if ($(this).parent().hasClass('ui-btn-on')) {
				$('#pnl_time').popup('open');
			} else {
				$('#pnl_time').popup('close');
			}
		}
	});
	$('#btn_legend').button({ mini: true }).on('click', function () {
		console.info('#btn_legend.onClick');
		$(this).parent().toggleClass('ui-btn-on');

		if ($('#btn_time').parent().hasClass('ui-btn-on')) {
			$('#btn_time').parent().removeClass('ui-btn-on');
			$('#pnl_time').popup('close').on('popupafterclose', function (evt, ui) {
				if ($('#btn_legend').parent().hasClass('ui-btn-on')) {
					$('#pnl_legend').popup('open');
				}
				$('#pnl_time').unbind('popupafterclose');
			});
		} else {
			if ($(this).parent().hasClass('ui-btn-on')) {
				$('#pnl_legend').popup('open');
			} else {
				$('#pnl_legend').popup('close');
			}
		}
	});
	$('#btn_home').button({ mini: true }).on('click', function () {
		console.info('#btn_home.onClick');
		$(this).parent().addClass('ui-btn-on');
		zoomToRun();
		$(this).parent().removeClass('ui-btn-on');
		//$('#pnl_run-opts').panel('close');
	});
	$('#btn_weather').button({ mini: true }).on('click', function () {
		console.info('#btn_weather.onClick');
		//$('#pnl_run-opts').panel('close');
		$(this).parent().toggleClass('ui-btn-on');
		ninjaRun.LoadForecasts = $(this).parent().hasClass('ui-btn-on');
		var i = $('#timeSlider').val();
		var forecastLayer = ninjaRun.ForecastLayers[i];
		if (forecastLayer !== undefined) {
			if (ninjaRun.LoadForecasts) {
				forecastLayer.setVisible(true);
			} else {
				forecastLayer.setVisible(false);
			}
		}
	});
	// not really buttons, but inputs
	$('input[name="layers"]').on('change', function () {
		var ids = [];
		$('input[name="layers"]').each(function (i) {
			if ($(this).is(':checked'))
				ids.push($(this).val());
		});
		console.log(ids);
		toggleLayers(ids);
	});
	$('#baseMap').on('change', function () {
		var val = $(this).val();
		$.each(baseMaps, function () {
			if (this.get('id') === val)
				this.setVisible(true);
			else
				this.setVisible(false);
		});
	});

	// panels next
	// Basemap/Layers Panel
	$('#pnl_layers').panel({
		display: 'overlay',
		theme: 'b',
		dismissible: false,
		beforeopen: function (evt, ui) {
			$('#btn_layers').parent().addClass('ui-btn-on');
		},
		beforeclose: function (evt, ui) {
			$('#btn_layers').parent().removeClass('ui-btn-on');
		}
	}).panel('open').panel('close');
	// Run Options Panel
	$('#pnl_run-opts').panel({
		position: 'right',
		display: 'overlay',
		theme: 'b',
		dismissible: false,
		beforeopen: function (evt, ui) {
			$('#btn_run-opts').parent().addClass('ui-btn-on');
		},
		beforeclose: function (evt, ui) {
			$('#btn_run-opts').parent().removeClass('ui-btn-on');
		}
	});

	// popups last
	// Legend Popup
	$('#pnl_legend').popup({
		theme: 'b',
		positionTo: '#btn_layers',
		transition: 'pop',
		tolerance: '50,' + $(0.5).toPx(),
		dismissible: false,
		history: false
	}).popup('open').popup('close');
	$('#pnl_legend > div.ui-header').on('click', function () {
		$('#btn_legend').trigger('click');
	});
	$('#pnl_legend-screen').remove();
	// Forecast Slider Popup
	$('#pnl_time').popup({
		theme: 'none',
		positionTo: '#foot',
		transition: 'pop',
		tolerance: '50, 15',
		dismissible: false,
		history: false
	}).popup('open').popup('close');
	$('#pnl_time-screen').remove();

	$('#createRun').on('click', function () {
		$(this).button('refresh');
		submitJob();
	});
	$('#runSelect').on('change', function () {
		$(this).selectmenu('refresh');
		removeRun();
		initRun();
	});
	$('#deleteEvent').on('click', function () {
		$(this).button('refresh');
		if (confirm('Are you sure you wish to delete this run?')) {
			deleteEvent();
		}
	});
	$('#forecastModel').on('change', function () {
		var model = $(this).val();
		var slider = $('#forecastDuration');

		switch (model) {
			case 'UCAR-NAM-CONUS-12-KM':
				slider.attr({ 'min': 3, 'max': 84, 'step': 3 }).val(3).slider('refresh');
				break;
			case 'NOMADS-HRRR-CONUS-3-KM':
				slider.attr({ 'min': 1, 'max': 15, 'step': 1 }).val(1).slider('refresh');
				break;
			case 'NOMADS-NAM-ALASKA-11.25-KM':
				slider.attr({ 'min': 3, 'max': 36, 'step': 3 }).val(3).slider('refresh');
				break;
			case 'NOMADS-NAM-CONUS-12-KM':
				slider.attr({ 'min': 1, 'max': 36, 'step': 1 }).val(1).slider('refresh');
				break;
		}
	});
	$('#loadRun').on('click', function () {
		$(this).button('disable').prop('disabled', true).button('refresh');
		$('#removeRun').button('enable').prop('disabled', false).button('refresh');
		$('#pnl_Runs').panel('close');
		$('#spinner').spin('windninja');

		var displayType = $('#displayType').val();
		loadRun(displayType);
	});
	$('#removeRun').on('click', function () {
		$(this).button('disable').button('refresh');
		$('#loadRun').button('enable').removeAttr('disabled').button('refresh');

		removeRun();
	});
	$('#getJobStatus').on('click', function () {
		$(this).button('refresh');
		getJobStatus();
	});
	$('#timeSlider').slider({
		start: function () {
			$('#spinner').spin('windninja');
		},
		stop: function () {
			ninjaRun.SetVisible(parseInt($(this).val()));
			console.info('slider::stop - ' + ninjaRun.VisibleLayer);

			var outputLayer = ninjaRun.OutputLayers[ninjaRun.VisibleLayer];
			if (outputLayer !== undefined) {
				$('#runDate').text('').text(new Date(outputLayer.get('date')).toLocaleString());
				//updateLegend();
			}

			$('#spinner').spin(false);
		}
	});
	$('#displayType').on('change', function () {
		var type = $(this).val();

		if (ninjaRun.Outputs.hasOwnProperty(type)) {
			var count = ninjaRun.Outputs[type].length;
			$('#timeSlider').attr({ 'min': 1, 'max': count }).val(1);
			$('#layerSliderStart').attr({ 'min': 1, 'max': count }).val(1);
			$('#layerSliderEnd').attr({ 'min': 1, 'max': count }).val(count);
			$('#loadRun').button('enable').prop('disabled', false).button('refresh');
			$('#layerSlider').rangeslider('enable').rangeslider('refresh');
		} else {
			$('#timeSlider').attr({ 'min': 0, 'max': 0 }).val(0);
			$('#layerSliderStart').attr({ 'min': 0, 'max': 0 }).val(0);
			$('#layerSliderEnd').attr({ 'min': 0, 'max': 0 }).val(0);
			$('#loadRun').button('diable').prop('disabled', true).button('refresh');
			$('#layerSlider').rangeslider('disable').rangeslider('refresh');
		}
	});
	$('#gotItBtn').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		$('#splash').popup('close');
	});
	$('#btn_ok').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		$('#welcome').popup('close');
	});

	// Initialize Settings Panel
	$('#userName').on('keyup', _enableRegister);
	$('#userEmail').on('keyup', _enableRegister);
	$('#vectorOutput').flipswitch({ mini: true });
	$('#rasterOutput').flipswitch({ mini: true });
	$('#topoOutput').flipswitch({ mini: true });
	$('#googlOutput').prop('disabled', true).flipswitch({ mini: true, disabled: true });
	$('#geopdfOutput').prop('disabled', true).flipswitch({ mini: true, disabled: true });
	$('#saveSettings').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		_saveConfig(true);
	});
	$('#register').button({ mini: true, disabled: true }).prop('disabled', true).on('click', function () {
		$(this).prop('disabled', true).button('disable').button('refresh');
		_registerInstall();
	});
	$('#sbmtFeedback').button({ mini: true, disabled: true }).on('click', function () {
		$(this).button('refresh');
		$('#feedback-panel').popup('open');
	});
	$('#help').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		$('#splash').popup('open');
	});
	$('#submit').on('click', function () {
		$(this).button('refresh');
		var feedback = $('#feedbackInfo').val();
		$('#feedback-panel').popup('close');
		_submitFeedback(feedback);
		$('#feedbackInfo').val('');
	});
	$('#cancel').on('click', function () {
		$(this).button('refresh');
		$('#feedback-panel').popup('close');
		$('#feedbackInfo').val('');
	});

	// Handle window resizing (rotating device)
	$(window).on('resize', setmapsize);
	setmapsize();
}
// Set map element size
function setmapsize() {
	var scrnHeight = $.mobile.getScreenHeight(); // total available screen height
	var headHeight = $('#head').outerHeight(); // outer most height of the header (title bar)
	var footHeight = $('#foot').outerHeight(); // outer most height of the footer (action buttons)
	var helpHead = $('#helpHeader').outerHeight(); // outer most height of the 'help' header
	var helpFoot = $('#helpFooter').outerHeight(); // outer most height of the 'help' footer

	// If this is iOS 7+, reduce the total height by 20px to account for the status bar that can't be hidden
	if (isIOS7) {
		scrnHeight -= 20;
	}

	// map should only be between the bottom of the header to the top of the footer
	// add one because the 'footer' is set to 'bottom: -1px', so we adjust..
	var mapHeight = scrnHeight - headHeight - footHeight + 1;
	// panels should not scroll over the header, but covering the footer is ok
	var panelHeight = scrnHeight - headHeight - ($(1.25).toPx());
	// 0.5em buffer on the top and bottom of the 'help' dialog/popup (so it still looks like a dialog box)
	var helpHeight = panelHeight - helpHead - helpFoot - ($(0.5).toPx());

	$('#map').height(mapHeight);
	$('#menuContent').height(panelHeight);
	$('#requestContent').height(panelHeight);
	$('#settingsContent').height(panelHeight);
	$('#helpContent').css({ 'max-height': helpHeight + 'px' });
}
// Generic fail method
function fail(err) {
	console.error(err.message, Error().stack);
}
// Initialize WindNinja run data
function initRun() {
	console.info('initRun()');
	var id = $('#runSelect').val();
	var name = $('#runSelect option:selected').text();
	if (guidRegex.test(id)) {
		$('#displayType').empty();
		$('#loadRun').button('disable').prop('disabled', true);
		$('#removeRun').button('disable').prop('disabled', true);
		$('#timeSlider').attr({ 'min': 0, 'max': 0, 'value': 0 });
		$('#inputWind').flipswitch('disable').prop('disabled', true).flipswitch('refresh');
		$('#layerSlider').rangeslider('disable');
		$('#layerSliderStart').attr({ 'min': 0, 'max': 0 }).val(0);
		$('#layerSliderEnd').attr({ 'min': 0, 'max': 0 }).val(0);
		$('#layerSlider').rangeslider('refresh');

		//@TODO move the run removal logic to the WinNinja object
		removeRun();
		ninjaRun = new WindNinjaRun(id, name);

		ninjaRun.InitRun().done(function () {
			$('#displayType').selectmenu('enable').prop('disabled', false);

			for (var type in this.Outputs) {
				if (this.Outputs.hasOwnProperty(type)) {
					if (type !== 'vector') {
						$('#displayType').append($('<option />')
							.val(type)
							.text(type.toTitleCase())
						);
					}
				}
			}
			type = undefined;

			$('#displayType').selectmenu('refresh');
			var displayType = 'raster';//$('#displayType').val();

			if (this.Outputs.hasOwnProperty(displayType)) {
				var count = this.Outputs[displayType].length;
				$('#loadRun').button('enable').prop('disabled', false);

				if (this.Forecasts.hasOwnProperty(displayType)) {
					$('#inputWind').flipswitch('enable').prop('disabled', false).flipswitch('refresh');
				}

				$('#layerSlider').rangeslider('enable');
				$('#layerSliderStart').attr({ 'min': 1, 'max': count }).val(1);
				$('#layerSliderEnd').attr({ 'min': 1, 'max': count }).val(count);
				$('#layerSlider').rangeslider('refresh');
			}
		});
	}
}
// Delete a WindNinja run from the device
function deleteEvent() {
	var run = $('#runSelect').val();

	dataDir.getDirectory(run, null, function (dir) {
		dir.removeRecursively(function (entry) {
			console.info('removed entry ' + entry);
			navigator.notification.alert("Deleted Run " + run, null, 'Run Deleted', 'Ok');
			_initRunList();
		}, fail);
	}, fail);
}
// Toggle overlay layer(s) visibility
function toggleLayers(IDs) {
	console.log('toggleLayers()', IDs, mapLayers);
	var len = mapLayers.length;
	for (var i = 0; i < len; i++) {
		var l = mapLayers[i];
		if (IDs && IDs.indexOf(l.get('name')) !== -1) {
			l.setVisible(true);
		} else {
			l.setVisible(false);
		}
	}
}
// Get the status of a WindNinja run
function getJobStatus() {
	var selectedJob = $('#runSelect').val();
	// check if the run has already been downloaded
	$.ajax({
		url: ninjaRun.BaseURL + '/job.json',
		dataType: 'json'
	}).done(function (job) {
		if (job.status === 'Succeeded') {
			navigator.notification.confirm('This run is finished and has already been downloaded to your device, would you like to re-download the data?', function (index) {
				if (index === 1) {
					_onDownloadReady(job, selectedJob);
				}
			}, 'WindNinja Run Status', ['Download', 'Cancel']);
		} else {
			getData(selectedJob);
		}
	});
}
// Submit a WindNinja run to the server for creation
function submitJob() {
	var name = $('#runName').val();
	if (name !== '') {
		$('#spinner').spin('windninja');
		var extent;
		try {
			extent = sketchPolyFeature.getGeometry().getExtent();
		} catch (err) {
			extent = mapView.calculateExtent(map.getSize());

			// make the extent square
			var diff = ((extent[2] - extent[0]) - (extent[3] - extent[1])) / 2;

			extent[3] -= (diff);
			extent[1] += (diff);

		}
		// If the user accidentally selects a single point, the extent will be infinite.

		if ($.inArray(Infinity, extent) !== -1) {
			extent = mapView.calculateExtent(map.getSize());

			// make the extent square
			var diff = ((extent[2] - extent[0]) - (extent[3] - extent[1])) / 2;

			extent[3] -= (diff);
			extent[1] += (diff);
		}
		var newExtent = ol.proj.transformExtent(extent, mapProj, latLonProj);

		var xmin = newExtent[0];
		var ymin = newExtent[1];
		var xmax = newExtent[2];
		var ymax = newExtent[3];

		var source = $('#forecastModel').val();
		var dur = $('#forecastDuration').val();
		var veg = $('#vegetation').val();
		var email = $('#email').prop('checked');
		var phone = $('#text').prop('checked');
		var notify = '';
		var outputs = {
			vector: false,
			raster: false,
			topo: false,
			googl: false,
			geopdf: false,
			weather: true
		};
		for (var type in config.Outputs) {
			if (outputs.hasOwnProperty(type) && config.Outputs.hasOwnProperty(type)) {
				outputs[type] = config.Outputs[type];
			}
		};

		if (email && config.Email)
			notify = config.Email;
		if (phone && config.Phone) {
			if (notify)
				notify += ',' + config.Phone;
			else
				notify = config.Phone;
		}

		var mesh = 'fine';
		var params = {
			'xmin': xmin,
			'ymin': ymin,
			'xmax': xmax,
			'ymax': ymax,
			'forecast': source,
			'parameters': 'forecast_duration:' + dur + ';vegetation:' + veg + ';mesh_choice:' + mesh,
			'name': name,
			'products': 'vector:' + true + ';raster:' + outputs.raster + ';topofire:' + outputs.topo + ';geopdf:' + outputs.geopdf + ';weather:' + outputs.weather
		};
		if (notify) {
			params['email'] = notify;
		}
		var url = serverURL + "api/jobs?" + $.param(params);

		$.ajax({
			type: 'POST',
			url: url,
			contentType: 'application/x-www-form-urlencoded'
		}).done(function (data) {
			$('#spinner').spin(false);
			$('#request-panel').panel('close');

			dataDir.getDirectory(data.id, { create: true, exclusive: false }, function (dir) {
				dir.getFile("job.json", { create: true }, function (file) {
					file.createWriter(function (fileWriter) {
						var blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
						fileWriter.write(blob);
						navigator.notification.alert("Run '" + data.name + "' has been sent to the server for computation. \n The results will be ready shortly in the Runs tab.", function () {
							_cleanSketch();
							_initRunList();
						}, 'Run Created', 'Ok');
					});
				});
			}, fail);
		}).fail(function (data) {
			$('#spinner').spin(false);
			navigator.notification.alert("Server Error: " + data.statusMessage, null, 'Error', 'Ok');
		}).always(function () {
			$('#runName').val('');
		});
	} else {
		navigator.notification.alert("You must enter a name for this run.", null, 'Error', 'Ok');
	}
}
// Get the WindNinja run status from the server
function getData(id) {
	var url = serverURL + "api/jobs/" + String(id).replace(/-/g, "");
	$.ajax({
		type: 'GET',
		url: url
	}).done(function (data) {
		if (data.status === 'Succeeded') {
			navigator.notification.confirm('Files ready to download', function (index) {
				if (index === 1) {
					_onDownloadReady(data, id);
				}
			}, 'WindNinja Overlay Download', ['Download', 'Cancel']);
		} else {
			navigator.notification.alert(data.status, null, 'Event Status', 'Ok');
		}
	}).fail(function (data) {
		navigator.notification.alert("Server Error: " + data.statusMessage, null, 'Error', 'Ok');
	});
}
// Download WindNinja run data
function _onDownloadReady(results, id) {
	console.log(results);
	var downloadSize = results.output.products.length || 0
	, doneOutputs = 0
	, files = 0
	, done = 0
	, outputs = [];
	$('#loader').popup('open', { positionTo: 'window', transition: 'pop' });
	$('#totalLabel').text('Outputs: 0/' + downloadSize);
	$('#productLabel').text('Files: 0/..');
	$('#totalprogress').progressbar({ value: 0, max: downloadSize });
	$('#productProgress').progressbar({ value: 0 });

	// Create job file and initialize run.
	dataDir.getDirectory(id, { create: true, exclusive: false }, function (dir) {
		dir.getFile("job.json", { create: true, exclusive: false }, function (file) {
			console.log("created job.json", file);
			file.createWriter(function (fileWriter) {
				var blob = new Blob([JSON.stringify(results)], { type: 'application/json' });
				fileWriter.write(blob);

				$.each(results.output.products, function (i, p) {
					files += p.files.length;
					$('#productLabel').text('Files: ' + done + '/' + files);
					$('#productProgress').progressbar({ max: files });
					var def = $.Deferred();
					outputs.push(def.promise());
					downloadProduct(id, p).progress(function () {
						done++;
						$('#productLabel').text('Files: ' + done + '/' + files);
						$('#productProgress').progressbar({ value: done });
					}).done(function () {
						doneOutputs++;
						$('#totalLabel').text('Outputs: ' + doneOutputs + '/' + downloadSize);
						$('#totalprogress').progressbar({ value: doneOutputs });
						def.resolve();
					});
				});

				$.when.apply($, outputs).done(function () {
					$('#loader').popup('close');
					initRun();
				});
			});
		});
	}, fail);
}
// Download a specific Product (Vectors, Rasters, etc.) and place it in the appropriate location
function downloadProduct(id, product) {
	var deferred = $.Deferred()
	, URL = product.baseUrl
	, DIR = dataDir.nativeURL + id;

	// There is a package for this product, download it instead of each individual file (or folder)
	if (product.package !== '') {
		var fileTransfer = new FileTransfer();

		fileTransfer.download(URL + '/' + product.package, DIR + '/' + product.package, function (entry) {
			if (product.type === 'basemap') {
				var name = product.name.split(' Basemap')[0];
				zip.unzip(DIR + '/' + product.package, cacheDir.nativeURL + name + '/', function (s) {
					if (s === 0) {
						console.log('Basemap package extracted successfully to /' + name)
					} else {
						console.log('Failed to extract basemap package.');
					}

					deferred.resolve();
				});
			} else if (product.type === 'raster') {
				zip.unzip(DIR + '/' + product.package, DIR + '/tiles/', function (s) {
					if (s === 0) {
						console.log('Raster package: ' + product.package + ' extracted successfully to ' + DIR + '/tiles/')
					} else {
						console.log('Failed to extract raster package ' + product.package);
					}

					deferred.resolve();
				});
			}
		});
	} else { // Download the individual file(s)
		var defs = [];

		$.each(product.files, function (i, f) {
			var def = $.Deferred()
			, fileTransfer = new FileTransfer();
			defs.push(def.promise());
			fileTransfer.download(URL + '/' + f, DIR + '/' + f, function (entry) {
				console.log(entry.name + ' downloaded.');
				deferred.notify();
				def.resolve();
			});
		});

		$.when.apply($, defs).done(function () {
			deferred.resolve();
		});
	}

	return deferred.promise();
}
// Load a WindNinja run (create layers)
function loadRun(displayType) {
	$('#spinner').spin('windninja');
	var min = parseInt($('#layerSliderStart').val());
	var max = parseInt($('#layerSliderEnd').val());

	ninjaRun.RemoveRun();
	ninjaRun.OutputLayers = [];
	ninjaRun.ForecastLayers = [];

	mapView.fit(ninjaRun.Extent, map.getSize());
	map.renderSync();

	ninjaRun.LoadRun(min, max, displayType).done(function () {
		console.log('ninjaRun.loadRun() :: done, updating UI');
		$.each([this.OutputLayers, this.ForecastLayers], function (i, g) {
			$.each(g, function (j, layer) {
				if (layer) {
					map.addLayer(layer);
				}
			});
		});

		$('#spinner').spin(false);
		$('#tbl_Date').show();

		var count = this.OutputLayers.length;
		$('#timeSlider').attr({ 'min': 0, 'max': count - 1 }).val(0).slider('refresh');
		$('#runDate').text(new Date(this.OutputLayers[this.VisibleLayer].get('date')).toLocaleString());
		$('#btn_run-opts').button('enable');
		updateLegend();
		navigator.vibrate(200);
	});
}
// Remove a WindNinja run from the map
function removeRun() {
	var loaded = ninjaRun && ninjaRun.Loaded();

	$('#tbl_Date').hide();
	$('#removeRun').button('disable').button('refresh');
	if (loaded) {
		ninjaRun.RemoveRun();
		navigator.notification.alert("All layers have been removed", null, 'Layers Removed', 'Ok');
		$('#btn_run-opts').button('disable');
	}
}
// Zoom to the extents of a WindNinja run
function zoomToRun() {
	if (ninjaRun && ninjaRun.Extent) {
		mapView.fit(ninjaRun.Extent, map.getSize());
	}
}
// Update map legend with current layer's speeds
function updateLegend() {
	$('#spd_0').text('0.00 - ' + ninjaRun.RunSpeeds[0] + ' mph');
	$('#spd_1').text(ninjaRun.RunSpeeds[0] + ' - ' + ninjaRun.RunSpeeds[1] + ' mph');
	$('#spd_2').text(ninjaRun.RunSpeeds[1] + ' - ' + ninjaRun.RunSpeeds[2] + ' mph');
	$('#spd_3').text(ninjaRun.RunSpeeds[2] + ' - ' + ninjaRun.RunSpeeds[3] + ' mph');
	$('#spd_4').text(ninjaRun.RunSpeeds[3] + ' - ' + ninjaRun.RunSpeeds[4] + '+ mph');
}
// Start GPS watch
function _onGPSOn() {
	console.log("finding position....");
	navigator.geolocation.getCurrentPosition(function (pos) {
		$('#btn_GPS').removeClass('off').addClass('on');
		$.each(gpsSource.getFeatures(), function () {
			gpsSource.removeFeature(this);
		});

		var point = new ol.geom.Point(ol.proj.transform([pos.coords.longitude, pos.coords.latitude], latLonProj, mapProj));

		gpsSource.addFeature(new ol.Feature(point));
		map.addLayer(gpsLayer);

		//Zoom to our location
		mapView.setCenter(point.getCoordinates());
		//mapView.setZoom(10);
	}, fail, { enableHighAccuracy: true });
}
// Stop GPS watch
function _onGPSOff() {
	$('#btn_GPS').removeClass('on').addClass('off');
	map.removeLayer(gpsLayer);
}

//
// WindNinja Functions/classes
//
function WindNinjaRun(id, name) {
	var _isLoaded = false;
	this.InitRun = function () {
		console.log('InitRun()');
		var fileParts
		, min
		, hour
		, file
		, date;

		// AJAX load job file
		return $.ajax({
			url: this.BaseURL + '/job.json',
			dataType: 'json',
			context: this
		}).done(function (job) {
			// Output Products
			for (var i = 0; i < job.output.products.length; i++) {
				var product = job.output.products[i]
				, isOutput;

				if (product.type === 'basemap')
					continue;

				if (product.name.toLowerCase().indexOf('weather') !== -1)
					isOutput = false;
				else if (product.name.toLowerCase().indexOf('windninja') !== -1)
					isOutput = true;
				else
					continue;

				// Product Files
				var len = product.files.length;
				for (var j = 0; j < len; j++) {
					var f = product.files[j];
					if (isOutput)
						fileParts = f.split('.')[0].split(oRegex);
					else
						fileParts = f.split('.')[0].split(fRegex);

					min = fileParts[3].slice(-2);
					hour = fileParts[3].slice(-4, -2);
					date = fileParts[2] + ' ' + hour + ':' + min;
					file = new this.resultFile(f, date);
					file.Type = product.type;

					if (!this.Outputs[file.Type])
						this.Outputs[file.Type] = [];
					if (!this.Forecasts[file.Type])
						this.Forecasts[file.Type] = [];

					if (product.data)
						file.Data = product.data[j];

					if (isOutput)
						this.Outputs[file.Type].push(file);
					else
						this.Forecasts[file.Type].push(file);
				}
			}
			this.__sortFiles();

			// Domain
			var extent = [
				job.input.domain.xmin
				, job.input.domain.ymin
				, job.input.domain.xmax
				, job.input.domain.ymax
			];
			this.Extent = ol.proj.transformExtent(extent, latLonProj, mapProj);
		}).fail(function (err) {
			this.__fail(new Error(err).stack);
		});
	};
	this.LoadRun = function (min, max, displayType) {
		console.group('Loading WindNinja run.');
		console.time('Run load time');
		console.info('LoadRun(' + min + ', ' + max + ', ' + displayType + ')');
		this.__resetLayers();
		var deferred = $.Deferred()
		, self = this
		, count = (max - min) + 1;
		// subtract 1 from min and max to adjust from 'real' numbers to array indicies
		min--;
		max--;

		//always create vector forecast layers
		var fLayers = this.__loadForecastLayers(min, max, 'vector');
		var oLayers = this.__loadOutputLayers(min, max, displayType);

		fLayers.progress(function (i) {
			console.info('WindNinjaRun.LoadRun() :: Done creating Forecast Layer (' + i + '/' + count + ')');
		});
		oLayers.progress(function (i) {
			console.info('WindNinjaRun.LoadRun() :: Done creating Output layer (' + i + '/' + count + ')');
		});

		$.when(oLayers, fLayers).done(function () {
			self.__sortlayers();
			self.__setVisibleLayer(self.VisibleLayer);

			console.timeEnd('Run load time');
			self._isLoaded = true;
			deferred.resolveWith(self);
		}).fail(function () {
			self.__fail(new Error('WindNinjaRun.LoadRun() :: Error').stack);
		}).always(function () {
			console.groupEnd();
		});

		return deferred.promise();
	};
	this.RemoveRun = function () {
		$.each([this.OutputLayers, this.ForecastLayers], function () {
			$.each(this, function (i, l) {
				map.removeLayer(l);
			});
		});
		this._isLoaded = false;
	};
	this.SetVisible = function (index) {
		this.__setVisibleLayer(index);
	};
	this.Loaded = function () { return this._isLoaded; };

	this.__init(id, name);
	return this;
}

WindNinjaRun.prototype = {
	__verbose: true
	, __clusterDistance: 12
	, __dir: ''

	, __init: function (id, name) {
		if (this.__verbose)
			console.log('__init()');

		this.BaseURL = this.__dir + id + '/';
		this.ID = id;
		this.Name = name;
		this.LoadForecasts = false;
		this.ForecastLayers = [];
		this.OutputLayers = [];
		this.Forecasts = {};
		this.Outputs = {};
		this.VisibleLayer = 0;
		this.RunSpeeds = [];
		this.MaxSpeed = 0.00;
		this.Extent = null;
	}
	, __resetLayers: function () {
		this.ForecastLayers.length = 0;
		this.OutputLayers.length = 0;
		this.VisibleLayer = 0;
		this.RunSpeeds.length = 0;
		this.MaxSpeed = 0.00;
	}
	, __fail: function (err) {
		console.error('__fail :: ', err.stack);
	}
	, __sortFiles: function () {
		for (var type in this.Outputs) {
			if (this.Outputs.hasOwnProperty(type)) {
				this.Outputs[type].sort(this.resultFileSort);

				if (this.Forecasts.hasOwnProperty(type))
					this.Forecasts[type].sort(this.resultFileSort);
			}
		}
	}
	, __sortlayers: function () {
		this.OutputLayers.sort(this.layerSort);
		this.ForecastLayers.sort(this.layerSort);
	}
	, __loadForecastLayers: function (min, max, displayType) {
		if (this.__verbose) {
			console.log('__loadForecastLayers()');
			console.time('load forecast layers');
		}

		var deferred = $.Deferred()
		, self = this
		, defs = []
		, items = 0
		, fileList
		, dataType;

		if (this.Forecasts.hasOwnProperty(displayType)) {
			fileList = this.Forecasts[displayType];

			switch (displayType) {
				case 'vector':
					dataType = 'json';
					break;
				case 'raster':
					dataType = 'dir';
					break;
				case 'google':
					dataType = 'xml';
					break;
			}

			if (this.__verbose)
				console.info('creating ' + displayType + ' forecast layers');

			for (var i = 0; i < fileList.length; i++) {
				if (min <= i && i <= max) {
					var file = fileList[i];
					if (dataType !== 'dir') {
						defs.push($.ajax({
							url: this.BaseURL + file.Name,
							dataType: dataType,
							context: file
						}).done(function (data) {
							self.__makeLayer('weather', data, this.Date).done(function (layer) {
								self.ForecastLayers.push(layer);
								items++;
								deferred.notifyWith(self, [items]);
							});
						}));
					} else {
						var def = $.Deferred();
						defs.push(def.promise());
						this.__makeLayer(displayType, file.Data + ':true', file.Date).done(function (layer) {
							this.ForecastLayers.push(layer);
							items++;
							deferred.notifyWith(this, [items]);
							def.resolveWith(this);
						});
					}
				}
			}

			$.when.apply($, defs).done(function () {
				if (self.__verbose)
					console.timeEnd('load forecast layers');
				self.ForecastLayers.sort(self.layerSort);
				deferred.resolveWith(self);
			});
		}

		return deferred.promise();
	}
	, __loadOutputLayers: function (min, max, displayType) {
		if (this.__verbose) {
			console.log('__loadOutputLayers()');
			console.time('load output layers');
		}

		var deferred = $.Deferred()
		, self = this
		, defs = []
		, items = 0
		, fileList
		, dataType

		if (this.Outputs.hasOwnProperty(displayType)) {
			fileList = this.Outputs[displayType];

			switch (displayType) {
				case 'vector':
					dataType = 'json';
					break;
				case 'raster':
					dataType = 'dir';
					break;
				case 'google':
					dataType = 'xml';
					break;
			}

			if (this.__verbose)
				console.info('creating ' + displayType + ' output layers');
			for (var i = 0; i < fileList.length; i++) {
				if (min <= i && i <= max) {
					var file = fileList[i];
					if (dataType !== 'dir') {
						defs.push($.ajax({
							url: this.BaseURL + file.Name,
							dataType: dataType,
							context: file
						}).done(function (data) {
							self.__makeLayer(displayType, data, this.Date).done(function (layer) {
								if (items === self.VisibleLayer) {
									self.RunSpeeds = layer.get('speeds');
								}
								self.OutputLayers.push(layer);
								items++;
								deferred.notifyWith(self, [items]);
							});
						}));
					} else {
						var def = $.Deferred();
						defs.push(def.promise());
						this.__makeLayer(displayType, file.Data + ':false', file.Date).done(function (layer) {
							this.OutputLayers.push(layer);
							items++;
							deferred.notifyWith(this, [items]);
							def.resolveWith(this);
						});
					}
				}
			};

			$.when.apply($, defs).done(function () {
				if (self.__verbose)
					console.timeEnd('load output layers');
				self.OutputLayers.sort(self.layerSort);
				self.RunSpeeds = self.__getSpdRanges(self.MaxSpeed);
				deferred.resolveWith(self);
			});
		}

		return deferred.promise();
	}
	, __makeLayer: function (type, data, date) {
		if (this.__verbose) {
			console.group('__makeLayer()');
			console.time('total');
		}
		var deferred = $.Deferred();

		var __KMLLayer = $.proxy(function () {
			if (this.__verbose) {
				console.groupCollapsed('KML');
				console.time('creating source');
			}

			var source = new ol.source.KML({
				doc: data,
				projection: mapProj
			});

			if (this.__verbose) {
				console.timeEnd('creating source');
				console.time('creating layer');
			}

			var layer = new ol.layer.Vector({
				source: source,
				visible: false
			});

			layer.set('type', 'KML');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);
		var __RasterLayer = $.proxy(function () {
			var ranges = []
			, name = data.split(':')[0]
			, speed = parseFloat(data.split(':')[1])
			, isForecast = (data.split(':')[2] === 'true');

			if (this.__verbose) {
				console.groupCollapsed('Raster');
			}

			this.MaxSpeed = (speed > this.MaxSpeed) ? speed : this.MaxSpeed;

			if (this.__verbose) {
				console.time('creating source');
			}

			var source = new ol.source.XYZ({
				maxZoom: 16,
				url: this.BaseURL + 'tiles/' + name + '/{z}/{x}/{y}.png'
			});

			if (this.__verbose) {
				console.timeEnd('creating source');
				console.time('creating layer');
			}

			var layer = new ol.layer.Tile({
				source: source,
				visible: false
			});

			layer.set('type', 'Raster');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);
		var __ImageVectorLayer = $.proxy(function () {
			var size = data.features.length;
			var newSize = 0;
			var self = this;

			if (this.__verbose) {
				console.groupCollapsed('ImageVector');
				console.time('max speed calculation');
			}

			data.features = $.grep(data.features, function (feat, i) {
				if (feat.properties.speed <= 0.00) {
					return false;
				}

				var speed = feat.properties.speed;
				self.MaxSpeed = (speed > self.MaxSpeed) ? speed : self.MaxSpeed;
				return true;
			});

			if (this.__verbose) {
				console.timeEnd('max speed calculation');
				console.time('creating source');
			}

			var vectorSource = new ol.source.Vector({
				features: (new ol.format.GeoJSON()).readFeatures(data)
			});

			if (this.__verbose) {
				console.timeEnd('creating source');
				console.time('creating layer');
			}

			var source = new ol.source.ImageVector({
				source: vectorSource,
				style: $.proxy(this.__vectorStyle, this)
			});

			var layer = new ol.layer.Image({
				source: source,
				visible: false
			});

			layer.set('type', 'ImageVector');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);
		var __ClusterImageVectorLayer = $.proxy(function () {
			var size = data.features.length;
			var newSize = 0;
			var self = this;

			if (this.__verbose) {
				console.groupCollapsed('ClusterImageVector');
				console.time('max speed calculation');
			}

			data.features = $.grep(data.features, function (feat, i) {
				if (feat.properties.speed < 0) {
					return false;
				}

				var speed = feat.properties.speed;
				self.MaxSpeed = (speed > self.MaxSpeed) ? speed : self.MaxSpeed;
				return true;
			});

			if (this.__verbose) {
				console.timeEnd('max speed calculation');
				console.time('creating source');
			}

			var clusterSource = new ol.source.Cluster({
				source: new ol.source.Vector({
					features: (new ol.format.GeoJSON()).readFeatures(data)
				}),
				distance: this.__clusterDistance
			});

			if (this.__verbose) {
				console.timeEnd('creating source');
				console.time('creating layer');
			}

			var source = new ol.source.ImageVector({
				source: clusterSource,
				style: $.proxy(this.__clusterVectorStyle, this)
			});

			var layer = new ol.layer.Image({
				source: source,
				visible: false
			});

			layer.set('type', 'ClusterImageVector');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);

		switch (type) {
			case 'vector':
				__ClusterImageVectorLayer();
				break;
			case 'weather':
				__ImageVectorLayer();
				break;
			case 'google':
				__KMLLayer();
				break;
			case 'raster':
				__RasterLayer();
				break;
		}

		console.groupEnd();
		return deferred.promise();
	}
	, __setVisibleLayer: function (index) {
		this.VisibleLayer = index || 0;
		if (this.__verbose)
			console.info('setting visible layer to index: ' + this.VisibleLayer);

		for (var i = 0; i < this.OutputLayers.length; i++) {
			var layer = this.OutputLayers[i];
			var forecast = this.ForecastLayers[i];

			if (layer) {
				if (i === index)
					layer.setVisible(true);
				else
					layer.setVisible(false);
			}
			if (forecast) {
				if (i === index && this.LoadForecasts)
					forecast.setVisible(true);
				else
					forecast.setVisible(false);
			}
		}
	}
	, __makeVectorArrow: function (feat, angle, scale) {
		var dist = scale;

		var __createArrowShaft = function (pt, angle) {
			var points = [];
			var x = pt.getCoordinates()[0];
			var y = pt.getCoordinates()[1];
			var x1 = x + (dist * Math.cos(angle));
			var y1 = y - (dist * Math.sin(angle));

			var __createPoint = function (pt, angle, num) {
				var brng = (num == 3) ? (angle + (135).toRad()) : (num == 4) ? (angle - (135).toRad()) : null;
				var len = dist / 3;
				var x = pt[0];
				var y = pt[1];
				try {
					var x1 = x + (Math.cos(brng) * len);
					var y1 = y - (Math.sin(brng) * len);
					return [x1, y1];
				} catch (err) {
					return [0, 0];
				}
			};

			points[0] = [x, y];
			points[1] = [x1, y1];
			points[2] = __createPoint([x1, y1], angle, 3);
			points[3] = [x1, y1];
			points[4] = __createPoint([x1, y1], angle, 4);
			var arrow = new ol.geom.LineString(points);

			return arrow;
		};

		return __createArrowShaft(feat.getGeometry(), angle);
	}
	, __getArrowColor: function (speed) {
		var color;
		var __isInRange = function (x, min, max) {
			return min <= x && x <= max;
		};

		switch (true) {
			case __isInRange(speed, 0, this.RunSpeeds[0]):
				color = '#0000FF';
				break;
			case __isInRange(speed, this.RunSpeeds[0], this.RunSpeeds[1]):
				color = '#00FF00';
				break;
			case __isInRange(speed, this.RunSpeeds[1], this.RunSpeeds[2]):
				color = '#FFFF00';
				break;
			case __isInRange(speed, this.RunSpeeds[2], this.RunSpeeds[3]):
				color = '#FFA500';
				break;
			case __isInRange(speed, this.RunSpeeds[3], this.RunSpeeds[4] + 100):
				color = '#FF0000';
				break;
		}
		return color;
	}
	, __vectorStyle: function (feat, res) {
		var angle = feat.get('AM_dir').toRad();
		var scale = res * ((clusterDistance * 2) * 0.75);
		var arrow = this.__makeVectorArrow(feat, angle, scale);
		var color = this.__getArrowColor(feat.get('speed'));

		return [new ol.style.Style({
			geometry: arrow,
			stroke: new ol.style.Stroke({
				color: color,
				width: 2
			}),
			fill: new ol.style.Fill({
				color: color
			})
		})];
	}
	, __clusterVectorStyle: function (feat, res) {
		var feature = feat.get('features')[0];
		var angle = feature.get('AM_dir').toRad();
		var scale = res * (clusterDistance * 0.75);
		var arrow = this.__makeVectorArrow(feat, angle, scale);
		var color = this.__getArrowColor(feature.get('speed'));

		return [new ol.style.Style({
			geometry: arrow,
			stroke: new ol.style.Stroke({
				color: color,
				width: 2
			}),
			fill: new ol.style.Fill({
				color: color
			})
		})];
	}
	, __getSpdRanges: function (max) {
		var ranges = [5];
		var interval = parseFloat((max / 5).toFixed(2));
		ranges[0] = interval;
		ranges[1] = parseFloat((ranges[0] + interval).toFixed(2));
		ranges[2] = parseFloat((ranges[1] + interval).toFixed(2));
		ranges[3] = parseFloat((ranges[2] + interval).toFixed(2));
		ranges[4] = parseFloat((max + 0.1).toFixed(2));

		return ranges;
	}

	, resultFile: function (name, date) {
		this.Name = name;
		this.Type = '';
		this.Date = date;
		this.Data = '';

		return this;
	}
	, resultFileSort: function (a, b) {
		return new Date(a.Date).getTime() - new Date(b.Date).getTime();
	}
	, layerSort: function (a, b) {
		return new Date(a.get('date')).getTime() - new Date(b.get('date')).getTime();
	}
}