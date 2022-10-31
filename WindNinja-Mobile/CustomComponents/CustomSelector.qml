import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

Popup{
    property int delegateHeight: 50
    property string selection: ""
    property alias model: list.model
    property alias title: titleLabel.text

    signal okClose(string valueSelected);
    signal cancelClose();

    id:popup
    width: app.width - 120
    height: app.height - 200

    Component.onCompleted: {
        var totalHeight = titleLabel.height + list.height + separator.height + buttons.height
        if(totalHeight < app.height - 200){
            height = totalHeight
        }
    }

    x:(app.width/2) - (width/2)
    y:(app.height/2) - (height/2) - 56*app.scaleFactor

    padding: 0
    modal: true
    focus: true
    clip:true

    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

    background: Rectangle{
        radius: 3
    }

    onClosed: {
        app.pageMain.forceActiveFocus();
    }

    contentItem: Rectangle{
        radius: 3

        Label{
            id:titleLabel
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.leftMargin: 20
            anchors.rightMargin: 20
            height: 50

            font.family: app.fontRobotoMedium.name
            horizontalAlignment: Qt.AlignHCenter
            verticalAlignment: Qt.AlignVCenter
            font.pixelSize: 18
            elide: Label.ElideRight
            color: "#3C3C36"

            text: qsTr("Title")

            Component.onCompleted: {
                while(truncated){
                    font.pixelSize = font.pixelSize-2;
                }
            }
        }

        Flickable{
            anchors.top: titleLabel.bottom
            anchors.bottom: separator.top
            anchors.left: parent.left
            anchors.right: parent.right

            clip:true
            contentHeight: list.height

            ListView{
                id: list
                clip:true
                Layout.alignment: Qt.AlignHCenter
                width: parent.width;
                height: model.length * delegateHeight
                orientation: ListView.Vertical
                interactive: false
                highlightRangeMode: ListView.StrictlyEnforceRange
                spacing: 0
                model:[]
                delegate: RadioButton{
                    height: delegateHeight
                    width: list.width*0.9
                    Layout.margins: 0
                    anchors.left: parent.left
                    anchors.leftMargin: 20
                    spacing: 20
                    text:qsTr(modelData)
                    Material.accent: "#008DFF"
                    font.family: app.fontRobotoRegular.name
                    font.pixelSize: 16
                    onClicked: {
                        selection = text;
                    }
                }
            }
        }

        Rectangle{
            id:separator
            anchors.horizontalCenter: parent.horizontalCenter
            width: popup.width
            height: 1
            color: "#000000"
            opacity: 0.12
            anchors.bottom: buttons.top
        }

        RowLayout{
            id:buttons
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 50
            spacing: 0



            Rectangle{
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "transparent"
            }

            Label{
                Layout.fillHeight: true
                Layout.minimumWidth: app.width*0.2
                Layout.maximumWidth: app.width*0.25

                font.family: app.fontRobotoMedium.name
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                font.pixelSize: 14
                elide: Label.ElideRight
                color: "#008DFF"

                text: qsTr("Cancel")
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        popup.close();
                        selection = "";
                        cancelClose();
                    }
                }
            }

            Label{
                Layout.fillHeight: true
                Layout.minimumWidth: app.width*0.2
                Layout.maximumWidth: app.width*0.25

                font.family: app.fontRobotoMedium.name
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                font.pixelSize: 14
                elide: Label.ElideRight
                color: "#008DFF"

                text: qsTr("Ok")
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        popup.close();
                        okClose(selection);
                    }
                }
            }
        }
    }
}
