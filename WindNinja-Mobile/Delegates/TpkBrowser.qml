import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import ArcGIS.AppFramework 1.0
import QtQuick.Dialogs 1.3

import QtQuick.LocalStorage 2.0
import "../Lib/js/DatabaseFunctions.js" as DatabaseFunctions

Item {
    id:itemBaseMaps

    property alias fileBrowserAlias: fileDialog

    FileDialog
    {
        id: fileDialog
        title: "str_action_settings_tpk_dialog"
        folder:
        {
            shortcuts.documents
        }

        nameFilters: ["TPK files (*.tpk)"]
        onAccepted:
        {
            var fileSelected=fileDialog.fileUrl.toString()
            var fileSplit=fileSelected.split("/")
            var fileLen=fileSplit.length
            var file=fileSplit[fileLen-1]

            if (Qt.platform.os=="ios")
            {
                //console.log("FileDialog: iOS platform OS")
                DatabaseFunctions.saveParameter("TPK_PATH", '~/'+file);
            }
            else if (Qt.platform.os=="android")
            {
                //console.log("FileDialog: Android platform OS")
                DatabaseFunctions.saveParameter("TPK_PATH", fileSelected.substring(7));
            }else{
                //console.log("FileDialog: Other platform OS")
                DatabaseFunctions.saveParameter("TPK_PATH", fileSelected.substring(8));
            }
        }
        onRejected:
        {
            //console.log("Canceled")
        }
        visible: false
    }   

    ColumnLayout{
        anchors.centerIn: itemBaseMaps
        anchors.fill: parent
        anchors.margins: 10        

        Flickable{
            id:fliki
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: parent.width
            clip:true
            GridLayout{
                id: baseMapListview
                anchors.fill:parent
                columns: 4
                Repeater{
                    id:repeaterIdentifier
                    model:DatabaseFunctions.getAllLayers()
                    BaseMapButton{
                        Layout.fillWidth: true
                        Layout.preferredWidth: 0.2*baseMapListview.width
                    }
                    onVisibleChanged: {
                        if(visible){
                            model = DatabaseFunctions.getAllLayers()
                            var test = Math.ceil((DatabaseFunctions.countLayers()/4)%DatabaseFunctions.countLayers())
                            fliki.contentHeight = 90 * test
                        }
                    }
                }
            }
        }
    }
}
