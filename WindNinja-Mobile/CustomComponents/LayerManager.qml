import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

import QtQuick.LocalStorage 2.0
import "../Lib/js/DatabaseFunctions.js" as DatabaseFunctions

import "../Delegates"

Item {
    id:item

    anchors.fill: parent

    property string layerSelected: "";
    FileBrowser{
        id:myFileBrowser
        width:parent.width
        height: parent.height
        folder:tpkBrowserElement.fileBrowserAlias.shortcuts.documents
        onFileSelected: {
            var fileSplit=file.split("/")
            var fileLen=fileSplit.length
            var fileFinal=fileSplit[fileLen-1]
            //console.log("FileBrowser: file selected: " + fileSelected)
            if(file===""){
                //console.log("FileBrowser: No file selected...")
            }else{

                DatabaseFunctions.addLayers(fileFinal, "ArcGISTiledLayer", [file],"0", 1)
            }
            tpkBrowserElement.visible = false
            tpkBrowserElement.visible = true

        }
    }
    Rectangle{
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        height: content.height+20



        radius: 5
        color: "#FFFFFF"

        Rectangle{
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            color: parent.color
            height: parent.radius
        }

        ColumnLayout{
            id:content
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.bottom: parent.bottom

            anchors.leftMargin: 10
            anchors.rightMargin: 10
            anchors.bottomMargin: 10


            RowLayout{
                id:titleBaseMaps
                Layout.fillWidth: true
                spacing: 20

                Label{
                    text: "Base Maps"
                    color: "#008DFF"
                    font.pixelSize:  14
                    font.family: app.fontRobotoMedium.name
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                CustomFontIcon{
                    color: "#3C3C36"
                    icon: app.fontIcons._add_tpk
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            myFileBrowser.open()
                        }
                    }
                }

                CustomFontIcon{
                    color: "#3C3C36"
                    icon: app.fontIcons._clear
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            item.visible = false
                        }
                    }
                }
            }

            TpkBrowser{
                id:tpkBrowserElement
                Layout.preferredHeight: 150
                Layout.fillWidth: true
            }

            Rectangle{
                id:separator
                anchors.right: parent.right
                anchors.left: parent.left
                anchors.rightMargin: -20
                anchors.leftMargin: -20
                height: 1
                color: "#838383"
                opacity: 0.25
            }

            RowLayout{
                id:titleMapLayers
                Layout.fillWidth: true
                spacing: 10

                Label{
                    text: "Map Layers"
                    color: "#008DFF"
                    font.pixelSize:  14
                    font.family: app.fontRobotoMedium.name
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }
            }

            CustomListItemSwitch{
                id:switchOfflineMap
                text: "Offline Map"
                height: 40
                icon: app.fontIcons._layers
                onClicked: check(text)
            }

            CustomListItemSwitch{
                visible: false
                id:switchGeoMac
                text: "GeoMac"
                height: 40
                icon: app.fontIcons._layers
                onClicked: check(text)
            }

            CustomListItemSwitch{
                id:switchModis
                text: "MODIS"
                height: 40
                icon: app.fontIcons._layers
                onClicked: check(text)
            }

            CustomListItemSwitch{
                id:switchViirs
                text: "VIIRS"
                height: 40
                icon: app.fontIcons._layers
                onClicked: check(text)
            }                        

            CustomListItemSwitch{
                id:switchFuelModels
                text: "Fuel Models"
                height: 40
                icon: app.fontIcons._layers
                onClicked: check(text)
                visible: false
            }

            CustomListItemSwitch{
                visible: false
                id:switchVegetation
                text: "Vegetation"
                height: 40
                icon: app.fontIcons._layers
                onClicked: check(text)
            }

            CustomListItemSwitch{
                id:switchFirePerimeters
                text: "Fire Perimeters"
                height: 40
                icon: app.fontIcons._layers
                onClicked: check(text)
            }
        }
    }

    function unCheckAll(){
        switchOfflineMap.checked = false;
        switchGeoMac.checked = false;
        switchModis.checked = false;
        switchViirs.checked = false;
        switchFuelModels.checked = false;
        switchVegetation.checked = false;

        layerSelected = "";
    }

    function check(switchText){

        if(switchText === "Offline Map"){
            switchOfflineMap.checked = !switchOfflineMap.checked;
        }

        if(switchText === "GeoMac"){
            switchGeoMac.checked = !switchGeoMac.checked;
        }

        if(switchText === "MODIS"){
            switchModis.checked = !switchModis.checked;
        }

        if(switchText === "VIIRS"){
            switchViirs.checked = !switchViirs.checked;
        }

        if(switchText === "Fuel Models"){
            switchFuelModels.checked = !switchFuelModels.checked;
        }

        if(switchText === "Vegetation"){
            switchVegetation.checked = !switchVegetation.checked;
        }

        if(switchText === "Fire Perimeters"){
            switchFirePerimeters.checked = !switchFirePerimeters.checked;
        }

        layerSelected = switchText;
        pageMain.changeLayer(layerSelected);
    }
}
