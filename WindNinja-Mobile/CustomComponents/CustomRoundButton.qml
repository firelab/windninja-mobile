import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

RoundButton{
    property alias buttonIcon: customFontIconRoundButton.icon
    property string color: "gray"

    height: 50
    width: 50

    CustomFontIcon{
        id:customFontIconRoundButton
        anchors.centerIn: parent
        color: "black"
    }

    Component.onCompleted: {
        if(color == "blue"){
            customFontIconRoundButton.color = "white"
            customFontIconRoundButton.font.pixelSize =  customFontIconRoundButton.font.pixelSize+4
            Material.background = "#008DFF"
            height = 60
            width = 60
        }else{
            customFontIconRoundButton.font.pixelSize = customFontIconRoundButton.font.pixelSize-4
        }
    }
}
