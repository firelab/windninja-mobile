import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

import ArcGIS.AppFramework 1.0
import Esri.ArcGISRuntime 100.12





Item
{

    id:myroot


    property var legendColor: ["#1101FC","#06FE02","#FBFC00","#FDA402","#FC0400"]
    property var legendRange: [0,1,2,4,10]
    property real vectorSize:0.01
    property real vectorHeight: 100
    property var dataList:[]
    property var graphicOverlay
    property real ntime: 1
    property var timeIndex: 0
    property var sv: undefined;

    property alias playingAnimation: timer.running;

    //AUXILIARY OBJECTS
    PolylineBuilder { id: polylineBuilderWGS84;spatialReference: SpatialReference.createWgs84() }
    PointBuilder{id:pointbuilderWGS84;spatialReference: SpatialReference.createWgs84() }
    FileFolder  { id:fileFolder }


    Component.onCompleted:
    {
        var lsp = ArcGISRuntimeEnvironment.createObject("LayerSceneProperties", {surfacePlacement:  Enums.SurfacePlacementDraped });
        var go = ArcGISRuntimeEnvironment.createObject("GraphicsOverlay", {  id: "wxOverlay", sceneProperties : lsp,
                                                           renderingMode:   Enums.GraphicsRenderingModeDynamic //if necesary for performance change to static mode
                                                       });
        graphicOverlay=go;
        sv.graphicsOverlays.append( graphicOverlay)
    }

    onVisibleChanged: {
        if(visible){
            plotWindField(timeIndex);
        }else{
            graphicOverlay.graphics.clear();
        }
    }

    Timer {
        id:timer
        interval: 1000
        running: false
        repeat: true
        onTriggered:
        {
            plotWindField(timeIndex+1);
        }
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

    //load json files from a given jobpath and filtering by name. For example "Wx_*"
    function loadJsonFiles(jobpath, nameFilter)
    {
        fileFolder.path=jobpath;
        var listFiles=fileFolder.fileNames(nameFilter,false);
        listFiles.sort();

        timeIndex = 0;
        ntime=listFiles.length;
        dataList=  new Array(ntime);

        for (var tt=0;tt<listFiles.length;tt++)
        {
            var data=fileFolder.readJsonFile(jobpath+"/"+listFiles[tt])
            dataList[tt]= data;
        }

        plotWindField(timeIndex)
    }




    function plotWindField(_timeIndex)
    {
        timeIndex=_timeIndex;
        if (timeIndex==ntime){
            timeIndex=0;
        }
        if (timeIndex<0){
            timeIndex=ntime-1
        }
        if(!visible) {return;}

        graphicOverlay.graphics.clear()
        var holder =[];
        var data=dataList[timeIndex]

        for (var kk=0;kk<data.features.length;kk++)
        {
            var speed=data.features[kk].properties.speed;
            var dir=data.features[kk].properties.dir;
            var xx=data.features[kk].geometry.coordinates[0];
            var yy=data.features[kk].geometry.coordinates[1];
            var pp=webMercatorToGeographic_simple(xx,yy)

            dir = dir+180
            if (dir>360){dir=dir-360}

            var lat=pp.y
            var lon=pp.x

            holder.push(arrowWgs( lon,lat, vectorSize,  vectorHeight,  speed,dir))

        }
        graphicOverlay.graphics.appendAll(holder)
    }


    function base( posx,posy)
    {
        var point = ArcGISRuntimeEnvironment.createObject("Point", {x: posx, y: posy, spatialReference: SpatialReference.createWgs84()});
        var pointSymbol=ArcGISRuntimeEnvironment.createObject("SimpleMarkerSymbol",  {style: Enums.SimpleMarkerSymbolStyleCircle, color:"red",size:5});
        var pointGraph = ArcGISRuntimeEnvironment.createObject("Graphic", {geometry: point, symbol: pointSymbol});
        return pointGraph
    }



    function arrowWgs( posx,posy,mod, height,  speed,  aspect)
    {

        var color=legendColor[searchWindIndex(speed,legendRange)]
        aspect*=Math.PI/180;
        polylineBuilderWGS84.parts.removeAll()

        var p= [[0,-0.5],[0,0.5],[0.25,0.25],[0,0.501],[-0.25,0.25]]

        for (var i = 0; i < p.length; i++)
        {
            p[i][0] = mod * p[i][0];
            p[i][1] = mod * p[i][1];
            var x= p[i][0] * Math.cos(aspect) + p[i][1] * Math.sin(aspect) + posx;
            var y=-p[i][0] * Math.sin(aspect) + p[i][1] * Math.cos(aspect) + posy;
            polylineBuilderWGS84.addPointXY(x,y);
        }
        var mySymbol=ArcGISRuntimeEnvironment.createObject("SimpleLineSymbol", {color:color, width:2 });
        var myGraphic = ArcGISRuntimeEnvironment.createObject("Graphic", {geometry:  polylineBuilderWGS84.geometry, symbol:mySymbol });
        myGraphic.attributes.insertAttribute("speed",speed)
        return myGraphic;
    }


    function searchWindIndex( value,  range)
    {
        ///ge the index in the range such that the value is lower
        var index = 0;
        while (value > range[index]){
            index++;
        }

        return index;

    }

    function searchRangeIndex( value,  range)
    {
        ///ge the index in the range such that the value is lower
        var index = range.length - 1;
        while (value < range[index] && index > 0) { index--; }
        return index;

    }


    function webMercatorToGeographic_simple( x, y )
    {
        var radius = 6378137;
        var num3 = x / radius;
        var num4 = num3 * 57.295779513082323;
        var num5 = Math.floor((num4 + 180.0) / 360.0);
        var num6 = num4 - (num5 * 360.0);
        var num7 = 1.5707963267948966 - (2.0 * Math.atan(Math.exp((-1.0 * y) / 6378137.0)));
        var lat = num7 * 57.295779513082323;
        var lon = num6;
        return { x: lon, y: lat }

    }

    function setMaxSpeed(maxSpeed){
        var speedStep = Math.round(maxSpeed/5)
        legendRange = [speedStep, speedStep*2, speedStep*3, speedStep*4, speedStep*5]
    }

    function clear(){
        visible = false;
        graphicOverlay.graphics.clear();
    }
}

