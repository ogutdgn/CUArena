// The Word-like ribbon: a tab strip over a horizontally-scrollable group strip,
// both driven entirely by ribbonData (resources/ribbon.json). Adding/moving
// tabs or commands is a data change — never a QML change (CLAUDE.md value #2).
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Rectangle {
    id: root
    property var ribbonModel             // { schemaVersion, tabs: [...] }
    property var engine
    property var stateMap: ({})
    property int currentTab: 0

    readonly property var tabs: (ribbonModel && ribbonModel.tabs) ? ribbonModel.tabs : []
    readonly property var currentGroups: (currentTab >= 0 && currentTab < tabs.length)
                                         ? tabs[currentTab].groups : []

    implicitHeight: 146
    color: "#2b2b2b"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // --- tab strip ---
        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: 6
            Layout.preferredHeight: 30
            spacing: 0
            Repeater {
                model: root.tabs
                delegate: ItemDelegate {
                    required property int index
                    required property var modelData
                    text: modelData.name
                    padding: 10
                    onClicked: root.currentTab = index
                    contentItem: Text {
                        text: parent.text
                        color: index === root.currentTab ? "#ffffff" : "#c8c8c8"
                        font.pixelSize: 13
                        verticalAlignment: Text.AlignVCenter
                    }
                    background: Rectangle {
                        color: index === root.currentTab ? "#1f1f1f" : "transparent"
                        Rectangle {                       // Word-blue accent underline
                            visible: index === root.currentTab
                            anchors.bottom: parent.bottom
                            anchors.horizontalCenter: parent.horizontalCenter
                            width: parent.width * 0.7
                            height: 2
                            color: "#4a6fb5"
                        }
                    }
                }
            }
            Item { Layout.fillWidth: true }
        }

        // --- group strip (scrolls horizontally if it overflows) ---
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#1f1f1f"

            Flickable {
                anchors.fill: parent
                contentWidth: groupRow.width
                contentHeight: height
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }

                Row {
                    id: groupRow
                    height: parent.height
                    leftPadding: 6
                    Repeater {
                        model: root.currentGroups
                        delegate: RibbonGroup {
                            required property var modelData
                            group: modelData
                            engine: root.engine
                            stateMap: root.stateMap
                            height: groupRow.height
                        }
                    }
                }
            }
        }
    }
}
