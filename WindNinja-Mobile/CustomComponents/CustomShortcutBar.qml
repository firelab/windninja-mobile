import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import "../Lib/js/UtilFunctions.js" as UtilFunctions

Rectangle{
    color: "#FFFFFF"
    height: 50

    RowLayout{
        anchors.fill: parent
        spacing: 0

        Rectangle{
            id:simulationsElement
            Layout.fillWidth: true
            Layout.fillHeight: true
            CustomFontIcon{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.verticalCenter
                anchors.bottomMargin: -5
                icon: app.fontIcons._simulation_list
                Layout.fillWidth: true
            }
            Label{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.verticalCenter
                anchors.topMargin: 10
                text: "Simulations"
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                font.pixelSize: 10
                font.family: app.fontRobotoRegular.name
            }
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    //console.log("Pressed icon: Simulation list")
                    pageLoader.source = "../Pages/PageSimulations.qml"
                }
            }
        }

        Rectangle{
            id:mapLayersElement
            Layout.fillWidth: true
            Layout.fillHeight: true
            CustomFontIcon{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.verticalCenter
                anchors.bottomMargin: -5
                icon: app.fontIcons._layers
                Layout.fillWidth: true
            }
            Label{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.verticalCenter
                anchors.topMargin: 10
                text: "Map Layers"
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                font.pixelSize: 10
                font.family: app.fontRobotoRegular.name
            }
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    //console.log("Pressed icon: Map Layers")
                    layerManager.visible = !layerManager.visible
                }
            }
        }

        Rectangle{
            id:resetMapElement
            Layout.fillWidth: true
            Layout.fillHeight: true
            CustomFontIcon{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.verticalCenter
                anchors.bottomMargin: -5
                icon: app.fontIcons._settings
                Layout.fillWidth: true
            }

            Label{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.verticalCenter
                anchors.topMargin: 10
                text: "Settings"
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                font.pixelSize: 10
                font.family: app.fontRobotoRegular.name
            }
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    //console.log("Settings");
                    pageLoader.source = "../Pages/PageSettings.qml"
                }
            }
        }

        Rectangle{
            id:myLocationElement
            Layout.fillWidth: true
            Layout.fillHeight: true
            CustomFontIcon{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.verticalCenter
                anchors.bottomMargin: -5
                icon: app.fontIcons._my_location
                Layout.fillWidth: true
            }
            Label{
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.verticalCenter
                anchors.topMargin: 10
                text: "My Location"
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                font.pixelSize: 10
                font.family: app.fontRobotoRegular.name
            }
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    //console.log("Pressed icon: My Location")
                    if(app.gpsPositionSource.active){
                        zoomToGPS()
                    }else{
                       app.gpsPositionSource.active = true;
                    }


pageMain.map.retryLoad();


                }
            }
        }
    }
}
