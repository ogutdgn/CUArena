// Writer shell — W2 skeleton. Word-like layout placeholders; the real ribbon
// (W3, driven by resources/command-catalog.json) and the LOK tile canvas
// (W2 binding step) replace the placeholders below.
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

ApplicationWindow {
    id: win
    width: 1200
    height: 780
    visible: true
    title: "Document1 — Writer"
    color: "#1f1f1f"

    // Word M365 ribbon tab order (placeholder strip; real ribbon = W3).
    readonly property var ribbonTabs: [
        "File", "Home", "Insert", "Draw", "Design", "Layout",
        "References", "Mailings", "Review", "View", "Help"
    ]
    property int currentTab: 1   // Home

    header: Rectangle {
        height: 92
        color: "#2b2b2b"
        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // tab row
            RowLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 6
                spacing: 0
                Repeater {
                    model: win.ribbonTabs
                    delegate: ItemDelegate {
                        required property int index
                        required property string modelData
                        text: modelData
                        font.pixelSize: 13
                        onClicked: win.currentTab = index
                        contentItem: Text {
                            text: parent.text
                            color: index === win.currentTab ? "#ffffff" : "#c8c8c8"
                            font: parent.font
                            verticalAlignment: Text.AlignVCenter
                        }
                        background: Rectangle {
                            color: index === win.currentTab ? "#1f1f1f" : "transparent"
                            Rectangle {  // accent underline (Word blue)
                                visible: index === win.currentTab
                                anchors.bottom: parent.bottom
                                anchors.horizontalCenter: parent.horizontalCenter
                                width: parent.width * 0.6
                                height: 2
                                color: "#2b5797"
                            }
                        }
                    }
                }
                Item { Layout.fillWidth: true }
            }

            // ribbon group strip (placeholder — W3 fills from command catalog)
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#1f1f1f"
                Label {
                    anchors.centerIn: parent
                    color: "#6f6f6f"
                    font.pixelSize: 11
                    text: "ribbon groups for “" + win.ribbonTabs[win.currentTab] + "” — wired in W3 from command-catalog.json"
                }
            }
        }
    }

    // document workspace (LOK tiles blit onto the page in the W2 binding step)
    Rectangle {
        anchors.fill: parent
        color: "#3a3a3a"
        Rectangle {
            id: page
            width: 794            // ~A4 width @ 96dpi (real size from LOK getDocumentSize)
            height: 1123
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 28
            color: "white"
            Label {
                anchors.centerIn: parent
                color: "#bdbdbd"
                font.pixelSize: 12
                text: "document canvas — LOK tiled render (W2 binding)"
            }
        }
    }

    footer: Rectangle {
        height: 24
        color: "#2b5797"
        Label {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 10
            color: "white"
            font.pixelSize: 11
            text: "Page 1   ·   0 words   ·   Writer (LOK engine)"
        }
    }
}
