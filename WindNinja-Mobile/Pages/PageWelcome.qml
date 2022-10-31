import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import "../CustomComponents"

Item {

    property bool isAnIos: app.isAnIos();
    property string welcome1Title: qsTr("Welcome To WindNinja!")
    property string welcome1Text: qsTr("\nView spatially varying wind fields for wildland fire support and complex terrain in 3D.\n\n"+
                                       "Generate high-resolution surface wind predictions for your area of interest. Download simulations locally to your device and and load local TPK base map layers for easy offline use in the field.\n\n" +
                                       "To learn more about how to use the application, take a brief tour. You can also access this tour and a detailed user guide through the settings menu in the application for later use.")

    property string welcome2Title: qsTr("Creating a Simulation")
    property string welcome2Text: qsTr("Change the location and size of the simulation boundary to select an area of interest. The simulation area is restricted to a maximum of 70 sq. miles.")

    property string welcome3Title: qsTr("View Simulation in 3D")
    property string welcome3Text: qsTr("Simulations are viewed in a 3D mapping environment. Place fingers on the screen and slide them up and down to adjust the 3D viewing angle.")

    property string welcome4Title: qsTr("Sharing Simulations")
    property string welcome4Text: qsTr("Simulations can be shared with other WindNinja users. A unique identifier is generated for every simulation that can be imported by other users.")

    property string welcome5Title: qsTr("Disclaimer")
    property string welcome5Text: qsTr("The USFS Fire Sciences Laboratory makes no warranties or guarantees, either expressed or implied as to the completeness, accuracy, or correctness of the data portrayed in this product, nor accepts any liability, arising from any incorrect, incomplete or misleading information contained therein. All information, data and databases, are provides “As Is” with no warranty, expressed or implied, including but not limited to, fitness for a particular purpose.\n\n"+
                                       "By downloading, accessing or using this application and/or data contained within the databases, you hereby release The Missoula Fire Sciences Laboratory, its employees, agents, contractors, and suppliers from any and all responsibility and liability associated with its use. In no event shall The USFS Fire Sciences Laboratory or its officers, employees, agents, contractors, and suppliers be liable for any damages arising in any way out of the use of the application or use of the information contained in the databases herein including, but not limited to the Wind Ninja products.\n\n"+
                                       "The USFS Fire Sciences Laboratory makes no warranties, either expressed or implied, concerning the accuracy, completeness, reliability, or suitability of the information provided herein. Nor does The USFS Fire Sciences Laboratory warrant that the use of this information is free of any claims of copyright infringement. THE INFORMATION/APPLICATION IS BEING PROVIDED “AS IS” AND WITHOUT WARRANTY OF ANY KIND EITHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND INFRIGNEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE APPLICATION, SOFTWARE OR DATA OR THE USE OR OTHER DEALINGS IN THE APPLICATION.\n\n")

    id:pageWelcome

    anchors.fill: parent
    signal next()

    Rectangle {
        anchors.fill: parent
        color: "#ffffff"

        ColumnLayout{
            id: controlsLayout
            anchors.fill: parent
            spacing: 12*app.scaleFactor

            SwipeView {
                id: swipeView
                currentIndex: 0
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.topMargin: 30

                WelcomeGifModel{
                    id: welcomeModel1
                    title: welcome1Title
                    contentText: welcome1Text
                    imageSource: "../Assets/Welcome/welcome-screen-image.png"
                    isGif: false
                }
                WelcomeGifModel{
                    id: welcomeModel2
                    title: welcome2Title
                    contentText: welcome2Text
                    imageSource: "../Assets/Welcome/1-create-new-sim-border.gif"
                    isGif: true                    
                }
                WelcomeGifModel{
                    id: welcomeModel3
                    title: welcome3Title
                    contentText: welcome3Text
                    imageSource: "../Assets/Welcome/2-view-sim-3d-border.gif"
                    isGif: true
                }
                WelcomeGifModel{
                    id: welcomeModel4
                    title: welcome4Title
                    contentText: welcome4Text
                    imageSource: "../Assets/Welcome/3-sim-sharing-border.gif"
                    isGif: true
                }

                Component.onCompleted: {
                    var maxCardHeight = Math.max(welcomeModel1.cardHeight,
                                                 welcomeModel2.cardHeight,
                                                 welcomeModel3.cardHeight,
                                                 welcomeModel4.cardHeight)

                    welcomeModel1.cardHeight = maxCardHeight;
                    welcomeModel2.cardHeight = maxCardHeight;
                    welcomeModel3.cardHeight = maxCardHeight;
                    welcomeModel4.cardHeight = maxCardHeight;
                }

            }

            Rectangle{
                id:buttonsLayout
                anchors.left: parent.left
                anchors.right: parent.right
                color: "transparent"
                height: 50

                CustomButton{
                    id:startButton
                    visible:(swipeView.currentIndex === 0) ? true : false
                    text: qsTr("Get started")
                    down:false
                    Material.background: "White"
                    Material.foreground: "Black"
                    Material.primary: "white"
                    Layout.preferredWidth: parent.width * 0.3

                    anchors.left: parent.left

                    onClicked: {
                        if(app.settings.isRegistered){

                            pageMainLoader.source = "PageMain.qml"
                            pageLoader.source = "PageSettings.qml";
                        }else{
                            app.disclaimerCallback = "Login";
                            pageLoader.source = "PageDisclaimer.qml";
                        }
                    }
                }
                CustomButton{
                    id:skipButton
                    visible:(swipeView.currentIndex !== 0) ? true : false
                    text: qsTr("Skip")
                    down:false
                    Material.background: "White"
                    Material.foreground: "Black"
                    Material.primary: "white"
                    width: startButton.width

                    anchors.left: parent.left

                    onClicked: {

                        if(app.settings.isRegistered){
                            pageMainLoader.source = "PageMain.qml"
                            pageLoader.source = "PageSettings.qml";
                        }else{
                            app.disclaimerCallback = "Login";
                            pageLoader.source = "PageDisclaimer.qml";
                        }
                    }
                }
                PageIndicator {
                    id: carousel
                    count: swipeView.count
                    currentIndex: swipeView.currentIndex
                    delegate: Rectangle {
                        implicitWidth: 6*app.scaleFactor
                        implicitHeight: 6*app.scaleFactor
                        radius: width / 2
                        color: index === carousel.currentIndex ? "#008DFF" : "#3C3C36"
                        opacity: index === carousel.currentIndex ? 0.95 : pressed ? 0.7 : 0.45
                        Behavior on opacity {
                            OpacityAnimator {
                                duration: 100
                            }
                        }
                    }
                    onCurrentIndexChanged: {

                    }

                    anchors.centerIn: parent
                }
                CustomButton{
                    id:continueButton
                    text: (swipeView.currentIndex === swipeView.count-1) ? qsTr("Finish") : qsTr("Next")
                    visible: (swipeView.currentIndex !== 0) ? true : false
                    Material.background: "White"
                    Material.foreground: "#008DFF"
                    Material.primary: "White"
                    down:false
                    width: takeaTourButton.width

                    anchors.right: parent.right

                    onClicked: {
                        if(swipeView.currentIndex != swipeView.count-1){
                            swipeView.currentIndex = swipeView.currentIndex+1
                        }else{
                            //Load...

                            if(app.settings.isRegistered){
                                pageLoader.sourceComponent = undefined;
                                pageMainLoader.source = "PageMain.qml"
                                pageLoader.source = "PageSettings.qml";
                            }else{
                                app.disclaimerCallback = "Login";
                                pageLoader.source = "PageDisclaimer.qml";
                            }
                        }
                    }
                }

                CustomButton{
                    id:takeaTourButton
                    visible:(swipeView.currentIndex === 0) ? true : false
                    color: "blue"
                    text: qsTr("Take a tour")
                    Layout.preferredWidth: parent.width * 0.3

                    anchors.right: parent.right

                    onClicked: {
                        swipeView.currentIndex = swipeView.currentIndex+1
                    }
                }
            }

        }
    }
    focus: true // important - otherwise we'll get no key events
    Keys.onReleased: {
        if (event.key === Qt.Key_Back) {
            event.accepted = true
            backButtonPressed()
        }
    }
}
