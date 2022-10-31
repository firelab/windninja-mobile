import QtQuick 2.7
import QtQuick.Controls 2.1

Rectangle{
    width: parent.width
    height: 40

    property string text: "Text"
    property string icon: "o"

    CustomFontIcon{
        id:icon
        icon: parent.icon
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: parent.left
        anchors.leftMargin: 10

        color:"#3C3C36"
    }

    Label{
        id:label
        text: parent.text
        font.family: app.fontRobotoRegular.name
        font.pixelSize: 16
        color:"#3C3C36"
        anchors.verticalCenter: parent.verticalCenter
        anchors.left: icon.right
        anchors.leftMargin: 20
    }
}
