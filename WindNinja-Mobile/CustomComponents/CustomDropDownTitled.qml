import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1

Rectangle{
    anchors.left: parent.left
    anchors.right: parent.right
    height: titleLabel.height + dropDown.height
    property string title: "Title"
    property alias text: dropDown.text
    property alias placeholderText: dropDown.placeholderText

    Label{
        id:titleLabel
        text: title
        color: "#838383"
        font.pixelSize:  14
        font.family: app.fontRobotoRegular.name
        anchors.top: parent.top
    }

    CustomDropDown{
        id:dropDown
        anchors.top: titleLabel.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.topMargin: 3
        anchors.leftMargin: 10
        anchors.rightMargin: 10
    }
}
