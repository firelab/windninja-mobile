import QtQuick 2.0
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1

Item {

    property alias title: titleLabel.text;
    property alias text: contentLabel.text;
    property alias textFieldText: textField.text;
    property alias textFieldPlaceholderText: textField.placeholderText;

    signal okPressed(var value);

    anchors.fill: parent;

    Popup{

        property string name: ""

        id:popup
        width: app.width - 120
        height: titleLabel.height + contentLabel.height + separator.height + buttons.height + textField.height + 20

        x:(app.width/2) - (width/2)
        y:(app.height/2) - (height/2)

        padding: 0
        modal: true
        focus: true
        clip:true

        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutsideParent

        background: Rectangle{
            radius: 3
        }

        contentItem: Rectangle{

            Label{
                id:titleLabel
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top

                anchors.leftMargin: 0.05*app.width
                anchors.rightMargin: 0.05*app.width

                height: 60

                font.family: app.fontRobotoMedium.name
                verticalAlignment: Qt.AlignVCenter
                font.pixelSize: 20
                elide: Label.ElideRight
                color: "#3C3C36"

                text: qsTr("Title")
            }

            Label{
                id:contentLabel
                text: "Text."
                Layout.preferredWidth: 0.85*app.width
                wrapMode: Text.WordWrap
                color: "#838383"
                lineHeight: 1.1
                font.pixelSize:  16
                font.family: app.fontRobotoRegular.name
                verticalAlignment: Qt.AlignVCenter

                height: lineCount*20

                anchors.leftMargin: 0.05*app.width
                anchors.rightMargin: 0.05*app.width

                anchors.top: titleLabel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                onTextChanged: {

                }
            }

            CustomTextField{
                id:textField
                anchors.top: contentLabel.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.topMargin: 3
                anchors.leftMargin: 20
                anchors.rightMargin: 20
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
                            okPressed(textFieldText);
                            popup.close();
                        }
                    }
                }
            }
        }
        onClosed: {
            textField.text = "";
            app.pageMain.forceActiveFocus();
        }

    }


    function open(){
        popup.open()
    }

    function close(){
        popup.close()
    }
}
