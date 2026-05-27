// One ribbon group: large buttons first, then small buttons packed into a
// 3-row grid (columns wrap), with the group name centred underneath and a
// vertical separator on the right. Data-driven from a ribbon.json group.
import QtQuick

Item {
    id: root
    required property var group         // { name, items: [...] }
    property var engine
    property var stateMap: ({})

    function isCombo(i) { return i.kind === "fontname" || i.kind === "fontsize"; }
    readonly property var comboItems: (group.items || []).filter(function (i) { return root.isCombo(i); })
    readonly property var largeItems: (group.items || []).filter(function (i) { return i.size === "lg" && !root.isCombo(i); })
    readonly property var smallItems: (group.items || []).filter(function (i) { return i.size !== "lg" && !root.isCombo(i); })

    // wide enough for the buttons OR the group label, whichever is wider
    implicitWidth: Math.max(body.implicitWidth, nameLabel.implicitWidth) + 18
    implicitHeight: 108

    Column {
        id: col
        anchors.centerIn: parent
        spacing: 4

        Row {
            id: body
            spacing: 3
            anchors.horizontalCenter: parent.horizontalCenter

            // editable combos (font name / size) stacked, vertically centred
            Column {
                spacing: 3
                anchors.verticalCenter: parent.verticalCenter
                visible: root.comboItems.length > 0
                Repeater {
                    model: root.comboItems
                    delegate: RibbonCombo {
                        required property var modelData
                        item: modelData
                        engine: root.engine
                        stateMap: root.stateMap
                    }
                }
            }

            Repeater {
                model: root.largeItems
                delegate: RibbonButton {
                    required property var modelData
                    item: modelData
                    engine: root.engine
                    stateMap: root.stateMap
                }
            }

            Grid {
                rows: 3
                flow: Grid.TopToBottom
                rowSpacing: 2
                columnSpacing: 2
                Repeater {
                    model: root.smallItems
                    delegate: RibbonButton {
                        required property var modelData
                        item: modelData
                        engine: root.engine
                        stateMap: root.stateMap
                    }
                }
            }
        }

        Text {
            id: nameLabel
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.group.name
            color: "#9a9a9a"
            font.pixelSize: 10
        }
    }

    Rectangle {            // right separator
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        width: 1
        height: parent.height * 0.72
        color: "#3a3a3a"
    }
}
