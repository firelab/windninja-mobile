import QtQuick 2.7

Rectangle
{
    color: "transparent"
    anchors.fill: parent
    property int leftBorderwidth : 0
    property int rightBorderwidth : 0
    property int topBorderwidth : 0
    property int bottomBorderwidth : 0

    property int commonBorderWidth : 0

    z : -1

    property string borderColor : "black"

    Rectangle{
        id: leftBorder
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        color: borderColor
        width: commonBorderWidth == 0 ? leftBorderwidth : commonBorderWidth
    }

    Rectangle{
        id: rightBorder
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        color: borderColor
        width: commonBorderWidth == 0 ? rightBorderwidth : commonBorderWidth
    }

    Rectangle{
        id: topBorder
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        color: borderColor
        height: commonBorderWidth == 0 ? topBorderwidth : commonBorderWidth
    }

    Rectangle{
        id: bottomBorder
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        color: borderColor
        height: commonBorderWidth == 0 ? bottomBorderwidth : commonBorderWidth
    }
}
