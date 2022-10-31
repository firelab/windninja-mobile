import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import ArcGIS.AppFramework 1.0

Item {
    id:item
    property string idSim: ""
    property string simName: ""
    property string simStatusColor: ""

    visible: false

    height: 76 + (item.simStatusColor == "#59A0D9" ? 30 : 0)
    width: dropDownShare.width > dropDownDelete.width ? dropDownShare.width + 30 : dropDownDelete.width + 30


    Rectangle{

        anchors.fill: parent
        radius: 5

        ColumnLayout{
            anchors.fill: parent

            anchors.topMargin: 10
            anchors.bottomMargin: 10
            spacing: 0

            Rectangle{
                anchors.right: parent.right
                anchors.left: parent.left
                Layout.fillHeight: true
                visible: item.simStatusColor == "#59A0D9"
                Label{
                    id:dropDownDownload
                    text: qsTr("Download");
                    elide: Label.ElideRight
                    font.family: app.fontRobotoRegular.name
                    font.pixelSize: 14
                    Material.foreground: "#3C3C36"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    anchors.left: parent.left
                    anchors.rightMargin: 15
                    anchors.leftMargin: 15
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        item.visible = false
                        //console.log("Getting data...");
                        windNinjaServer.getTilesOutput(idSim.replace(/-/g, ""));
                    }
                }
            }

            Rectangle{
                anchors.right: parent.right
                anchors.left: parent.left
                Layout.fillHeight: true
                Label{
                    id:dropDownShare
                    text: qsTr("Share");
                    elide: Label.ElideRight
                    font.family: app.fontRobotoRegular.name
                    font.pixelSize: 14
                    Material.foreground: "#3C3C36"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.right: parent.right
                    anchors.left: parent.left
                    anchors.rightMargin: 15
                    anchors.leftMargin: 15
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        //console.log("Share");
                        item.visible = false;

                        //check if the sim was on the server
                        windNinjaServer.checkJobStatusAndShare(item.idSim);
                    }
                }
            }

            Rectangle{
                anchors.right: parent.right
                anchors.left: parent.left
                Layout.fillHeight: true
                Label{
                    id:dropDownDelete
                    text: qsTr("Delete Simulation");
                    elide: Label.ElideRight
                    font.family: app.fontRobotoRegular.name
                    font.pixelSize: 14
                    Material.foreground: "#3C3C36"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.left: parent.left
                    anchors.leftMargin: 15
                }
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        //console.log("Delete Simulation")
                        item.visible = false
                        simulationListView.simToDelete = item.idSim;
                    }
                }
            }
        }
    }
}
