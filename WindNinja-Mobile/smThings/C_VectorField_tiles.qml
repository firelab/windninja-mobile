import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

import ArcGIS.AppFramework 1.0
import Esri.ArcGISRuntime 100.12


import "../Lib/js/geoFunctions.js" as Geo


Item
{
    id:myroot

    //SIM VALUES
    property string simName: ""
    property string controllerCurrentTimestamp: ""

    property alias playingAnimation: timer.running;

    property var webtilelayer: 0
    property var timeNames: []
    property bool isActive: false
    property var simFolder: ""
    property var job: ""

    //LEYEND CONFIGURATION
    property real myFontsize: 10



    //VECTOR CONFIGURATION
    property var vectorColor: ["blue","green","yellow","orange","red"]
    property var vectorSpeedRange: [0,0,0,0,0]

    //RASTER VARIABLES in wgs84
    property var rasDir: []
    property var rasMod: []

    property real xmin:0
    property real xmax: 0
    property real ymin:0
    property real ymax: 0
    property real nrow: 0
    property real ncol: 0
    property real ntime: 0
    property real timeIndex:0
    property var cellsize: 0
    property var outPath: AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/")

    property int maxWindSpeedRaster: 0
    property int maxWindSpeedWx: 0
    signal simulationChanged();

    property var layersByTime: []

    //AUXILIARY OBJECTS
    PolylineBuilder { id: polylineBuilderWGS84;spatialReference: SpatialReference.createWgs84() }
    PointBuilder{id:pointbuilderWGS84;spatialReference: SpatialReference.createWgs84() }


    //INTERFACE
    Dialog {
        id: msgDialog
        title: "Point information"
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        Label {
            id:msgText
            anchors.fill: parent
            horizontalAlignment: Qt.AlignLeft
            verticalAlignment: Qt.AlignTop
        }
    }

    FileFolder
    {
        id:fileFolder
        path:outPath
    }

    Timer {
        id:timer
        interval: 1000
        running: false
        repeat: true
        onTriggered:
        {
            timeEvolution(1);
        }
    }



    Component.onCompleted:
    {
        _constructor()

    }

    function _constructor()
    {
        isActive=true
        mainMap.mouseDoubleClicked.connect(onMouseDoubleClicked)
    }

    function _destructor()
    {
        mainMap.mouseDoubleClicked.disconnect(onMouseDoubleClicked)
        rasMod=[]
        rasDir=[]
    }

    //USER FUNCTIONS///////

    function loadWindninja(jobpath)
    {
        job=fileFolder.readJsonFile(jobpath)
        simFolder=job.id
        while (simFolder!=simFolder.replace("-",""))  {simFolder=simFolder.replace("-","")  }

        xmin = job.input.domain.xmin;
        xmax = job.input.domain.xmax;
        ymin = job.input.domain.ymin;
        ymax = job.input.domain.ymax;

        simName = job.name

        //Get tile names
        timeNames=[];
        for (var tt=0; tt<job.output.raster.files.length; tt++)
        {
            timeNames.push(job.output.raster.files[tt])
        }
        timeNames.sort()

        ntime=job.output.raster.files.length;

        //PREPARE LEYEND
        maxWindSpeedRaster = job.output.raster.data.maxSpeed.overall;
        maxWindSpeedWx = job.output.weather.data.maxSpeed.overall;


        //PREPARE TILES
        for(var i = 0; i < ntime; i++){
            layersByTime.push(
                        ArcGISRuntimeEnvironment.createObject(
                            "WebTiledLayer",  {
                                templateUrl: outPath+ "/" + simFolder+"/tiles/"+ timeNames[i]+"/{level}/{col}/{row}.png"
                                }
                            )
                        );
        }

        layersByTime.forEach(function(item, index, array){
            map.operationalLayers.append(item);
        });

        timeEvolution(0)
        app.simulationLoaded = true;
        simulationChanged()
    }




    function timePlayStop()
    {
        if(ntime>1 && playingAnimation)
            timer.stop();
        else
            timer.start();
    }

    function timeStop(){
        timer.stop();
    }

    function timeEvolution(dt)
    {
        timeIndex=timeIndex+dt
        if (timeIndex>=ntime)
            timeIndex=0;
        if (timeIndex<0)
            timeIndex=ntime-1;

        var pathChecked = outPath+"/"+simFolder+"/tiles/"+timeNames[timeIndex]+"/{level}/{col}/{row}.png";

        controllerCurrentTimestamp = timeNames[timeIndex];
        var layersLoadedOffset = 0;
        map.operationalLayers.forEach(function(element, index, array){
            if(element.templateUrl !== undefined && !element.templateUrl.includes("topofire")){
                var mustBeShowed = element.templateUrl === pathChecked ? 1 : 0;
                element.opacity = mustBeShowed;
                element.visible = (mustBeShowed || layersLoadedOffset > 0) && !wx.visible;
                if(mustBeShowed){
                    layersLoadedOffset = 2;
                }else{
                    layersLoadedOffset--;
                }
            }
        });
    }

    function reloadLayers()
    {
        var pathChecked = outPath+"/"+simFolder+"/tiles/"+timeNames[timeIndex]+"/{level}/{col}/{row}.png";

        controllerCurrentTimestamp = timeNames[timeIndex];
        var layersLoadedOffset = 0;
        map.operationalLayers.forEach(function(element, index, array){
            if(element.templateUrl !== undefined && !element.templateUrl.includes("topofire")){
                var mustBeShowed = element.templateUrl === pathChecked ? 1 : 0;
                element.opacity = mustBeShowed;
                element.visible = (mustBeShowed || layersLoadedOffset > 0) && !wx.visible;
                if(mustBeShowed){
                    layersLoadedOffset = 2;
                }else{
                    layersLoadedOffset--;
                }
            }
        });
    }



    function addData(data)
    {
        if (rasDir.length==0)
        {
            //OBTAIN NROW NCOL
            var _kk=0;
            while (data.features[_kk].geometry.coordinates[0]<data.features[_kk+1].geometry.coordinates[0]){_kk++}
            nrow=_kk+1;
            ncol=data.features.length/(_kk+1)
            ntime=0

            //COMPUTE CELLSIZES
            var dcol_lon=Math.abs(data.features[0].geometry.coordinates[0]-data.features[1].geometry.coordinates[0])
            var dcol_lat=Math.abs(data.features[0].geometry.coordinates[1]-data.features[1].geometry.coordinates[1])
            var drow_lon=Math.abs(data.features[0].geometry.coordinates[1]-data.features[ncol].geometry.coordinates[1])
            var drow_lat=Math.abs(data.features[0].geometry.coordinates[1]-data.features[ncol].geometry.coordinates[1])

            //ADD DATA
            var auxDir= get2Dmatrix(nrow,ncol)
            var auxMod= get2Dmatrix(nrow,ncol)
            var nn=-1
            for (var jj = 0; jj < ncol; jj++)
            {
                for (var ii = 0; ii < nrow; ii++)
                {
                    nn++
                    auxMod[ii][jj]=data.features[nn].properties.speed
                    auxDir[ii][jj]=data.features[nn].properties.dir
                }
            }

            rasDir.push(auxDir)
            rasMod.push(auxMod)

            ntime=rasDir.length

        }
    }



    /////////////////////////////////////////////////////////////
    //SCENE VIEW EVENTS//////////////////////////////////////////
    /////////////////////////////////////////////////////////////

    function onMouseDoubleClicked(mouse)
    {

    }



    function searchWindIndex( value,  range)
    {
        ///ge the index in the range such that the value is lower
        var index = 0;
        while (value > range[index]) { index++; }

        return index;

    }

    function searchRangeIndex( value,  range)
    {
        ///ge the index in the range such that the value is lower
        var index = range.length - 1;
        while (value < range[index] && index > 0) { index--; }

        return index;

    }



    ////////////////////////////
    ////////////////////////////////////
    ////LIB/////////////////////
    ////////////////////////////

    function constrainAngle(degree)
    {
        degree=degree % 360;
        if (degree<0){degree=degree+360;}
        return degree
    }

    function directionBearing(degrees)
    {
        degrees=constrainAngle(degrees)
        if (degrees>180){degrees=degrees-360}


        var bearing = "";

        if (degrees > -22.5  && degrees <= 22.5){
            bearing = "N";
        }else if (degrees > 22.5 && degrees <= 67.5){
            bearing = "NE";
        }else if (degrees > 67.5 && degrees <= 112.5){
            bearing = "E";
        }else if (degrees > 112.5 && degrees <= 157.5){
            bearing = "SE";
        }else if( (degrees > 157.5 ) || (degrees <= -157.5)){
            bearing = "S";
        }else if (degrees > -157.5 && degrees <= -112.5){
            bearing = "SW";
        }else if (degrees > -112.5 && degrees <= -67.5){
            bearing = "W";
        }else if (degrees > -67.5 && degrees <= -22.5){
            bearing = "NW";
        }

        return bearing
    }

    function isDefined(variable)
    {
        if (typeof variable === 'undefined' || !variable) {return false }
        else{return true}

    }

    function get3Dmatrix(a,b,c)
    {
        var ras=  new Array(a);
        for (var i = 0; i < a; i++)
        {
            ras[i] = new Array(  b);
        }
        for (var i = 0; i < a; i++)
        {
            for (var j = 0; j < b; j++)
            {
                ras[i][j] = new Array(c);
            }
        }
        return ras
    }

    function get2Dmatrix(nrow,ncol)
    {
        var ras=  new Array(nrow);
        for (var i = 0; i < nrow; i++)
        {
            ras[i] = new Array(  ncol);
        }

        return ras;
    }


    function getVectorSpeedRange(){
        return vectorSpeedRange;
    }

    function getMaxWindSpeedRaster(){
        return maxWindSpeedRaster;
    }

    function getMaxWindSpeedWx(){
        return maxWindSpeedWx;
    }

    function clear(){
        layersByTime = [];
        var mustBeRemoved = [];
        map.operationalLayers.forEach(function(element, index, array){
            if(element.templateUrl !== undefined && !element.templateUrl.includes("topofire")){
                element.visible = false;
                mustBeRemoved.push(index)
            }
        });

        mustBeRemoved = mustBeRemoved.reverse();

        mustBeRemoved.forEach(function(element, index, array){
            map.operationalLayers.remove(element,1);
        });
    }




}

