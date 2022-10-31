import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

TextField{
    placeholderText: qsTr("placeholderText")

    Layout.fillWidth: true
    Layout.rightMargin: 30
    Layout.leftMargin: 30

    implicitWidth: 100
    implicitHeight: 43

    font.family: app.fontRobotoRegular.name

    Material.foreground: "#2F619C"
    Material.accent: "#2F619C"

    background: Rectangle {
        radius: 4
        color: "#F4F4F6"
        implicitWidth: 100
        implicitHeight: 24
        anchors.fill: parent
        anchors.bottomMargin: 5
        anchors.rightMargin: -10
        anchors.leftMargin: -10
    }
}
