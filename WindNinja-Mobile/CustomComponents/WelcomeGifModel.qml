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
    property bool isGif: false

    id:welcomePage
    clip:true

    AnimatedImage {
        id: gif
        height: parent.height*0.74
        width: parent.width
        source:imageSource
        visible: isGif
        fillMode: Image.PreserveAspectFit
        anchors.horizontalCenter: parent.horizontalCenter
    }



        Image {
            id: image
            width: parent.width*0.9
            fillMode: Image.PreserveAspectFit
            Layout.alignment: Qt.AlignHCenter
            source:imageSource
            visible: !isGif
            anchors.horizontalCenter: parent.horizontalCenter

        }
        Label{
            id:titleLabel
            text: title
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.leftMargin: parent.width*0.1
            anchors.rightMargin: parent.width*0.1
            anchors.topMargin: 20
            anchors.top: isGif ? gif.bottom : image.bottom
            Layout.preferredWidth: 0.8*parent.width
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            color: "#3C3C36"
            font.pixelSize: 20
            font.family: app.fontRobotoMedium.name
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
}
