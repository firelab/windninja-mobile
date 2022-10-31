import QtQuick 2.7
import QtQuick.Layouts 1.1
import QtQuick.Controls 2.1
import QtQuick.Controls.Material 2.1
import "../CustomComponents"

Item {

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

            WelcomeModel{
                title: welcome5Title
                contentText: welcome5Text
                isFlickable: true
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

            RowLayout{
                id:buttonsLayout
                anchors.left: parent.left
                anchors.right: parent.right
                spacing: 0

                Rectangle{
                    Layout.fillWidth: true
                    color: "transparent"
                    height: 1
                }

                CustomButton{
                    id:takeaTourButton
                    color: "blue"
                    text: qsTr("Close")
                    onClicked: {
                        if(app.disclaimerCallback === "Settings"){
                            pageLoader.source = "PageSettings.qml"
                        }else{
                            pageLoader.source = "PageRegister.qml"
                        }
                    }
                }

                Rectangle{
                    Layout.fillWidth: true
                    color: "transparent"
                    height: 1
                }
            }

            Item{
                Layout.fillWidth: true
                Layout.preferredHeight: 1
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
