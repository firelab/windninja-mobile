import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.2
import QtQuick.Controls.Material 2.1

Item {
    id: item
    height: 25

    anchors.left: parent.left
    anchors.right: parent.right

    property alias text: label.text
    property string icon: ""
    property alias checked: _switch.checked
    property alias enabled: _switch.enabled;

    signal clicked();
    property bool fullListener: true;

    RowLayout{
        anchors.left: parent.left
        anchors.right: parent.right

        CustomFontIcon{
            id:customFontIcon
            icon: item.icon
            color: "#3C3C36"
            visible: item.icon != ""
            Layout.rightMargin: 15
        }

        Label{
            id:label
            Layout.fillWidth: true
            color: "#3C3C36"
            font.pixelSize: 16
            font.family: app.fontRobotoRegular.name
            elide: Text.ElideRight            
        }

        Switch{
            id:_switch
            Material.accent: "#008DFF"
        }
    }

    MouseArea{
        anchors.fill: fullListener ? parent : "";
        onClicked: {
            item.clicked();
        }
    }
}
