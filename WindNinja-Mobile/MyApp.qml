import QtQuick 2.7
import QtQuick.Controls 2.1
import QtQuick.Layouts 1.1
import QtQuick.Controls.Material 2.1
import QtPositioning 5.2

import ArcGIS.AppFramework 1.0

import QtQuick.LocalStorage 2.0
import "./Lib/js/DatabaseFunctions.js" as DatabaseFunctions

import "./Pages"
import "./CustomComponents"
import "./Lib/QML"

App {
    id: app
    width: 421
    height: 750

    property real scaleFactor: AppFramework.displayScaleFactor

    property string currentVersion: ""
    property string currentBaseMap: "Imagery"
    property bool simulationLoaded: false;
    property bool editingSimulation: false;
    property string currentSimId: "";
    property string disclaimerCallback: "Settings"
    property alias gpsPositionSource: gpsPositionSource;

    signal simulationSelected(string jobpath);

    //Fonts

    readonly property alias fontRobotoMedium: fontRobotoMedium
    readonly property alias fontRobotoRegular: fontRobotoRegular
    readonly property alias fontWindNinjaUi: fontWindNinjaUi

    property real itemHeight: 50
    property real itemWidth: 100
    property real scaledMargin: 15

    FontLoader { id: fontRobotoMedium; source: app.folder.fileUrl("./Assets/Fonts/Roboto-Medium.ttf") }
    FontLoader { id: fontRobotoRegular; source: app.folder.fileUrl("./Assets/Fonts/Roboto-Regular.ttf") }
    FontLoader { id: fontWindNinjaUi; source: app.folder.fileUrl("./Assets/Fonts/Wind-Ninja-Mobile.ttf") }


    readonly property alias fontIcons: fontIcons

    property alias settings: settings;
    property alias windNinjaServer: windNinjaServer;
    property var pageMain: undefined;
    Settings{
        id:settings;
        property string userName: "";
        property string userEmail: "";
        property string userPhone: "";
        property string userPhoneProvider: "";

        property string deviceModel: "";
        property string devicePlatform: "";
        property string deviceVersion: "";
        property string deviceId: "";

        property bool isRegistered: false;
        property string registrationId: "";
        property string registrationStatus: "";

        property bool canSimulate: false;
    }

    WindNinjaServer{
        id:windNinjaServer;
        popUpWaitServer: popUpWaitServer;
    }
    Timer {
        id: timerServer
        running: false
        repeat: true
        interval: 500

        onTriggered: {
            ////console.log("Timer server tick")
            switch(windNinjaServer.currentRequestName){
            case windNinjaServer.getOutputTilesRequestName:
                windNinjaServer.getTopofireOutput(windNinjaServer.currentJobId.replace(/-/g, ""));
                break;
            case windNinjaServer.getOutputTopofireRequestName:
                windNinjaServer.getWxOutput(windNinjaServer.currentJobId.replace(/-/g, ""));
                break;
            case windNinjaServer.getOutputWxRequestName:
                zipReader.removeFiles(windNinjaServer.currentJobId.replace(/-/g, ""))
                popUpWaitServer.close();
                break;
            }
            timerServer.stop();
        }
    }

    CustomPopUp{
        id:generalPopUp
    }

    Loader {
        id: pageLoader;
        anchors.fill: parent;
        z:9999999
        onSourceChanged: {
            editingSimulation = false;
            pageMain.c_areaSquare.clearAll();
            pageMain.stopAnimation();
        }

        onSourceComponentChanged: {
            editingSimulation = false;
            pageMain.c_areaSquare.clearAll();
            pageMain.stopAnimation();
        }
    }

    Loader {
        id: pageMainLoader;
        anchors.fill: parent;
        onSourceChanged: {
        }

        onSourceComponentChanged: {
        }
    }

    Component.onCompleted: {

        if(settings.deviceId === ""){
            settings.devicePlatform = AppFramework.osName;
            settings.deviceVersion = AppFramework.osVersion;
            settings.deviceModel = AppFramework.systemInformation.hasOwnProperty("model") ? AppFramework.systemInformation.model : Undefined;
        }

        filefolder.makePath(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/"))
        filefolder.writeFile(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/.nomedia"), "");


        gpsPositionSource.active = true;
        app.gpsPositionSource.active = true;
        if(!settings.isRegistered){
            pageLoader.source = "Pages/PageWelcome.qml"
        }else{
            pageMainLoader.source = "Pages/PageMain.qml"
        }
    }


    PositionSource{
                    id:gpsPositionSource
                    active: true
                    onPositionChanged: {
                        pageMain.updateLocationPoint(position)
                    }
                    updateInterval: 30000
                }

    FileFolder{
        id: appFolder
        path: app.folder.path
        Component.onCompleted: {
            var res = readJsonFile("appinfo.json");
            var versionMajor = res.version.major === undefined ? 0 : res.version.major
            var versionMinor = res.version.minor === undefined ? 0 : res.version.minor
            var versionMicro = res.version.micro === undefined ? 0 : res.version.micro
            currentVersion = versionMajor + "." + versionMinor + "." + versionMicro

            var databaseVersion = DatabaseFunctions.getParameter("VERSION");

            if(databaseVersion !== currentVersion){
                DatabaseFunctions.restoreDatabase();
            }
        }
    }

    onSimulationSelected: {
        pageMain.vectorField.loadWindninja(jobpath);
        simulationLoaded = true;
        pageMain.wx.timeIndex = 0;
        pageMain.vectorField.timeIndex = 0;
        pageLoader.sourceComponent = undefined;
        popUpWaitServer.close();
    }

    PopupWaitServer{
        id: popUpWaitServer;
        z:99;
        focus: true // important - otherwise we'll get no key events
             Keys.onReleased: {
                 if (event.key === Qt.Key_Back) {
                     event.accepted = true
                 }
             }}

    FileFolder {
        id:filefolder;
    }

    ZipReader {
        id:zipReader
        property string internalPath: "ArcGIS/AppStudio/Data/WindNinja";
        property string zipResponseName: "/response.zip"
        property string zipTilesFileName: "/tiles.zip";
        property string zipTopofireFileName: "/topofire.zip";
        property string zipWxFileName: "/wx_geojson.zip";
        property int lastPercentProgress: 0;
        property string currentProgressName: "";
        path: AppFramework.userHomeFolder.filePath(internalPath);

        function extractJobZip(jobId) {
            popUpWaitServer.text = "Extracting files...";
            currentSimId = jobId;
            currentProgressName = "Simulation";
            path = AppFramework.userHomeFolder.filePath(internalPath + zipResponseName);
            zipReader.extractAll(AppFramework.userHomeFolder.filePath(internalPath + "/" + jobId));
        }

        function extractTilesZip(jobId, callback){
            currentProgressName = "Tiles";
            path = AppFramework.userHomeFolder.filePath(internalPath + "/" + jobId + zipTilesFileName);
            var zipSucceddedExtracted = zipReader.extractAll(AppFramework.userHomeFolder.filePath(internalPath + "/" + jobId.replace(/-/g, '') + "/tiles"));
            DatabaseFunctions.setSimulationDownloaded(jobId);
        }

        function extractTopofireZip(){
            currentProgressName = "Topofire";
            path = AppFramework.userHomeFolder.filePath(internalPath + zipTopofireFileName);
            var zipSucceddedExtracted = zipReader.extractAll(AppFramework.userHomeFolder.filePath(internalPath + "/topofire"));
        }

        function extractWxZip(jobId){
            currentProgressName = "Wx";
            path = AppFramework.userHomeFolder.filePath(internalPath + "/" + jobId.replace(/-/g, '') + zipWxFileName);
            var zipSucceddedExtracted = zipReader.extractAll(AppFramework.userHomeFolder.filePath(internalPath + "/" + jobId.replace(/-/g, '')  + "/wx"));
        }

        function removeFiles(jobId){
            ////console.log("Removing zip files");
            filefolder.removeFile(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/" + jobId.replace(/-/g, '') + zipTilesFileName));
            filefolder.removeFile(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja" + zipTopofireFileName));
            filefolder.removeFile(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/" + jobId.replace(/-/g, '') + zipWxFileName));
        }

        onProgress: {
            var currentPercentProgress = Math.floor(percent);
            if(lastPercentProgress < currentPercentProgress){
                popUpWaitServer.text = "Extracting " + currentProgressName + " files...\nProgress: " + currentPercentProgress + "%";
                lastPercentProgress = currentPercentProgress;
            }
        }

        onCompleted: {
            zipReader.close();
            lastPercentProgress = 0;
            currentProgressName = "";
        }
    }

    Item{
        id:fontIcons
        readonly property string _next:"next"
        readonly property string _previous:"previous"
        readonly property string _pause:"pause"
        readonly property string _play:"play"
        readonly property string _zoom_to_sim_exten:"zoom-to-sim-exten"
        readonly property string _confirm:"confirm"
        readonly property string _delete:"delete"
        readonly property string _add_tpk:"add-tpk"
        readonly property string _refresh:"refresh"
        readonly property string _more_menu:"more-menu"
        readonly property string _back_arrow:"back-arrow"
        readonly property string _create_sim:"create-sim"
        readonly property string _map_pin:"map-pin"
        readonly property string _disclaimer:"disclaimer"
        readonly property string _help:"help"
        readonly property string _feedback:"feedback"
        readonly property string _about:"about"
        readonly property string _register:"register"
        readonly property string _dropdown:"dropdown"
        readonly property string _clear:"clear"
        readonly property string _north_compass:"north-compass"
        readonly property string _my_location:"my-location"
        readonly property string _settings:"settings"
        readonly property string _search:"search"
        readonly property string _legend:"legend"
        readonly property string _layers:"layers"
        readonly property string _simulation_list:"simulation-list"
        readonly property string _close:"close"
        readonly property string _share:"share"
        readonly property string _plus:"plus"
        readonly property string _fail_sim:"fail-Sim"
        readonly property string _processing:"processing"
        readonly property string _download:"download"
        readonly property string _view:"view"
    }


    function isValidMail(mail){
        var validMail = /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i.test(mail);
        return validMail;
    }

    function isValidPhone(phone){
        var validPhone1 = /^\d{3}-\d{3}-\d{4}$/.test(phone);
        var validPhone2 = /^(\d{3}) \d{3}-\d{4}$/.test(phone)
        var validPhone3 = /^\d{10}$/.test(phone);
        return validPhone1 || validPhone2 || validPhone3;
    }

    function isAnIos(){
        return AppFramework.osName.toLowerCase() == "ios";
    }

    focus: true // important - otherwise we'll get no key events
    Keys.onReleased: {
        if (event.key === Qt.Key_Back) {
            backButtonPressed()
            event.accepted = true
        }
    }

    function backButtonPressed(){

var currentPage = pageLoader.source.toString();
        if(currentPage.includes("PageSimulations.qml") || currentPage.includes("PageSettings.qml")){
            pageLoader.sourceComponent = undefined;
        }else if(currentPage.includes("PageAbout.qml") || currentPage.includes("PageFeedback.qm")
                 || currentPage.includes("PageHelp.qml")){
            pageLoader.source = "Pages/PageSettings.qml";
        }else if(currentPage == ""){
            pageMain.hideLayerManager();
        }
    }
}

