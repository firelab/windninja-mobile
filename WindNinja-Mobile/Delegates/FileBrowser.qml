import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1

import Qt.labs.folderlistmodel 2.1


    Rectangle {
        function isTPK(name){
            if(name.endsWith(".tpk")){
                return true
            }
            return false
        }

        id: fileBrowser
        color: "transparent"
        z: 4

        property string folder:{ "/" }        
        property bool shown: loader.sourceComponent

        signal fileSelected(string file)

        function selectFile(file) {
            if (file !== "" && file.endsWith(".tpk")) {
                folder = loader.item.folders.folder
                fileBrowser.fileSelected(file)
            }else{
                fileBrowser.fileSelected("")
            }
            loader.sourceComponent = undefined

        }

        Loader {
            id: loader
        }

        function open() {
            loader.sourceComponent = fileBrowserComponent
            loader.item.parent = fileBrowser
            loader.item.anchors.fill = fileBrowser
            loader.item.folder = fileBrowser.folder
        }

        Component {
            id: fileBrowserComponent

            Rectangle {
                id: root
                color: "White"
                property bool showFocusHighlight: false
                property variant folders: folders1
                property variant view: view1
                property alias folder: folders1.folder
                property color textColor: "#008DFF"
                clip:true
                FolderListModel {
                    id: folders1
                    folder: folder
                }

                FolderListModel {
                    id: folders2
                    folder: folder
                }

                SystemPalette {
                    id: palette
                }

                Component {
                    id: folderDelegate

                    Rectangle {
                        id: wrapper
                        function launch() {
                            var path = "file://";
                            if (filePath.length > 2 && filePath[1] === ':') // Windows drive logic, see QUrl::fromLocalFile()
                                path += '/';
                            path += filePath;
                            if (folders.isFolder(index))
                                down(path);
                            else
                                fileBrowser.selectFile(path)
                        }
                        width: root.width
                        height: itemHeight
                        color: "transparent"

                        Rectangle {
                            id: highlight; visible: false
                            anchors.fill: parent
                            color: palette.highlight
                            gradient: Gradient {
                                GradientStop { id: t1; position: 0.0; color: palette.highlight }
                                GradientStop { id: t2; position: 1.0; color: Qt.lighter(palette.highlight) }
                            }
                        }

                        Item {
                            width: itemHeight; height: itemHeight
                            Image {
                                source: folders.isFolder(index) ? "../Assets/back-arrow.png" : "../Assets/WindNinja-AppIcon-Android.png"
                                rotation: isTPK(nameText.text) ? 0 : 180
                                fillMode: Image.PreserveAspectFit
                                anchors.fill: parent
                                anchors.margins: scaledMargin
                                visible: folders.isFolder(index) || isTPK(nameText.text)
                            }
                        }

                        Text {
                            id: nameText
                            anchors.fill: parent;
                            verticalAlignment: Text.AlignVCenter
                            text: fileName
                            anchors.leftMargin: itemHeight + scaledMargin
                            font.pixelSize: 12
                            color: (wrapper.ListView.isCurrentItem && root.showFocusHighlight) ? palette.highlightedText : "#008DFF"
                            elide: Text.ElideRight
                        }

                        MouseArea {
                            id: mouseRegion
                            anchors.fill: parent
                            onPressed: {
                                root.showFocusHighlight = false;
                                wrapper.ListView.view.currentIndex = index;
                            }
                            onClicked: { if (folders == wrapper.ListView.view.model) launch() }
                        }

                        states: [
                            State {
                                name: "pressed"
                                when: mouseRegion.pressed
                                PropertyChanges { target: highlight; visible: true }
                                PropertyChanges { target: nameText; color: palette.highlightedText }
                            }
                        ]
                    }
                }

                ListView {
                    id: view1
                    anchors.top: titleBar.bottom
                    anchors.bottom: cancelButton.top
                    x: 0
                    width: parent.width
                    model: folders1
                    delegate: folderDelegate
                    highlight: Rectangle {
                        color: palette.highlight
                        visible: root.showFocusHighlight && view1.count != 0
                        gradient: Gradient {
                            GradientStop { id: t1; position: 0.0; color: palette.highlight }
                            GradientStop { id: t2; position: 1.0; color: Qt.lighter(palette.highlight) }
                        }
                        width: view1.currentItem == null ? 0 : view1.currentItem.width
                    }
                    highlightMoveVelocity: 1000
                    pressDelay: 50
                    focus: true
                    state: "current"
                    states: [
                        State {
                            name: "current"
                            PropertyChanges { target: view1; x: 0 }
                        },
                        State {
                            name: "exitLeft"
                            PropertyChanges { target: view1; x: -root.width }
                        },
                        State {
                            name: "exitRight"
                            PropertyChanges { target: view1; x: root.width }
                        }
                    ]
                    transitions: [
                        Transition {
                            to: "current"
                            SequentialAnimation {
                                NumberAnimation { properties: "x"; duration: 250 }
                            }
                        },
                        Transition {
                            NumberAnimation { properties: "x"; duration: 250 }
                            NumberAnimation { properties: "x"; duration: 250 }
                        }
                    ]
                    Keys.onPressed: root.keyPressed(event.key)
                }

                ListView {
                    id: view2
                    anchors.top: titleBar.bottom
                    anchors.bottom: cancelButton.top
                    x: parent.width
                    width: parent.width
                    model: folders2
                    delegate: folderDelegate
                    highlight: Rectangle {
                        color: palette.highlight
                        visible: root.showFocusHighlight && view2.count != 0
                        gradient: Gradient {
                            GradientStop { id: t13; position: 0.0; color: palette.highlight }
                            GradientStop { id: t23; position: 1.0; color: Qt.lighter(palette.highlight) }
                        }
                        width: view1.currentItem == null ? 0 : view1.currentItem.width
                    }
                    highlightMoveVelocity: 1000
                    pressDelay: 50
                    states: [
                        State {
                            name: "current"
                            PropertyChanges { target: view2; x: 0 }
                        },
                        State {
                            name: "exitLeft"
                            PropertyChanges { target: view2; x: -root.width }
                        },
                        State {
                            name: "exitRight"
                            PropertyChanges { target: view2; x: root.width }
                        }
                    ]
                    transitions: [
                        Transition {
                            to: "current"
                            SequentialAnimation {
                                NumberAnimation { properties: "x"; duration: 250 }
                            }
                        },
                        Transition {
                            NumberAnimation { properties: "x"; duration: 250 }
                        }
                    ]
                    Keys.onPressed: root.keyPressed(event.key)
                }

                Button {
                    id: cancelButton
                    width: parent.width
                    //height: itemHeight
                    Material.background:  "#008DFF"
                    Material.foreground:  "#000000"
                    anchors { bottom: parent.bottom; right: parent.right; }
                    text: "Cancel"
                    onClicked: fileBrowser.selectFile("")
                }

                Keys.onPressed: {
                    root.keyPressed(event.key);
                    if (event.key === Qt.Key_Return || event.key === Qt.Key_Select || event.key === Qt.Key_Right) {
                        view.currentItem.launch();
                        event.accepted = true;
                    } else if (event.key === Qt.Key_Left) {
                        up();
                    }
                }

                // titlebar
                Rectangle {
                    color: "#008DFF"
                    width: parent.width;
                    height: itemHeight
                    id: titleBar

                    Rectangle {
                        id: upButton
                        width: titleBar.height
                        height: titleBar.height
                        color: "transparent"
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: scaledMargin
                        Image { anchors.fill: parent; anchors.margins: scaledMargin; source: "../Assets/back-arrow.png" }
                        MouseArea { id: upRegion; anchors.fill: parent; onClicked: up() }
                        states: [
                            State {
                                name: "pressed"
                                when: upRegion.pressed
                                PropertyChanges { target: upButton; color: palette.highlight }
                            }
                        ]
                    }

                    Text {
                        anchors.left: upButton.right; anchors.right: parent.right; height: parent.height
                        anchors.leftMargin: 10; anchors.rightMargin: 4
                        text: folders.folder
                        color: "white"
                        elide: Text.ElideLeft; horizontalAlignment: Text.AlignLeft; verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                }

                Rectangle {
                    color: "#353535"
                    width: parent.width
                    height: 1
                    anchors.top: titleBar.bottom
                }

                function down(path) {
                    if (folders == folders1) {
                        view = view2
                        folders = folders2;
                        view1.state = "exitLeft";
                    } else {
                        view = view1
                        folders = folders1;
                        view2.state = "exitLeft";
                    }
                    view.x = root.width;
                    view.state = "current";
                    view.focus = true;
                    folders.folder = path;
                }

                function up() {
                    var path = folders.parentFolder;
                    if (path.toString().length === 0 || path.toString() === 'file:')
                        return;
                    if (folders == folders1) {
                        view = view2
                        folders = folders2;
                        view1.state = "exitRight";
                    } else {
                        view = view1
                        folders = folders1;
                        view2.state = "exitRight";
                    }
                    view.x = -root.width;
                    view.state = "current";
                    view.focus = true;
                    folders.folder = path;
                }

                function keyPressed(key) {
                    switch (key) {
                        case Qt.Key_Up:
                        case Qt.Key_Down:
                        case Qt.Key_Left:
                        case Qt.Key_Right:
                            root.showFocusHighlight = true;
                        break;
                        default:
                            // do nothing
                        break;
                    }
                }
            }
        }
    }

