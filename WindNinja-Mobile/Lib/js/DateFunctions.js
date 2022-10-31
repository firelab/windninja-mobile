// MM/dd/yyyy - HH:mm
function dateFormat(date) {
    date = new Date(date);
    var month = ("0" + (date.getMonth() +1 )).slice(-2);
    var day = ("0" + date.getDate()).slice(-2);
    var year = date.getFullYear();

    var hour = ("0" + date.getHours()).slice(-2);
    var minutes = ("0" + date.getMinutes()).slice(-2);

    var returnValue = month + "/" + day + "/" + year + " - " + hour + ":" + minutes;

    return returnValue;
}

//From  dem_05-15-2017_1800_201m to MM/dd/yyyy - HH:mm
function formatDemDate(demDate){
    var demDateSplited = demDate.split("_");
    var firstPart = demDateSplited[1].replace("-", "/").replace("-", "/");
    var secondPart = demDateSplited[2].substring(0, 2) + ":" + demDateSplited[2].substring(2, 4);
    return firstPart + " - " + secondPart;
}

//From  20190311T0800 to MM/dd/yyyy - HH:mm
function formatTDate(TDate){
    var TDateSplited = TDate.split("T");
    var firstPart = TDateSplited[0].substring(0, 4) + "/" + TDateSplited[0].substring(4, 6) + "/" + TDateSplited[0].substring(6, 8);
    var secondPart = TDateSplited[1].substring(0, 2) + ":" + TDateSplited[1].substring(2, 4);
    return firstPart + " - " + secondPart;
}

//
function formatMessageDate(messageDate){
    var splitedMessageDate = messageDate.split("T");
    var splitedDate = splitedMessageDate[0].split("-");
    var splitedTime = splitedMessageDate[1].split(":");
    var year = splitedDate[0];
    var month = splitedDate[1];
    var day = splitedDate[2];
    var hour = splitedTime[0];
    var minute = splitedTime[1];
    var completeTime = year + "/" + month + "/" + day + ", " + hour + ":" + minute;
    return completeTime;
}
