import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

Item{
    id:item
    //anchors.fill: parent
    anchors.left: parent.left
    anchors.right: parent.right
    height: content.height+100

    signal previousPressed();
    signal nextPressed();
    signal playPressed();
    signal wxPressed();
    signal legendPressed();
    signal extendPressed();
    signal closePressed();

    property alias maxWindSpeed: legend.maxSpeed;
    property alias simName: simName.text;
    property alias currentTimestamp: controllerCurrentTimestamp.text
    readonly property alias legendVisible: legend.visible;
    property bool wxVisible: false

    property bool playing: false;

    CustomLeyend{
        id:legend
    }

    Rectangle{
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.left: parent.left

        height: content.height+10

        color: "#FFFFFF"
        radius: 5

        Rectangle{
            color:parent.color
            height: parent.radius
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.left: parent.left
        }

        ColumnLayout{
            id:content

            anchors.top: parent.top
            anchors.right: parent.right
            anchors.left: parent.left
            anchors.topMargin: 5
            anchors.leftMargin: 10
            anchors.rightMargin: 10

            RowLayout{
                Layout.fillWidth: true
                spacing: 10

                Label{
                    id:simName
                    text: "Simulation Name"
                    color: "#3C3C36"
                    font.pixelSize:  20
                    font.family: app.fontRobotoMedium.name
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                Label{
                    text: "Wx"
                    color: wxVisible ? "#008DFF" : "#3C3C36"
                    font.pixelSize:  16
                    font.family: app.fontRobotoMedium.name
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            wxPressed();
                        }
                    }
                }

                CustomFontIcon{
                    color: legend.visible ? "#008DFF" : "#3C3C36"
                    icon: app.fontIcons._legend
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            legend.visible = !legend.visible;
                            legendPressed();
                        }
                    }
                }

                CustomFontIcon{
                    color: "#3C3C36"
                    icon: app.fontIcons._zoom_to_sim_exten
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            extendPressed();
                        }
                    }
                }

                CustomFontIcon{
                    color: "#3C3C36"
                    icon: app.fontIcons._clear
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            closePressed();
                        }
                    }
                }
            }

            Rectangle{
                color: "#838383"
                height: 1
                anchors.right: parent.right
                anchors.left: parent.left

                opacity: 0.25

                anchors.leftMargin: -20
                anchors.rightMargin: -20
            }

            RowLayout{
                Layout.fillWidth: true
                spacing: 10

                Label{
                    id:controllerCurrentTimestamp;
                    text: "dd/MM/yyyy - HH:mm"
                    color: "#008DFF"
                    font.pixelSize:  20
                    font.family: app.fontRobotoMedium.name
                    Layout.fillWidth: true
                    elide: Text.ElideRight
                }

                CustomFontIcon{
                    color: "#838383"
                    icon: app.fontIcons._previous
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            previousPressed();
                        }
                    }
                }

                CustomFontIcon{
                    id:playIcon
                    color: "#3C3C36"
                    icon: vectorField.playingAnimation ? app.fontIcons._pause : app.fontIcons._play
                    font.pixelSize: 50
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            playPressed();

                            if(vectorField.playingAnimation){
                                playIcon.changeIcon(app.fontIcons._pause);
                            }else{
                                playIcon.changeIcon(app.fontIcons._play);
                            }
                        }
                    }
                }

                CustomFontIcon{
                    color: "#838383"
                    icon: app.fontIcons._next
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            nextPressed();
                        }
                    }
                }
            }

            ProgressBar{
                anchors.right: parent.right;
                anchors.left: parent.left;
                anchors.bottom: parent.bottom;
                anchors.leftMargin: -10;
                anchors.rightMargin: -10;
                anchors.bottomMargin: 2;
                from:0;
                to:vectorfield.ntime-1;
                value: vectorfield.timeIndex;
                Material.accent: "#008DFF";

                Rectangle{
                    anchors.right: parent.right;
                    anchors.left: parent.left;
                    anchors.top: parent.top;
                    color: "#FFFFFF";
                    height: 0;
                    z:999;
                }

                Rectangle{
                    height: 8;
                    width: 8;
                    radius: 8;
                    color: "#008DFF";
                    z:9999;
                    anchors.left: parent.left;
                    anchors.leftMargin: parent.width * parent.position - 4;
                    anchors.verticalCenter: parent.verticalCenter;
                }
            }

            Rectangle{
                color: "#838383"
                height: 2
                anchors.right: parent.right
                anchors.left: parent.left
                opacity: 0.25
                anchors.leftMargin: -20
                anchors.rightMargin: -20
            }
        }

    }

    function reset(){
        playing = false;
        wxVisible = false;
        wx.visible = false;
        vectorField.reloadLayers();
        legend.visible = true;

        if(vectorField.playingAnimation){
            playIcon.changeIcon(app.fontIcons._pause);
        }else{
            playIcon.changeIcon(app.fontIcons._play);
        }
    }

    function close(){
        closePressed();
    }
}
