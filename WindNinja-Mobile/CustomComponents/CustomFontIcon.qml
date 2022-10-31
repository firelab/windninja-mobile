import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

Label{
    property string icon: ""
    text: ""
    font.family: app.fontWindNinjaUi.name;
    font.pixelSize: 25
    horizontalAlignment: Text.AlignHCenter

    Component.onCompleted: resolveTextIcon();

    function changeIcon(icon){
        switch(icon){
            case "next":
                text = "a";
                break;
            case "previous":
                text = "b";
                break;
            case "pause":
                text = "c";
                break;
            case "play":
                text = "d";
                break;
            case "zoom-to-sim-exten":
                text = "e";
                break;
            case "confirm":
                text = "f";
                break;
            case "delete":
                text = "g";
                break;
            case "add-tpk":
                text = "h";
                break;
            case "refresh":
                text = "i";
                break;
            case "more-menu":
                text = "j";
                break;
            case "back-arrow":
                text = "k";
                break;
            case "create-sim":
                text = "l";
                break;
            case "map-pin":
                text = "m";
                break;
            case "disclaimer":
                text = "n";
                break;
            case "help":
                text = "o";
                break;
            case "feedback":
                text = "p";
                break;
            case "about":
                text = "q";
                break;
            case "register":
                text = "r";
                break;
            case "dropdown":
                text = "s";
                break;
            case "clear":
                text = "t";
                break;
            case "north-compass":
                text = "u";
                break;
            case "my-location":
                text = "v";
                break;
            case "settings":
                text = "w";
                break;
            case "search":
                text = "x";
                break;
            case "legend":
                text = "y";
                break;
            case "layers":
                text = "z";
                break;
            case "simulation-list":
                text = "1";
                break;
            case "close":
                text = "2";
                break;
            case "fail-Sim":
                text = "4";
                break;
            case "share":
                text = "5";
                break;
            case"plus":
                text = "6"
                break;
            default:
                text = "o";
        }
    }

    function resolveTextIcon(){
        if(icon != "" && text == ""){
            switch(icon){
                case "next":
                    text = "a";
                    break;
                case "previous":
                    text = "b";
                    break;
                case "pause":
                    text = "c";
                    break;
                case "play":
                    text = "d";
                    break;
                case "zoom-to-sim-exten":
                    text = "e";
                    break;
                case "confirm":
                    text = "f";
                    break;
                case "delete":
                    text = "g";
                    break;
                case "add-tpk":
                    text = "h";
                    break;
                case "refresh":
                    text = "i";
                    break;
                case "more-menu":
                    text = "j";
                    break;
                case "back-arrow":
                    text = "k";
                    break;
                case "create-sim":
                    text = "l";
                    break;
                case "map-pin":
                    text = "m";
                    break;
                case "disclaimer":
                    text = "n";
                    break;
                case "help":
                    text = "o";
                    break;
                case "feedback":
                    text = "p";
                    break;
                case "about":
                    text = "q";
                    break;
                case "register":
                    text = "r";
                    break;
                case "dropdown":
                    text = "s";
                    break;
                case "clear":
                    text = "t";
                    break;
                case "north-compass":
                    text = "u";
                    break;
                case "my-location":
                    text = "v";
                    break;
                case "settings":
                    text = "w";
                    break;
                case "search":
                    text = "x";
                    break;
                case "legend":
                    text = "y";
                    break;
                case "layers":
                    text = "z";
                    break;
                case "simulation-list":
                    text = "1";
                    break;
                case "close":
                    text = "2";
                    break;
                case "fail-Sim":
                    text = "4";
                    break;
                case "share":
                    text = "5";
                    break;
                case"plus":
                    text = "6"
                    break;
                case"processing":
                    text = "7"
                    break;
                case"download":
                    text = "8"
                    break;
                case"view":
                    text = "9"
                    break;
                default:
                    text = "o";
            }
        }else if(icon == "" && text != ""){
            switch(text){
                case "a":
                    icon = "next";
                    break;
                case "b":
                    icon = "previous";
                    break;
                case "c":
                    icon = "pause";
                    break;
                case "d":
                    icon = "play";
                    break;
                case "e":
                    icon = "zoom-to-sim-exten";
                    break;
                case "f":
                    icon = "confirm";
                    break;
                case "g":
                    icon = "delete";
                    break;
                case "h":
                    icon = "add-tpk";
                    break;
                case "i":
                    icon = "refresh";
                    break;
                case "j":
                    icon = "more-menu";
                    break;
                case "k":
                    icon = "back-arrow";
                    break;
                case "l":
                    icon = "create-sim";
                    break;
                case "m":
                    icon = "map-pin";
                    break;
                case "n":
                    icon = "disclaimer";
                    break;
                case "o":
                    icon = "help";
                    break;
                case "p":
                    icon = "feedback";
                    break;
                case "q":
                    icon = "about";
                    break;
                case "r":
                    icon = "register";
                    break;
                case "s":
                    icon = "dropdown";
                    break;
                case "t":
                    icon = "clear";
                    break;
                case "u":
                    icon = "north-compass";
                    break;
                case "v":
                    icon = "my-location";
                    break;
                case "w":
                    icon = "settings";
                    break;
                case "x":
                    icon = "search";
                    break;
                case "y":
                    icon = "legend";
                    break;
                case "z":
                    icon = "layers";
                    break;
                case "1":
                    icon = "simulation-list";
                    break;
                case "2":
                    icon = "close";
                    break;
                case "4":
                    text = "fail-Sim";
                    break;
                case "5":
                    text = "share";
                    break;
                case"6":
                    text = "plus"
                    break;
                case"7":
                    text = "processing"
                    break;
                case"8":
                    text = "download"
                    break;
                case"9":
                    text = "view"
                    break;
                default:
                    text = "o";
            }
        }else if(icon == "" && text == ""){
            text = "o"
        }
    }
}
