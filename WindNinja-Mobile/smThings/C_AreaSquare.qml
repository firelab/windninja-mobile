import QtQuick 2.6
import QtQuick.Controls 2.1
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1
import QtPositioning 5.3
import QtSensors 5.3
import QtGraphicalEffects 1.0

import ArcGIS.AppFramework 1.0
import Esri.ArcGISRuntime 100.12
import "../Lib/js/geoFunctions.js" as Geo
import "../CustomComponents"


Item
{
    visible: app.editingSimulation;
    property bool isActive: false
    property real pointToMove: 0
    property real myFontsize: 10
    property real clickTolerance: 0.05*app.width
    property real maxSquareMiles: 70;
    property real currentSquareMiles: 0;
    property bool alowedToSim: false;
    property string circleColor: "#44ffffff";
    property string circleSelectedColor: "#990000ff";
    property string circleBorderColor: "ffffffff";
    property string rectangleAllowedColorBorder: Qt.rgba(0,1,0,1);
    property string rectangleNotAllowedColorBorder: Qt.rgba(1,0,0,1);
    property string rectangleAllowedColorFill: Qt.rgba(0,1,0,0.1);
    property string rectangleNotAllowedColorFill: Qt.rgba(1,0,0,0.3);

    property real lastXPointA: 0;
    property real lastYPointA: 0;
    property real lastXPointB: 0;
    property real lastYPointB: 0;
    property real lastXPointC: 0;
    property real lastYPointC: 0;

    property var symbolSize: 25;

    PolygonBuilder { id:polygonBuilder; spatialReference: SpatialReference.createWgs84() }
    GraphicsOverlay { id: overlaySquare; LayerSceneProperties { surfacePlacement: Enums.SurfacePlacementDraped }}

    PolylineBuilder  { id: edit_line_builder; spatialReference: SpatialReference.createWgs84()}

    PointBuilder{id:pointA;spatialReference: SpatialReference.createWgs84()}
    PointBuilder{id:pointB;spatialReference: SpatialReference.createWgs84()}
    PointBuilder{id:pointC;spatialReference: SpatialReference.createWgs84()}

    Rectangle{
        id:lblHolder
        radius: 5
        color: "#FFFFFF"
        height: 50
        visible: app.editingSimulation;
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.rightMargin: 10
        anchors.leftMargin: 10
        anchors.topMargin: 10

        Label{
            id:lblOutput
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            verticalAlignment: Qt.AlignVCenter
            horizontalAlignment: Qt.AlignHCenter
            font.family: app.fontRobotoRegular.name
            color:"#3C3C36";
            font.pixelSize:  16;
        }
    }

    DropShadow{
        visible: lblHolder.visible
        anchors.fill: lblHolder
        horizontalOffset: 3
        verticalOffset: 3
        radius: 8.0
        samples: 17
        color: "#80000000"
        source: lblHolder
    }

    SimpleFillSymbol
    {
        id: simpleFillSymbol
        color: Qt.rgba(1,0,0,0.3)
        style: Enums.SimpleFillSymbolStyleSolid
        SimpleLineSymbol {
            id:simpleFillSymbolborder
            style: Enums.SimpleLineSymbolStyleSolid
            color: "red"
            width: 2.0
        }
    }

    Component.onCompleted: {_constructor() }

    function _constructor()
    {
        isActive=true;
        mainMap.mousePressedAndHeld.connect(onMousePressedAndHeld)
        mainMap.mousePositionChanged.connect(onMouseMoved)
        mainMap.mouseReleased.connect(onMouseReleased);
        if ( mainMap.graphicsOverlays.contains(overlaySquare)==false) {  mainMap.graphicsOverlays.append(overlaySquare) }
    }

    function _destructor()
    {
        isActive=false;
        edit_line_builder.parts.removeAll();
        mainMap.mousePressedAndHeld.disconnect(onMousePressedAndHeld)
        mainMap.mousePositionChanged.disconnect(onMouseMoved)
        mainMap.mouseReleased.disconnect(onMouseReleased);

    }

    function setInitialSquare()
    {
        var dd=Math.min(app.width,app.height)*0.1;
        var a= mainMap.screenToBaseSurface(app.width/2-dd,app.height/2-dd)
        var b=mainMap.screenToBaseSurface(app.width/2+dd,app.height/2+dd)
        if (isNaN(a.x)==false && isNaN(b.x)==false )
        {
            visible = true;
            pointA.setXY(a.x,a.y)
            pointB.setXY(b.x,b.y)
            drawSquare(circleColor,circleColor)

            if(c_areaSquare.currentSquareMiles > pageMain.c_areaSquare.maxSquareMiles){
                generalPopUp.pleaseZoomWarn();
                visible = false;
                editingSimulation = false;
                c_areaSquare.clearAll();
            }else if(mainMap.currentViewpointCamera.pitch > 60){
                generalPopUp.pleasePerpendicularWarn();
                visible = false;
                editingSimulation = false;
                c_areaSquare.clearAll();
            }
        }else{
            generalPopUp.pleasePerpendicularWarn();
            visible = false;
            editingSimulation = false;
            c_areaSquare.clearAll();
        }
    }


    function drawSquare(color1,color2)
    {
        if(!app.editingSimulation)
            return;
        var webMercatorPointA=Geo.geographicToWebMercator_simple(pointA.x,pointA.y  )
        var webMercatorPointB=Geo.geographicToWebMercator_simple(pointB.x,pointB.y  )

        var dx_miles=Math.abs(webMercatorPointA.x-webMercatorPointB.x)*0.000621371*Math.cos(pointA.y*Math.PI/180)
        var dy_miles=Math.abs(webMercatorPointA.y-webMercatorPointB.y)*0.000621371*Math.cos(pointA.y*Math.PI/180)
        var area_ac=dx_miles*dy_miles*640;
        var area_sm = Math.round((dx_miles*dy_miles)*100)/100;

        currentSquareMiles = area_sm;
        var textToSet = "Selected Area Size: " + area_sm + " sq miles";

        lblOutput.text=textToSet;

        polygonBuilder.parts.removeAll();
        polygonBuilder.addPointXY(pointA.x,pointA.y)
        polygonBuilder.addPointXY(pointA.x,pointB.y)
        polygonBuilder.addPointXY(pointB.x,pointB.y)
        polygonBuilder.addPointXY(pointB.x,pointA.y)

        var mediumX = (pointA.x + pointB.x)/2;
        var mediumY = (pointA.y + pointB.y)/2;

        pointC.setXY(mediumX,mediumY);

        overlaySquare.graphics.clear()

        alowedToSim = area_sm < maxSquareMiles;
        if (alowedToSim)
        {
            simpleFillSymbol.color = rectangleAllowedColorFill;
            simpleFillSymbolborder.color = rectangleAllowedColorBorder;
        }
        else
        {
            simpleFillSymbol.color = rectangleNotAllowedColorFill;
            simpleFillSymbolborder.color = rectangleNotAllowedColorBorder;
        }

        if(pointToMove !== 0){
            simpleFillSymbolborder.color = "#990000ff"
        }

        var gr2 = ArcGISRuntimeEnvironment.createObject("Graphic", {geometry:  polygonBuilder.geometry, symbol:simpleFillSymbol });
        overlaySquare.graphics.append(gr2)


        var outline = ArcGISRuntimeEnvironment.createObject("SimpleLineSymbol",
                                                            {
                                                                style: "SimpleLineSymbolStyleSolid",
                                                                width: 1,
                                                                color: circleBorderColor
                                                            });

        var simpleMarkerSymbol=ArcGISRuntimeEnvironment.createObject("SimpleMarkerSymbol",
                                                                     {
                                                                         style: Enums.SimpleMarkerSymbolStyleCircle,
                                                                         color:color1,
                                                                         size:symbolSize,
                                                                         outline:outline
                                                                     });

        var graphA = ArcGISRuntimeEnvironment.createObject("Graphic",
                                                           {
                                                               geometry: pointA.geometry,
                                                               symbol: simpleMarkerSymbol
                                                           });

        simpleMarkerSymbol=ArcGISRuntimeEnvironment.createObject("SimpleMarkerSymbol",
                                                                 {
                                                                     style: Enums.SimpleMarkerSymbolStyleCircle,
                                                                     color:color2,
                                                                     size:symbolSize,
                                                                     outline:outline
                                                                 });
        var graphB = ArcGISRuntimeEnvironment.createObject("Graphic",
                                                           {
                                                               geometry: pointB.geometry,
                                                               symbol: simpleMarkerSymbol
                                                           });




        simpleMarkerSymbol=ArcGISRuntimeEnvironment.createObject("SimpleMarkerSymbol",
                                                                 {
                                                                     style: Enums.SimpleMarkerSymbolStyleCross,
                                                                    color:"#44ffffff",
                                                                     size:symbolSize,
                                                                     outline:outline
                                                                 });
        var graphC = ArcGISRuntimeEnvironment.createObject("Graphic",
                                                           {
                                                               geometry: pointC.geometry,
                                                               symbol: simpleMarkerSymbol
                                                           });

        overlaySquare.graphics.append(graphA);
        overlaySquare.graphics.append(graphB);
        overlaySquare.graphics.append(graphC);

        lastXPointA = pointA.x;
        lastYPointA = pointA.y;
        lastXPointB = pointB.x;
        lastYPointB = pointB.y;
        lastXPointC = pointC.x;
        lastYPointC = pointC.y;
    }

    function moveSquare()
    {
        if(!app.editingSimulation)
            return;

        var diferenceX = pointC.x - lastXPointC;
        var diferenceY = pointC.y - lastYPointC;

        pointA.setXY(lastXPointA + diferenceX,lastYPointA + diferenceY);
        pointB.setXY(lastXPointB + diferenceX, lastYPointB + diferenceY);


        var webMercatorPointA=Geo.geographicToWebMercator_simple(pointA.x,pointA.y  )
        var webMercatorPointB=Geo.geographicToWebMercator_simple(pointB.x,pointB.y  )

        var dx_miles=Math.abs(webMercatorPointA.x-webMercatorPointB.x)*0.000621371*Math.cos(pointA.y*Math.PI/180)
        var dy_miles=Math.abs(webMercatorPointA.y-webMercatorPointB.y)*0.000621371*Math.cos(pointA.y*Math.PI/180)
        var area_ac=dx_miles*dy_miles*640;
        var area_sm = Math.round((dx_miles*dy_miles)*100)/100;

        currentSquareMiles = area_sm;
        var textToSet = "Selected Area Size: " + area_sm + " sq miles";

        lblOutput.text=textToSet;

        polygonBuilder.parts.removeAll();
        polygonBuilder.addPointXY(pointA.x,pointA.y)
        polygonBuilder.addPointXY(pointA.x,pointB.y)
        polygonBuilder.addPointXY(pointB.x,pointB.y)
        polygonBuilder.addPointXY(pointB.x,pointA.y)

        var mediumX = (pointA.x + pointB.x)/2;
        var mediumY = (pointA.y + pointB.y)/2;

        pointC.setXY(mediumX,mediumY);

        overlaySquare.graphics.clear()

        alowedToSim = area_sm < maxSquareMiles;
        if (alowedToSim)
        {
            simpleFillSymbol.color = rectangleAllowedColorFill;
            simpleFillSymbolborder.color = "#990000ff";
        }
        else
        {
            simpleFillSymbol.color = rectangleNotAllowedColorFill;
            simpleFillSymbolborder.color = "#990000ff";
        }
        var gr2 = ArcGISRuntimeEnvironment.createObject("Graphic", {geometry:  polygonBuilder.geometry, symbol:simpleFillSymbol });
        overlaySquare.graphics.append(gr2)


        var outline = ArcGISRuntimeEnvironment.createObject("SimpleLineSymbol",
                                                            {
                                                                style: "SimpleLineSymbolStyleSolid",
                                                                width: 1,
                                                                color: circleBorderColor
                                                            });

        var simpleMarkerSymbol=ArcGISRuntimeEnvironment.createObject("SimpleMarkerSymbol",
                                                                     {
                                                                         style: Enums.SimpleMarkerSymbolStyleCircle,
                                                                         color:"#44ffffff",
                                                                         size:symbolSize,
                                                                         outline:outline
                                                                     });

        var graphA = ArcGISRuntimeEnvironment.createObject("Graphic",
                                                           {
                                                               geometry: pointA.geometry,
                                                               symbol: simpleMarkerSymbol
                                                           });

        simpleMarkerSymbol=ArcGISRuntimeEnvironment.createObject("SimpleMarkerSymbol",
                                                                 {
                                                                     style: Enums.SimpleMarkerSymbolStyleCircle,
                                                                     color:"#44ffffff",
                                                                     size:symbolSize,
                                                                     outline:outline
                                                                 });
        var graphB = ArcGISRuntimeEnvironment.createObject("Graphic",
                                                           {
                                                               geometry: pointB.geometry,
                                                               symbol: simpleMarkerSymbol
                                                           });




        simpleMarkerSymbol=ArcGISRuntimeEnvironment.createObject("SimpleMarkerSymbol",
                                                                 {
                                                                     style: Enums.SimpleMarkerSymbolStyleCross,
                                                                     color:"#990000ff",
                                                                     size:symbolSize,
                                                                     outline:outline
                                                                 });
        var graphC = ArcGISRuntimeEnvironment.createObject("Graphic",
                                                           {
                                                               geometry: pointC.geometry,
                                                               symbol: simpleMarkerSymbol
                                                           });

        overlaySquare.graphics.append(graphA);
        overlaySquare.graphics.append(graphB);
        overlaySquare.graphics.append(graphC);

        lastXPointA = pointA.x;
        lastYPointA = pointA.y;
        lastXPointB = pointB.x;
        lastYPointB = pointB.y;
        lastXPointC = pointC.x;
        lastYPointC = pointC.y;
    }

    function onMousePressedAndHeld(mouse)
    {
        if(!app.editingSimulation)
            return;
        else if (isActive==true && pointToMove==0)
        {
            var a=mainMap.locationToScreen(pointA.geometry).screenPoint;
            var b=mainMap.locationToScreen(pointB.geometry).screenPoint;
            var c = mainMap.locationToScreen(pointC.geometry).screenPoint;
            var da=Math.sqrt((a.x-mouse.x)*(a.x-mouse.x)+(a.y-mouse.y)*(a.y-mouse.y));
            var db=Math.sqrt((b.x-mouse.x)*(b.x-mouse.x)+(b.y-mouse.y)*(b.y-mouse.y));
            var dc=Math.sqrt((c.x-mouse.x)*(c.x-mouse.x)+(c.y-mouse.y)*(c.y-mouse.y));

            if (da<db && da<dc && da<clickTolerance)
            {
                pointToMove = 1;
                drawSquare(circleSelectedColor,circleColor);
            }
            else if (db<da && db<dc && db<clickTolerance)
            {
                pointToMove = 2;
                drawSquare(circleColor,circleSelectedColor);
            }
            else if(dc<da && dc<db && dc<clickTolerance){
                pointToMove = 3
                moveSquare();
            }
        }
    }

    function onMouseMoved(mouse)
    {
        if(!app.editingSimulation)
            return;
        else if (isActive==true && pointToMove!==0)
        {
            var pto=mainMap.screenToBaseSurface(mouse.x,mouse.y);
            if (isNaN(pto.x)===false && isNaN(pto.x)===false )
            {
                if (pointToMove == 1)
                {
                    pointA.setXY(pto.x,pto.y);
                    drawSquare(circleSelectedColor,circleColor);
                }
                else if (pointToMove == 2)
                {
                    pointB.setXY(pto.x,pto.y);
                    drawSquare(circleColor,circleSelectedColor);
                }
                else if (pointToMove == 3)
                {
                    pointC.setXY(pto.x,pto.y);
                    moveSquare();
                }
            }
        }
    }

    function onMouseReleased(mouse)
    {
        if (polygonBuilder.parts.size > 0 && isActive==true)
        {
            pointToMove = 0;
            drawSquare(circleColor,circleColor);
        }
    }

    function clearAll(){
        visible = false;
        polygonBuilder.parts.removeAll();
        overlaySquare.graphics.clear()
    }

    function getExtent(){
        var xMin,xMax,yMin,yMax;
        if(pointA.x < pointB.x){
            xMin = pointA.x;
            xMax = pointB.x
        }else{
            xMax = pointA.x;
            xMin = pointB.x
        }
        if(pointA.y < pointB.y){
            yMin = pointA.y;
            yMax = pointB.y
        }else{
            yMax = pointA.y;
            yMin = pointB.y
        }
        return {"xMin":xMin, "xMax":xMax, "yMin":yMin, "yMax":yMax}
    }
}

