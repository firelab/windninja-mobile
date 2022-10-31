import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1

Rectangle{
    id:item
    anchors.top: parent.top
    anchors.right: parent.right
    anchors.left: parent.left

    height: 75

    color: "#FFFFFF"
    radius: 5

    property int maxSpeed: 25

    Rectangle{
        color:parent.color
        height: parent.radius
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.left: parent.left
    }

    ColumnLayout{
        id:content
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.left: parent.left
        anchors.topMargin: 10
        anchors.leftMargin: 20
        anchors.rightMargin: 20

        RowLayout{
            Layout.fillWidth: true

            Label{
                text: "Wind Speed (mph)"
                color: "#008DFF"
                font.pixelSize:  14
                font.family: app.fontRobotoMedium.name
            }

            Rectangle{
                color: "transparent"
                Layout.fillWidth: true
                height: 1
            }

            CustomFontIcon{
                color: "#3C3C36"
                icon: app.fontIcons._clear
                MouseArea{
                    anchors.fill: parent
                    onClicked: {
                        item.visible = false
                    }
                }
            }
        }

        RowLayout{
            Layout.fillWidth: true

            Rectangle{
                color: "transparent"
                height: 10
                Layout.fillWidth: true

                Rectangle{
                    width: arrow5.width + arrowText5.width
                    color: "transparent"
                    height: 5
                    anchors.horizontalCenter: parent.horizontalCenter

                    CustomFontIcon{
                        id:arrow1
                        icon: app.fontIcons._back_arrow
                        color: "#1101FC"
                        rotation: 180
                    }
                    Label{
                        id:arrowText1
                        text: "0-0"
                        color: "#838383"
                        font.pixelSize:  12
                        font.family: app.fontRobotoMedium.name
                        anchors.verticalCenter:arrow1.verticalCenter
                        anchors.left: arrow1.right
                    }
                }
            }

            Rectangle{
                color: "transparent"
                height: 10
                Layout.fillWidth: true

                Rectangle{
                    width: arrow5.width + arrowText5.width
                    color: "transparent"
                    height: 5
                    anchors.horizontalCenter: parent.horizontalCenter

                    CustomFontIcon{
                        id:arrow2
                        icon: app.fontIcons._back_arrow
                        color: "#06FE02"
                        rotation: 180
                    }
                    Label{
                        id:arrowText2
                        text: "0-0"
                        color: "#838383"
                        font.pixelSize:  12
                        font.family: app.fontRobotoMedium.name
                        anchors.verticalCenter:arrow2.verticalCenter
                        anchors.left: arrow2.right
                    }
                }
            }

            Rectangle{
                color: "transparent"
                height: 10
                Layout.fillWidth: true

                Rectangle{
                    width: arrow5.width + arrowText5.width
                    color: "transparent"
                    height: 5
                    anchors.horizontalCenter: parent.horizontalCenter

                    CustomFontIcon{
                        id:arrow3
                        icon: app.fontIcons._back_arrow
                        color: "#FBFC00"
                        rotation: 180
                    }
                    Label{
                        id:arrowText3
                        text: "0-0"
                        color: "#838383"
                        font.pixelSize:  12
                        font.family: app.fontRobotoMedium.name
                        anchors.verticalCenter:arrow3.verticalCenter
                        anchors.left: arrow3.right
                    }
                }
            }

            Rectangle{
                color: "transparent"
                height: 10
                Layout.fillWidth: true

                Rectangle{
                    width: arrow5.width + arrowText5.width
                    color: "transparent"
                    height: 5
                    anchors.horizontalCenter: parent.horizontalCenter

                    CustomFontIcon{
                        id:arrow4
                        icon: app.fontIcons._back_arrow
                        color: "#FDA402"
                        rotation: 180
                    }
                    Label{
                        id:arrowText4
                        text: "0-0"
                        color: "#838383"
                        font.pixelSize:  12
                        font.family: app.fontRobotoMedium.name
                        anchors.verticalCenter:arrow4.verticalCenter
                        anchors.left: arrow4.right
                    }
                }
            }

            Rectangle{
                color: "transparent"
                height: 10
                Layout.fillWidth: true

                Rectangle{
                    width: arrow5.width + arrowText5.width
                    color: "transparent"
                    height: 5
                    anchors.horizontalCenter: parent.horizontalCenter

                    CustomFontIcon{
                        id:arrow5
                        icon: app.fontIcons._back_arrow
                        color: "#FC0400"
                        rotation: 180
                    }
                    Label{
                        id:arrowText5
                        text: "100-150"
                        color: "#838383"
                        font.pixelSize:  12
                        font.family: app.fontRobotoMedium.name
                        anchors.verticalCenter:arrow5.verticalCenter
                        anchors.left: arrow5.right
                    }
                }
            }
        }
    }

    onMaxSpeedChanged: setSpeedValues();

    Component.onCompleted: maxSpeed = 111
    function setSpeedValues(){
        var speedStep = Math.round(maxSpeed/5)
        arrowText1.text = "0 - "+speedStep
        arrowText2.text = speedStep+" - "+speedStep*2
        arrowText3.text = speedStep*2+" - "+speedStep*3
        arrowText4.text = speedStep*3+" - "+speedStep*4
        arrowText5.text = speedStep*4+" - "+maxSpeed
    }

}
