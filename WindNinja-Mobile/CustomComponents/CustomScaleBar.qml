import QtQuick 2.7
import QtQuick.Controls 2.1
import Esri.ArcGISRuntime 100.12

Item {
    id: scaleBar

    property MapView map: null

    signal clicked()
    signal doubleClicked()

    implicitWidth: 70
    implicitHeight: 20

    width: 70
    height: 20

    Rectangle{
        id: background
        anchors.fill: parent
        radius: 2
        opacity: 0.55
        color: "#FFFFFF"
    }

    Label{
        text: "500 mi"
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
        //wrapMode: Text.WordWrap
        horizontalAlignment: Text.AlignHCenter
        color: "#FFFFFF"
        font.pixelSize:  8
        font.family: app.fontRobotoRegular.name
    }

    Rectangle{
        id: borders
        anchors.fill: parent
        anchors.topMargin: 5
        anchors.leftMargin: 5
        anchors.rightMargin: 5
        anchors.bottomMargin: 3
        color: "transparent"
        CustomBorder{
            opacity: parent.opacity
            leftBorderwidth: 2
            rightBorderwidth: 2
            bottomBorderwidth: 2
            borderColor: "white"
        }
    }

    MouseArea {
        anchors.fill: parent

        onClicked: {
            scaleBar.clicked();
        }

        onDoubleClicked: {
            scaleBar.doubleClicked();
        }
    }



    Component.onCompleted: {
        if (!map && parent && parent.objectType && parent.objectType === "MapView") {
            map = parent;
        }
    }
}
