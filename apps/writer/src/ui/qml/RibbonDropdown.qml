// Generic ribbon dropdown — a small icon button with a ▾ arrow that opens a
// popup menu of options. Each option dispatches its own .uno: (optionally with
// args). Used for LineSpacing, PageMargin, Orientation, AttributePageSize,
// Zoom, ChangeCase, PageColumnType, TextWrap, Bullets/Numbering, …
//
// item shape in ribbon.json:
//   { cmd, label, icon, size, kind:"dropdown",
//     options:[ { label, cmd, args?, icon?, divider?, checkKey? } ] }
//
// `checkKey` (optional) names a STATE_CHANGED key whose "true" lights up that
// option (e.g. SpacePara15 for "1.5") so the menu shows the active value.
import QtQuick
import QtQuick.Controls.Basic

Item {
    id: root
    required property var item
    property var engine
    property var stateMap: ({})

    readonly property bool isLarge: item.size === "lg"
    implicitWidth: isLarge ? Math.max(96, contentRow.implicitWidth + 14) : 40
    implicitHeight: isLarge ? 68 : 28

    Rectangle {
        anchors.fill: parent
        radius: 4
        color: hov.hovered || menu.opened ? "#3a3a3a" : "transparent"

        Row {
            id: contentRow
            anchors.centerIn: parent
            spacing: 3
            Image {
                anchors.verticalCenter: parent.verticalCenter
                source: "qrc:/resources/icons/" + root.item.icon + ".svg"
                sourceSize.width: root.isLarge ? 20 : 16
                sourceSize.height: root.isLarge ? 20 : 16
            }
            Label {
                visible: root.isLarge
                anchors.verticalCenter: parent.verticalCenter
                text: root.item.label; color: "#e8e8e8"; font.pixelSize: 10
            }
            Label {
                anchors.verticalCenter: parent.verticalCenter
                text: "▾"; color: "#bdbdbd"; font.pixelSize: 10
            }
        }

        HoverHandler { id: hov }
        TapHandler { onTapped: menu.popup(0, root.height) }

        ToolTip.visible: hov.hovered && !menu.opened
        ToolTip.delay: 400
        ToolTip.text: root.item.label + "   (" + root.item.cmd + ")"
    }

    Menu {
        id: menu
        background: Rectangle { color: "#262626"; border.color: "#454545"; border.width: 1; radius: 4 }
        Repeater {
            model: root.item.options || []
            delegate: MenuItem {
                id: mi
                required property var modelData
                readonly property bool isDivider: modelData && modelData.divider === true
                readonly property bool isActive: {
                    var ck = modelData ? modelData.checkKey : null;
                    return !!ck && root.stateMap[ck] === "true";
                }
                text: modelData ? (modelData.label || "") : ""
                height: isDivider ? 1 : 26
                enabled: !isDivider
                contentItem: Item {
                    Rectangle { visible: mi.isDivider; anchors.fill: parent; color: "#3a3a3a" }
                    Row {
                        visible: !mi.isDivider
                        anchors.fill: parent
                        anchors.leftMargin: 8; anchors.rightMargin: 12
                        spacing: 6
                        Label { width: 12
                            anchors.verticalCenter: parent.verticalCenter
                            text: mi.isActive ? "✓" : ""
                            color: "#4a6fb5"; font.pixelSize: 12
                        }
                        Label {
                            anchors.verticalCenter: parent.verticalCenter
                            text: mi.text; color: "#e8e8e8"; font.pixelSize: 12
                        }
                    }
                }
                background: Rectangle {
                    color: mi.highlighted && !mi.isDivider ? "#3d5a8a" : "transparent"
                }
                onTriggered: {
                    if (!isDivider && modelData && modelData.cmd) {
                        root.engine.postUno(modelData.cmd, modelData.args || "");
                    }
                }
            }
        }
    }
}
