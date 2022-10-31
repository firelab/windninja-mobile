import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import "../CustomComponents"

Page {
    id:pageRegister

    anchors.fill: parent
    Material.background: "#FFFFFF"

    ColumnLayout{
        anchors.fill:parent
        spacing: app.height*0.02

        Rectangle{
            height: logoImage.height*0.05
            color: "transparent"
        }

        Image{
            id:logoImage
            Layout.preferredWidth: app.height*0.15
            Layout.preferredHeight: app.height*0.15
            Layout.alignment: Qt.AlignHCenter
            source:"../Assets/launch-screen-logo.png"
        }

        ColumnLayout{
            spacing: app.height*0.015

            Label{
                text: "Account Registration"
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                color: "#3C3C36"
                font.pixelSize:  20
                font.bold: true
                font.family: app.fontRobotoMedium.name
            }

            Label{
                text: "Please enter your name and email address to register WindNinja on this device. You will notified once your account has been verified."
                Layout.preferredWidth: 0.9*app.width
                anchors.horizontalCenter: parent.horizontalCenter
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                color: "#838383"
                lineHeight: 1.3
                font.pixelSize:  16
                font.family: app.fontRobotoRegular.name
            }

            CustomTextField{
                id:registerName
                placeholderText: qsTr("Name")
                text: app.settings.userName !== "" ? app.settings.userName : "";
            }

            CustomTextField{
                id:registerEmail
                placeholderText: qsTr("Email")
                text: app.settings.userEmail !== "" ? app.settings.userEmail : "";
            }

            RowLayout{
                id: registrationButtons
                anchors.horizontalCenter: parent.horizontalCenter
                CustomButton{
                    id:registerSkipButton;
                    text: qsTr("Skip");

                    onClicked: {
                        pageLoader.sourceComponent = undefined;

                        app.windNinjaServer.checkRegistration();
                        pageMainLoader.source = "PageMain.qml"
                    }
                }
                CustomButton{
                    id:registerRegisterButton;
                    color: "blue";
                    enabled: registerName.text.length > 0 && registerEmail.text.length > 0;
                    text: qsTr("Register");
                    onClicked: {
                        if(app.isValidMail(registerEmail.text)){
                            //console.log("Saving configuration")
                            app.settings.userName = registerName.text
                            app.settings.userEmail = registerEmail.text

                            app.windNinjaServer.register();
                        }else{
                            generalPopUp.badMailWarn();
                            registerEmail.clear();
                        }
                    }
                }
            }
        }

        Label{

            text: "If you would like to explore the app features first, you can view test data provided and register later through the settings menu. <font color=\"#3C3C36\"><b>You will not be able to run new simulations until you register.</b></font>"
            Layout.preferredWidth: 0.9*app.width
            anchors.horizontalCenter: parent.horizontalCenter
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            color: "#838383"
            lineHeight: 1.1
            font.pixelSize:  14
            font.family: app.fontRobotoMedium.name
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
