import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtGraphicalEffects 1.0


Item {
    property color paneColor:"#393939"
    property string title: "Title"
    property string contentText: "Content Text"
    property string imageSource: ""
    property bool isFlickable: false
    property alias cardHeight: containRectangle.height

    id:welcomePage
    clip:true

    Image {
        id: image
        width: parent.width*0.9

        fillMode: Image.PreserveAspectFit
        Layout.alignment: Qt.AlignHCenter
        source:imageSource
        visible: !isFlickable
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: containRectangle.top;
    }

    Rectangle{
        id:containRectangle
        color:"white"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        anchors.leftMargin: -5
        anchors.rightMargin: -5

        Component.onCompleted: {
            if (imageSource == ""){
                anchors.top = parent.top
            }
        }

        height:titleLabel.height + contentLabel.height + titleLabel.anchors.topMargin + flickableElement.anchors.topMargin + 20
        width: parent.width*0.9

        Label{
            id:titleLabel
            text: title
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.leftMargin: parent.width*0.1
            anchors.rightMargin: parent.width*0.1
            anchors.topMargin: 20

            Layout.preferredWidth: 0.8*parent.width
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            color: "#3C3C36"
            font.pixelSize: 20
            font.family: app.fontRobotoMedium.name
        }
        Rectangle{
            id:gradientTransparentTop
            visible: imageSource == ""
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.top: titleLabel.bottom
            height: 50
            color: "transparent"
            OpacityMask {
                source: maskTop
                maskSource: gradientTransparentTop
            }
            LinearGradient {
                id: maskTop
                anchors.fill: parent
                gradient: Gradient {
                    GradientStop { position: 0.5; color: "white"}
                    GradientStop { position: 1; color: "transparent" }
                }
            }
            z: flickableElement.z+1
        }
        Flickable{
            id:flickableElement

            anchors.top: titleLabel.bottom
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right

            anchors.topMargin:10
            clip:true
            contentHeight: contentLabel.height+10


            Label{
                id:contentLabel
                text: contentText
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.right: parent.right
                anchors.left: parent.left
                anchors.leftMargin: parent.width*0.1
                anchors.rightMargin: parent.width*0.1

                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter

                Layout.preferredWidth: 0.8*parent.width
                color: "#838383"
                font.pixelSize: 16
                font.family: app.fontRobotoRegular.name
                Component.onCompleted: {
                    if(imageSource == ""){
                        text = "\n"+text
                    }
                }
            }
        }
        Rectangle{
            id:gradientTransparentBottom
            visible: imageSource == ""
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            height: 50
            color: "transparent"
            OpacityMask {
                source: maskBottom
                maskSource: gradientTransparentBottom
            }
            LinearGradient {
                id: maskBottom
                anchors.fill: parent
                gradient: Gradient {
                    GradientStop { position: 0.2; color: "transparent"}
                    GradientStop { position: 1; color: "white" }
                }
            }
        }
    }

    DropShadow{
        anchors.fill: containRectangle
        horizontalOffset: 0
        verticalOffset: -3
        radius: 8.0
        samples: 17
        color: "#33000000"
        source: containRectangle
        visible: imageSource != ""
    }
}
