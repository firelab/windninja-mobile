import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtGraphicalEffects 1.0
import "../CustomComponents"

Page {
    id:pageSettings

    property bool infoEdited: false;

    anchors.fill: parent
    Material.background: "#FFFFFF"


    header: CustomHeader{
        title: "Settings"
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
                text: "User Info"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#008DFF"
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            Label{
                text: "Fill in your contact information below and hit ‘‘SAVE”. We will use this information to notify you via email or text when your simulation is ready for download."
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#3C3C36"
                lineHeight: 1.1
                font.pixelSize:  14
                font.family: app.fontRobotoRegular.name
            }

            CustomTextFieldTitled{
                id: textFieldName;
                title: "Name"
                placeholderText: "Enter yout name..."
                text: app.settings.userName !== "" ? app.settings.userName : "";
                onTextChanged: {
                    infoEdited = true;
                }
            }

            CustomTextFieldTitled{
                id: textFieldEmail;
                title: "Email"
                placeholderText: "email@address.com"
                text: app.settings.userEmail !== "" ? app.settings.userEmail : "";
                onTextChanged: {
                    infoEdited = true;
                }
            }

            CustomTextFieldTitled{
                id: textFieldCellPhoneNumber;
                title: "Cell Phone Number"
                placeholderText: "xxx-xxx-xxxx"
                text: app.settings.userPhone !== undefined ? app.settings.userPhone : "";
                onTextChanged: {
                    infoEdited = true;
                }
            }

            CustomDropDownTitled{
                id: dropDownCellPhoneProvider
                title: "Cell Phone Provider"
                placeholderText: "Please select..."
                text: app.settings.userPhoneProvider !== undefined ? app.settings.userPhoneProvider : "";
                MouseArea{
                    anchors.fill: parent
                    onClicked: selector.open()
                }
                onTextChanged: {
                    infoEdited = true;
                }
            }

            RowLayout{

                anchors.horizontalCenter: parent.horizontalCenter

                CustomButton{
                    text: "Cancel"
                    color: "gray"
                    enabled: infoEdited;
                    onClicked: {
                        textFieldName.text = app.settings.userName !== "" ? app.settings.userName : "";
                        textFieldEmail.text = app.settings.userEmail !== "" ? app.settings.userEmail : "";
                        textFieldCellPhoneNumber.text = app.settings.userPhone !== "" ? app.settings.userPhone : "";
                        dropDownCellPhoneProvider.text = app.settings.userPhoneProvider !== "" ? app.settings.userPhoneProvider : "";
                        infoEdited = false;
                    }
                }

                CustomButton{
                    text: "Save"
                    color: "blue"
                    enabled: infoEdited && textFieldName.text.length > 0 && textFieldEmail.text.length > 0 && textFieldName.text.length > 0;
                    onClicked: {
                        if(validFields()){
                            app.settings.userName = textFieldName.text
                            app.settings.userEmail = textFieldEmail.text
                            app.settings.userPhone = textFieldCellPhoneNumber.text
                            app.settings.userPhoneProvider = dropDownCellPhoneProvider.text
                            infoEdited = false;
                            generalPopUp.configurationSaved();
                        }
                    }
                }
            }

            Rectangle{
                width: app.width
                height: 1
                color: "#838383"
                opacity: 0.25
            }

            Label{
                text: "Additional Links"
                Layout.preferredWidth: 0.9*app.width
                wrapMode: Text.WordWrap
                color: "#008DFF"
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._register
                text: "Register"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        pageLoader.source = "PageRegister.qml"
                    }
                }
            }
            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._about
                text: "About"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        pageLoader.source = "PageAbout.qml"
                    }
                }
            }
            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._feedback
                text: "Feedback and Questions"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        pageLoader.source = "PageFeedback.qml"
                    }
                }
            }
            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._help
                text: "Help"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        pageLoader.source = "PageHelp.qml"
                    }
                }
            }
            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._disclaimer
                text: "Disclaimer"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        app.disclaimerCallback = "Settings";
                        pageLoader.source = "PageDisclaimer.qml"
                    }
                }
            }

            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._simulation_list
                text: "WindNinja Website"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                         Qt.openUrlExternally("https://weather.firelab.org/windninja/")
                    }
                }
            }

            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._north_compass
                text: "App tour"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                         pageLoader.source = "PageWelcome.qml"
                    }
                }
            }

            CustomListIconElement{
                Layout.fillWidth: true
                icon: app.fontIcons._help
                text: "Extended Help"

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        Qt.openUrlExternally("https://weather.firelab.org/windninja/mobile/help/#top")
                    }
                }
            }

            Rectangle{
                height: 1
                color: "transparent"
            }
        }

    }

    CustomSelector{
        id:selector;
        title: "Select CellPhone Provider"
        model: [
            "Alltel Wireless",
            "AT&T Wireless",
            "AT&T Mobility (Cingular)",
            "Boost Mobile",
            "Cricket",
            "Metro PCS",
            "Sprint (PCS)",
            "Sprint (Nextel)",
            "T-Mobile",
            "U.S. Cellular",
            "Verizon Wireless (inc. Straight Talk)",
            "Virgin Mobile",
            "None"
        ]
        onOkClose: {
            dropDownCellPhoneProvider.text = valueSelected == "None" ? "" : valueSelected;
        }
    }

    function validFields(){
        var validName, validMail, validPhone;

        validName = textFieldName.text.length > 0;
        if(!validName){
            generalPopUp.configurationNameError();
            return false;
        }

        validMail = app.isValidMail(textFieldEmail.text);
        if(!validMail){
            generalPopUp.configurationEmailError();
            return false;
        }

        validPhone = app.isValidPhone(textFieldCellPhoneNumber.text) || textFieldCellPhoneNumber.text == "";
        if(!validPhone){
            generalPopUp.configurationPhoneError();
            return false;
        }

        if(validName && validMail && validPhone){
            return true;
        }

        generalPopUp.configurationError();
        return false;
    }

    focus: true // important - otherwise we'll get no key events
    Keys.onReleased: {
        if (event.key === Qt.Key_Back) {
            event.accepted = true
            backButtonPressed()
        }
    }
}
