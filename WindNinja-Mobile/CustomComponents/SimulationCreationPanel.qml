import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1

Item {
    id:item
    anchors.bottom: parent.bottom
    anchors.right: parent.right
    anchors.left: parent.left
    height: content.height < parent.height ? content.height +20 : parent.height+20

    property alias mailSwitchChecked: selectorEmail.checked;
    property alias smsSwitchChecked: selectorSms.checked;

    signal simulatePressed(var name, var duration, var emailChecked, var smsChecked)


    Rectangle{
        anchors.fill: parent
        radius: 5
        color: "#FFFFFF"

        Flickable{
            clip:true
            contentHeight: content.height +20
            anchors.fill: parent

            Rectangle{
                color:parent.color
                height: parent.radius*2
                anchors.bottom: parent.bottom
                anchors.right: parent.right
                anchors.left: parent.left
            }

            ColumnLayout{
                id:content
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top

                anchors.leftMargin: 10
                anchors.rightMargin: 10
                anchors.topMargin: 20

                spacing: 10

                Label{
                    text: "Enter Simulation Details"
                    anchors.left: parent.left
                    anchors.right: parent.right
                    color: "#008DFF"
                    font.pixelSize:  16
                    font.family: app.fontRobotoMedium.name
                    elide: Text.ElideRight
                }

                CustomTextFieldTitled{
                    id:simulationTitleTextField
                    title: "Simulation Name"
                    placeholderText: "Enter a name..."
                }

                Rectangle{
                    color: "transparent"
                    height:forecastDurationTitleLabel.height+forecastDurationSlider.height
                    width: parent.width


                    Label{
                        id:forecastDurationTitleLabel
                        text: "Forecast Duration (hr)"
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        color: "#838383"
                        font.pixelSize:  14
                        font.family: app.fontRobotoRegular.name
                    }

                    CustomTextAreaSlider{
                        id:forecastDurationSlider
                        anchors.top:forecastDurationTitleLabel.bottom
                        anchors.topMargin: 3
                        Component.onCompleted: x=x+10
                    }
                }

                Rectangle{
                    color: "transparent"
                    height:notificationsTitleLabel.height+notificationsTextLabel.height-13
                    width: parent.width

                    Label{
                        id:notificationsTitleLabel
                        text: "Notifications"
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        color: "#838383"
                        font.pixelSize:  14
                        font.family: app.fontRobotoRegular.name
                    }

                    Label{
                        id:notificationsTextLabel
                        text: "The simulation will be completed on a remote server. Enable text/email options below if you want to be notified when your simulation is completed. Add your email and phone information in the settings menu."
                        width: 0.93*app.width
                        wrapMode: Text.WordWrap
                        color: "#3C3C36"
                        lineHeight: 1.1
                        font.pixelSize:  14
                        font.family: app.fontRobotoRegular.name

                        anchors.top:notificationsTitleLabel.bottom
                        anchors.topMargin: 3
                    }
                }

                CustomListItemSwitch{
                    id: selectorEmail;
                    text: "Email"
                    enabled: app.settings.userEmail != "";
                    fullListener: false;
                }

                CustomListItemSwitch{
                    id: selectorSms;
                    text: "Text Message"
                    enabled: true;
                    fullListener: false;

                    onCheckedChanged: {
                        if(checked && (app.settings.userPhone == "" || app.settings.userPhoneProvider == "")){
                            generalPopUp.pleaseEnterPhoneNumber();
                            checked = false;
                        }
                    }
                }

                Rectangle{
                    color: "transparent"
                    height: 1
                    width: 1
                }

                Rectangle{
                    color: "#838383"
                    opacity: 0.25
                    height: 1
                    anchors.right: parent.right
                    anchors.left: parent.left
                    anchors.margins: -20
                }


                RowLayout{

                    anchors.horizontalCenter: parent.horizontalCenter
                    spacing: app.width*0.02

                    CustomButton{
                        text: "cancel"
                        color: "gray"
                        onClicked: {
                            item.visible = false
                        }
                    }

                    CustomButton{
                        text: "Submit"
                        color: "blue"
                        opacity: simulationTitleTextField.text.length < 1 ? 0.25 : 1
                        onClicked: {
                            if(simulationTitleTextField.text.length > 0){
                                simulatePressed(simulationTitleTextField.text, forecastDurationSlider.value, selectorEmail.checked, selectorSms.checked);
                                item.visible = false

                            }else{
                                //console.log("Simulation name needed")
                            }
                        }
                    }
                }
            }
        }
    }

    onVisibleChanged: {
        forecastDurationSlider.value = 1;
        forecastDurationSlider.text = "1";
        simulationTitleTextField.text = "";
        mailSwitchChecked = false;
        smsSwitchChecked = false;
    }
}
