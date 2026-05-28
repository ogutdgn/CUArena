// Split colour-picker button — Word's Font Color / Highlight / Page Color UX.
// Clicking the icon applies the last picked colour; clicking ▾ opens a palette
// (theme + standard swatches + "Automatic" / "No Fill" + "More Colours…" that
// hands off to the engine's picker).
//
// item shape in ribbon.json:
//   { cmd, label, icon, size, kind:"colorpicker",
//     argName:"FontColor.Color",       // SfxItem arg name
//     swatchColor:"#c0392b",           // initial swatch colour (visual)
//     autoLabel:"Automatic" | "No Fill",
//     defaultColor:-1 }                // applied as "Automatic" by default
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Item {
    id: root
    required property var item
    property var engine
    property var stateMap: ({})

    // Track the most-recent picked colour (hex like "#ff0000"; "" = automatic).
    property string lastColor: item.swatchColor || ""

    implicitWidth: 44     // a touch wider so the ▾ click zone is comfortable
    implicitHeight: 28

    // Convert "#rrggbb" -> long int 0xRRGGBB; "" -> defaultColor (default -1).
    function colorInt(hex) {
        if (!hex || hex === "")
            return (root.item.defaultColor !== undefined) ? root.item.defaultColor : -1;
        var s = hex.replace("#", "");
        return parseInt(s, 16);
    }
    function dispatchColor(hex) {
        var v = root.colorInt(hex);
        var args = {};
        args[root.item.argName] = { type: "long", value: v };
        root.engine.postUno(root.item.cmd, JSON.stringify(args));
    }

    Rectangle {
        anchors.fill: parent
        radius: 4
        color: hov.hovered || palette.opened ? "#3a3a3a" : "transparent"

        // Left half: icon + swatch (primary action — apply last colour).
        Rectangle {
            id: primary
            anchors.left: parent.left; anchors.top: parent.top; anchors.bottom: parent.bottom
            width: parent.width - 16
            color: "transparent"
            Column {
                anchors.centerIn: parent
                spacing: 1
                Image {
                    anchors.horizontalCenter: parent.horizontalCenter
                    source: "qrc:/resources/icons/" + root.item.icon + ".svg"
                    sourceSize.width: 16; sourceSize.height: 16
                }
                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: 16; height: 3; radius: 1
                    color: root.lastColor !== "" ? root.lastColor : "#888"
                }
            }
            HoverHandler { id: primHov }
            TapHandler { onTapped: root.dispatchColor(root.lastColor) }
        }
        Rectangle {                            // right ▾ click-zone
            id: arrowArea
            anchors.right: parent.right; anchors.top: parent.top; anchors.bottom: parent.bottom
            width: 16
            color: arrowHov.hovered ? "#2f2f2f" : "transparent"
            Label {
                anchors.centerIn: parent
                text: "▾"; color: "#bdbdbd"; font.pixelSize: 9
            }
            HoverHandler { id: arrowHov }
            TapHandler { onTapped: palette.open() }
        }

        HoverHandler { id: hov }
        ToolTip.visible: hov.hovered && !palette.opened
        ToolTip.delay: 400
        ToolTip.text: root.item.label + "   (" + root.item.cmd + ")"
    }

    // 8×5 Word-style palette + Automatic / No-Fill row.
    readonly property var swatches: [
        "#000000","#7f7f7f","#a5a5a5","#ffffff","#c00000","#ff0000","#ffc000","#ffff00",
        "#92d050","#00b050","#00b0f0","#0070c0","#002060","#7030a0","#264653","#2a9d8f",
        "#e76f51","#e9c46a","#264653","#ff66cc","#660066","#cc3333","#996633","#666633",
        "#003366","#6699cc","#669966","#cccc66","#cc9999","#cc6666","#666666","#cccccc",
        "#1e3a5f","#3a5f8a","#5f8abf","#bdd7ee","#deebf7","#fff2cc","#fce4d6","#e2efda"
    ]

    Popup {
        id: palette
        x: 0; y: root.height
        padding: 8
        modal: false
        background: Rectangle { color: "#262626"; border.color: "#454545"; border.width: 1; radius: 4 }
        contentItem: ColumnLayout {
            spacing: 8
            Label {
                text: root.item.autoLabel || "Automatic"
                color: "#e8e8e8"; font.pixelSize: 11
                Layout.fillWidth: true
                MouseArea { anchors.fill: parent; onClicked: {
                    root.lastColor = ""; root.dispatchColor(""); palette.close(); } }
            }
            Grid {
                columns: 8; spacing: 3
                Repeater {
                    model: root.swatches
                    delegate: Rectangle {
                        required property string modelData
                        width: 22; height: 22; radius: 2
                        color: modelData
                        border.color: hovSw.hovered ? "#e8e8e8" : "#454545"
                        border.width: hovSw.hovered ? 2 : 1
                        HoverHandler { id: hovSw }
                        TapHandler { onTapped: {
                            root.lastColor = modelData; root.dispatchColor(modelData); palette.close(); } }
                    }
                }
            }
            Label {
                text: "More Colours…"
                color: "#bdbdbd"; font.pixelSize: 11
                Layout.fillWidth: true
                MouseArea { anchors.fill: parent; onClicked: {
                    // Open the engine's full picker (it's a JSDialog in our DialogHost).
                    root.engine.postUno(root.item.cmd, "");
                    palette.close();
                } }
            }
        }
    }
}
