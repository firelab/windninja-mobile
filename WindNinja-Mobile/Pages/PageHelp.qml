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
        title: "Help"
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

        clip:true;
        contentHeight: content.height;
        anchors.fill: parent;

        ColumnLayout{
            id:content;
            anchors.left: parent.left;
            anchors.right: parent.right;
            anchors.margins: 10;
            spacing: app.height*0.02;

            Rectangle{
                height: 1;
                color: "transparent";
            }

            Label{
                text: "Support";
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#008DFF";
                font.pixelSize:  14;
                font.family: app.fontRobotoMedium.name;
            }

            Label{
                text: "Have a question or want to report a bug or feature request? Contact us at <b><font color=\"#008DFF\"><a href=\"mailto:wind.ninja.support@gmail.com\"  style=\"text-decoration: none;\">wind.ninja.support@gmail.com</a></font></b> or use the form found in the Feedback section of this application. For more information on WindNinja Mobile, go to <b><font color=\"#008DFF\"><a href=\"https://weather.firelab.org/windninja/mobile/help\"  style=\"text-decoration: none;\">weather.firelab.org/windninja/mobile/help</a></font></b>.";
                onLinkActivated: Qt.openUrlExternally(link);
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#3C3C36";
                lineHeight: 1.1;
                font.pixelSize:  14;
                font.family: app.fontRobotoRegular.name;
            }

            Rectangle{
                width: app.width;
                height: 1;
                color: "#838383";
                opacity: 0.25;
                Layout.leftMargin: -10;
            }

            Label{
                text: "Registration";
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#008DFF";
                font.pixelSize:  14;
                font.family: app.fontRobotoMedium.name;
            }

            Label{
                text: "In order to run new simulations, you will need to register. You will be prompted to register when you first open the application. However, if you choose to skip registration initially, you can access the registration screen through the Settings menu. Once you have submitted your registration you will receive an email to confirm you account. After account confirmation, you will be able to create new simulations.";
                onLinkActivated: Qt.openUrlExternally(link);
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#3C3C36";
                lineHeight: 1.1;
                font.pixelSize:  14;
                font.family: app.fontRobotoRegular.name;
            }

            Rectangle{
                width: app.width;
                height: 1;
                color: "#838383";
                opacity: 0.25;
                Layout.leftMargin: -10;
            }

            Label{
                text: "Notifications";
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#008DFF";
                font.pixelSize:  14;
                font.family: app.fontRobotoMedium.name;
            }

            Label{
                text: "WindNinja has been set up to allow you to receive either/both SMS and email notifications once your simulation is ready for download. There is a notifications section in the Settings menu where you can enter the email and phone number where you would like the notifications to be sent. You will have the option to turn on notifications when you create a new simulation.";
                onLinkActivated: Qt.openUrlExternally(link);
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#3C3C36";
                lineHeight: 1.1;
                font.pixelSize:  14;
                font.family: app.fontRobotoRegular.name;
            }

            Rectangle{
                width: app.width;
                height: 1;
                color: "#838383";
                opacity: 0.25;
                Layout.leftMargin: -10;
            }

            Label{
                text: "Creating and Viewing a Simulation";
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#008DFF";
                font.pixelSize:  14;
                font.family: app.fontRobotoMedium.name;
            }

            Label{
                text:
                    "<b>1.</b> Navigate (zoom/pinch/pan, search) to an area of interest on the map.<br/><br/>" +
                    "<b>2.</b> Tap the blue pen icon in the bottom right of the screen. A rectangle will appear on the map with upper left and lower right corners that can be moved to increase or decrease the size of the simulation domain. Tap and hold one of the corners marked with a circle and drag on the map to increase or decrease the size of the domain. Tap and hold the plus sign in the center of the rectangle and drag to reposition the domain on the map. A green box indicates the selected area is within the maximum size limit and a red rectangle indicates that the simulation domain is too large to simulate. When you are satisfied with your selected area, tap on the blue circle with the check mark. If you want to cancel, tap the white circle with the 'X' icon.<br/><br/>" +
                    "<b>3.</b> Give the simulation a name, select a duration and select your notification preferences for that simulation. Then click “Run Simulation”. The simulation parameters will be sent to the remote server where the simulation will be performed. If the email or text notification options were selected, you will be notified when your simulation is ready for download from the server.<br/><br/>" +
                    "<b>4.</b> Once submitted, your simulation will appear in the simulation list. This is where you will be able to see the status of your simulation(s) and download them locally to your device. You will also be able to share simulations you have run or import simulations that have been shared by others. The simulation list icons are color coded: red indicates the simulation has been submitted and is running on the server; blue indicates the simulation is complete and is ready for download to your device for viewing; green indicates the simulation is complete and has been downloaded to your device; grey indicates there was a problem on the server and the simulation has failed. You will need to refresh the simulation list to see a change in the status of your simulations. <b>Before you can view a simulation you will have to download it locally to your device</b>.<br/><br/>" +
                    "<b>5.</b> When your simulation has been completed, open the simulation list by tapping the wind icon located in the bottom toolbar. Refresh the simulation list to make sure the simulations are showing the most up-to-date status. When your simulation is blue, tap on it to download the simulation to your device. Once the simulation has downloaded, the icon will turn green indicating it is ready to be viewed. Tap on the simulation to load it on the map.<br/><br/>" +
                    "<b>6.</b> Once a simulation has been selected, it will be loaded onto the map. You can control the simulation by using the play, pause, next and previous buttons. A progress bar will indicate where you are within the simulation duration. A timestamp will also indicate the current time of the simulation you are viewing.<br/><br/>" +
                    "<b>7.</b> To stop viewing a simulation, tap the round “X” icon located at the top right of the simulation control panel.<br/><br/>" +
                    "<b>8.</b> You can view a legend by clicking the legend icon located in the bottom toolbar.<br/><br/>" +
                    "<b>9.</b> You can return to the original map extent of the simulation by tapping the four corners square icon.<br/><br/>" +
                    "<b>10.</b> You can view the coarse weather model used to initialize WindNinja by tapping the Wx icon.<br/><br/>" +
                    "<b>11.</b> To view the simulation and map in 3D use 2 fingers and drag them up or down on the screen at the same time. You can also pinch to zoom and rotate to move the map around in 3D.";
                onLinkActivated: Qt.openUrlExternally(link);
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#3C3C36";
                lineHeight: 1.1;
                font.pixelSize:  14;
                font.family: app.fontRobotoRegular.name;
            }

            Rectangle{
                width: app.width;
                height: 1;
                color: "#838383";
                opacity: 0.25;
                Layout.leftMargin: -10;
            }

            Label{
                text: "Sharing, Importing, and Deleting a Simulation";
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#008DFF";
                font.pixelSize:  14;
                font.family: app.fontRobotoMedium.name;
            }

            Label{
                text:
                    "<b>1.</b> To share a simulation, open the simulation list and tap the arrow icon next to the simulation name. This will generate a unique code for that simulation and give you a variety of ways to share that code.<br/><br/>" +
                    "<b>2.</b> To import a simulation run by another user, open the simulation list and tap the blue circle with the folder icon in the bottom right of the screen. A pop up will appear where you can enter the unique code for the simulation that was shared with you. Once you hit okay the simulation will be added to your simulation list for viewing. The simulation may need to be downloaded locally to your device before viewing.<br/><br/>" +
                    "<b>3.</b> You can delete a simulation from the simulation list by tapping the trashcan icon with the ‘X’ next to the simulation name.";
                onLinkActivated: Qt.openUrlExternally(link);
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#3C3C36";
                lineHeight: 1.1;
                font.pixelSize:  14;
                font.family: app.fontRobotoRegular.name;
            }

            Rectangle{
                width: app.width;
                height: 1;
                color: "#838383";
                opacity: 0.25;
                Layout.leftMargin: -10;
            }

            Label{
                text: "Layers and Base Maps";
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#008DFF";
                font.pixelSize:  14;
                font.family: app.fontRobotoMedium.name;
            }

            Label{
                text: "You can change the base map, load local base maps and apply different map layers through the layers panel. To do this, click on the layer icon located in the bottom toolbar.";
                onLinkActivated: Qt.openUrlExternally(link);
                Layout.preferredWidth: 0.9*app.width;
                wrapMode: Text.WordWrap;
                color: "#3C3C36";
                lineHeight: 1.1;
                font.pixelSize:  14;
                font.family: app.fontRobotoRegular.name;
            }

            Rectangle{
                height: 1
                color: "transparent"
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
