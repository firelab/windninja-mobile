import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtGraphicalEffects 1.0
import Esri.ArcGISRuntime 100.12

Item{
id:item

    property var currentPoint
    property int compassDegree: 0
    property bool isShowBackground: false
    property bool isSuggestion: true

    property string currentLocatorTaskId: ""
    property string currentQueryTaskId:""
    property alias searchText: searchTextField.text

    signal resultSelected(var point)

    height: searchBar.height + results.height + 30


    onIsSuggestionChanged: {
        if(!isSuggestion) {
            resultListModel.clear();
            geocodeAddress();
        }
    }












    Rectangle{
        id:searchBar
        radius: 5
        color: "#FFFFFF"
        height: 50

        anchors.top: parent.top
        anchors.right: parent.right
        anchors.left: parent.left

        RowLayout{
            anchors.fill: parent
            anchors.rightMargin: 10
            anchors.leftMargin: 10
            spacing: 15
            CustomFontIcon{
                id:searchIcon
                icon: app.fontIcons._search
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        //console.log("Search");
                    }
                }
            }

            TextField{
                id:searchTextField
                placeholderText: qsTr("Search...")
                Layout.fillWidth: true

                Layout.bottomMargin: -10

                font.family: app.fontRobotoRegular.name

                Material.foreground: "#3C3C36"
                Material.accent: "#3C3C36"

                background: Rectangle{color:"transparent"}


                onFocusChanged: {
                    if(!focus){
                        Qt.inputMethod.hide();
                    } else {
                        if(searchTextField.text>""){
                            isShowBackground = true;
                        }
                    }
                }
                onTextChanged: {
                    if(text>"" && !isShowBackground){
                        isShowBackground = true;
                    }

                    if(!text.length > 0){
                        hidePin();
                        searchTextField.clear();
                        graphicsOverlay.visible = false
                    }
                    isSuggestion = true;
                }
            }

            CustomFontIcon{
                id:clearIcon
                icon: app.fontIcons._clear
                color:"#838383"
                visible: searchTextField.text.length >0
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        searchTextField.clear();
                        isShowBackground=false;
                    }
                }
            }
        }
    }

    Rectangle{
        id:results
        radius: 5
        color: "#FFFFFF"

        height: 250

        anchors.top:searchBar.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.topMargin: 10

        visible: isShowBackground

        ListView{
            id: searchResultListView
            anchors.fill: parent
            clip: true
            model: isSuggestion? locatorTask.suggestions:resultListModel
            spacing: 0
            delegate: Item {
                width: parent.width
                height: 50*app.scaleFactor
                Item {
                    anchors.fill: parent
                    visible: isSuggestion
                    Item{
                        width: parent.height
                        height: parent.height
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        Rectangle{
                            anchors.fill: parent
                            anchors.centerIn: parent
                            anchors.margins: parent.height*0.2
                            radius: parent.height
                            color:"#F4F4F6"
                        }

                        CustomFontIcon{
                            anchors.fill: parent
                            anchors.margins: parent.width*0.25
                            anchors.centerIn: parent
                            icon:app.fontIcons._map_pin
                            color:"#008DFF"
                        }
                    }

                    Label{
                        anchors.fill: parent
                        verticalAlignment: Label.AlignVCenter
                        elide: Label.ElideRight
                        clip: true
                        font.family: app.fontRobotoRegular.name
                        font.pixelSize: 16
                        leftPadding: 50*app.scaleFactor
                        rightPadding: 40*app.scaleFactor
                        color: "#838383"
                        text: isSuggestion? (locatorTask.suggestions && locatorTask.suggestions.get(index)? locatorTask.suggestions.get(index).label.replace(new RegExp(searchTextField.text,"ig"), "<font color=\"#3C3C36\"><b>"+searchTextField.text+"</b></font>") : ""):""
                        opacity: 0.9
                    }

                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            Qt.inputMethod.hide();
                            searchTextField.focus = false;
                            searchTextField.text = locatorTask.suggestions.get(index).label;
                            resultListModel.clear();
                            isSuggestion = false;
                        }
                    }

                    Rectangle{
                        width: parent.width-50*app.scaleFactor
                        height: 1
                        color: "#19000000"
                        visible: index != locatorTask.suggestions.count-1
                        anchors.bottom: parent.bottom
                        anchors.right: parent.right
                    }
                }

                Item {
                    anchors.fill: parent
                    visible: !isSuggestion
                    Item{
                        width: parent.height
                        height: parent.height
                        anchors.left: parent.left

                        Rectangle{
                            anchors.fill: parent
                            anchors.centerIn: parent
                            anchors.margins: parent.height*0.2
                            radius: parent.height
                            color:"#F4F4F6"
                        }

                        CustomFontIcon{
                            anchors.fill: parent
                            anchors.margins: parent.width*0.25
                            anchors.centerIn: parent
                            icon:app.fontIcons._map_pin
                            color:"#008DFF"
                        }

                        Label{
                            width: parent.width
                            height: parent.height*0.30
                            font.family: app.fontRobotoRegular.name
                            anchors.horizontalCenter: parent.horizontalCenter
                            horizontalAlignment: Label.AlignHCenter
                            text: !isSuggestion? distanceText:""
                            font.pixelSize: titleLabel.font.pixelSize*0.85
                            opacity: 0.4
                        }
                    }

                    Label{
                        id: titleLabel
                        width: parent.width
                        height: parent.height*0.45
                        font.family: app.fontRobotoRegular.name
                        anchors.top: parent.top
                        anchors.topMargin: parent.height*0.10
                        padding: 0
                        font.pixelSize: 13*app.scaleFactor
                        verticalAlignment: Label.AlignVCenter
                        elide: Label.ElideRight
                        clip: true
                        leftPadding: 55*app.scaleFactor
                        rightPadding: 40*app.scaleFactor
                        text: !isSuggestion? name:""
                        opacity: 0.9
                    }

                    Label{
                        width: parent.width
                        height: parent.height*0.4
                        anchors.top: titleLabel.bottom
                        verticalAlignment: Label.AlignTop
                        elide: Label.ElideRight
                        clip: true
                        font.pixelSize: titleLabel.font.pixelSize*0.85
                        padding: 0
                        leftPadding: 55*app.scaleFactor
                        font.family: app.fontRobotoRegular.name
                        rightPadding: 40*app.scaleFactor
                        text: !isSuggestion? address:""
                        opacity: 0.6
                    }

                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            Qt.inputMethod.hide();
                            searchTextField.focus = false;
                            var point = geometryJson;
                            isShowBackground = false;
                            resultSelected(point);
                        }
                    }

                    Rectangle{
                        width: parent.width-50*app.scaleFactor
                        height: 1
                        color: "#19000000"
                        visible: index != locatorTask.suggestions.count-1
                        anchors.bottom: parent.bottom
                        anchors.right: parent.right
                    }
                }
            }
        }

    }


    GeocodeParameters {
        id: geocodeParameters
        minScore: 75
        maxResults: 10
        resultAttributeNames: ["Place_addr", "Match_addr", "Postal", "Region"]
    }

    LocatorTask {
        id: locatorTask
        url: "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer"
        suggestions.suggestParameters: SuggestParameters{
            maxResults: 10
            countryCode: "USA"
        }
        suggestions.searchText: searchTextField.text.length > 0 ? searchTextField.text : ""
        onGeocodeStatusChanged: {
            if (geocodeStatus === Enums.TaskStatusCompleted) {
                if(geocodeResults.length>0){
                    for(var i in geocodeResults) {
                        var e = geocodeResults[i];
                        var point = e.displayLocation;
                        var name = e.label;
                        var address = e.attributes.Place_addr;
                        var linearUnit  = ArcGISRuntimeEnvironment.createObject("LinearUnit", {linearUnitId: Enums.LinearUnitIdMillimeters});
                        var angularUnit = ArcGISRuntimeEnvironment.createObject("AngularUnit", {angularUnitId: Enums.AngularUnitIdDegrees});
                        var results = GeometryEngine.distanceGeodetic(currentPoint, point, linearUnit, angularUnit, Enums.GeodeticCurveTypeGeodesic)
                        var degrees = results.azimuth1;
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

                        resultListModel.append({"name": name, "distanceText": "", "address": address, "geometryJson": point, "bearing": bearing, "degrees": degrees});
                    }
                }
            }
        }
    }

    DropShadow{
        visible: searchBar.visible
        anchors.fill: searchBar
        horizontalOffset: 3
        verticalOffset: 3
        radius: 8.0
        samples: 17
        color: "#80000000"
        source: searchBar
    }

    DropShadow{
        visible: results.visible
        anchors.fill: results
        horizontalOffset: 3
        verticalOffset: 3
        radius: 8.0
        samples: 17
        color: "#80000000"
        source: results
    }

    BusyIndicator {
        anchors.centerIn: parent
        running: locatorTask.loadStatus === Enums.LoadStatusLoading || locatorTask.geocodeStatus === Enums.TaskStatusInProgress
        Material.accent: "steelblue"
    }

    ListModel{
        id: resultListModel
    }

    function geocodeAddress() {
        if(currentLocatorTaskId > "" && locatorTask.loadStatus === Enums.LoadStatusLoading) locatorTask.cancelTask(currentLocatorTaskId);
        currentLocatorTaskId = locatorTask.geocodeWithParameters(searchTextField.text, geocodeParameters);
    }
}

