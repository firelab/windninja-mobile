import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

RoundButton{

    property string color: "gray"

    Layout.preferredWidth: app.width*0.45
    Layout.preferredHeight: 50
    highlighted: false
    down: true
    radius: 2
    flat: true
    Material.foreground: color == "gray" ? "#393939" : "#FFFFFF"
    Material.primary: color == "gray" ? "#393939" : "#FFFFFF"
    Material.background: color == "gray" ? "#FaFaFa" : "#008DFF"

    font.family: app.fontRobotoMedium.name
    font.pixelSize: 14

    text: qsTr("text")
    Layout.alignment: Qt.AlignHCenter
}
