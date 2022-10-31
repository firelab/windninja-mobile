import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

import ArcGIS.AppFramework 1.0
import Esri.ArcGISRuntime 100.12


import "../Lib/js/geoFunctions.js" as Geo

Item
{
    id:scaleMarker
     z:9999
    property real myCount: 0
    property real lineposx: 0 //screen position of the points use for the marker
    property real lineposy: 0


    PolylineBuilder { id: polylineBuilderWGS84;spatialReference: SpatialReference.createWgs84() }
     GraphicsOverlay { id: scaleOverlay; LayerSceneProperties { surfacePlacement: Enums.SurfacePlacementDraped } }

    Graphic
    {
        id:myBar;
        symbol:  SimpleLineSymbol {
            style:Enums.SimpleLineSymbolStyleSolid
            color: "blue"; width: 4.0}
    }

    Component.onCompleted:
    {
        mainMap.currentViewpointCameraChanged.connect(onCurrentViewpointCameraChanged)
    }

    Text
    {
        id:myDistanceLabel
        font.pointSize:15
        text: "xxx km"
        color: "blue"
    }

    Rectangle
    {
        anchors.top:myDistanceLabel.bottom
        anchors.topMargin: 6
        id:screenScale
        width: scaleMarker.width
        height: 2
       radius: 2
       opacity: 1
       color: "blue"

        Component.onCompleted: {


            //ge the screen position
            var l = screenScale.mapToItem(mainMap, 0, 0)
            lineposx=l.x
            lineposy=l.y;
        }

    }


    Timer {
        id:myTimer
        property var hasCameraChanged: 0
        interval: 100
        running: false
        repeat: false
        onTriggered:
        {
            //this will be triggered only when currentviewpointchanged is finished
            myBar.geometry=polylineBuilderWGS84.geometry
            scaleOverlay.graphics.append(myBar)
            screenScale.opacity=1;
        }
    }



    function onCurrentViewpointCameraChanged()
    {
        if (screenScale.opacity==0){screenScale.opacity=0.8;}
        if (scaleOverlay.graphics.count>0){ scaleOverlay.graphics.clear()};

        var a=mainMap.screenToBaseSurface(lineposx,lineposy);
        var b=mainMap.screenToBaseSurface(lineposx+screenScale.width,lineposy)

        var aa=Geo.geographicToWebMercator_simple(a.x,a.y  )
        var bb=Geo.geographicToWebMercator_simple(b.x,b.y  )


        var conv_mToMiles=0.000621371

        var dx=bb.x-aa.x;
        var dy=bb.y-aa.y
        var dd_miles=Math.sqrt(dx*dx+dy*dy)*conv_mToMiles*Math.cos(a.y*Math.PI/180);

        if (isNaN(dd_miles) )
        {
           myDistanceLabel.text=""
        }
       else if (dd_miles>1)
        {
            myDistanceLabel.text=Math.round(dd_miles*10)/10+" mi";
        }
        else
        {
            var conv_milesTofeet=5280;
            myDistanceLabel.text=Math.round(dd_miles*conv_milesTofeet)+" feet";
        }



        polylineBuilderWGS84.parts.removeAll()
        polylineBuilderWGS84.addPoint(a)
        polylineBuilderWGS84.addPoint(b)

    }
    function isDefined(variable)
    {
        if (typeof variable === 'undefined' || !variable) {return false }
        else{return true}

    }

}

