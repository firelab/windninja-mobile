import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1


//POPUP WAIT...
Popup{
    id: popUpWaitServer;
    property alias busyIndicator: busyIndicatorServer
    property alias text: waitText.text
    x:(app.width - width)/2;
    y:(app.height - height)/2;
    width: app.width*0.8;
    height: app.height*0.25;
    modal: true;
    focus: true;
    background: Rectangle{ radius: 15; }

    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside;
    contentItem: Item{
        anchors.fill:parent;
        ColumnLayout{
            anchors.centerIn: parent
            anchors.margins: 10
            spacing: 20
            BusyIndicator {
                width: 0.3*popUpWaitServer.width
                height: 0.3*popUpWaitServer.height
                Layout.alignment: Qt.AlignHCenter
                id:busyIndicatorServer
                running: true
                Material.accent: "#008DFF"
            }
            Label {
                id:waitText
                Layout.fillWidth: true
                Layout.margins: 10
                text: qsTr("Waiting for server...")
                elide: Label.ElideRight
                font.bold: true
                font.family: app.fontRobotoMedium.name
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                font.pixelSize: 20
                Material.foreground: "#3C3C36"
                wrapMode: Text.WordWrap
            }
        }
    }
    onClosed: {
        waitText.text = "Waiting for server...";
        app.pageMain.forceActiveFocus();
    }
}
