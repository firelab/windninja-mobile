import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtSensors 5.1
import QtPositioning 5.2
import ArcGIS.AppFramework 1.0
import QtGraphicalEffects 1.0
import Esri.ArcGISRuntime 100.12

import "../CustomComponents"
import "../smThings"

import "../Lib/js/geoFunctions.js" as GeoFunctions
import "../Lib/js/DateFunctions.js" as DateFunctions
import "../Lib/js/UtilFunctions.js" as UtilFunctions

Page {
    id:pageMain

    anchors.fill: parent
    Material.background: "#FFFFFF"

    property alias vectorField: vectorfield;
    property alias c_areaSquare: c_areaSquare
    property alias wx: wx;
    property alias map: map;



    PointBuilder {
        id: pointAux;
        spatialReference: Factory.SpatialReference.createWebMercator()
    }

    PointBuilder {
        id: pointMyPosition
        spatialReference: Factory.SpatialReference.createWebMercator()
    }

    SceneView{
        id: mainMap
        anchors.fill: parent

        signal pointCreated(var pointX, var pointY)

        onCurrentViewpointCameraChanged: {
            imageCompass.rotation = currentViewpointCamera.heading*-1
        }

        Scene {
            id:map

            property bool layerVisibilityOfflineTopoFire: false;
            property bool layerVisibilityGeoMac: false;
            property bool layerVisibilityModis: false;
            property bool layerVisibilityViirs: false;
            property bool layerVisibilityFuelModels: false;
            property bool layerVisibilityVegetation: false;
            property bool firePerimetersLayerVisibility: false;

            Surface {
                ArcGISTiledElevationSource {
                    url: "https://elevation3d.arcgis.com/arcgis/rest/services/WorldElevation3D/Terrain3D/ImageServer"
                }
                elevationExaggeration: 1.5
            }

            //Offline TopoFire
            WebTiledLayer{
                visible: map.layerVisibilityOfflineTopoFire
                templateUrl: AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/") + "/topofire/{level}/{col}/{row}.jpg"
                noDataTileBehavior: Enums.NoDataTileBehaviorBlank
            }

            //Fuel Models (LANDFIRE)
            //US
            WmsLayer {
                visible: map.layerVisibilityFuelModels
                url:"https://landfire.cr.usgs.gov/arcgis/services/Landfire/US_140/MapServer/WMSServer?request=GetCapabilities&service=WMS"
                layerNames: "US_140FBFM13"
            }
            //AK
            WmsLayer {
                visible: map.layerVisibilityFuelModels
                url:"https://landfire.cr.usgs.gov/arcgis/services/Landfire/AK_140/MapServer/WMSServer?request=GetCapabilities&service=WMS"
                layerNames: "AK_140FBFM13"
            }

            //FirePerimeters
            FeatureLayer {
                visible: map.firePerimetersLayerVisibility
                ServiceFeatureTable {
                    url: "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/CY_WildlandFire_Perimeters_ToDate/FeatureServer/0"
                }
            }

            //Vegetation (LANDFIRE)
            //US
            WmsLayer {
                visible: map.layerVisibilityVegetation
                url:"https://landfire.cr.usgs.gov/arcgis/services/Landfire/US_140/MapServer/WMSServer?request=GetCapabilities&service=WMS"
                layerNames: {["US_140CH", "US_140CC"]}
                opacity: 0.5
            }
            //AK
            WmsLayer {
                visible: map.layerVisibilityVegetation
                url:"https://landfire.cr.usgs.gov/arcgis/services/Landfire/AK_140/MapServer/WMSServer?request=GetCapabilities&service=WMS"
                layerNames: {["AK_140CH", "AK_140CC"]}
                opacity: 0.5
            }

            //GeoMac (Current Fires & Perimeters
            //CONUS
            FeatureLayer {
                visible: map.layerVisibilityGeoMac
                ServiceFeatureTable {
                    url:"https://wildfire.cr.usgs.gov/ArcGIS/rest/services/geomac_dyn/MapServer/0"
                }
            }
            FeatureLayer {
                visible: map.layerVisibilityGeoMac
                ServiceFeatureTable {
                    url:"https://wildfire.cr.usgs.gov/ArcGIS/rest/services/geomac_dyn/MapServer/2"
                }
            }
            //Alaska
            FeatureLayer {
                visible: map.layerVisibilityGeoMac
                ServiceFeatureTable {
                    url:"https://wildfire.cr.usgs.gov/ArcGIS/rest/services/geomacAK_dyn/MapServer/0"
                }
            }
            FeatureLayer {
                visible: map.layerVisibilityGeoMac
                ServiceFeatureTable {
                    url:"https://wildfire.cr.usgs.gov/ArcGIS/rest/services/geomacAK_dyn/MapServer/2"
                }
            }

            //MODIS
            WmsLayer {
                visible: map.layerVisibilityModis
                url:"https://aws.wfas.net/geoserver/firms/wms/?SERVICE=WMS&VERSION=1.3.0&REQUEST=getCapabilities"
                layerNames: {["modis_c6_1_global"]}
                customParameters: {"time": "P3D/PRESENT"}
            }

            //VIIRS
            WmsLayer {
                visible: map.layerVisibilityViirs
                url:"https://aws.wfas.net/geoserver/firms/wms?service=wms&request=getCapabilities"
                layerNames: {["j1_viirs_c2_global", "suomi_viirs_c2_global"]}
                customParameters: {"time": "P3D/PRESENT"}
            }
        }

        GraphicsOverlay {
            id: graphicsOverlay
            SimpleRenderer {
                TextSymbol{
                    size:20
                    text: "m"
                    fontFamily: app.fontWindNinjaUi.name
                    color:"yellow"
                    backgroundColor: "white"
                }
            }
        }

        GraphicsOverlay {
            id: currentPositionOverlay
        }





        onPointCreated: {
            geocoder.isShowBackground = false

                pointAux.setXY(pointX,pointY)
                showPin(pointAux.geometry)
                graphicsOverlay.visible = true


        }

        Component.onCompleted: {
            setDefaultBaseMap();
            mainMap.locationDisplay.start();
        }

        function setDefaultBaseMap(){

            var localTpk = ArcGISRuntimeEnvironment.createObject("Basemap",{name: "localTpk"});


            var pathsArray = ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer","https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer"];
            var layerType = "ArcGISTiledLayer";

            pathsArray.forEach(function(element){
                var currentLayer;
                switch(layerType){
                case "ArcGISTiledLayer":
                    currentLayer = ArcGISRuntimeEnvironment.createObject("ArcGISTiledLayer", {url: element});
                    break;
                case "WebTiledLayer":
                    currentLayer = ArcGISRuntimeEnvironment.createObject("WebTiledLayer", {templateUrl: element});
                    break;
                }
                localTpk.baseLayers.append(currentLayer);
            });

            map.basemap = localTpk;
            app.currentBaseMap = name
        }
    }

    function updateLocationPoint(position){
        var posWeb = GeoFunctions.geographicToWebMercator_simple(position.coordinate.longitude,position.coordinate.latitude)
        pointMyPosition.setXY(posWeb.x,posWeb.y)
        currentPositionOverlay.graphics.clear();
        var currentPositionGraphic = ArcGISRuntimeEnvironment.createObject("Graphic", {geometry: pointMyPosition.geometry, symbol: currentPositionSymbol});
        currentPositionOverlay.graphics.append(currentPositionGraphic);
    }



    CustomGeocoder{
        id:geocoder
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 10
        z:rectangleCompass.z+1

        visible: !editingSimulation && !simulationLoaded;

        onResultSelected: {
            var XY = GeoFunctions.geographicToWebMercator_simple(point.x, point.y)
            mainMap.pointCreated(XY.x, XY.y)
            pointAux.setXY(XY.x,XY.y)
            zoomTo(pointAux.geometry)
        }
    }

    Rectangle{
        id:rectangleCompass;
        height: 48;
        width: 48;
        radius: 24;
        color: "white";
        anchors.top: parent.top;
        anchors.right: parent.right;
        anchors.topMargin: geocoder.visible || editingSimulation ? 70 : simulationController.legendVisible ? 85 : 10;
        anchors.rightMargin: 10;

        border.color: "#11838383";
        border.width: 2;
        Image {
            id: imageCompass;
            source: "../Assets/ic_compass.png";
            anchors.centerIn: parent;
            height: 45;
            width: 45;
        }
        MouseArea{
            anchors.fill: parent;
            onClicked: {
                rotateCameraTo(0);
            }
        }
    }

    DropShadow{
        visible: rectangleCompass.visible;
        anchors.fill: rectangleCompass;
        horizontalOffset: 3;
        verticalOffset: 3;
        radius: 8.0;
        samples: 17;
        color: "#80000000";
        source: rectangleCompass;
    }

    CustomRoundButton{
        id: cancelSimButton
        color: "gray"
        buttonIcon: app.fontIcons._clear
        anchors.bottom:confirmSimButton.top
        anchors.horizontalCenter: confirmSimButton.horizontalCenter
        visible: editingSimulation && !simulationLoaded;
        onClicked: {
            editingSimulation = false;
            c_areaSquare.clearAll();
        }
    }

    CustomRoundButton{
        id: confirmSimButton
        color: "blue"
        buttonIcon: app.fontIcons._confirm
        anchors.bottom:shortcutBar.top
        anchors.right: shortcutBar.right
        anchors.margins: 10
        visible: editingSimulation && !simulationLoaded;

        onClicked: {

            if(c_areaSquare.alowedToSim){
                editingSimulation = false;
                c_areaSquare.clearAll();
                simulationCreationPanel.visible = true;
            }else{
                generalPopUp.selectedAreaTooLargeWarn();
            }
        }
    }

    CustomRoundButton{
        id: createSimButton
        color: "blue"
        buttonIcon: app.fontIcons._create_sim
        anchors.bottom:shortcutBar.top
        anchors.right: shortcutBar.right
        anchors.margins: 10
        visible: !editingSimulation && !simulationLoaded;
        onClicked: {
            if(app.settings.canSimulate){
                editingSimulation = true;
                c_areaSquare.setInitialSquare();
            }else{
                app.windNinjaServer.checkRegistration();
                switch (app.settings.registrationStatus) {
                case 'accepted':
                    app.settings.canSimulate = true;
                    editingSimulation = true;
                    c_areaSquare.setInitialSquare();
                    break;
                case 'pending':
                    generalPopUp.registrationStatusPending();
                    break;
                case 'disabled':
                    generalPopUp.registrationStatusDisabled();
                    break;
                }
            }
        }
    }

    CustomShortcutBar{
        id: shortcutBar
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.bottom: parent.bottom
    }

    CustomSimulationController{
        id:simulationController;
        visible: simulationLoaded;

        anchors.top: parent.top
        anchors.bottom: shortcutBar.top

        onPreviousPressed: {
            vectorfield.timeEvolution(-1);
            wx.plotWindField(vectorfield.timeIndex);
        }

        onPlayPressed: {
            vectorfield.timePlayStop();
            wx.timePlayStop();
        }

        onNextPressed: {
            vectorfield.timeEvolution(+1);
            wx.plotWindField(vectorfield.timeIndex);
        }

        onWxPressed: {
            simulationController.wxVisible = !simulationController.wxVisible;
            wx.visible = simulationController.wxVisible;
            vectorField.reloadLayers();
            simulationController.maxWindSpeed = simulationController.wxVisible ? vectorField.getMaxWindSpeedWx() : vectorField.getMaxWindSpeedRaster();
        }

        onExtendPressed: {
            zoomToSim();
        }
        onClosePressed: {
            vectorField.clear();
            vectorfield.timeStop();
            wx.clear();
            wx.timeStop();
            visible = false;
            simulationLoaded = false;
        }
    }

    SimulationCreationPanel{
        id:simulationCreationPanel;
        visible: false;
        z:2;

        onSimulatePressed: {
            var simExtent = c_areaSquare.getExtent();

            var notify = "";
            if (emailChecked && app.settings.userEmail != "")
                notify = app.settings.userEmail;

            if (smsChecked && app.settings.userPhone != "" && app.settings.userPhoneProvider != "") {
                if (notify != "")
                    notify += ',' + app.settings.userPhone.replace(/-/g, "") + "@" + UtilFunctions.getProviderMail(app.settings.userPhoneProvider);
                else
                    notify = app.settings.userPhone.replace(/-/g, "") + "@" + UtilFunctions.getProviderMail(app.settings.userPhoneProvider);
            }

            windNinjaServer.simulate(
                        name,
                        simExtent.xMin, simExtent.yMin, simExtent.xMax, simExtent.yMax,
                        "forecast_duration:" + duration + ";vegetation:grass;mesh_choice:coarse",
                        "AUTO",
                        "vector:true;raster:true;topofire:true;geopdf:false;clustered:false;weather:true",
                        app.settings.registrationId,
                        notify
                        );
        }
    }

    LayerManager{
        id:layerManager
        visible: false;
        z:2

        onLayerSelectedChanged:{

        }
    }

    function hideLayerManager(){
        layerManager.visible = false;
    }

    ScreenFilterModal{
        id:screenFilterModal
        visible: layerManager.visible || simulationCreationPanel.visible
    }

    PictureMarkerSymbol{
        id:pms
        width: 50
        height: 50
        url: "../Assets/Map/map-pin-icon.png"
    }

    SimpleMarkerSymbol {
        id: currentPositionSymbol
        style: "SimpleMarkerSymbolStyleCircle"
        color: "#59A0D9"
        size: 16
        outline: SimpleLineSymbol{
            style: "SimpleLineSymbolStyleSolid"
            width: 2
        }
    }






    //smThings
    C_AreaSquare {
        z:99
        anchors.fill: parent
        id:c_areaSquare
    }

    C_VectorField_tiles {
        id:vectorfield ;
        z:3;
        anchors.fill: parent;

        Component.onCompleted:  {

        }

        onControllerCurrentTimestampChanged: {
            simulationController.currentTimestamp = DateFunctions.formatTDate(vectorField.controllerCurrentTimestamp);
        }

        onSimulationChanged: {
            simulationController.simName = vectorField.simName;
            wx.setMaxSpeed(vectorField.maxWindSpeedWx);
            wx.loadJsonFiles(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/" + vectorField.job.id.replace(/-/g, '')  + "/wx"),"wx*");
            simulationController.visible = app.simulationLoaded;
            simulationController.maxWindSpeed =vectorField.getMaxWindSpeedRaster();
            zoomToSim();
        }
    }

    C_Wx{
        id:wx
        sv: mainMap;
        visible: false;
    }

    //Functions

    Component.onCompleted: {
        app.pageMain = pageMain;
        zoomToStart();
        app.windNinjaServer.checkRegistration();
    }

    function zoomToGPS(){
        var xy=GeoFunctions.geographicToWebMercator_simple(gpsPositionSource.position.coordinate.longitude, gpsPositionSource.position.coordinate.latitude )
        pointAux.setXY(xy.x,xy.y)
        zoomTo(pointAux)
    }

    function zoomTo(point){
        zoomToScaled(point, undefined)
    }

    function zoomToScaled(point, scale){
        scale = scale !== undefined ? scale : 100000
        var soCalPoint = ArcGISRuntimeEnvironment.createObject("Point", {x: point.x, y: point.y, spatialReference: Factory.SpatialReference.createWebMercator()});
        var soCalViewpoint = ArcGISRuntimeEnvironment.createObject("ViewpointCenter", {center: soCalPoint, targetScale: scale});
        mainMap.setViewpoint(soCalViewpoint);
    }

    function zoomToHome(){
        var viewPointCenter = ArcGISRuntimeEnvironment.createObject("ViewpointCenter",{center: pointAux.geometry, targetScale: 100000*0.5});

        mainMap.setViewpoint(viewPointCenter, 4.0,  Enums.AnimationCurveEaseInOutCubic);
    }

    function zoomToStart(){
        pointAux.setXY(-11000000,4400000);
        zoomToScaled(pointAux,35000000)
    }

    function zoomToSim(){

        var minxy=GeoFunctions.geographicToWebMercator_simple(vectorfield.xmin, vectorfield.ymin)
        var maxxy=GeoFunctions.geographicToWebMercator_simple(vectorfield.xmax, vectorfield.ymax)


        pointAux.setXY((minxy.x + maxxy.x)/2,(minxy.y + maxxy.y)/2);

        var aux = (maxxy.x - minxy.x)*10

        zoomToScaled(pointAux, aux);
    }

    function hidePin(){
        graphicsOverlay.graphics.remove(0, 1);
        graphicsOverlay.visible = false;
        geocoder.searchText = ""
    }

    function rotateCameraTo(value){
        mainMap.setViewpointCamera(mainMap.currentViewpointCamera.rotateTo(value,0,0));
    }

    function showPin(point){
        graphicsOverlay.visible = true;
        graphicsOverlay.graphics.remove(0, 1);
        var graphic = ArcGISRuntimeEnvironment.createObject("Graphic", {geometry: point, symbol: pms});
        graphicsOverlay.graphics.insert(0, graphic);
    }

    function changeLayer(selectedLayer){
        if(selectedLayer === "Offline Map"){
            map.layerVisibilityOfflineTopoFire = !map.layerVisibilityOfflineTopoFire;
        }

        if(selectedLayer === "GeoMac"){
            map.layerVisibilityGeoMac = selectedLayer === "GeoMac" && !map.layerVisibilityGeoMac;
        }

        if(selectedLayer === "MODIS"){
            map.layerVisibilityModis = !map.layerVisibilityModis;
        }

        if(selectedLayer === "VIIRS"){
            map.layerVisibilityViirs = !map.layerVisibilityViirs;
        }

        if(selectedLayer === "Fuel Models"){
            map.layerVisibilityFuelModels = !map.layerVisibilityFuelModels;
        }

        if(selectedLayer === "Vegetation"){
            map.layerVisibilityVegetation = !map.layerVisibilityVegetation;
        }

        if(selectedLayer === "Fire Perimeters"){
            map.firePerimetersLayerVisibility = !map.firePerimetersLayerVisibility;
        }
    }

    function stopAnimation(){
        vectorfield.timeStop();
        wx.timeStop();
        simulationController.reset();
    }

    function closeSimulationController(){
        simulationController.close();
    }

    focus: true // important - otherwise we'll get no key events
    Keys.onReleased: {
        if (event.key === Qt.Key_Back) {
            event.accepted = true
            backButtonPressed()
        }
    }
}
