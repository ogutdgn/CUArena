// Editable ribbon combo for the Font group's name/size pickers (W3 composite
// controls). Reflects the current cursor format from STATE_CHANGED
// (.uno:CharFontName / .uno:FontHeight) and dispatches the change back.
import QtQuick
import QtQuick.Controls.Basic

ComboBox {
    id: combo
    required property var item          // { cmd, kind: "fontname"|"fontsize" }
    property var engine
    property var stateMap: ({})

    readonly property bool isName: item.kind === "fontname"
    editable: true
    implicitWidth: isName ? 150 : 64
    implicitHeight: 26

    model: isName
        ? ["Liberation Serif", "Liberation Sans", "Liberation Mono", "Arial", "Calibri",
           "Times New Roman", "Courier New", "Georgia", "Verdana", "Tahoma", "Cambria"]
        : ["8", "9", "10", "10.5", "11", "12", "14", "16", "18", "20", "24", "28", "36", "48", "72"]

    // Reflect the engine's current value (STATE_CHANGED) without firing a dispatch.
    property string cur: {
        var v = stateMap[item.cmd];
        if (v === undefined) return "";
        v = "" + v;
        return combo.isName ? v : v.replace(/\.0+$/, ""); // "12.000" -> "12"
    }
    onCurChanged: if (cur !== "" && cur !== editText) editText = cur

    function apply(value) {
        if (!value) return;
        if (isName)
            engine.postUno(item.cmd, JSON.stringify(
                { "CharFontName.FamilyName": { type: "string", value: "" + value } }));
        else
            engine.postUno(item.cmd, JSON.stringify(
                { "FontHeight.Height": { type: "float", value: parseFloat(value) } }));
    }
    onActivated: apply(currentText)
    onAccepted: apply(editText)

    contentItem: TextField {
        text: combo.editText
        onTextChanged: combo.editText = text
        color: "#f0f0f0"
        font.pixelSize: 12
        verticalAlignment: Text.AlignVCenter
        leftPadding: 6
        background: null
        onAccepted: combo.apply(text)
    }
    background: Rectangle { radius: 3; color: "#2b2b2b"; border.color: "#555"; border.width: 1 }

    delegate: ItemDelegate {
        width: combo.width
        required property var modelData
        contentItem: Text { text: modelData; color: "#e8e8e8"; font.pixelSize: 12
            verticalAlignment: Text.AlignVCenter }
        background: Rectangle { color: parent.hovered ? "#3a3a3a" : "#262626" }
    }
    popup.background: Rectangle { color: "#262626"; border.color: "#555" }
}
