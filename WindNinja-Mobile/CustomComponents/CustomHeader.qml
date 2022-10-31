import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

Rectangle{
    height: 56*app.scaleFactor
    width: parent.width
    color: "#3C3C36"

    id:item
    property string title: "title"
    property var origin: undefined


    Rectangle{
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: parent.width*0.12
        color: "transparent"

        CustomFontIcon{
            id:backButton
            anchors.centerIn: parent
            icon: item.origin === undefined ? app.fontIcons._back_arrow : app.fontIcons._close;
            color: "#FFFFFF"
        }

        MouseArea{
            anchors.fill: parent
            onClicked: {
                //console.log("Back")
                if(item.origin === undefined){
                    pageLoader.sourceComponent = item.origin;
                }else{
                    pageLoader.source = "../Pages/" + item.origin;
                }
            }
        }
    }

    Label {
        Layout.fillWidth: true
        text: qsTr(title)
        elide: Label.ElideRight
        font.bold: true
        font.family: app.fontRobotoMedium.name
        horizontalAlignment: Qt.AlignHCenter
        verticalAlignment: Qt.AlignVCenter
        font.pixelSize: 20
        color: "#FFFFFF"
        anchors.centerIn: parent
    }
}


