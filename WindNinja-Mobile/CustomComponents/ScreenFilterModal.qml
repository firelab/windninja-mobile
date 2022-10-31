import QtQuick 2.7

Item {
    anchors.fill: parent
    visible: false
    z:1
    Rectangle{
        id:modalFilter
        anchors.fill: parent
        color: "black"
        opacity: 0.5
        MouseArea{
            anchors.fill: parent
        }
    }
}
