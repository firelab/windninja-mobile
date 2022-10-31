import QtQuick 2.5
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.1

import ArcGIS.AppFramework 1.0

import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1

import QtQuick.Controls.Material 2.1

import QtQuick.LocalStorage 2.0
import "../js/DatabaseFunctions.js" as DatabaseFunctions
import "../js/WindNinjaClient.js" as WindNinjaClientJs
import "../js/UtilFunctions.js" as UtilFunctions
import "../js/DateFunctions.js" as DateFunctions


NetworkRequest {
    id: networkRequest

    followRedirects: true;
    ignoreSslErrors: true;
    responseType: "json";


    readonly property var baseUrl: "https://windninja.org/";

    readonly property string registerRequestPath: "services/registration/register";
    readonly property string checkRegistrationRequestPath: "api/account/" + app.settings.registrationId;
    readonly property string getMessagesRequestPath: "api/notification";
    readonly property string feedbackRequestPath: "api/feedback";
    readonly property string simulateRequestPath: "api/job";
    readonly property string checkJobStatusRequestPath: "api/job/";
    readonly property string getOutputRequestPath: "output/";

    property string currentRequestName: "";
    readonly property string simulateRequestName: "simulate";
    readonly property string checkJobStatusRequestName: "getJobStatus";
    readonly property string registerRequestName: "register";
    readonly property string checkRegistrationRequestName: "checkRegistration";
    readonly property string getOutputWxRequestName: "getOutputWx";
    readonly property string getOutputTopofireRequestName: "getOutputTopofire";
    readonly property string getOutputTilesRequestName: "getOutputTiles";
    readonly property string getMessagesRequestName: "getMessages";
    readonly property string feedbackRequestName: "feedback";

    readonly property string downloadTextTiles: "simulation";
    readonly property string downloadTextTopofire: "offline map";
    readonly property string downloadTextWx: "Wx";

    property var popUpWaitServer: undefined;
    property string waitServerText: "";

    property int lastPercentDownload: 0;
    property string requestUrlPath: "";
    property string requestParametersGet: "";
    property var requestParametersPost: ({});

    property string currentJobId: "";
    property string currentOutput: "";

    url: baseUrl + requestUrlPath + '?' + requestParametersGet;




    onReadyStateChanged: {
        switch(readyState){
        case NetworkRequest.ReadyStateUninitialized:
            //console.log("Ready State Changed to Uninitialized");
            break;
        case NetworkRequest.ReadyStateInitialized:
            //console.log("Ready State Changed to Initialized");
            break;
        case NetworkRequest.ReadyStateSending:
            //console.log("Ready State Changed to Sending");
            break;
        case NetworkRequest.ReadyStateProcessing:
            //console.log("Ready State Changed to Processing");
            break;
        case NetworkRequest.ReadyStateComplete:
            //console.log("Ready State Changed to Complete");

            var timer = Qt.createQmlObject("import QtQuick 2.3; Timer {interval: 100; repeat: false; running: true;}",parent,"networkRequest");
            timer.triggered.connect(function(){
                try{
                    requestDone();
                }catch(e){
                    //console.exception(e)
                    popUpWaitServer.close();
                    generalPopUp.showCustomMessage("Error", "Please, try again in a few minutes.")
                }
            });

            break;
        }
    }
    onUrlChanged: lastPercentDownload = 0;

    onProgressChanged: {
        var currentPercentDownload = Math.floor((progress-0.5)*200);
        if(lastPercentDownload < currentPercentDownload){
            //console.log("Progress: " + currentPercentDownload + "%");

            switch(currentRequestName){
            case getOutputTilesRequestName:
                popUpWaitServer.text ="Downloading " + downloadTextTiles + "...\nProgress: " + currentPercentDownload + "%";
                break;
            case getOutputTopofireRequestName:
                popUpWaitServer.text ="Downloading " + downloadTextTopofire + "...\nProgress: " + currentPercentDownload + "%";
                break;
            case getOutputWxRequestName:
                popUpWaitServer.text ="Downloading " + downloadTextWx + "...\nProgress: " + currentPercentDownload + "%";
                break;
            default:
                popUpWaitServer.text ="Please wait...";
            }
        }
        lastPercentDownload = currentPercentDownload;
    }

    function sendRequest(requestMethod, _requestParametersGet, _requestParametersPost, requestName, _requestUrlPath, _responsePath){

        popUpWaitServer.open();
        waitServerText = popUpWaitServer.text;
        setTimer(_requestUrlPath);

        requestUrlPath = _requestUrlPath;
        currentRequestName = requestName;

        requestParametersGet = "";
        requestParametersPost = "";

        networkRequest.method = requestMethod;
        requestParametersPost = _requestParametersPost !== undefined ? _requestParametersPost : ({});
        requestParametersGet = _requestParametersGet  !== undefined ? _requestParametersGet : "";
        responsePath = _responsePath;

        networkRequest.send(requestParametersPost);
    }


    function setTimer(currentRequest){
        var timeoutMs = 30000;
        var timer = Qt.createQmlObject("import QtQuick 2.3; Timer {interval: " + timeoutMs + "; repeat: false; running: true;}",networkRequest,"requestTimer");
        timer.triggered.connect(function(){
            //console.log("Timer for the request: " + currentRequest)
        });
    }

    function warnNoServerConnection(){

        popUpWaitServer.close();

        requestParametersGet = "";
        requestParametersPost = "";
    }

    //
    function requestDone(){
        lastPercentDownload = 0;


        if(networkRequest.status == 0){
            popUpWaitServer.close();
            generalPopUp.connectionUnavailable();
            return;
        }

        switch(currentRequestName){
        case simulateRequestName:

            try{
                //console.log(response)
            }catch(e){
                //console.exception(e)
            }



            try{
                //console.log(JSON.stringify(response))
            }catch(e){
                //console.exception(e)
            }

            manageSimulate();
            break;
        case checkJobStatusRequestName:
            manageCheckJobStatus();
            break;
        case registerRequestName:
            manageRegister();
            break;
        case checkRegistrationRequestName:
            manageCheckRegistration();
            break;
        case getMessagesRequestName:

            break;
        case getOutputTilesRequestName:
            manageGetOutputTiles();
            break;
        case getOutputTopofireRequestName:
            manageGetOutputTopofire();
            break;
        case getOutputWxRequestName:
            manageGetOutputWx();
            break;
        case feedbackRequestName:
            manageFeedback();
            break;
        }

        if(currentRequestName != getOutputTilesRequestName && currentRequestName != getOutputTopofireRequestName && currentRequestName != getOutputWxRequestName ){
            popUpWaitServer.close();
        }

        responsePath = "";
    }


    //
    function register(){
        if(app.settings.userName !== "" && app.settings.userEmail !== ""){

            app.settings.deviceId = UtilFunctions.generateUnicId(app.settings.userEmail, app.settings.deviceModel, app.settings.devicePlatform, app.settings.deviceVersion);

            var registration = {
                    "name": app.settings.userName,
                    "email": app.settings.userEmail,
                    "model": app.settings.deviceModel,
                    "platform": app.settings.devicePlatform,
                    "version": app.settings.deviceVersion,
                    "deviceId": app.settings.deviceId
            }

            var stringifyedParameters = "";

            for(var k in registration) {
               stringifyedParameters += k + "=" + registration[k] + "&";
            }

            popUpWaitServer.open();
            var requestUrl = baseUrl + registerRequestPath + "?" + stringifyedParameters;

            WindNinjaClientJs.requestPost(requestUrl, JSON.stringify(registration), function(status, response)
            {
                if(status === 404){

                }else if (status === 0){
                    generalPopUp.connectionUnavailable();
                }else{
                    manageRegister(response)
                }
                popUpWaitServer.close()
            })
        }
    }

    function manageRegister(_response){
        app.settings.registrationId = _response.account;
        app.settings.isRegistered = true;
        app.settings.registrationStatus = _response.accountStatus;
        //checking if its already registered:
        if(_response.message === "Registration accepted; Account pending verification"){
            generalPopUp.registrationAccepted();
        }else if(_response.message === "Account and device exist"){
            generalPopUp.registrationAlreadyExist();
        }
        pageMainLoader.source = "../../Pages/PageMain.qml"
        pageLoader.sourceComponent = undefined;
    }


    //
    function checkRegistration(){
        popUpWaitServer.open();
        var requestUrl = baseUrl + checkRegistrationRequestPath;

        WindNinjaClientJs.requestGet(requestUrl, function(status, response)
        {
            if(status === 404){
                generalPopUp.pleaseRegisterWarn();
            }else if (status === 0){
                generalPopUp.connectionUnavailable();
            }else{
                var newRegistrationStatus = response.status;

                switch (newRegistrationStatus) {
                case 'accepted':
                    if(newRegistrationStatus !== app.settings.registrationStatus){
                        generalPopUp.registrationStatusComplete();
                        app.settings.canSimulate = true;
                    }
                    break;
                case 'pending':
                    generalPopUp.registrationStatusPending();
                    app.settings.canSimulate = false;
                    break;
                case 'disabled':
                    generalPopUp.registrationStatusDisabled();
                    app.settings.canSimulate = false;
                    break;
                }

                app.settings.registrationStatus = newRegistrationStatus;
            }
            popUpWaitServer.close()
        })

    }

    function manageCheckRegistration(){
        if(networkRequest.status == 404){
            generalPopUp.pleaseRegisterWarn();
            return;
        }

        var newRegistrationStatus = response.status;

        switch (newRegistrationStatus) {
        case 'accepted':
            if(newRegistrationStatus !== app.settings.registrationStatus){
                generalPopUp.registrationStatusComplete();
                app.settings.canSimulate = true;
            }
            break;
        case 'pending':
            generalPopUp.registrationStatusPending();
            app.settings.canSimulate = false;
            break;
        case 'disabled':
            generalPopUp.registrationStatusDisabled();
            app.settings.canSimulate = false;
            break;
        }

        app.settings.registrationStatus = newRegistrationStatus;
    }


    //
    function simulate(name, xMin,yMin, xMax, yMax, parameters, forecast, products, account, email){
        var simulation = {
            "name": name,
            "xmin": xMin,
            "ymin": yMin,
            "xmax": xMax,
            "ymax": yMax,
            "parameters": parameters,
            "forecast": forecast,
            "products": products,
            "account": account,
            "email": email
        }

        var stringifyedParameters = "";

        for(var k in simulation) {
           stringifyedParameters += k + "=" + simulation[k] + "&";
        }

        popUpWaitServer.open();
        var requestUrl = baseUrl + simulateRequestPath + "?" + stringifyedParameters;

        WindNinjaClientJs.requestPost(requestUrl, JSON.stringify(simulation), function(status, response)
        {
            if(status === 404){

            }else if (status === 0){
                generalPopUp.connectionUnavailable();
            }else{
                manageSimulate(response)
            }
            popUpWaitServer.close()
        })
    }

    function manageSimulate(_response){
        if(_response === undefined){
            generalPopUp.tryToSimulateAgainWarn();
            return;
        }

        var parameters = [];
        var duration = 0;
        var vegetation = "";
        var model = "";
        try{
            parameters = _response.input.parameters.split(";");
            var durationVegetation = UtilFunctions.getDurationVegetation(parameters);

            duration = durationVegetation.forecast_duration;
            vegetation = durationVegetation.vegetation;
            model = ""
        }catch(err){
            //console.exception(err)
        }



        var _simulation = {
            "idSim" : _response.id,
            "status" : "new",
            "name" : _response.name,
            "subbmitedTimestamp" : UtilFunctions.getSubbmitedTimestamp(_response.messages),
            "model" : model,
            "vegetation" : vegetation,
            "imported" : false,
            "vector" : true,
            "raster" : true,
            "topofire" : true,
            "geopdf" : false,
            "clustered" : false,
            "weather" : true,
            "duration" : duration
        }

        DatabaseFunctions.createSimulation(_simulation)

        pageLoader.source = "../../Pages/PageSimulations.qml"
    }


    //
    function checkJobStatus(jobId, callback){
        checkJobStatusAndUpdate(jobId, callback)
    }

    function manageCheckJobStatus(){

        if(status != 404){
            var checkedIdSim = response.id;
            var checkedSimStatus = response.status;

            switch (checkedSimStatus){
            case "failed":
                deletingFailedSimWarn();
                DatabaseFunctions.deleteSimulation(checkedIdSim);
            case "executing":
            case "succeeded":
                DatabaseFunctions.setSimulationStatus(checkedIdSim, checkedSimStatus);
                break;
            }
        }else{

        }
    }

    function getTilesOutput(jobId){
        //console.log("Getting output tiles.zip for simulation " + jobId)
        currentJobId = jobId;
        var responsePathTiles = AppFramework.userHomeFolder.filePath(zipReader.internalPath + "/" + jobId.replace(/-/g, "") + zipReader.zipTilesFileName);
        sendRequest("GET", undefined, undefined, getOutputTilesRequestName, getOutputRequestPath + jobId.replace(/-/g, "") + zipReader.zipTilesFileName, responsePathTiles);
    }

    function getTopofireOutput(jobId){
        //console.log("Getting output wx_geojson.zip for simulation " + jobId)
        currentJobId = jobId;
        var responsePathTopofire = AppFramework.userHomeFolder.filePath(zipReader.internalPath + "/topofire.zip")//zipReader.zipTopofireFileName);
        sendRequest("GET", undefined, undefined, getOutputTopofireRequestName, getOutputRequestPath + jobId.replace(/-/g, "") + zipReader.zipTopofireFileName, responsePathTopofire);
    }

    function getWxOutput(jobId){
        //console.log("Getting output wx_geojson.zip for simulation " + jobId)
        currentJobId = jobId;
        responseType = "zip"
        var responsePathWx = AppFramework.userHomeFolder.filePath(zipReader.internalPath + "/" + jobId.replace(/-/g, "") + zipReader.zipWxFileName);
        sendRequest("GET", undefined, undefined, getOutputWxRequestName, getOutputRequestPath + jobId.replace(/-/g, "") + zipReader.zipWxFileName, responsePathWx);
    }

    function manageGetOutputTiles(){
        zipReader.extractTilesZip(currentJobId);
        timerServer.start();
    }

    function manageGetOutputTopofire(){
        zipReader.extractTopofireZip();
        timerServer.start();
    }

    function manageGetOutputWx(){
        zipReader.extractWxZip(currentJobId);
        timerServer.start();
    }

    function checkJobStatusAndUpdate(jobId, callback){

        var requestUrl = baseUrl + checkJobStatusRequestPath + jobId;
        popUpWaitServer.open();
        WindNinjaClientJs.requestGet(requestUrl, function(status, response)
        {
            if(status === 404){
                generalPopUp.oldSimulationsWarn();
                DatabaseFunctions.deleteNotDownloadedSimulation(jobId);
                callback(true);
            }else if (status === 0){
                generalPopUp.connectionUnavailable();
            }else{
                var checkedIdSim = response.id;
                var checkedSimStatus = response.status;

                switch (checkedSimStatus){
                case "failed":
                    var errorMessage = "A simulation process failed on the server side and its going to be removed from the simulations list.";
                    errorMessage = UtilFunctions.getErrorMessage(response.messages)
                    DatabaseFunctions.setErrorCause(checkedIdSim, errorMessage);
                    generalPopUp.title = "Simulation error";
                    generalPopUp.text = errorMessage;
                    generalPopUp.open();
                    DatabaseFunctions.setSimulationStatus(checkedIdSim, checkedSimStatus);
                    filefolder.removeFolder(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/" + checkedIdSim.replace(/-/g, "")), true);
                    break;
                case "executing":
                case "succeeded":
                    writeJsonJob(jobId, response);
                    try{
                        DatabaseFunctions.setSimulationDuration(jobId, response.output.weather.files.length);
                    }catch(err){
                        //console.error(err);
                    }
                    DatabaseFunctions.setSimulationSubbmitedTimestamp(checkedIdSim, UtilFunctions.getSubbmitedTimestamp(response.messages));
                    DatabaseFunctions.setSimulationModel(checkedIdSim, UtilFunctions.getModel(response.messages));

                    DatabaseFunctions.setSimulationStatus(checkedIdSim, checkedSimStatus);
                    break;
                }
                callback(true);
            }
            popUpWaitServer.close();
        })
    }

    function checkJobStatusAndSave(jobId){

        popUpWaitServer.open();
        var requestUrl = baseUrl + checkJobStatusRequestPath + jobId;

        WindNinjaClientJs.requestGet(requestUrl, function(status, response)
        {
            if(status === 404){
                generalPopUp.importSimulationInvalidWarn();
            }else if (status === 0){
                generalPopUp.connectionUnavailable();
            }else{
                var importedSimStatus = response.status;

                switch (importedSimStatus){
                case "failed":
                    generalPopUp.importSimulationInvalidWarn();
                    break;
                case "executing":
                case "succeeded":
                    var importedIdSim = response.id;
                    var importedSimName = response.name;
                    var importedSimDuration = 0;
                    var importedSimVegetation = "";
                    var importedSubbmitedTimestamp = "";
                    var importedSimModel = "";

                    var importedParameters = response.input.parameters.split(";");


                    var importedDurationVegetation = UtilFunctions.getDurationVegetation(importedParameters);
                    importedSimVegetation = importedDurationVegetation.vegetation;

                    try{
                        importedSimDuration = response.output.weather.files.length;
                    }catch(err){
                        //console.error(err);
                    }

                    importedSimModel = UtilFunctions.getModel(response.messages);

                    importedSubbmitedTimestamp = UtilFunctions.getSubbmitedTimestamp(response.messages);
                    writeJsonJob(jobId, response);
                    DatabaseFunctions.importSimulation(importedIdSim, importedSimStatus, importedSimName, importedSubbmitedTimestamp,importedSimDuration, importedSimModel, importedSimVegetation);
                    break;
                }
            }
            popUpWaitServer.close();
        });
    }

    function checkJobStatusAndShare(jobId){

        popUpWaitServer.open();
        var requestUrl = baseUrl + checkJobStatusRequestPath + jobId;

        WindNinjaClientJs.requestGet(requestUrl, function(status, response)
        {
            if(status === 404){
                generalPopUp.shareDeletedSim();
            }else if (status === 0){
                generalPopUp.connectionUnavailable();
            }else{
                var checkedIdSim = response.id;
                var checkedSimStatus = response.status;

                switch (checkedSimStatus){
                case "failed":
                    generalPopUp.shareFailedSim();
                    break;
                case "executing":
                    generalPopUp.shareProcesingSim();
                    break;
                case "succeeded":
                    //console.log("Check this simulation on WindNinja!\n" + jobId);
                    AppFramework.clipboard.share("Check this simulation on WindNinja!\n" + jobId);
                    break;
                }
            }
            popUpWaitServer.close()
        })
    }


    function submitFeedback(account, feedback){
        var feedbackData = {
                'account': account,
                'comments': feedback
            };

        var stringifyedParameters = "";

        for(var k in feedbackData) {
           stringifyedParameters += k + "=" + feedbackData[k] + "&";
        }

        popUpWaitServer.open();
        var requestUrl = baseUrl + feedbackRequestPath + "?" + stringifyedParameters;

        //console.log(JSON.stringify(feedbackData))
        WindNinjaClientJs.requestPost(requestUrl, JSON.stringify(feedbackData), function(status, response)
        {
            //console.log(response)
            //console.log(JSON.stringify(response))
            if(status === 404){

            }else if (status === 0){
                generalPopUp.connectionUnavailable();
            }else{
                generalPopUp.feedbackSubmited();
            }
            popUpWaitServer.close()
        })
    }

    function manageFeedback(){
        generalPopUp.feedbackSubmited();
    }

    function writeJsonJob(job, json){
        job = job.replace(/-/g, "");
        json = JSON.stringify(json);
        filefolder.makePath(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/" + job + "/"));
        filefolder.writeFile(AppFramework.userHomeFolder.filePath("ArcGIS/AppStudio/Data/WindNinja/" + job + "/job.json"), json);
    }
}



