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
	, wgs84Sphere = new ol.Sphere(6378137)
	, baseMaps = []
	, mapLayers = []
	, runList = []
	, ninjaRun
	, startPixel
	, holdPromise
	, connection
	, downloading = false
	, legendOpen = false
	, legendWasOpen = false
	, sliderOpen = false
	, sliderWasOpen = false
	, curIndex = 0
	, playTimeout
	, dataDir
	, cacheDir
	, serverURL = 'http://windninja2.wfmrda.com/'
	, serverTZ = 'America/Denver'
	, eRegex = /[-a-z0-9~!$%^&*_=+}{\'?]+(\.[-a-z0-9~!$%^&*_=+}{\'?]+)*@([a-z0-9_][-a-z0-9_]*(\.[-a-z0-9_]+)*\.(aero|arpa|biz|com|coop|edu|gov|info|int|mil|museum|name|net|org|pro|travel|mobi|[a-z][a-z])|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))(:[0-9]{1,5})?/
	, oRegex = /(dem_(\d{2}-\d{2}-\d{4})_(\d{4})_\d{1,3}[a-z]{1})/
	, fRegex = /((?:(?:UCAR|NOMADS)-(?:NAM|HRRR)-(?:CONUS|ALASKA)-(?:\d{1,4}-KM|DEG))-(\d{2}-\d{2}-\d{4})_(\d{4}))/
	, dRegex = /(domain)/
	, rRegex = /(relief)/
	, rasRegex = /(tiles)/
	, guidRegex = /[\da-zA-Z]{8}-([\da-zA-Z]{4}-){3}[\da-zA-Z]{12}/
	, demoJob = {
		"status": "new",
		"output": {},
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
			"parameters": "forecast_duration:12;vegetation:trees",
			"products": "vector:true;raster:false;topofire:true;geopdf:false;clustered:true;weather:true",
			"forecast": "NOMADS-NAM-CONUS-12-KM"
		}
	}
	, version = '1.1.0';

// Device listeners
$(document).on('deviceready', _onDeviceReady);
$(document).on('offline', _onOffilne);
$(document).on('online', _onOnline);
$(document).on('pause', _onSuspend);
$(document).on('resume', _onResume);
$(document).on('backbutton', _onBack);

