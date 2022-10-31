import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.2
import QtQuick.Controls.Material 2.1

Item {
    id: item
    height: 25

    anchors.left: parent.left
    anchors.right: parent.right

    property alias text: radioItem.text
    property string icon: ""
    property alias checked: radioItem.checked

    signal clicked();

    Label{
        id:helpLabel
        visible: false
        text: text
    }

    RowLayout{
        anchors.left: parent.left
        anchors.right: parent.right

        CustomFontIcon{
            id:customFontIcon
            icon: item.icon
            color: "#3C3C36"
            visible: item.icon != ""
        }

        RadioDelegate{
            id:radioItem
            Material.accent: "#008DFF"
            Layout.fillWidth: true
        }
    }

    MouseArea{
        anchors.fill: parent;
        onClicked: {
            item.clicked();
        }
    }
}
