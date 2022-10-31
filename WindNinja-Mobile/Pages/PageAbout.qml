import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtGraphicalEffects 1.0
import "../CustomComponents"

import ArcGIS.AppFramework 1.0

Page {
    id:pageAbout

    anchors.fill: parent
    Material.background: "#FFFFFF"


    header: CustomHeader{
        title: "About"
        origin: "./PageSettings.qml"
    }
    Rectangle{
        id:dummyHeader
        anchors.bottom: parent.top
        anchors.right: parent.right
        anchors.left: parent.left
        height: 20
    }

    DropShadow{
        anchors.fill: dummyHeader
        horizontalOffset: 0
        verticalOffset: 3
        radius: 8.0
        samples: 17
        color: "#33000000"
        source: dummyHeader
    }


    Flickable{

        clip:true
        contentHeight: content.height
        anchors.fill: parent

        ColumnLayout{
            id:content
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 10
            spacing: app.height*0.02

            Rectangle{
                height: 1
                color: "transparent"
            }

            Label{
                text: "WindNinja Mobile"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#008DFF"
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            Label{
                text: "Wind is one of the most influential environmental factors affecting wildland fire behavior. The complex terrain of fire-prone landscapes causes local changes in wind speed and direction that are not predicted well by standard weather models or expert judgment. WindNinja was developed to help fire managers predict these winds."
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                lineHeight: 1.1
                font.pixelSize:  14
                font.family: app.fontRobotoRegular.name
            }

            Label{
                id:versionLabel
                text: "Version"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#838383"
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            Label{
                text: app.currentVersion
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                lineHeight: 1.1
                font.pixelSize:  14
                font.family: app.fontRobotoRegular.name

                anchors.top:versionLabel.bottom
                anchors.topMargin: 3
            }

            Rectangle{
                width: app.width
                height: 1
                color: "#838383"
                opacity: 0.25
            }

            Label{
                text: "Acknowledgements"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#008DFF"
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            Label{
                id:developedByLabel
                text: "Developed By"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#838383"
                font.pixelSize:  14
                font.family: app.fontRobotoRegular.name
            }

            Label{
                text:
                    "<b>Missoula Fire Sciences Laboratory</b><br/>"+
                    "Rocky Mountain Research Station<br/>"+
                    "USDA Forest Service<br/>"+
                    "5775 W. US Highway 10<br/>"+
                    "Missoula, MT 59808<br/>"+
                    "<br/>"+
                    "<b>Technosylva Inc.</b><br/>"+
                    "La Jolla, CA 90237<br/>"+
                    "www.technosylva.com"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                lineHeight: 1.1
                font.pixelSize:  16
                font.family: app.fontRobotoRegular.name

                anchors.top:developedByLabel.bottom
                anchors.topMargin: 3
            }

            Label{
                id:sponsoredByLabel
                text: "Sponsored By"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#838383"
                font.pixelSize:  14
                font.family: app.fontRobotoRegular.name
            }

            Label{
                text:
                    "USDA Forest Service\n" +
                    "Center for Environmental Management\n" +
                    "of Military Lands at Colorado State University\n"+
                    "Joint Fire Sciences Program\n"+
                    "Washington State University"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                lineHeight: 1.1
                font.pixelSize:  16
                font.family: app.fontRobotoRegular.name

                anchors.top:sponsoredByLabel.bottom
                anchors.topMargin: 3
            }

            Rectangle{
                height: 1
                color: "transparent"
            }
        }
    }

    focus: true // important - otherwise we'll get no key events
    Keys.onReleased: {
        if (event.key === Qt.Key_Back) {
            event.accepted = true
            backButtonPressed()
        }
    }
}