// Cordova Device ready
function _onDeviceReady() {
	window.open = cordova.InAppBrowser.open;
	// Initialize UI
	$(document).ready(initUI);
	// Fix for iOS 7 and the status bar overlaying the web view
	if (device.platform === 'iOS' && parseFloat(device.version) >= 7) {
		isIOS7 = true;
		StatusBar.overlaysWebView(false);
		StatusBar.styleDefault();
		StatusBar.backgroundColorByName('lightGray');

		// Reset our map size to account for the status bar
		setmapsize();
	}

	// Initialize cache directory (offline map tiles), and initialize our map
	window.resolveLocalFileSystemURL(cordova.file.cacheDirectory, function (directoryEntry) {
		directoryEntry.getDirectory('tilesCache', { create: true, exclusive: false }, function (dir) {
			if (_DEBUG) {
				console.info('tiles cache directory created/set.');
			}
			cacheDir = dir;
			_initMap();
		}, fail);
	}, fail);

	// Initialize data directory (where run data is stored), and load any existing runs
	window.resolveLocalFileSystemURL(cordova.file.dataDirectory, function (directoryEntry) {
		configDir = directoryEntry;

		_loadConfig().always(function () {
			if (_DEBUG) {
				console.info('config loaded, initializing run data directory');
			}
			directoryEntry.getDirectory('runs', { create: true, exclusive: false }, function (dir) {
				if (_DEBUG) {
					console.info('run data directory created/set.');
				}
				dataDir = dir;
				WindNinjaRun.prototype.__dir = dataDir.toURL();
				// is a demo run included?
				if (_includeDemo) {
					if (_DEBUG) {
						console.info('including demo run');
					}
					// Initialize demo run
					dataDir.getDirectory(demoJob.id, { create: true, exclusive: false }, function (testDir) {
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

				// Make sure the splash screen is hidden after 10 seconds
				setTimeout(function () {
					navigator.splashscreen.hide();
					setmapsize();
					//_initRunList();
				}, 8000);
			}, fail);
		});
	}, fail);
}
// Loss of network connection
function _onOffilne() {
	connection = false;
	$('#createRun').button('disable').prop({ 'disabled': true });
	$('[data-online="true"]').each(function () { $(this).prop({ 'disabled': true }); });
	//navigator.notification.alert('Network Connection lost', null, 'Network Status', 'OK');
}
// Reacquire network connection
function _onOnline() {
	connection = true;
	$('#createRun').button('enable').prop('disabled', false);
	$('[data-online="true"]').each(function () { $(this).prop('disabled', false); });
}
// Phone in 'sleep mode'
function _onSuspend() {
	if (_DEBUG) {
		console.log('_onSuspend()');
	}
	_saveConfig(false);
	_onOffilne();
}
// Phone wakes from 'sleep mode'
function _onResume() {
	if (_DEBUG) {
		console.log('_onResume()');
	}
	if (navigator.connection.type !== Connection.NONE) {
		_onOnline();
	}

	if ($('#loader-popup').hasClass('ui-popup-active') && !downloading) {
		$('#loader').popup('close');
	}

	$('#spinner').spin(false);
	map.renderSync();
}
// Load config file
function _loadConfig() {
	return $.ajax({
		url: configDir.toURL() + 'config.json',
		dataType: 'json',
		method: 'GET',
		cache: false
	}).done(function (configData) {
		if (_DEBUG) {
			console.info('config loaded successfully');
		}
		config = configData;
		if (!config.DisplayTZ) {
			config.DisplayTZ = "Etc/GMT";
		}
	}).fail(function () {
		if (_DEBUG) {
			console.info('config not found or corrupt, setting defaults');
		}
		config = {
			"Name": "",
			"Email": "",
			"Phone": "",
			"Outputs": {
				"vector": true,
				"raster": false,
				"topo": false,
				"googl": false,
				"geopdf": false,
				"clustered": true,
				"weather": true
			},
			"Device": device.model,
			"Platform": device.platform,
			"Version": device.version,
			"DeviceId": device.uuid,
			"DisplayTZ": "Etc/GMT",
			"Registration": {
				"isRegistered": false,
				"RegistrationId": undefined,
				"Status": undefined
			}
		};
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
		if (config.Phone && config.Phone.indexOf('@') === 10) {
			$('#text').prop('disabled', false).flipswitch('enable');
		} else {
			$('#text').prop({ 'checked': false, 'disabled': true }).flipswitch('disable').flipswitch('refresh');
		}

		_checkRegistration();
	});
}
// Save config file
function _saveConfig(alert) {
	// Save UI elements to the config object
	config.Name = $('#userName').val();
	config.Email = $('#userEmail').val();
	config.Phone = $('#userPhone').val().replace(/\D/g, '') + '@' + $('#provider').val();

	// If there's no values, try setting from the registration information
	if (!config.Name)
		config.Name = $('#registrationName').val();
	if (!config.Email)
		config.Email = config.Registration.RegistrationId;

	config.DisplayTZ = 'Etc/GMT';


	config.Outputs = {
		"vector": $('#vectorOutput').prop('checked'),
		"raster": $('#rasterOutput').prop('checked'),
		"topo": $('#topoOutput').prop('checked'),
		"googl": $('#googlOutput').prop('checked'),
		"geopdf": $('#geopdfOutput').prop('checked'),
		"clustered": true,
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
	if (config.Phone.indexOf('@') === 10) {
		$('#text').prop('disabled', false).flipswitch('enable');
	} else {
		$('#text').prop({ 'checked': false, 'disabled': true }).flipswitch('disable').flipswitch('refresh');
		config.Phone = '';
	}

	if (_DEBUG) {
		console.info(config);
	}
	var blob = new Blob([JSON.stringify(config)], { type: 'application/json' });

	configDir.getFile('config.json', { create: true, exclusive: false }, function (file) {
		file.createWriter(function (fileWriter) {
			fileWriter.write(blob);
			if (alert)
				navigator.notification.alert('Settings Saved.', null, 'Settings');
		}, fail);
	});
}
// Check if the 'Register' button should be enabled
function _checkRegistration() {
	if (config.Registration.isRegistered) {
		$('#register').remove();
		$('#sbmtFeedback').prop('disabled', false).button('enable').button('refresh');

		var url = serverURL + 'api/account/' + config.Registration.RegistrationId;
		// Registered, check status
		$.ajax({
			url: url,
			cache: false
		}).done(function (data) {
			config.Registration.Status = data.status;
		}).fail(function (data) {
			navigator.notification.alert('There was an error checking your account status. Please verify network connectivity. ' + data.status + ' :: ' + data.state(), null, 'Account Status');
		}).always(function () {
			switch (config.Registration.Status) {
				case 'accepted':
					_registrationAccepted();
					break;
				case 'pending':
					_registrationPending();
					break;
				case 'disabled':
					_registrationDisabled();
					break;
			}
		});
	} else {
		// Not registered, show registration page
		_showRegistrationPage();
	}

	_getMessages();
}
// display the registration page
function _showRegistrationPage() {
	$("#registration").popup('open');
	setmapsize();
}
// hide the registration page
function _hideRegistrationPage() {
	$("#registration").popup('close');
}
// User is fully registered
function _registrationAccepted() {
	// Allow the draw button to work properly
	$('#btn_draw').unbind('click');
	$('#btn_draw').on('click', function () {
		if (sliderOpen) {
			//close slider
			$('#btn_time').trigger('click');
		} else if (legendOpen) {
			//close legend
			$('#btn_legend').trigger('click');
		}

		$('#draw').hide();
		$('#sketch').show();
		_removeSketch();
		_cleanSketch();
		map.addLayer(sketchLayer);
		map.addInteraction(sketch);
	});
}
// User's registration is pending
function _registrationPending() {
	$('#btn_draw').unbind('click');
	$('#btn_draw').on('click', _showPendingRegistration);
}
// User's registration is disabled
function _registrationDisabled() {
	$('#btn_draw').unbind('click');
	$('#btn_draw').on('click', _showDisabledRegistration);
	$('#sbmtFeedback').prop('disabled', true).button('disable').button('refresh');
}
// Show the Registration Pending notification
function _showPendingRegistration() {
	navigator.notification.alert('Your registration is pending approval. You will not be able to create/submit any new runs until your account is verified.', null, 'Registration', 'OK');
}
// Show Disabled Account notification
function _showDisabledRegistration() {
	navigator.notification.alert('Your account has been disabled. You will not be able to create/submit runs, but will still be able to display any runs already created.', null, 'Registration', 'OK');
}
// Register device for support and feedback
function _registerInstall() {
	var registration = {
		"name": $('#registrationName').val(),
		"email": $("#registrationEmail").val(),
		"model": config.Device,
		"platform": config.Platform,
		"version": config.Version,
		"deviceId": config.DeviceId
	};

	if (registration.email !== '' && registration.name !== '') {
		$.ajax({
			url: serverURL + 'services/registration/register',
			method: 'POST',
			contentType: 'application/json',
			dataType: 'json',
			data: JSON.stringify(registration)
		}).done(function (data) {
			if (_DEBUG) {
				console.log(data);
			}
			config.Registration.RegistrationId = data.account;
			config.Registration.isRegistered = true;
			config.Registration.Status = data.status;
			if ($('#userEmail').val() === '') {
				$('#userEmail').val(data.account);
			}
			if ($('#userName').val() === '') {
				$('#userName').val($('#registrationName').val());
			}
			_saveConfig(false);
			navigator.notification.alert(data.message, null, 'Registration Complete');
			//$('#pnl_Settings').panel('open');
			$('#qStart').popup('open');
		}).fail(function (data) {
			if (_DEBUG) {
				console.log(data);
			}
			config.Registration.isRegistered = false;
			_saveConfig(false);
			navigator.notification.alert('Error attempting to register WindNinja Mobile. Please try again shortly.');
		}).always(_checkRegistration);
	}
}

function _getMessages() {
	$.ajax({
		url: serverURL + 'api/notification',
		method: 'GET',
		ContentType: 'application/json'
	}).done(function (data) {
		console.log(data);
		_displayMessages(data);
	})
}

function _displayMessages(msgList) {
	$('#messageContent').empty();
	var list = $('<ul />');
	$.each(msgList, function (i, m) {
		console.log("i: " + i + ' :: m: ' + m);
		list.append($('<li />').html(m.message));
	});

	$('#messageContent').append(list);
	if (msgList.length > 0) {
		$('#messages').popup('open');
	}
}
// Submit feedback
function _submitFeedback(feedback) {
	var data = {
		'account': config.Registration.RegistrationId,
		'comments': feedback
	};
	$.ajax({
		url: serverURL + 'api/feedback',
		method: 'POST',
		contentType: 'application/json',
		dataType: 'json',
		data: JSON.stringify(data)
	}).done(function (data) {
		navigator.notification.alert('Thanks, your feedback has been submitted.', null, 'Feedback');
	}).fail(function () {
		navigator.notification.alert('Error submitting feedback. Please verify internet connectivity and try again shortly.');
	});
}
// Initialize map objects
function _initMap() {
	if (_DEBUG) {
		console.info('cache directory initialized, creating and configuring map objects.');
	}
	// Set map projections
	mapProj = ol.proj.get('EPSG:3857'); // Web-Mercator
	latLonProj = ol.proj.get('EPSG:4326'); // Lat/Lon
	var center = ol.proj.transform([-98.579404, 39.828127], latLonProj, mapProj);
	baseMaps = [];

	//get the GeoMAC layer ids
	var geomacIDs = '';
	var parser = new ol.format.WMSCapabilities();
	$.ajax({
		url: 'https://wildfire.cr.usgs.gov/arcgis/services/geomac_dyn/MapServer/WMSServer?service=wms&request=GetCapabilities',
		type: 'GET',
		dataType: 'xml'
	}).done(function (data) {
		var c = parser.read(data);
		$.each(c.Capability.Layer.Layer, function (i, l) {
			if (l.Title.toLowerCase() === 'current fire perimeters' || l.Title.toLowerCase() === 'current fires') {
				geomacIDs += l.Name + ',';
			}
		});
		geomacIDs = geomacIDs.replace(/,\s*$/, "");
	}).always(function () {
		/*
		* Base-maps
		*/
		// OSM
		baseMaps.push(new ol.layer.Tile({
			id: 'osm',
			visible: true,
			preload: Infinity,
			source: new ol.source.XYZ({
				url: 'http://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}'
			})
		}));
		// Satellite
		baseMaps.push(new ol.layer.Tile({
			id: 'sat',
			visible: false,
			preload: Infinity,
			source: new ol.source.XYZ({
				url: 'http://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}'
			})
		}));
		// TopoFire
		baseMaps.push(new ol.layer.Tile({
			id: 'topofire',
			visible: false,
			source: new ol.source.OSM({
				url: 'http://topofire.dbs.umt.edu/topomap/relief/{z}/{x}/{y}.jpg',
				crossOrigin: 'anonymous'
			})
		}));
		// Local TopoFire Tiles (must be downloaded with each run - cached locally)
		baseMaps.push(new ol.layer.Tile({
			id: 'local',
			visible: false,
			source: new ol.source.XYZ({
				url: cacheDir.toURL() + 'TopoFire/{z}/{x}/{y}.jpg'
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
		// Fuel Models (LANDFIRE)
		mapLayers.push(new ol.layer.Group({
			name: 'fuel',
			id: 'fuel',
			visible: false,
			opacity: 0.55,
			layers: [
				new ol.layer.Image({
					source: new ol.source.ImageWMS({
						url: 'https://landfire.cr.usgs.gov/arcgis/services/Landfire/US_140/MapServer/WMSServer',
						params: { 'LAYERS': 'US_140FBFM13' },
						crossOrigin: 'anonymous'
					})
				}),
				new ol.layer.Image({
					source: new ol.source.ImageWMS({
						url: 'https://landfire.cr.usgs.gov/arcgis/services/Landfire/AK_140/MapServer/WMSServer',
						params: { 'LAYERS': 'AK_140FBFM13' },
						crossOrigin: 'anonymous'
					})
				})
			]
		}));
		// Vegetation (LANDFIRE)
		mapLayers.push(new ol.layer.Group({
			name: 'vegetation',
			id: 'vegetation',
			visible: false,
			opacity: 0.55,
			layers: [
				new ol.layer.Image({
					source: new ol.source.ImageWMS({
						url: 'https://landfire.cr.usgs.gov/arcgis/services/Landfire/US_140/MapServer/WMSServer',
						params: { 'LAYERS': 'US_140CH,US_140CC' },
						crossOrigin: 'anonymous'
					})
				}),
				new ol.layer.Image({
					source: new ol.source.ImageWMS({
						url: 'https://landfire.cr.usgs.gov/arcgis/services/Landfire/AK_140/MapServer/WMSServer',
						params: { 'LAYERS': 'AK_140CH,AK_140CC' },
						crossOrigin: 'anonymous'
					})
				})
			]
		}));
		// GeoMac (Current Fires & Perimeters)
		mapLayers.push(new ol.layer.Group({
			name: 'geomac',
			id: 'geomac',
			visible: false,
			layers: [
				new ol.layer.Image({ // CONUS
					source: new ol.source.ImageWMS({
						url: 'http://wildfire.cr.usgs.gov/ArcGIS/services/geomac_dyn/MapServer/WMSServer',
						params: { 'LAYERS': geomacIDs },
						serverType: 'mapserver',
						crossOrigin: 'anonymous'
					})
				}),
				new ol.layer.Image({ // Alaska
					source: new ol.source.ImageWMS({
						url: 'http://wildfire.cr.usgs.gov/ArcGIS/services/geomacAK_dyn/MapServer/WMSServer',
						params: { 'LAYERS': geomacIDs },
						serverType: 'mapserver',
						crossOrigin: 'anonymous'
					})
				})
			]
		}));
		// MODIS
		mapLayers.push(new ol.layer.Tile({
			name: 'modis',
			id: 'modis',
			visible: false,
			source: new ol.source.TileWMS({
				url: 'https://fsapps.nwcg.gov/afm/cgi-bin/mapserv.exe?map=conus.map&',
				params: {
					'LAYERS': 'Last 24 hour fire detections,Last 12 hour fire detections,Current Large incidents',
					'VERSION': '1.1.0'
				},
				crossOrigin: 'anonymous',
				projection: mapProj
			})
		}));
		// VIIRS
		mapLayers.push(new ol.layer.Tile({
			name: 'viirs',
			id: 'viirs',
			visible: false,
			source: new ol.source.TileWMS({
				url: 'https://fsapps.nwcg.gov/afm/cgi-bin/mapserv.exe?map=conus_viirs_iband.map&',
				params: {
					'LAYERS': 'Last 24 hour fire detections,Current Large incidents',
					'VERSION': '1.1.0'
				},
				crossOrigin: 'anonymous',
				projection: mapProj
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
			controls: [new ol.control.Rotate(), new ol.control.Zoom(), new ol.control.ScaleLine({ units: 'us' })]
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
				// Remove the line string
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

		//add GPS button to 'zoom' controls (have to add this here because UI initialization has already occurred)
		$('div.ol-zoom.ol-unselectable.ol-control').append($('<button id="btn_GPS" title="GPS" />').on('click', _onGPSOn));

		// Start GPS location
		_onGPSOn();
	});
}
// Check the size of the domain for the sketch (too small or too big)
function _checkSketchSize() {
	var geom = sketchPolyFeature.getGeometry();
	if (!geom)
		return -1;
	var area = getArea(geom);
	if (_DEBUG) {
		console.log(area);
	}
	if (area > 0) {
		if (area > 10000) {
			// if the area is > 2331 sq km, it's too large (900 sq mi)
			if (Math.round(area / 1000000 * 100) / 100 > 2331)
				return 1;
		}
		return 0;
	}
	return -1;
}
// Get the geodesic area of a polygon in km
function getArea(polygon) {
	var geom = polygon.clone().transform(mapProj, latLonProj);
	var coordinates = geom.getLinearRing(0).getCoordinates();
	if (coordinates.length > 0)
		return Math.abs(wgs84Sphere.geodesicArea(coordinates));
	else return 0;
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
	if (_DEBUG) {
		console.info('initializing run list.');
	}
	runList = [];
	var dir = dataDir.toURL();
	var directoryReader = dataDir.createReader();
	var container = $('#runs_list');
	var defs = [];

	container.empty();
	directoryReader.readEntries(function (entries) {
		$.each(entries, function (i, entry) {
			if (entry.isDirectory && entry.name !== 'Documents') {
				var def = $.Deferred(),
					url = dir + entry.name + '/' + 'job.json';
				defs.push(def.promise());

				$.ajax({
					url: url,
					dataType: 'json',
					cache: false
				}).done(function (job) {
					runList.push(job);
					if (_DEBUG) {
						console.log(job.name + ' added to run list');
					}
					def.resolve();
				}).fail(function (err) {
					def.reject([err.statusText]);
				});
			}
		});

		$.when.apply($, defs).done(function () {
			if (_DEBUG) {
				console.log('runList length: ' + runList.length);
			}
			runList.sort(function (a, b) {
				var an = a.name.toLowerCase(),
					bn = b.name.toLowerCase();
				return an < bn ? -1 : an > bn ? 1 : 0;
			});

			$.each(runList, _createRunMenuItem);
		}).fail(function (err) {
			fail(err);
		}).always(function () {
			if (_DEBUG) {
				console.log('creating container: ');
			}
			container.trigger('create');
		});
	});
}
// Create run menu item
function _createRunMenuItem(index, jobJson) {
	if (_DEBUG) {
		console.log('creating menu item: ' + jobJson.name);
	}
	// create the buttons for the run (action button and delete button)
	var actionBtn = $('<span />').addClass('actionBtn').data({ 'runId': jobJson.id, 'runName': jobJson.name });
	var delBtn = $('<span />').text('Delete').addClass('deleteBtn').data({ 'runId': jobJson.id, 'runName': jobJson.name });

	// parse and create the submitted and last updated dates from the messages
	if (jobJson.messages.length > 0) {
		try {
			submitDate = new moment.tz(jobJson.messages[0].split(' | ')[0], serverTZ);
			updateDate = new moment.tz(jobJson.messages[jobJson.messages.length - 1].split(' | ')[0], serverTZ);
		} catch (e) {
			if (_DEBUG) {
				console.log(e);
			}
		}
	} else {
		submitDate = new moment.tz(serverTZ);
		updateDate = new moment.tz(serverTZ);
	}
	// create the run panel
	var pnl = $('<div />').attr('id', jobJson.id).data('runName', jobJson.name)
		.append($('<h3 />').text(jobJson.name))
		.append($('<div data-role="controlgroup" data-type="horizontal">')
			.css({ 'text-align': 'right' })
			.append(actionBtn)
			.append(delBtn)
		)
		.append('<br />')
		.append($('<span />').addClass('runTime').text('Submitted: ' + prettyDate(submitDate)))
		.append('<br />')
		.append($('<span />').addClass('runTime').text('Updated: ' + prettyDate(updateDate)));

	$('#runs_list').append(pnl);
	pnl.collapsible({
		mini: true,
		corners: true,
		expand: function () {
			if (_DEBUG) {
				console.log('expanding/initializing run: ' + $(this).data('runName'));
			}
			initRun($(this).attr('id'), $(this).data('runName'));
		},
		collapse: function () {
			if (_DEBUG) {
				console.log('collapsing/removing run: ' + $(this).data('runName'));
			}
			removeRun();
		}
	});

	// setup action button title and click events
	delBtn.button({ mini: true, corners: true }).on('click', function () {
		if (confirm('Are you sure you want to delete the run ' + $(this).data('runName') + '?')) {
			deleteEvent($(this).data('runId'), $(this).data('runName'));
		}
	});
	actionBtn.button({ mini: true, corners: true });
	toggleActionButton(jobJson.id, jobJson.status);
}
// Initialize UI elements and handlers
function initUI() {
	if (_DEBUG) {
		console.info('document loaded, initializing UI.');
	}
	$('#version').text(version);

	// Registration pop-up
	$("#registration").popup({
		theme: 'a',
		positionTo: 'window',
		transition: 'pop',
		tolerance: 0,
		dismissible: false,
		history: false
	});
	$('#messages').popup({
		theme: 'a',
		positionTo: 'window',
		transition: 'pop',
		tolerance: 0,
		dismissible: true,
		history: false
	});

	// Footer Buttons
	$('#btn_layers').button({
		icon: 'grid',
		iconpos: 'left',
		mini: true
	}).on('click', function () {
		if (_DEBUG) {
			console.info('#btn_layers.onClick');
		}
		$(this).parent().toggleClass('ui-btn-on');
		$('#pnl_layers').panel('toggle');

	});
	// by default, the draw button should open the registration page
	$('#btn_draw').on('click', _showRegistrationPage);
	$('#btn_submit').on('click', function () {
		map.removeInteraction(sketch);
		$('#draw').show();
		$('#sketch').hide();
		var size = _checkSketchSize();
		if (size === 0) {
			$('#request-panel').panel('open');
		} else if (size === -1) {
			navigator.notification.alert('The selected run size is too small (single point), please redraw your area and try again.', null, 'Run Size');
		} else if (size === 1) {
			navigator.notification.alert('The selected run size is too large (> 900sq mi), please redraw your area and try again.', null, 'Run Size');
		}
	});
	$('#btn_cancel').on('click', function () {
		_removeSketch();
		$('#sketch').hide();
		$('#draw').show();
	});
	$('#btn_run-opts').button({
		mini: true,
		disabled: true
	}).on('click', function () {
		if (_DEBUG) {
			console.info('#btn_run-opts.onClick');
		}
		$('#pnl_run-opts').panel('toggle');
	});

	// Run Options panel buttons
	$('#btn_time').button({ mini: true }).on('click', function () {
		if (_DEBUG) {
			console.info('#btn_time.onClick');
		}
		sliderOpen = !sliderOpen;
		$(this).parent().toggleClass('ui-btn-on');
		$('#tbl_time').toggle();
	});
	$('#btn_legend').button({ mini: true }).on('click', function () {
		if (_DEBUG) {
			console.info('#btn_legend.onClick');
		}
		legendOpen = !legendOpen;
		$(this).parent().toggleClass('ui-btn-on');

		if (legendOpen) {
			$('#pnl_legend').popup('open');
		} else {
			$('#pnl_legend').popup('close');
		}
	});
	$('#btn_home').button({ mini: true }).on('click', function () {
		if (_DEBUG) {
			console.info('#btn_home.onClick');
		}
		$(this).parent().addClass('ui-btn-on');
		zoomToRun();
		$(this).parent().removeClass('ui-btn-on');
	});
	$('#btn_weather').button({ mini: true }).on('click', function () {
		if (_DEBUG) {
			console.info('#btn_weather.onClick');
		}
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
		if (_DEBUG) {
			console.log(ids);
		}
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

	// Basemap/Layers Panel
	$('#pnl_layers').panel({
		display: 'overlay',
		theme: 'b',
		dismissible: false,
		beforeopen: function (evt, ui) {
			if (legendOpen) {
				legendWasOpen = true;
				//close legend
				$('#btn_legend').trigger('click');
			}

			$('#btn_layers').parent().addClass('ui-btn-on');
		},
		beforeclose: function (evt, ui) {
			if (sliderWasOpen) {
				$('#btn_time').trigger('click');
			} else if (legendWasOpen) {
				$('#btn_legend').trigger('click');
			}
			sliderWasOpen = false;
			legendWasOpen = false;

			$('#btn_layers').parent().removeClass('ui-btn-on');
		}
	});

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

	// setup beforeOpen and close handlers on settings panel to close/re-open any pop-ups
	$('#pnl_Settings').on('panelbeforeopen', function () {
		if (sliderOpen) {
			sliderWasOpen = true;
			//close slider
			$('#btn_time').trigger('click');
		} else if (legendOpen) {
			legendWasOpen = true;
			//close legend
			$('#btn_legend').trigger('click');
		}
	}).on('panelclose', function () {
		if (sliderWasOpen) {
			$('#btn_time').trigger('click');
		} else if (legendWasOpen) {
			$('#btn_legend').trigger('click');
		}
		sliderWasOpen = false;
		legendWasOpen = false;
	});
	// Run Request Panel
	$('#request-panel').on('panelbeforeclose', _removeSketch);

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

	// Play controls
	$('#run_first').on('click', function () {
		curIndex = 0;
		setVisible(curIndex);
	});
	$('#run_back').on('click', function () {
		curIndex = curIndex -= 1;
		if (curIndex < 0) curIndex = 0;
		setVisible(curIndex);
	});
	$('#run_pause').on('click', function () {
		$('#run_play').show();
		$(this).hide();
		if (playTimeout) {
			clearTimeout(playTimeout);
		}
	});
	$('#run_play').on('click', function () {
		$('#run_pause').show();
		$(this).hide();
		play();
	});
	$('#run_next').on('click', function () {
		curIndex = curIndex += 1;
		if (curIndex >= ninjaRun.OutputCount)
			curIndex = ninjaRun.OutputCount - 1;
		setVisible(curIndex);
	});
	$('#run_last').on('click', function () {
		curIndex = ninjaRun.OutputCount - 1;
		setVisible(curIndex);
	});

	$('#createRun').on('click', function () {
		$(this).button('refresh');
		submitJob();
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
	$('#timeSlider').slider({
		start: function () {
			$('#spinner').spin('windninja');
		},
		stop: function () {
			var index = parseInt($(this).val());
			curIndex = index;
			if (curIndex < 0) curIndex = 0;
			if (curIndex >= ninjaRun.OutputCount) curIndex = ninjaRun.OutputCount - 1;
			ninjaRun.SetVisible(curIndex);
			console.info('slider::stop - ' + ninjaRun.VisibleLayer);

			$('#runDate').text('').text(prettyDate(ninjaRun.__timeframe));

			$('#spinner').spin(false);
		}
	});
	$('#gotItBtn').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		$('#splash').popup('close');
	});

	// Initialize Settings Panel
	$('#vectorOutput').flipswitch({ mini: true });
	$('#rasterOutput').flipswitch({ mini: true });
	$('#topoOutput').flipswitch({ mini: true });
	$('#clusterOutput').flipswitch({ mini: true });
	$('#googlOutput').prop('disabled', true).flipswitch({ mini: true, disabled: true });
	$('#geopdfOutput').prop('disabled', true).flipswitch({ mini: true, disabled: true });
	$('#saveSettings').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		_saveConfig(true);
	});
	$('#register').button({ mini: true }).on('click', _showRegistrationPage);
	$('#sbmtFeedback').button({ mini: true, disabled: true }).on('click', function () {
		$(this).button('refresh');
		$('#feedback-panel').popup('open');
	});
	$('#showMessages').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		_getMessages();
	});
	$('#help').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		$('#splash').popup('open');
	});
	$('#about').button({ mini: true }).on('click', function () {
		$(this).button('refresh');
		$('#pop_about').popup('open');
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
	$("#skip").on('click', function () {
		$(this).button('refresh');
		$('#registration').popup('close');
	});
	$("#execute_register").on('click', function () {
		_registerInstall();
		$('#registration').popup('close');
	});

	$('#hlpLink').on('click', function () {
		window.open('http://www.firelab.org/project/windninja-mobile', '_system');
	});
	$('#emailLink').on('click', function () {
		cordova.plugins.email.open({
			'to': 'wind.ninja.support@gmail.com',
			'subject': 'WindNinja Mobile Help',
			'isHtml': true
		});
	});

	if (_DEBUG) {
		$('#debugOptions').show();
	}

	// Handle window resizing (rotating device)
	$(window).on('resize', setmapsize);
	setmapsize();
}
// When the back button is pressed (android)
function _onBack(evt) {
	console.debug('back button pressed: ', evt);
	evt.stopPropagation();
	evt.preventDefault();

	//if anything is open, close it. otherwise exit the app
	if ($('#pnl_Settings').hasClass('ui-panel-open')) {
		$('#pnl_Settings').panel('close');
	} else if ($('#pnl_Runs').hasClass('ui-panel-open')) {
		$('#pnl_Runs').panel('close');
	} else if ($('#pnl_layers').hasClass('ui-panel-open')) {
		$('#pnl_layers').panel('close');
	} else if ($('#pnl_run-opts').hasClass('ui-panel-open')) {
		$('#pnl_run-opts').panel('close');
	} else {
		navigator.app.exitApp();
	}
}
// Toggle the text/functionality of the 'Action' button for a run
function toggleActionButton(id, status) {
	var btn = $('#' + id + ' .actionBtn');
	btn.unbind('click');

	switch (status.toLowerCase()) {
		default:
		case 'created':
		case 'submitted':
		case 'executing':
			btn.text('Status').on('click', function () {
				if (_DEBUG) {
					console.log('Checking run status: ' + $(this).data('runName'));
				}
				_checkStatus($(this).data('runId'));
			});
			break;
		case 'downloaded':
			btn.text('Plot').on('click', function () {
				if (_DEBUG) {
					console.log('Loading run to map: ' + $(this).data('runName'));
				}
				$('#pnl_Runs').panel('close');
				$('#spinner').spin('windninja');
				toggleActionButton($(this).data('runId'), 'loaded');
				loadRun($('#output').val());
			});
			break;
		case 'succeeded':
			btn.text('Download').on('click', function () {
				if (_DEBUG) {
					console.log('Downloading run data: ' + $(this).data('runName'));
				}
				getData($(this).data('runId'));
			});
			break;
		case 'loaded':
			btn.text('Clear').on('click', function () {
				if (_DEBUG) {
					console.log('Removing run from map: ' + $(this).data('runName'));
				}
				removeRun();
			});
			break;
		case 'failed':
			btn.text('Failed').button('disable').prop('disabled', true).button('refresh');
			break;
	}

	btn.button('refresh');
}

function enableActionButton(id) {
	var btn = $('#' + id + ' .actionBtn');
	btn.button('enable').button('refresh');
}

function disableActionButton(id) {
	var btn = $('#' + id + ' .actionBtn');
	btn.button('disable').button('refresh');
}
// 'Play' the ninja run
function play() {
	setVisible(curIndex);
	playTimeout = setTimeout(function () {
		curIndex += 1;
		if (curIndex >= ninjaRun.OutputCount) {
			curIndex = 0;
		}
		play();
	}, 650);
}
// set the proper layer visible and update UI
function setVisible(index) {
	ninjaRun.SetVisible(index);
	$('#runDate').text('').text(prettyDate(ninjaRun.__timeframe));
	$('#timeSlider').val(index).slider('refresh');
	$('#spinner').spin(false);
}
// Set map element size
function setmapsize() {
	var scrnHeight = $.mobile.getScreenHeight(); // total available screen height
	var scrnWidth = $(window).width(); // total available screen width
	var headHeight = $('#head').outerHeight(); // outer most height of the header (title bar)
	var footHeight = $('#foot').outerHeight(); // outer most height of the footer (action buttons)
	var helpHead = $('#helpHeader').outerHeight(); // outer most height of the 'help' header
	var helpFoot = $('#helpFooter').outerHeight(); // outer most height of the 'help' footer

	// map should only be between the bottom of the header to the top of the footer
	var mapHeight = scrnHeight - headHeight - footHeight + 7;
	// panels should not scroll over the header, but covering the footer is OK
	var panelHeight = scrnHeight - headHeight - $(1.5).toPx();
	// 0.5em buffer on the top and bottom of the 'help' dialog/popup (so it still looks like a dialog box)
	var helpHeight = panelHeight - helpHead - helpFoot - $(0.5).toPx();

	var popupHeight = scrnHeight - $(0.5).toPx();

	$('#map').css({ 'min-height': mapHeight, 'max-height': mapHeight });
	$('[data-role="page"]').css({ 'min-height': mapHeight, 'max-height': mapHeight, 'overflow': 'hidden' });
	//$('#menuContent').height(panelHeight);
	//$('#requestContent').height(panelHeight);
	//$('#pnl_Settings').css({ 'max-height': scrnHeight + 'px' });
	//$('#settingsContent').height(panelHeight);
	//$('#helpContent').css({ 'max-height': helpHeight + 'px' });
	//$('#feedback-panel-popup').css({ 'max-height': popupHeight + 'px', 'top': 1 + 'em' });
	$('#registration-popup').css({ 'max-height': scrnHeight, 'height': scrnHeight });
	//if (!isIOS7) {
	//	$('#feedback-panel').top(0.5 + 'em');
	//}
	$('#registrationContent').outerHeight(scrnHeight - 1 - $('#registration-popup #head').outerHeight() - $(1.5).toPx() + 'px');


	// if there are any panels open, toggle visibility so heights get set properly
	$('.ui-panel-dismiss').css({ 'height': scrnHeight });

	if (sliderOpen) {
		//$('#pnl_time').popup('close');
		//setTimeout(function () { $('#pnl_time').popup('open'); }, 500);
	}
	if (legendOpen) {
		$('#pnl_legend').popup('close');
		setTimeout(function () { $('#pnl_legend').popup('open'); }, 500);
	}
}
// Generic fail method
function fail(err) {
	if (_DEBUG) {
		console.error(err);
	}
}
// Initialize WindNinja run data
function initRun(id, name) {
	if (_DEBUG) {
		console.info('initRun()');
	}
	if (guidRegex.test(id)) {
		$('#timeSlider').attr({ 'min': 0, 'max': 0, 'value': 0 });
		curIndex = 0;

		removeRun();
		ninjaRun = new WindNinjaRun(id, name);

		ninjaRun.InitRun().done(function () {
			this.LoadForecasts = $('#btn_weather').parent().hasClass('ui-btn-on');
			enableActionButton(this.ID);
		});
	}
}
// Delete a WindNinja run from the device
function deleteEvent(id, name) {
	// First check to see if the run to be deleted is 'active' and if so, remove it.
	if (ninjaRun && ninjaRun.ID === id) {
		removeRun();
	}

	// Delete all the run data
	dataDir.getDirectory(id, null, function (dir) {
		dir.removeRecursively(function (entry) {
			if (_DEBUG) {
				console.info('removed entry ' + entry);
			}
			navigator.notification.alert("Run '" + name + "' deleted.", null, 'Run Deleted', 'OK');
			_initRunList();
		}, fail);
	}, fail);
}
// Toggle overlay layer(s) visibility
function toggleLayers(IDs) {
	if (_DEBUG) {
		console.log('toggleLayers()', IDs, mapLayers);
	}
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
function _checkStatus(id) {
	$('#spinner').spin('windninja');
	// download the latest copy of the job.json file
	var url = serverURL + "api/job/" + String(id).replace(/-/g, "");
	$.ajax({
		type: 'GET',
		url: url,
		cache: false
	}).done(function (job) {
		dataDir.getDirectory(job.id, { create: true, exclusive: false }, function (dir) {
			dir.getFile("job.json", { create: true, exclusive: false }, function (file) {
				file.createWriter(function (fileWriter) {
					var blob = new Blob([JSON.stringify(job)], { type: 'application/json' }),
						updateDate,
						submitDate;
					fileWriter.write(blob);

					$('#spinner').spin(false);
					navigator.notification.alert(job.status, null, 'Run "' + job.name + '" Status', 'OK');

					var submit = $('#' + job.id + ' span.runTime')[0];
					var update = $('#' + job.id + ' span.runTime')[1];

					if (job.messages.length > 0) {
						try {
							submitDate = new moment.tz(job.messages[0].split(' | ')[0], serverTZ);
							updateDate = new moment.tz(job.messages[job.messages.length - 1].split(' | ')[0], serverTZ);
						} catch (e) {
							if (_DEBUG) {
								console.log(e);
							}
						}
					} else {
						submitDate = moment.tz(serverTZ);
						updateDate = moment.tz(serverTZ);
					}

					$(submit).text('Submitted: ' + prettyDate(submitDate));
					$(update).text('Updated: ' + prettyDate(updateDate));

					toggleActionButton(job.id, job.status);
				});
			});
		}, fail);
	}).fail(function (data) {
		navigator.notification.alert("Server Error: " + data.statusMessage, null, 'Error', 'OK');
	});
}
// Submit a WindNinja run to the server for creation
function submitJob() {
	var name = $('#runName').val();
	if (name !== '') {
		$('#spinner').spin('windninja');
		var extent,
			diff;
		try {
			extent = sketchPolyFeature.getGeometry().getExtent();
		} catch (err) {
			extent = mapView.calculateExtent(map.getSize());

			// make the extent square
			diff = (extent[2] - extent[0] - (extent[3] - extent[1])) / 2;

			extent[3] -= diff;
			extent[1] += diff;

		}
		// If the user accidentally selects a single point, the extent will be infinite.

		if ($.inArray(Infinity, extent) !== -1) {
			extent = mapView.calculateExtent(map.getSize());

			// make the extent square
			diff = (extent[2] - extent[0] - (extent[3] - extent[1])) / 2;

			extent[3] -= diff;
			extent[1] += diff;
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
			clustered: true,
			weather: true
		};
		for (var type in config.Outputs) {
			if (outputs.hasOwnProperty(type) && config.Outputs.hasOwnProperty(type)) {
				outputs[type] = config.Outputs[type];
			}
		}

		if (email && config.Email)
			notify = config.Email;
		if (phone && config.Phone) {
			if (notify)
				notify += ',' + config.Phone;
			else
				notify = config.Phone;
		}

		var params = {
			'account': config.Registration.RegistrationId,
			'xmin': xmin,
			'ymin': ymin,
			'xmax': xmax,
			'ymax': ymax,
			'forecast': source,
			'parameters': 'forecast_duration:' + dur + ';vegetation:' + veg,
			'name': name,
			'products': 'vector:' + outputs.vector + ';raster:false;topofire:' + outputs.topo + ';geopdf:' + outputs.geopdf + ';clustered:' + outputs.clustered + ';weather:' + outputs.weather
		};
		if (notify) {
			params['email'] = notify;
		}
		var url = serverURL + "api/job?" + $.param(params);

		$.ajax({
			type: 'POST',
			url: url,
			contentType: 'application/x-www-form-urlencoded'
		}).done(function (data) {
			$('#request-panel').panel('close');

			dataDir.getDirectory(data.id, { create: true, exclusive: false }, function (dir) {
				dir.getFile("job.json", { create: true }, function (file) {
					file.createWriter(function (fileWriter) {
						var blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
						fileWriter.write(blob);
						navigator.notification.alert("Run '" + data.name + "' has been sent to the server for computation. \n The results will be ready shortly in the Runs tab.", function () {
							_removeSketch();
							_cleanSketch();
							_initRunList();
							_checkStatus(data.id);
						}, 'Run Created', 'OK');
					});
				});
			}, fail);
		}).fail(function (data) {
			var error;
			if (data.statusMessage === 'undefined') {
				error = 'There appears to be an error communicating with the server, please try again shortly or connect to WiFi and try submitting again.';
			} else {
				error = data.statusMessage;
			}
			navigator.notification.alert("Server Error: " + error, null, 'Error', 'OK');
		}).always(function () {
			$('#runName').val('');
			$('#spinner').spin(false);
		});
	} else {
		navigator.notification.alert("You must enter a name for this run.", null, 'Error', 'OK');
	}
}
// Get the WindNinja run status from the server
function getData(id) {
	var url = serverURL + "api/job/" + String(id).replace(/-/g, "");
	$.ajax({
		type: 'GET',
		url: url,
		cache: false
	}).done(function (data) {
		if (data.status === 'succeeded') {
			_onDownloadReady(data, id);
		} else {
			navigator.notification.alert(data.status, null, 'Event Status', 'OK');
		}
	}).fail(function (data) {
		navigator.notification.alert("Server Error: " + data.statusMessage, null, 'Error', 'OK');
	});
}
// Download WindNinja run data
function _onDownloadReady(results, id) {
	if (_DEBUG) {
		console.log(results);
	}
	var files = 0
		, done = 0
		, outputs = []
		, prod = results.input.products.split(';')
		, prods = [];

	$('#loader').popup('open', { positionTo: 'window', transition: 'pop' });
	$('#productLabel').text('Files: 0/..');
	$('#productProgress').progressbar({ value: 0 });
	disableActionButton(id);
	downloading = true;

	$.each(prod, function (i, p) {
		var pr = p.split(':');
		if (pr[1] === 'true')
			prods.push(pr[0]);
	});

	files = prods.length;
	$('#productLabel').text('Files: ' + done + '/' + files);
	$('#productProgress').progressbar({ max: files });

	$.each(prods, function (i, p) {
		var product = results.output[p];
		var def = $.Deferred();
		outputs.push(def.promise());
		downloadProduct(id, product).progress(function () {
			done++;
			$('#productLabel').text('Files: ' + done + '/' + files);
			$('#productProgress').progressbar({ value: done });
		}).done(function () {
			def.resolve();
		}).fail(function () {
			def.reject();
		});
	});

	$.when.apply($, outputs).done(function () {
		if (_DEBUG) {
			console.debug('this says you\'re done downloading...');
		}
		downloading = false;

		//update job.json file with 'downloaded' status
		dataDir.getDirectory(id, { create: true, exclusive: false }, function (dir) {
			dir.getFile("job.json", { create: true, exclusive: false }, function (file) {
				if (_DEBUG) {
					console.log("created job.json", file);
				}
				file.createWriter(function (fileWriter) {
					results.status = 'Downloaded';
					var blob = new Blob([JSON.stringify(results)], { type: 'application/json' });
					fileWriter.write(blob);
				});
			});
		}, fail);

		var submit = $('#' + results.id + ' span.runTime')[0];
		var update = $('#' + results.id + ' span.runTime')[1];

		if (results.messages.length > 0) {
			try {
				submitDate = new moment.tz(results.messages[0].split(' | ')[0], serverTZ);
				updateDate = new moment.tz(results.messages[results.messages.length - 1].split(' | ')[0], serverTZ);
			} catch (e) {
				if (_DEBUG) {
					console.log(e);
				}
			}
		} else {
			submitDate = new moment.tz(serverTZ);
			updateDate = new moment.tz(serverTZ);
		}

		$(submit).text('Submitted: ' + prettyDate(submitDate));
		$(update).text('Updated: ' + prettyDate(updateDate));

		toggleActionButton(results.id, 'downloaded');

		initRun(results.id, results.name);
	}).always(function () {
		$('#loader').popup('close');
	});
}
// Download a specific Product (Vectors, Rasters, etc.) and place it in the appropriate location
function downloadProduct(id, product) {
	var deferred = $.Deferred()
		, URL = product.baseurl ? product.baseurl + product.package : serverURL + 'output/' + id + '/' + product.package
		, DIR = dataDir.toURL() + id;

	var fileTransfer = new FileTransfer()
		, pkgDir = DIR + '/' + product.package
		, pkgLocation;

	if (product.type === 'basemap') {
		pkgLocation = cacheDir.toURL() + product.name.split(' Basemap')[0] + '/';
	} else if (product.type === 'raster') {
		pkgLocation = DIR + '/tiles/';
	} else {
		pkgLocation = DIR;
	}

	fileTransfer.download(URL, pkgDir, function (entry) {
		deferred.notify();
		zip.unzip(pkgDir, pkgLocation, function (s) {
			if (s === 0) {
				if (_DEBUG)
					console.log('Package extracted successfully to: ' + pkgLocation);
				deferred.resolve();
			} else {
				if (_DEBUG)
					console.warn('Failed to extract package: ' + product.package);
				deferred.reject();
			}
		});
	});
	return deferred.promise();
}
// Load a WindNinja run (create layers)
function loadRun(displayType) {
	ninjaRun.RemoveRun();
	ninjaRun.OutputLayers = [];
	ninjaRun.ForecastLayers = [];
	curIndex = 0;

	mapView.fit(ninjaRun.Extent, map.getSize());
	map.renderSync();

	ninjaRun.LoadRun(displayType).done(function () {
		if (_DEBUG) {
			console.log('ninjaRun.loadRun() :: done, updating UI');
		}
		$.each([this.OutputLayers, this.ForecastLayers], function (i, g) {
			$.each(g, function (j, layer) {
				if (layer) {
					map.addLayer(layer);
				}
			});
		});

		$('#spinner').spin(false);
		$('#tbl_Date').show();

		var count = this.OutputCount;
		$('#timeSlider').attr({ 'min': 0, 'max': count - 1 }).val(0).slider('refresh');

		$('#runDate').text(prettyDate(this.__timeframe));

		$('#btn_run-opts').button('enable');
		updateLegend();

		$('#btn_time').trigger('click');
		$('#btn_legend').trigger('click');

		navigator.vibrate(200);
	});
}
// Remove a WindNinja run from the map
function removeRun() {
	var loaded = ninjaRun && ninjaRun.Loaded();

	$('#tbl_Date').hide();
	if (loaded) {
		if (playTimeout) {
			clearTimeout(playTimeout);
			$('#run_play').show();
			$('#run_pause').hide();
		}
		ninjaRun.RemoveRun();
		toggleActionButton(ninjaRun.ID, 'downloaded');
		navigator.notification.alert("All layers have been removed", null, 'Layers Removed', 'OK');
		$('#btn_run-opts').button('disable');

		$('#baseMap').val('osm').trigger('change');

		if ($('#pnl_legend').parent().hasClass('ui-popup-active')) {
			$('#btn_legend').trigger('click');
		}
		if (sliderOpen) {
			$('#btn_time').trigger('click');
		}
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
	if (_DEBUG) {
		console.log("finding position....");
	}
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
	}, fail);
}
// Stop GPS watch
function _onGPSOff() {
	$('#btn_GPS').removeClass('on').addClass('off');
	map.removeLayer(gpsLayer);
}
// Return a 'pretty' formatted date string for display
function prettyDate(date) {
	// Returns date in format MM/DD/YYYY, HH:MM:SS
	if (date.constructor === moment)
		return date.tz(config.DisplayTZ).format('MM/DD/YYYY, HH:mm:ss (z)');
	else
		return new moment.tz(date, config.DisplayTZ).format('MM/DD/YYYY, HH:mm:ss (z)');
}

//
// WindNinja Functions/classes
//
function WindNinjaRun(id, name) {
	var _isLoaded = false;
	this.InitRun = function () {
		if (_DEBUG) {
			console.log('InitRun()');
		}
		var file
			, date
			, self = this;

		// AJAX load job file
		return $.ajax({
			url: this.BaseURL + '/job.json',
			dataType: 'json',
			cache: false,
			context: this
		}).done(function (job) {
			var prod = job.input.products.split(';')
				, prods = []
				, self = this;

			$.each(prod, function (i, p) {
				var pr = p.split(':');
				if (pr[1] === 'true')
					prods.push(pr[0]);
			});

			switch (job.status.toLowerCase()) {
				default:
				case 'created':
				case 'submitted':
				case 'executing':
				case 'failed':
					break;
				case 'downloaded':
				case 'succeeded':
				case 'loaded':
					if (job.output.products) {
						//old run, needs to be removed
						navigator.notification.confirm('This run is invalid (old), would you like to remove it from your device?', function (btnIndex) {
							if (btnIndex === 1) {
								deleteEvent(job.id, job.name).then(function () {
									return $.Deferred().reject(new Error('Invalid run, removed'));
								});
							}
							else {
								toggleActionButton(job.id, 'failed');
								return $.Deferred().reject(new Error('Invalid run, not removed'));
							}
						}, 'Invalid Windninja Run', ['Remove', 'Cancel']);
					}

					// set time series
					this.TimeSteps = job.output.simulations.times.sort();
					$.each(this.TimeSteps, function (i, t) {
						self.TimeSteps[i] += job.output.simulations.utcOffset;
					});

					//create our file list
					$.each(job.output, function (outputType, product) {
						if (prods.indexOf(outputType) === -1 || !product || product.type === 'basemap')
							return true;

						var isOutput = false;

						if (outputType !== 'weather' && product.name.toLowerCase().indexOf('windninja') !== -1)
							isOutput = true;

						$.each(product.files, function (i, f) {
							if (product.type === 'cluster') {
								file = new self.resultFile(f, null);
							} else {
								if (!isOutput)
									date = f.split('.json')[0].slice(3) + job.output.simulations.utcOffset;
								else
									date = f.split('.json')[0] + job.output.simulations.utcOffset;
								file = new self.resultFile(f, date);
							}

							file.Type = product.type;
							file.Data = product.data;

							if (isOutput) {
								if (!self.Outputs[file.Type])
									self.Outputs[file.Type] = [];
								self.Outputs[file.Type].push(file);
							}
							else {
								if (!self.Forecasts[file.Type])
									self.Forecasts[file.Type] = [];
								self.Forecasts[file.Type].push(file);
							}
						});
					});

					this.__sortFiles();
					break;
			}

			// Domain
			var extent = [
				job.input.domain.xmin
				, job.input.domain.ymin
				, job.input.domain.xmax
				, job.input.domain.ymax
			];
			this.Extent = ol.proj.transformExtent(extent, latLonProj, mapProj);
		}).fail(function (err) {
			self.__fail(new Error(err).stack);
		});
	};
	this.LoadRun = function (displayType) {
		if (_DEBUG) {
			console.group('Loading WindNinja run.');
			console.time('Run load time');
			console.info('LoadRun(' + displayType + ')');
		}
		this.__resetLayers();
		var deferred = $.Deferred()
			, self = this
			, count = this.TimeSteps.length;

		if (this.Outputs.hasOwnProperty(displayType)) {
			this.MaxSpeed = this.Outputs[displayType][0].Data.maxSpeed.overall;
			this.DisplayType = displayType;
		}

		//always create vector forecast layers
		var fLayers = this.__loadForecastLayers('vector');
		var oLayers = this.__loadOutputLayers(displayType);

		fLayers.progress(function (i) {
			if (_DEBUG) {
				console.info('WindNinjaRun.LoadRun() :: Done creating Forecast Layer (' + i + '/' + count + ')');
			}
		});
		oLayers.progress(function (i) {
			if (_DEBUG) {
				console.info('WindNinjaRun.LoadRun() :: Done creating Output layer (' + i + '/' + count + ')');
			}
		});

		$.when(oLayers, fLayers).done(function () {
			self.__sortlayers();
			self.__setVisibleLayer(self.VisibleLayer);

			if (_DEBUG) {
				console.timeEnd('Run load time');
			}
			self._isLoaded = true;
			deferred.resolveWith(self);
		}).fail(function () {
			self.__fail(new Error('WindNinjaRun.LoadRun() :: Error').stack);
		}).always(function () {
			if (_DEBUG) {
				console.groupEnd();
			}
		});

		return deferred.promise();
	};
	this.RemoveRun = function () {
		$.each([this.OutputLayers, this.ForecastLayers], function () {
			$.each(this, function (i, l) {
				map.removeLayer(l);
			});
		});
		if (this.displayType === 'cluster') {
			mapView.un('change:resolution');
		}
		this.OutputCount = 0;
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
	__verbose: false
	, __clusterDistance: 15
	, __dir: ''
	, __timeframe: null
	, __styleCache: {}
	, __resCache: []
	, __featCache: {}
	, __forecastCache: []
	, __colorCache: {
		'1': 'rgba(0,0,255,1)',
		'2': 'rgba(0,255,0,1)',
		'3': 'rgba(255,255,0,1)',
		'4': 'rgba(255,165,0,1)',
		'5': 'rgba(255,0,0,1)'
	}
	, __stroke: new ol.style.Stroke({ color: 'rgba(255,255,255,1)', width: 2 })
	, __style: new ol.style.Style()
	, __symbolGeom: new ol.geom.MultiLineString([[[7, 14], [7, 0], [4, 4]], [[7, 0], [10, 4]]])
	, __source: null

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
		this.TimeSteps = [];
		this.OutputCount = 0;
		this.VisibleLayer = 0;
		this.RunSpeeds = [];
		this.MaxSpeed = 0.00;
		this.__style.setStroke(this.__stroke);
		this.Extent = null;
	}
	, __resetLayers: function () {
		this.ForecastLayers.length = 0;
		this.OutputLayers.length = 0;
		this.VisibleLayer = 0;
		this.OutputCount = 0;
		this.RunSpeeds.length = 0;
		this.MaxSpeed = 0.00;
		this.DisplayType = '';
		this.__styleCache = {};
		this.__resCache.length = 0;
		this.__featCache = {};
		this.__forecastCache.length = 0;
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
	, __loadForecastLayers: function (displayType) {
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
				var file = fileList[i];
				if (dataType !== 'dir') {
					defs.push($.ajax({
						url: this.BaseURL + file.Name,
						dataType: dataType,
						cache: false,
						context: file
					}).done(function (data) {
						self.__makeLayer('weather', data, this.Date).done(function (layer) {
							self.ForecastLayers.push(layer);
							items++;
							deferred.notifyWith(self, [items]);
						});
					}));
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
	, __loadOutputLayers: function (displayType) {
		if (this.__verbose) {
			console.log('__loadOutputLayers()');
			console.time('load output layers');
		}

		var deferred = $.Deferred()
			, self = this
			, defs = []
			, items = 0
			, fileList
			, dataType;

		if (this.Outputs.hasOwnProperty(displayType)) {
			fileList = this.Outputs[displayType];

			switch (displayType) {
				case 'vector':
					dataType = 'json';
					break;
				case 'cluster':
					dataType = 'json';
					break;
				case 'raster':
					dataType = 'dir';
					break;
				case 'google':
					dataType = 'dir';
					break;
			}

			if (this.__verbose)
				console.info('creating ' + displayType + ' output layers');
			for (var i = 0; i < fileList.length; i++) {
				var file = fileList[i];
				if (dataType !== 'dir') {
					var url = this.BaseURL + file.Name;
					defs.push($.ajax({
						url: url,
						type: 'GET',
						dataType: dataType,
						isLocal: true,
						context: file
					}).done(function (data) {
						console.debug(data);
						self.__makeLayer(displayType, data, this.Date).done(function (layer) {
							self.OutputLayers.push(layer);
							items++;
							deferred.notifyWith(self, [items]);
						});
					}).fail(function (data, var1, var2) {
						deferred.reject();
					}));
				} else {
					var def = $.Deferred();
					defs.push(def.promise());
					this.__makeLayer(displayType, file.Data, file.Date).done(function (layer) {
						this.OutputLayers.push(layer);
						items++;
						deferred.notifyWith(this, [items]);
						def.resolveWith(this);
					});
				}
			}

			$.when.apply($, defs).done(function () {
				if (self.__verbose)
					console.timeEnd('load output layers');
				self.OutputLayers.sort(self.layerSort);
				if (self.DisplayType !== 'cluster') {
					self.OutputCount = self.OutputLayers.length;
				}
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

			var source = new ol.source.Vector({
				url: this.BaseURL + data + '.kml',
				projection: mapProj,
				format: new ol.format.KML()
			});

			if (this.__verbose) {
				console.timeEnd('creating source');
				console.time('creating layer');
			}

			var layer = new ol.layer.Vector({
				source: source,
				visible: false
			});

			//layer.set('type', 'KML');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);
		var __RasterLayer = $.proxy(function () {
			if (this.__verbose) {
				console.groupCollapsed('Raster');
				console.time('creating source');
			}

			var source = new ol.source.XYZ({
				maxZoom: 17,
				url: this.BaseURL + 'tiles/' + data + '/{z}/{x}/{y}.png'
			});

			if (this.__verbose) {
				console.timeEnd('creating source');
				console.time('creating layer');
			}

			var layer = new ol.layer.Tile({
				source: source,
				extent: this.Extent,
				visible: false,
				preload: Infinity
			});

			//layer.set('type', 'Raster');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);
		var __ImageVectorLayer = $.proxy(function () {
			if (this.__verbose) {
				console.groupCollapsed('ImageVector');
				console.time('max speed calculation');
			}

			//data.features = $.grep(data.features, function (feat, i) {
			//	if (feat.properties.speed <= 0.00)
			//		return false;
			//	return true;
			//});

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

			//layer.set('type', 'ImageVector');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);
		var __ClusterImageVectorLayer = $.proxy(function () {
			if (this.__verbose) {
				console.groupCollapsed('ClusterImageVector');
			}

			//data.features = $.grep(data.features, function (feat, i) {
			//	if (feat.properties.speed < 0)
			//		return false;
			//	return true;
			//});

			if (this.__verbose) {
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
				extent: this.Extent,
				visible: false
			});

			//layer.set('type', 'ClusterImageVector');
			layer.set('date', date);

			if (this.__verbose) {
				console.timeEnd('creating layer');
				console.groupEnd();
				console.timeEnd('total');
			}
			deferred.resolveWith(this, [layer]);
		}, this);
		var __CanvasVectorLayer = $.proxy(function () {
			var lines = data.data
				, v, lv, feats, attr = data.header
				, i, li = lines.length
				, a, la = attr.length, col
				, val, pnt, feat, res
				, ts, speed, dt;

			if (this.__verbose) {
				console.groupCollapsed('CanvasVector');
				console.time('creating source');
			}

			for (a = 0; a < la; a++) {
				col = attr[a];
				if (col.startsWith('vel_')) {
					this.__forecastCache.push(col.slice(4));
				}
			}

			this.__forecastCache.sort();
			this.__timeframe = this.__forecastCache[0];
			this.OutputCount = this.__forecastCache.length;

			for (i = 0; i < li; i++) {
				val = lines[i]
					, lv = val.length;
				if (lv !== la)
					continue;

				res = val[0]
					, feats = this.__featCache[res];

				if (!feats) {
					this.__resCache.push(res);
					feats = this.__featCache[res] = new ol.source.Vector();
				}

				pnt = new ol.geom.Point([Number(val[1]), Number(val[2])]);

				feat = new ol.Feature(pnt);
				feat.setId(i);

				for (v = 3; v < lv; v++) {
					feat.set(attr[v], val[v]);
				}

				feat.setStyle(this.__clusterStyle(feat, this));

				feats.addFeature(feat);
			}

			this.__source = new ol.source.Vector({
				projection: mapProj,
				loader: $.proxy(this.__clusterLoader, this),
				strategy: ol.loadingstrategy.bbox
			});

			if (this.__verbose) {
				console.timeEnd('creating source');
				console.time('creating layer');
			}

			var source = new ol.source.ImageVector({
				source: this.__source
			});

			var layer = new ol.layer.Image({
				source: source,
				visible: true
			});
			//layer.set('type', 'CanvasVector');

			mapView.on('change:resolution', $.proxy(function () {
				this.__source.clear();
			}, this));

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
			case 'cluster':
				__CanvasVectorLayer();
				break;
		}

		if (this.__verbose) {
			console.groupEnd();
		}
		return deferred.promise();
	}
	, __setVisibleLayer: function (index) {
		this.VisibleLayer = index || 0;
		if (this.__verbose)
			console.info('setting visible layer to index: ' + this.VisibleLayer);

		if (this.DisplayType === 'cluster') {
			this.__timeframe = this.TimeSteps[index];
			var r = 0, rl = this.__resCache.length
				, res, src, feats, f, fl, feat;

			for (r = 0; r < rl; r++) {
				src = this.__featCache[this.__resCache[r]];
				feats = src.getFeatures();
				fl = feats.length;

				for (f = 0; f < fl; f++) {
					feat = feats[f];
					feat.setStyle(this.__clusterStyle(feat, this));
				}
			}

			this.__source.resolution = null;
			this.__source.clear(true);

			for (var i = 0; i < this.OutputCount; i++) {
				f = this.ForecastLayers[i];
				if (f) {
					if (i === index && this.LoadForecasts)
						f.setVisible(true);
					else
						f.setVisible(false);
				}
			}
		}
		else {
			for (i = 0; i < this.OutputCount; i++) {
				var layer = this.OutputLayers[i];
				var forecast = this.ForecastLayers[i];

				if (layer) {
					if (i === index) {
						this.__timeframe = this.TimeSteps[index];
						layer.setVisible(true);
					}
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
	}
	, __makeVectorArrow: function (feat, angle, scale) {
		var dist = scale;

		var __createArrowShaft = function (pt, angle) {
			var points = [];
			var x = pt.getCoordinates()[0];
			var y = pt.getCoordinates()[1];
			var x1 = x + dist * Math.cos(angle);
			var y1 = y - dist * Math.sin(angle);

			var __createPoint = function (pt, angle, num) {
				var brng = num === 3 ? angle + (135).toRad() : num === 4 ? angle - (135).toRad() : null;
				var len = dist / 3;
				var x = pt[0];
				var y = pt[1];
				try {
					var x1 = x + Math.cos(brng) * len;
					var y1 = y - Math.sin(brng) * len;
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
		var scale = res * (this.__clusterDistance * 2 * 0.75);
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
		var scale = res * (this.__clusterDistance * 0.75);
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
	, __clusterLoader: function (extent, res, proj) {
		var i, l = this.__resCache.length, featRes, symbolRes;

		this.__source.clear(true);
		this.__source.resolution = res;

		featRes = this.__resCache[l - 1];
		for (i = 0; i < l; i++) {
			symbolRes = Number(this.__resCache[i]) / this.__clusterDistance;
			if (symbolRes >= res && symbolRes < featRes) {
				featRes = this.__resCache[i];
				break;
			}
		}

		if (this.__featCache[featRes]) {
			this.__source.addFeatures(this.__featCache[featRes].getFeaturesInExtent(extent));
		}
	}
	, __clusterStyle: function (feat, self) {
		var vel = feat.get('vel_' + self.__timeframe.substring(0, 13))
			, ang = parseFloat(feat.get('ang_' + self.__timeframe.substring(0, 13)))
			, va = 's_{0}_{1}'.format(vel, ang)
			, style, size, color, canvas, context;

		style = self.__styleCache[va];
		if (!style) {
			size = [self.__clusterDistance, self.__clusterDistance];
			color = self.__colorCache[vel];
			self.__stroke.setColor(color);
			canvas = document.createElement('canvas');
			context = ol.render.toContext(canvas.getContext('2d'), { size: size, pixelRatio: 1 });
			context.setStyle(self.__style);
			context.drawGeometry(self.__symbolGeom);

			style = new ol.style.Style({
				image: new ol.style.Icon({
					img: canvas,
					imgSize: size,
					rotation: ang.toRad(),
					anchor: [0.5, 0],
					anchorOrigin: 'bottom-left'
				})
			});
			self.__styleCache[va] = style;
		}
		return style;
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
		return new moment.tz(a.Date, config.DisplayTZ).valueOf() - new moment.tz(b.Date, config.DisplayTZ).valueOf();
	}
	, layerSort: function (a, b) {
		return new moment.tz(a.get('date'), config.DisplayTZ).valueOf() - new moment.tz(b.get('date'), config.DisplayTZ).valueOf();
	}
};