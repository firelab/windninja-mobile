import QtQuick 2.0
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1

Item {

    property alias title: titleLabel.text
    property alias text: contentLabel.text

    anchors.fill: parent

    Popup{

        property string name: ""

        id:popup
        width: app.width - 120
        height: titleLabel.height + contentLabel.height + separator.height + buttons.height + 20

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

        onClosed: {
            app.pageMain.forceActiveFocus();
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

                    text: qsTr("Ok")
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            popup.close();
                        }
                    }
                }
            }
        }
    }

    function open(){
        popup.open()
    }

    function close(){
        popup.close()
    }










    function selectedAreaTooLargeWarn(){
        title = "Selected Area Is Too Large";
        text = "The area you have selected is too large. It is greater than " + pageMain.c_areaSquare.maxSquareMiles + " square miles. Please redraw a smaller area and try again.";
        open();
    }

    function pleaseRegisterWarn(){
        title = "Please Register";
        text = "You have not registered an account yet. You need to register in order to create new simulations. Access to registration can be found in the Settings menu.";
        open();
    }

    function registrationStatusComplete(){
        title = "Registration Status";
        text = "Registration Accepted.";
        open();
    }

    function registrationAccepted(){
        title = "Registration Status";
        text = "Registration Accepted.";
        open();
    }

    function registrationAlreadyExist(){
        title = "Account already registered";
        text = "Account and device were already registered in the server.";
        open();
    }

    function registrationStatusPending(){
        title = "Registration Status";
        text = "Your registration is pending approval. You will not be able to create/submit any new runs until your account is verified.";
        open();
    }

    function registrationStatusDisabled(){
        title = "Registration Status";
        text = "Your account has been disabled. You will not be able to create/submit runs, but will still be able to display any runs already created.";
        open();
    }

    function badMailWarn(){
        title = "Registration Error";
        text = "Please insert a correct mail.";
        open();
    }

    function deletingFailedSimWarn(){
        title = "Simulation error";
        text = "A simulation process failed on the server side and its going to be removed from the simulations list.";
        open();
    }

    function oldSimulationsWarn(){
        title = "Simulation info";
        text = "Some simulation is invalid (old) and is no longer on the server.";
        open();
    }

    function configurationError(){
        title = "Configuration error";
        text = "Invalid values entered, please check your settings and try again.";
        open();
    }

    function configurationNameError(){
        title = "Configuration error";
        text = "Invalid name entered, please check it and try again.";
        open();
    }

    function configurationEmailError(){
        title = "Configuration error";
        text = "Invalid Email entered, please check it and try again.";
        open();
    }

    function configurationPhoneError(){
        title = "Configuration error";
        text = "Invalid Cellphone Number entered, please check it and try again.";
        open();
    }

    function configurationSaved(){
        title = "Configuration saved";
        text = "Your configuration was saved successfully.";
        open();
    }

    function feedbackSubmited(){
        title = "Feedback submited";
        text = "Your commentary was sended to windninja, thanks.";
        open();
    }

    function connectionUnavailable(){
        title = "Connection Error";
        text = "It has not been possible to connect to the Windninja servers. Please try again in a few minutes.";
        open();
    }

    function shareDeletedSim(){
        title = "Info";
        text = "The selected simulation is no longer on the server and therefore can not be shared.";
        open();
    }

    function shareFailedSim(){
        title = "Info";
        text = "The selected simulation failed on the server and therefore can not be shared.";
        open();
    }

    function shareProcesingSim(){
        title = "Info";
        text = "The selected simulation is processing on the server, please wait a few minutes and try again.";
        open();
    }

    function importSimulationInvalidWarn(){
        title = "Simulation info";
        text = "The imported simulation is invalid (old) and is no longer on the server.";
        open();
    }

    function importSimulationFailedWarn(){
        title = "Simulation info";
        text = "The imported simulation failed on the server and therefore can not be imported.";
        open();
    }

    function simulationExistWarn(){
        title = "Simulation info";
        text = "That simulation was already imported.";
        open();
    }

    function wrongIdSimWarn(){
        title = "Simulation info";
        text = "The ID is not correct, please revise it and try again.";
        open();
    }

    function pleaseZoomWarn(){
        title = "Zoom info";
        text = "Please zoom into the map to start to draw a simulation.";
        open();
    }

    function pleasePerpendicularWarn(){
        title = "Zoom info";
        text = "Please place the point of view more perpendicular to the surface to start drawing a simulation.";
        open();
    }

    function tryToSimulateAgainWarn(){
        title = "Submit error";
        text = "There was an error submitting the simulation, please try again.";
        open();
    }

    function tryToLoadFailSimulation(){
        title = "Sim error";
        text = "Can not load a failed simulation.";
        open();
    }

    function showCauseOfDelete(idSim){
        title = "Sim error";
        text = DatabaseFunctions.getErrorCause(idSim);
        if(text == undefined || text == "")
            text = "Can not load a failed simulation.";

        open();
    }

    function pleaseEnterPhoneNumber(){
        title = "Submit error";
        text = "If you want to receive an SMS when the simulation ends, please go to the settings and enter your phone number";
        open();
    }

    function showCustomMessage(_title, _text){
        title = _title;
        text = _text;
        open();
    }
}
