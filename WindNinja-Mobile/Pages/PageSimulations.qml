import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import QtGraphicalEffects 1.0
import "../CustomComponents"
import "../Delegates"
import QtQuick.LocalStorage 2.0
import "../Lib/js/DatabaseFunctions.js" as DatabaseFunctions
import ArcGIS.AppFramework 1.0

Page {
    id:pageSimulations

    anchors.fill: parent
    Material.background: "#FFFFFF"

    header: CustomHeader{
        title: "Simulation List"

        Rectangle{
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            width: parent.width*0.12
            color: "transparent"

            CustomFontIcon{
                id:reloadButton
                anchors.centerIn: parent
                icon: app.fontIcons._refresh;
                color: "#FFFFFF"
            }

            MouseArea{
                anchors.fill: parent
                onClicked: {
                    reloadList();
                    simulationListView.model = DatabaseFunctions.getSimList(textFieldSearch.text);
                }
            }
        }
    }


    Rectangle{
        id:searchBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 62

        color: "#3C3C36"

        Rectangle{
            radius: 5
            color: "#FFFFFF"

            anchors.fill:parent
            anchors.margins: 6

            RowLayout{
                anchors.fill: parent
                anchors.rightMargin: 10
                anchors.leftMargin: 10
                spacing: 15
                CustomFontIcon{
                    id:searchIcon
                    icon: app.fontIcons._search
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                        }
                    }
                }

                TextField{
                    id:textFieldSearch
                    placeholderText: qsTr("Search...")
                    Layout.fillWidth: true

                    Layout.bottomMargin: -10

                    font.family: app.fontRobotoRegular.name

                    Material.foreground: "#838383"
                    Material.accent: "#838383"
                    background: Rectangle{color:"transparent"}

                    onTextChanged: {
                        simulationListView.model = DatabaseFunctions.getSimList(textFieldSearch.text);
                    }
                }

                CustomFontIcon{
                    id:clearIcon
                    icon: app.fontIcons._clear
                    color:"#838383"
                    visible: textFieldSearch.text.length >0
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            textFieldSearch.clear();
                        }
                    }
                }
            }
        }
    }

    DropShadow{
        id:searchBarDropShadow
        anchors.fill: searchBar
        horizontalOffset: 0
        verticalOffset: 3
        radius: 8.0
        samples: 17
        color: "#33000000"
        source: searchBar
    }

    ListView{
        id:simulationListView
        anchors.top: searchBar.bottom
        anchors.bottom: legend.top
        anchors.right: parent.right
        anchors.left: parent.left
        clip:true

        property bool lastMoveIsGoingUp: false
        property string lastElementId: "";

        delegate:SimulationListElement{}

        model: DatabaseFunctions.getSimList(textFieldSearch.text);

        property bool menuOpen: false

        onDragStarted: {
            if(menuOpen){
                for(var child in simulationListView.contentItem.children) {
                    try{
                        simulationListView.contentItem.children[child].closeDropDown();
                    }catch(err){
                        //console.error(err)
                    }
                }
            }
        }

        property string simToDelete: ""
        onSimToDeleteChanged: {
            if(simToDelete != ""){
                deleteSimulation()
                simToDelete = "";

            }
        }

        function deleteSimulation(){
            popupDelete.idSimToDelete = simToDelete;
            popupDelete.open()
        }

        //DropDownMenu
        CustomDropDownFrame{
            id:dropDown
            anchors.right: parent.right
            anchors.rightMargin: 15
        }

        DropShadow{
            anchors.fill: dropDown
            horizontalOffset: 0
            verticalOffset: 1
            radius: 8.0
            samples: 17
            color: "#55000000"
            source: dropDown
            spread: 0
            visible: dropDown.visible
        }

        onMovingVerticallyChanged: {
            if(simulationListView.atYEnd && height < contentHeight){
                importSimButton.stateVisible = false;
            }else{
                importSimButton.stateVisible = !lastMoveIsGoingUp;
            }
        }

        onVerticalVelocityChanged: {
            if(verticalVelocity != 0){
                lastMoveIsGoingUp = verticalVelocity < 0;
            }
        }

        onModelChanged: lastElementId = DatabaseFunctions.getOlderSimulation();

        Component.onCompleted:{
            reloadList();
        }

        Timer {
            id: timerReloadList
            running: true
            repeat: true
            interval:60000

            onTriggered: {
                reloadList();
            }
        }
    }

    CustomRoundButton{
        id: importSimButton
        color: "blue"
        buttonIcon: app.fontIcons._plus
        anchors.bottom:legend.top
        anchors.right: legend.right
        anchors.margins: 10
        visible: true

        onClicked: {
            generalPopUpTextField.open();
        }

        onOpacityChanged: {
            visible = opacity != 0
        }

        property bool stateVisible: true
        states: [
            State { when: importSimButton.stateVisible;
                PropertyChanges {   target: importSimButton; opacity: 1.0    }},
            State { when: !importSimButton.stateVisible;
                PropertyChanges {   target: importSimButton; opacity: 0.0    }}
        ]
        transitions: [ Transition { NumberAnimation { property: "opacity"; duration: 200}} ]
    }

    Rectangle{
        id:legend
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.left: parent.left
        height: 40

        RowLayout{
            anchors.fill: parent

            Rectangle{
                Layout.fillWidth: true
                height: parent.height

                RowLayout{
                    anchors.centerIn: parent
                    Rectangle{
                        height: 16
                        width: 16
                        color: "#89D394"
                        radius: 2

                        CustomFontIcon{
                            anchors.centerIn: parent
                            icon: app.fontIcons._view
                            color: "#FFFFFF"
                            font.pixelSize: 12
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: qsTr("View")
                        elide: Label.ElideRight

                        font.family: app.fontRobotoRegular.name
                        verticalAlignment: Qt.AlignVCenter
                        font.pixelSize: 12
                        color: "#838383"
                    }
                }

                MouseArea{
                    anchors.fill: parent
                    onClicked: {

                    }
                }
            }

            Rectangle{
                Layout.fillWidth: true
                height: parent.height

                RowLayout{
                    anchors.centerIn: parent
                    Rectangle{
                        height: 16
                        width: 16
                        color: "#59A0D9"
                        radius: 2

                        CustomFontIcon{
                            anchors.centerIn: parent
                            icon: app.fontIcons._download
                            color: "#FFFFFF"
                            font.pixelSize: 12
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: qsTr("Download")
                        elide: Label.ElideRight

                        font.family: app.fontRobotoRegular.name
                        verticalAlignment: Qt.AlignVCenter
                        font.pixelSize: 12
                        color: "#838383"
                    }
                }

                MouseArea{
                    anchors.fill: parent
                    onClicked: {

                    }
                }
            }

            Rectangle{
                Layout.fillWidth: true
                height: parent.height

                RowLayout{
                    anchors.centerIn: parent
                    Rectangle{
                        height: 16
                        width: 16
                        color: "#D06056"
                        radius: 2

                        CustomFontIcon{
                            anchors.centerIn: parent
                            icon: app.fontIcons._processing
                            color: "#FFFFFF"
                            font.pixelSize: 12
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: qsTr("Processing")
                        elide: Label.ElideRight

                        font.family: app.fontRobotoRegular.name
                        verticalAlignment: Qt.AlignVCenter
                        font.pixelSize: 12
                        color: "#838383"
                    }
                }

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                    }
                }
            }

            Rectangle{
                Layout.fillWidth: true
                height: parent.height

                RowLayout{
                    anchors.centerIn: parent
                    Rectangle{
                        height: 16
                        width: 16
                        color: "#838383"
                        radius: 2

                        CustomFontIcon{
                            anchors.centerIn: parent
                            icon: app.fontIcons._close
                            color: "#FFFFFF"
                            font.pixelSize: 12
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: qsTr("Failed")
                        elide: Label.ElideRight

                        font.family: app.fontRobotoRegular.name
                        verticalAlignment: Qt.AlignVCenter
                        font.pixelSize: 12
                        color: "#838383"
                    }
                }

                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                    }
                }
            }
        }
    }

    DropShadow{
        id:legendDropShadow
        anchors.fill: legend
        horizontalOffset: 0
        verticalOffset: -3
        radius: 8.0
        samples: 17
        color: "#33000000"
        source: legend
    }

    CustomPopUpTextField{
        id:generalPopUpTextField
        title: "Import Simulation";
        text: "Please enter the ID of the simulation you would like to import.\n\nEx. 5a5e52a0-786f-4f0d-94ef-ba860f1ff8a4\n";
        textFieldText: "";
        textFieldPlaceholderText: "00000000-0000-0000-0000-000000000000"

        onOkPressed: {
            var idTested = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(value);
            if(idTested){
                if(!DatabaseFunctions.simulationExist(value)){
                    windNinjaServer.checkJobStatusAndSave(value);
                }else{
                    generalPopUp.simulationExistWarn();
                }
            }else{
                generalPopUp.wrongIdSimWarn();
            }
        }
    }

    Popup{

        signal okClose(string valueSelected);
        signal cancelClose();
        property string idSimToDelete: "";

        id:popupDelete
        width: app.width - 120
        height: titleLabel.height + contentLabel.height + separator.height + buttons.height + 20

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

                text: qsTr("Delete Simulation?")
            }

            Label{
                id:contentLabel
                text: "This action will permanently delete the simulation."
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
            }

            Rectangle{
                id:separator
                anchors.horizontalCenter: parent.horizontalCenter
                width: popupDelete.width
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
                            popupDelete.close();
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
                            if(app.simulationLoaded && pageMain.vectorField.job.id.replace(/-/g, "") == popupDelete.idSimToDelete.replace(/-/g, "")){
                                pageMain.closeSimulationController();
                            }
                            filefolder.removeFolder(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/" + popupDelete.idSimToDelete.replace(/-/g, "")), true);
                            DatabaseFunctions.deleteSimulation(popupDelete.idSimToDelete);
                            popupDelete.close();
                            popupDelete.idSimToDelete = "";
                            simulationListView.model = DatabaseFunctions.getSimList(textFieldSearch.text);
                        }
                    }
                }
            }
        }
    }

    Timer {
        id: timer
        running: true
        repeat: true
        interval: 1000

        onTriggered: {
            simulationListView.model = DatabaseFunctions.getSimList(textFieldSearch.text);
        }
    }

    function reloadList(){
        var simsIds = DatabaseFunctions.getAllPendingSimsIds();
        if(simsIds.length > 0){
            for(var i in simsIds) {
                windNinjaServer.checkJobStatusAndUpdate(simsIds[i], function(needToReloadList){
                    if(needToReloadList){
                        simulationListView.model = DatabaseFunctions.getSimList(textFieldSearch.text);
                    }
                });
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




