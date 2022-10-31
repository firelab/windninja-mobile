import QtQuick 2.0
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

Item {
    id:item
    Layout.fillWidth: true

    Layout.leftMargin: 10

    implicitWidth: 300
    implicitHeight: 43

    property alias value: slider.value
    property alias text: customTextField.text

    CustomTextField{
        id:customTextField
        text: "1";
        readOnly:true
        horizontalAlignment: TextInput.AlignRight
        width: app.width*0.10
    }

    Slider{
        id:slider
        Layout.fillWidth: true
        width: app.width*0.80 - 30
        Material.accent: "#008DFF"
        anchors.left: customTextField.right
        anchors.leftMargin: app.width*0.10
        from:1
        to: 15
        stepSize: 1
        onMoved: {customTextField.text=Math.round((value)*100)/100}
    }
}
