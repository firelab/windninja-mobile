function requestGet(url, callback) {

    //console.log("js Client\nURL: " + url)
    var xhr = new XMLHttpRequest();

    var timer = Qt.createQmlObject("import QtQuick 2.3; Timer {interval: 60000; repeat: false; running: true;}",parent,"parent");
    timer.triggered.connect(function(){
        xhr.abort();
    });

    xhr.onreadystatechange = (function(myxhr) {
        return function() {
            if(myxhr.readyState === 4){
                timer.stop()
                if  (myxhr.status === 404)
                {
                    callback(myxhr.status, "")
                }
                else if(myxhr.status === 0){
                    //console.log("No internet connection")
                    callback(myxhr.status, "")
                }
                else
                {
                    var json=JSON.parse(myxhr.responseText)
                    callback(myxhr.status, json)
                }
            }
        }

    })(xhr);
    xhr.open('GET', url, true);
    xhr.send('');
}

function requestPost(url, params, callback) {
    //console.log("js Client\nURL: " + url)
    var xhr = new XMLHttpRequest();

    var timer = Qt.createQmlObject("import QtQuick 2.3; Timer {interval: 60000; repeat: false; running: true;}",parent,"requestTimer");
    timer.triggered.connect(function(){
        xhr.abort();
    });

    xhr.onreadystatechange = (function(myxhr) {
        return function() {
            if(myxhr.readyState === 4){
                timer.stop()
                if  (myxhr.status === 404)
                {
                    callback(myxhr.status, "")
                }
                else if(myxhr.status === 0){
                    //console.log("No internet connection")
                    callback(myxhr.status, "")
                }
                else
                {
                    var json=JSON.parse(myxhr.responseText)
                    callback(myxhr.status,json)
                }
            }
        }

    })(xhr);
    xhr.open('POST', url, true);
    xhr.send(params);
}
