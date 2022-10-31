import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import ArcGIS.AppFramework 1.0
import Esri.ArcGISRuntime 100.12
import QtGraphicalEffects 1.0

import "../CustomComponents"

import QtQuick.LocalStorage 2.0
import "../Lib/js/DatabaseFunctions.js" as DatabaseFunctions

Item {
    width: parent.width/5
    height: 75
    property string buttonName: modelData.name
    property string buttonImage: modelData.imagePath
    property string baseMap: "tpk"
    property string mapDistintive: "localTpk"

    property string layerType: modelData.layerType
    property string tpkPaths: modelData.paths

    property bool clickedOnTrash: false

    signal deleteTPK()

    id:itemBaseMaps

    function changeBasemap(name) {

        if(modelData.name == "Fuel Models" && modelData.deletable == 0){
            switchFuelModels.checked = true

            localTpk.baseLayers.clear();
            map.basemap = localTpk;
            app.currentBaseMap = name;
            layerSelected = "Fuel Models";
            map.layerVisibilityFuelModels = true;
            return;
        }else{
            switchFuelModels.checked = false
            map.layerVisibilityFuelModels = false;
        }

        //console.log("changeBasemap")
        if(true){


            localTpk.baseLayers.clear();

            var pathsArray = tpkPaths.split(",")

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
        //console.log("Changed layer to: " + name);
    }

    Basemap{
        id: localTpk
        name: "localTpk"
        ArcGISTiledLayer  {
            url: "";
        }
    }

    ColumnLayout{
        id: columnBaseMapButton
        anchors.fill: parent
        anchors.centerIn: parent
        Item{
            id:myBaseMapButton
            anchors.centerIn: parent
            Layout.fillWidth: true
            Layout.preferredHeight: 0.75*itemBaseMaps.height
            Image {
                id: img
                height: myBaseMapButton.height*0.9
                fillMode: Image.PreserveAspectFit
                property bool adapt: true
                source: buttonImage == 0 ? "../Assets/Map/tpk.jpg" : buttonImage;
                anchors.centerIn: parent

                Rectangle {
                    anchors.centerIn: parent
                    width: img.adapt ? img.width : Math.min(img.width, img.height)
                    height: img.adapt ? img.height : width                    
                    color: "transparent"
                    visible: app.currentBaseMap === buttonName
                    border.color: app.currentBaseMap === buttonName ? "#008DFF" : "transparent"
                    border.width: 1.5
                }

                MouseArea{
                    anchors.fill: parent
                    onClicked:{
                        if(DatabaseFunctions.layerExist(modelData.name)){
                            changeBasemap(modelData.name);
                        }else{
                            DatabaseFunctions.deleteLayers(modelData.name)                            
                            itemBaseMaps.visible = false
                        }
                    }
                }

                CustomFontIcon{
                    id: trashIcon
                    icon: app.fontIcons._delete
                    visible: modelData.deletable === 1
                    color:"#ffffff"
                    anchors.top: parent.top
                    anchors.topMargin: 3
                    anchors.right: parent.right
                    anchors.rightMargin: 5
                    Component.onCompleted: {
                        var aspectRatio = 5;
                        var tempHeigth = parent.height / aspectRatio;
                        var tempWidth = tempHeigth * trashIcon.width / trashIcon.height

                        trashIcon.height = tempHeigth;
                        trashIcon.width = tempWidth;
                    }
                }

                Rectangle{
                    visible: trashIcon.visible
                    color: "transparent";
                    height: 30;
                    width: 20;
                    anchors.top: parent.top;
                    anchors.right: parent.right;

                    MouseArea{
                        anchors.fill:parent
                        onClicked:{
                            DatabaseFunctions.deleteLayers(modelData.name)

                            if(app.currentBaseMap === modelData.name){
                                map.basemap = ArcGISRuntimeEnvironment.createObject("BasemapImageryWithLabels");
                                app.currentBaseMap = "Imagery"
                            }

                            tpkBrowserElement.visible = false
                            tpkBrowserElement.visible = true
                        }
                    }
                }
            }
        }

        Rectangle{
            anchors.top: myBaseMapButton.bottom
            anchors.horizontalCenter: myBaseMapButton.horizontalCenter

            Layout.preferredWidth: img.width
            width: img.width
            height: label.height
            color: "transparent"

            Label{
                id: label
                text: qsTr(buttonName)
                font.bold: app.currentBaseMap === buttonName ? true : false
                font.family:app.fontRobotoRegular.name
                font.pixelSize: 14
                Material.foreground: app.currentBaseMap === buttonName ? "#008DFF" : "#3C3C36"
                horizontalAlignment: Text.AlignHCenter
                elide: Label.ElideRight
                Layout.preferredWidth: img.width
                width: img.width
            }
        }
    }
}
