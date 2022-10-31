import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtGraphicalEffects 1.0
import "../CustomComponents"

Page {
    id:pageHelp

    anchors.fill: parent
    Material.background: "#FFFFFF"


    header: CustomHeader{
        title: "Feedback"
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
        id:flickable
        clip:true
        contentHeight: columnLayout.height
        anchors.top: dummyHeader.bottom
        anchors.bottom: buttonsSeparator.top
        anchors.right: parent.right
        anchors.left: parent.left

        ColumnLayout{
            id:columnLayout
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 10
            spacing: app.height*0.02

            Rectangle{
                height: 1
                color: "transparent"
            }

            Label{
                text: "Support"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#008DFF"
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            Label{
                text: "Have a question or want to report a bug or feature request? Contact us at <font color=\"#008DFF\"><a href=\"mailto:wind.ninja.support@gmail.com\"  style=\"text-decoration: none;\">wind.ninja.support@gmail.com</a></font>"
                onLinkActivated: Qt.openUrlExternally(link)
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                lineHeight: 1.1
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            CustomTextFieldTitled{
                id:textFieldName;
                title: "Name"
                placeholderText: "Enter your name..."
                text: app.settings.userName;
            }

            CustomTextFieldTitled{
                id:textFieldMail;
                title: "Email"
                placeholderText: "email@adress.com"
                text: app.settings.userEmail;
            }

            CustomTextFieldTitled{
                id:textFieldSubject;
                title: "Subject"
                placeholderText: "Enter subject"
            }

            Label{
                id:messageLabel
                text: "Message"
                color: "#838383"
                font.pixelSize: 14
                font.family: app.fontRobotoRegular.name
                //anchors.top: parent.top
            }

            CustomTextArea{
                id:content
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: messageLabel.bottom
                anchors.topMargin: 3
                anchors.bottomMargin: 5
                anchors.leftMargin: 10
                anchors.rightMargin: 10
                placeholderText: "Enter message"
                onHeightChanged: {
                    flickable.contentY = flickable.contentHeight - flickable.height + 10
                }
            }
        }

}
        Rectangle{
            id:buttonsSeparator
            width: app.width
            height: 1
            color: "#838383"
            opacity: 0.25

            anchors.bottom: buttons.top
            anchors.bottomMargin: 10

        }

        RowLayout{
            id:buttons
            Layout.fillWidth: true
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 10

            CustomButton{
                text: "Cancel"
                color: "gray"
                onClicked: {
                    textFieldName.text = app.settings.userName;
                    textFieldMail.text = app.settings.userEmail;
                    textFieldSubject.text = "";
                    content.text = "";
                }
            }
            CustomButton{
                text: "Send"
                color: "blue"
                onClicked: {
                    if(app.isValidMail(textFieldMail.text) && textFieldName.text.length > 0 && textFieldSubject.text.length > 0 &&  content.text.length > 0 ){
                        var feedbackMessage = textFieldName.text + "\n" + textFieldMail.text + "\n" + textFieldSubject.text + "\n" + content.text
                        app.windNinjaServer.submitFeedback(app.settings.registrationId, feedbackMessage);
                        textFieldSubject.text = "";
                        content.text = "";
                    }
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
