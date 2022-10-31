import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtGraphicalEffects 1.0
import "../CustomComponents"
import "../Lib/js/DateFunctions.js" as DateFunctions

import ArcGIS.AppFramework 1.0

Item {
    id:delegateSimulationList
    width:parent.width
    height: 70

    property string idSim: "00000000-0000-0000-0000-000000000000"
    property string simStatusColor: "#D06056"
    property string simName: "simName"
    property string simDate: "dd/MM/yyyy - HH:mm"
    property int simDuration: 1
    property bool imported: false

    RowLayout{
        anchors.rightMargin: 10
        anchors.leftMargin: 10
        anchors.fill: parent

        Rectangle{
            id:simulationIcon
            height: 40
            width: 40
            radius: 4
            color: simStatusColor

            CustomFontIcon{
                anchors.centerIn: parent
                icon: {
                    switch(simStatusColor){
                    case "#838383":
                        app.fontIcons._close
                        break;
                    case "#D06056":
                        app.fontIcons._processing
                        break;
                    case "#59A0D9":
                        app.fontIcons._download
                        break;
                    case "#89D394":
                        app.fontIcons._view
                        break;
                    default:
                        app.fontIcons._simulation_list
                    }
                }
                color: "#FFFFFF"
            }
        }

        ColumnLayout{
            id:dataLayout
            Layout.preferredWidth: parent.width

            Label{
                text: qsTr(simName)
                font.bold: true
                font.family: app.fontRobotoMedium.name
                font.pixelSize: 16
                elide: Label.ElideRight
                Material.foreground: "#3C3C36"
                Layout.fillWidth: true

                CustomFontIcon{
                    id:iconImported
                    icon: app.fontIcons._plus;
                    color: "#59A0D9";
                    font.pixelSize: 22;
                    opacity: imported;
                    anchors.left: parent.right;
                    anchors.leftMargin: -1*(parent.width-parent.contentWidth)+5;
                    anchors.top: parent.top;
                    anchors.topMargin: -2;
                }
            }

            RowLayout{
                Layout.fillWidth: true
                Label{
                    text: qsTr("Submitted:<br/><font color=\"#3C3C36\">" + simDate + "</font>");
                    elide: Label.ElideRight
                    font.family: app.fontRobotoRegular.name
                    font.pixelSize: 14
                    Material.foreground: "#838383"
                    Layout.preferredWidth: delegateSimulationList.width*0.5
                }

                Label{
                    text: qsTr("Duration:<br/><font color=\"#3C3C36\">" + simDuration + "h</font>");
                    elide: Label.ElideLeft
                    font.family: app.fontRobotoRegular.name
                    font.pixelSize: 14
                    Material.foreground: "#838383"
                    Layout.fillWidth: true
                }
            }
        }

        CustomFontIcon{
            id:buttonShare
            icon: app.fontIcons._share
            color: "#3C3C36"
            anchors.top: parent.top
            anchors.topMargin: 5
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    //console.log("Share");
                    //check if the sim was on the server
                    AppFramework.clipboard.copy(idSim)
                    windNinjaServer.checkJobStatusAndShare(idSim);
                }
            }
        }

        Rectangle{
            width: 1
            color:"transparent"
        }

        CustomFontIcon{
            id:buttonDelete
            icon: app.fontIcons._delete
            color: "#3C3C36"
            anchors.top: parent.top
            anchors.topMargin: 5
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    dropDown.idSim = idSim
                    dropDown.simName = simName
                    dropDown.simStatusColor = simStatusColor
                    simulationListView.simToDelete = idSim;
                }
            }
        }
    }

    Rectangle{
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.leftMargin: -50
        anchors.rightMargin: -50
        height: 1
        color: "#838383"
        opacity: 0.25
    }

    MouseArea{
        anchors.fill: parent

        anchors.rightMargin: parent.width - (dataLayout.width+simulationIcon.width+20)

        onClicked: {
            if(modelData.downloaded){
                //console.log("Selected simulation: " + idSim + " " + simName);
                app.simulationSelected(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja")+"/" + idSim.replace(/-/g, '') + "/job.json");
            }else if (modelData.status === "failed"){
                //console.log("Failed simulation");
                generalPopUp.showCauseOfDelete(idSim);
            }else if (modelData.status === "succeeded"){
                //console.log("Getting data...");
                windNinjaServer.getTilesOutput(idSim.replace(/-/g, ""));
            }
        }
    }

    Component.onCompleted: {
        setValues();
    }

    function setStatusColor(){
        switch(modelData.status){
        default:
        case "failed":
            simStatusColor = "#838383"
            break;
        case "new":
        case "executing":
            simStatusColor = "#D06056";
            break;
        case "succeeded":
            simStatusColor = modelData.downloaded ? "#89D394" : "#59A0D9";
            break;
        }
    }

    function setValues(){
        idSim = modelData.idSim;
        simName = modelData.name;
        var currentNewDate = new Date(modelData.submittedTimestamp);
        currentNewDate.setMinutes(currentNewDate.getMinutes() + currentNewDate.getTimezoneOffset()*-1);
        simDate = currentNewDate.toLocaleDateString(Qt.locale(),"yyyy/MM/dd") + ", " +
                    currentNewDate.toLocaleTimeString(Qt.locale(),"HH:mm");
        simDuration = modelData.duration;
        imported = modelData.imported;
        setStatusColor();
    }

    function closeDropDown(){
        dropDown.visible = false;
    }
}
