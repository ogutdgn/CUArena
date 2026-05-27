// A single ribbon command button, data-driven from a ribbon.json item.
// Large = icon over label (Word's primary buttons); small = icon-only (the
// 3-row stacks). Toggle items light up from STATE_CHANGED; the icon stays one
// constant tint and the background conveys hover/active/disabled (Word-style).
import QtQuick
import QtQuick.Controls.Basic

Item {
    id: root

    required property var item          // { cmd, label, icon, size, toggle?, args? }
    property var engine                 // lokEngine
    property var stateMap: ({})         // win.unoState (.uno:Cmd -> "true"/"false"/"disabled")

    readonly property bool isLarge: item.size === "lg"
    readonly property string st: (stateMap[item.cmd] === undefined) ? "" : ("" + stateMap[item.cmd])
    readonly property bool on: (item.toggle === true) && st === "true"
    readonly property bool disabled: st === "disabled"

    implicitWidth: isLarge ? 58 : 30
    implicitHeight: isLarge ? 68 : 28

    Rectangle {
        anchors.fill: parent
        radius: 4
        color: root.on ? "#3d5a8a"
                       : (hov.hovered && !root.disabled ? "#3a3a3a" : "transparent")
        border.width: root.on ? 1 : 0
        border.color: "#5a7cb8"

        // large: icon on top, label under it
        Column {
            visible: root.isLarge
            anchors.centerIn: parent
            spacing: 3
            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                source: "qrc:/resources/icons/" + root.item.icon + ".svg"
                sourceSize.width: 20; sourceSize.height: 20
                opacity: root.disabled ? 0.35 : 1.0
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                width: 56
                text: root.item.label
                color: root.disabled ? "#6f6f6f" : "#e8e8e8"
                font.pixelSize: 10
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }
        }

        // small: icon only (+ a colour swatch for the Font Color / Highlight buttons)
        Column {
            visible: !root.isLarge
            anchors.centerIn: parent
            spacing: 1
            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                source: "qrc:/resources/icons/" + root.item.icon + ".svg"
                sourceSize.width: 16; sourceSize.height: 16
                opacity: root.disabled ? 0.35 : 1.0
            }
            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                visible: root.item.kind === "fontcolor" || root.item.kind === "highlight"
                width: 16; height: 3; radius: 1
                color: root.item.kind === "highlight" ? "#ffd400" : "#c0392b"
            }
        }
    }

    HoverHandler { id: hov; enabled: !root.disabled }
    TapHandler {
        enabled: !root.disabled
        onTapped: root.engine.postUno(root.item.cmd, root.item.args !== undefined ? root.item.args : "")
    }

    ToolTip.visible: hov.hovered
    ToolTip.delay: 400
    ToolTip.text: root.item.label + "   (" + root.item.cmd + ")"
}
