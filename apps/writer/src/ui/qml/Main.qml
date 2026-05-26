// Writer shell — W2 skeleton. Word-like layout placeholders; the real ribbon
// (W3, driven by resources/command-catalog.json) and the LOK tile canvas
// (W2 binding step) replace the placeholders below.
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import WriterApp

ApplicationWindow {
    id: win
    width: 1200
    height: 780
    visible: true
    title: "Document1 — Writer"
    color: "#1f1f1f"

    // Word M365 ribbon tab order.
    readonly property var ribbonTabs: [
        "File", "Home", "Insert", "Draw", "Design", "Layout",
        "References", "Mailings", "Review", "View", "Help"
    ]
    property int currentTab: 1   // Home

    // Home tab groups — real .uno commands from command-catalog.json. (Other
    // tabs come next; Fluent icons replace the text glyphs in the W3 tail.)
    readonly property var homeGroups: [
        { name: "Clipboard", items: [
            { cmd: ".uno:Paste", glyph: "Paste", wide: true },
            { cmd: ".uno:Cut",   glyph: "Cut" },
            { cmd: ".uno:Copy",  glyph: "Copy" } ] },
        { name: "Font", items: [
            { cmd: ".uno:Bold",      glyph: "B", style: "b", toggle: true },
            { cmd: ".uno:Italic",    glyph: "I", style: "i", toggle: true },
            { cmd: ".uno:Underline", glyph: "U", style: "u", toggle: true },
            { cmd: ".uno:Strikeout", glyph: "S", style: "s", toggle: true },
            { cmd: ".uno:Grow",      glyph: "A▲" },
            { cmd: ".uno:Shrink",    glyph: "A▼" } ] },
        { name: "Paragraph", items: [
            { cmd: ".uno:DefaultBullet",    glyph: "• —", toggle: true },
            { cmd: ".uno:DefaultNumbering", glyph: "1. —", toggle: true },
            { cmd: ".uno:LeftPara",    glyph: "▤", toggle: true },
            { cmd: ".uno:CenterPara",  glyph: "▥", toggle: true },
            { cmd: ".uno:RightPara",   glyph: "▦", toggle: true },
            { cmd: ".uno:JustifyPara", glyph: "▧", toggle: true } ] },
        { name: "Editing", items: [
            { cmd: ".uno:SearchDialog", glyph: "Find" },
            { cmd: ".uno:SelectAll",    glyph: "Sel All", wide: true } ] }
    ]

    // .uno: toggle/enabled state streamed from the engine (STATE_CHANGED).
    property var unoState: ({})
    Connections {
        target: lokEngine
        function onUnoStateChanged(payload) {
            var eq = payload.indexOf("=");
            if (eq <= 0) return;
            var s = win.unoState;
            s[payload.substring(0, eq)] = payload.substring(eq + 1);
            win.unoState = s; // reassign to re-evaluate bindings
        }
    }

    header: Rectangle {
        height: 116
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

            // ribbon group strip
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#1f1f1f"

                // Home tab: real command groups
                Row {
                    anchors.fill: parent
                    anchors.leftMargin: 6
                    visible: win.currentTab === 1
                    spacing: 0
                    Repeater {
                        model: win.homeGroups
                        delegate: Item {
                            required property var modelData
                            width: groupCol.implicitWidth + 16
                            height: parent.height
                            // vertical separator
                            Rectangle { anchors.right: parent.right; width: 1; height: parent.height * 0.7
                                anchors.verticalCenter: parent.verticalCenter; color: "#3a3a3a" }
                            Column {
                                id: groupCol
                                anchors.centerIn: parent
                                spacing: 3
                                Flow {
                                    width: Math.min(170, modelData.items.length * 40)
                                    spacing: 2
                                    Repeater {
                                        model: modelData.items
                                        delegate: Rectangle {
                                            required property var modelData
                                            property bool on: win.unoState[modelData.cmd] === "true"
                                            width: modelData.wide ? 48 : 30
                                            height: 30
                                            radius: 3
                                            color: on ? "#2b5797" : (hov.hovered ? "#3a3a3a" : "transparent")
                                            Text {
                                                anchors.centerIn: parent
                                                text: modelData.glyph
                                                color: "#e8e8e8"
                                                font.pixelSize: modelData.wide ? 10 : 13
                                                font.bold: modelData.style === "b"
                                                font.italic: modelData.style === "i"
                                                font.underline: modelData.style === "u"
                                                font.strikeout: modelData.style === "s"
                                            }
                                            HoverHandler { id: hov }
                                            TapHandler { onTapped: lokEngine.postUno(modelData.cmd) }
                                            ToolTip.visible: hov.hovered
                                            ToolTip.text: modelData.cmd
                                        }
                                    }
                                }
                                Text { text: modelData.name; color: "#9a9a9a"; font.pixelSize: 10
                                    anchors.horizontalCenter: parent.horizontalCenter }
                            }
                        }
                    }
                }

                // other tabs: placeholder until wired
                Label {
                    anchors.centerIn: parent
                    visible: win.currentTab !== 1
                    color: "#6f6f6f"
                    font.pixelSize: 11
                    text: "“" + win.ribbonTabs[win.currentTab] + "” — groups wired next (Home is live)"
                }
            }
        }
    }

    // document workspace — scrollable LOK-rendered page(s).
    Rectangle {
        anchors.fill: parent
        color: "#3a3a3a"

        Flickable {
            id: flick
            anchors.fill: parent
            anchors.topMargin: 20
            contentWidth: width
            contentHeight: canvas.height + 40
            clip: true
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            DocumentCanvas {
                id: canvas
                engine: lokEngine
                width: 820
                // full page height at fit-width scale (preserve aspect ratio)
                height: (lokEngine.documentSize.width > 0)
                        ? width * lokEngine.documentSize.height / lokEngine.documentSize.width
                        : 1060
                x: Math.max(0, (flick.width - width) / 2)
            }
        }

        Label {
            anchors.centerIn: parent
            visible: !lokEngine.ready
            color: "#bdbdbd"
            font.pixelSize: 12
            text: "engine not ready — LOK failed to start"
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
