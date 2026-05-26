// Recursive renderer for one node of a LOK JSDialog widget tree (W4). Maps the
// engine's widget vocabulary to native QML controls and recurses into children.
// User interactions are funnelled through host.send(id, type, cmd, data) — the
// single seam that talks back to the engine via sendDialogEvent.
//
// Recursion note: QML forbids a component instantiating itself by type name, so
// child nodes are loaded via Loader-by-URL (resolved at runtime) — the standard
// recursive-QML idiom. childComp is that reusable child loader.
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Loader {
    id: root
    property var node: null
    property var host: null

    readonly property string t: (node && node.type) ? node.type : ""
    readonly property string nid: (node && node.id !== undefined) ? ("" + node.id) : ""
    readonly property bool enabled_: !(node && node.enabled === false)
    visible: !(node && node.visible === false)
    active: visible && node !== null

    sourceComponent: {
        switch (t) {
        case "dialog": case "modelessdialog": case "messagedialog":
        case "container": case "borderwindow": case "scrolledwindow":
        case "frame":                       return containerComp
        case "grid":                        return gridComp
        case "buttonbox":                   return buttonBoxComp
        case "fixedtext": case "label":     return labelComp
        case "edit":                        return editComp
        case "checkbox":                    return checkComp
        case "radiobutton":                 return radioComp
        case "listbox": case "combobox":    return comboComp
        case "spinfield": case "formattedfield": case "metricfield":
        case "spinbutton":                  return spinComp
        case "pushbutton": case "okbutton": case "cancelbutton":
        case "helpbutton": case "responsebutton": case "linkbutton":
                                            return buttonComp
        case "tabcontrol":                  return tabComp
        default:                            return (node && node.children) ? containerComp : unknownComp
        }
    }

    // ---- helpers -----------------------------------------------------------
    function kids() { return (node && node.children) ? node.children : [] }
    function clean(s) { return s ? ("" + s).replace(/~/g, "") : "" }

    // Reusable recursive child loader (breaks the static self-reference cycle).
    Component {
        id: childComp
        Loader {
            required property var modelData
            Layout.fillWidth: true
            source: "qrc:/src/ui/qml/DialogWidget.qml"
            onLoaded: { item.node = modelData; item.host = root.host }
        }
    }

    // ---- components --------------------------------------------------------
    Component {
        id: containerComp
        ColumnLayout {
            spacing: 6
            Repeater { model: root.kids(); delegate: childComp }
        }
    }

    Component {
        id: gridComp
        GridLayout {
            columnSpacing: 18
            rowSpacing: 5
            Repeater {
                model: root.kids()
                delegate: Loader {
                    required property var modelData
                    source: "qrc:/src/ui/qml/DialogWidget.qml"
                    Layout.row: modelData.top !== undefined ? modelData.top : 0
                    Layout.column: modelData.left !== undefined ? modelData.left : 0
                    Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                    onLoaded: { item.node = modelData; item.host = root.host }
                }
            }
        }
    }

    Component {
        id: buttonBoxComp
        RowLayout {
            spacing: 8
            Item { Layout.fillWidth: true }   // push buttons right (Word/LO order)
            Repeater { model: root.kids(); delegate: childComp }
        }
    }

    Component {
        id: labelComp
        Label {
            text: root.clean(root.node.text)
            color: root.enabled_ ? "#e8e8e8" : "#7a7a7a"
            font.pixelSize: 12
        }
    }

    Component {
        id: editComp
        TextField {
            text: root.node.text ? root.node.text : ""
            enabled: root.enabled_
            color: "#f0f0f0"
            selectByMouse: true
            background: Rectangle { radius: 3; color: "#2b2b2b"; border.color: "#555"; border.width: 1 }
            onEditingFinished: root.host.send(root.nid, "edit", "change", text)
        }
    }

    Component {
        id: checkComp
        CheckBox {
            text: root.clean(root.node.text)
            checked: root.node.checked === true
            enabled: root.enabled_
            contentItem: Label { text: parent.text; color: "#e8e8e8"; font.pixelSize: 12
                leftPadding: parent.indicator.width + 6; verticalAlignment: Text.AlignVCenter }
            onToggled: root.host.send(root.nid, "checkbox", "change", checked ? "true" : "false")
        }
    }

    Component {
        id: radioComp
        RadioButton {
            text: root.clean(root.node.text)
            checked: root.node.checked === true
            enabled: root.enabled_
            contentItem: Label { text: parent.text; color: "#e8e8e8"; font.pixelSize: 12
                leftPadding: parent.indicator.width + 6; verticalAlignment: Text.AlignVCenter }
            onToggled: if (checked) root.host.send(root.nid, "radiobutton", "change", "true")
        }
    }

    Component {
        id: comboComp
        ComboBox {
            model: root.node.entries ? root.node.entries : []
            enabled: root.enabled_
            currentIndex: (root.node.selectedEntries && root.node.selectedEntries.length > 0)
                          ? parseInt(root.node.selectedEntries[0]) : -1
            onActivated: root.host.send(root.nid, "combobox", "selected", index + ";" + textAt(index))
        }
    }

    Component {
        id: spinComp
        // QML SpinBox is integer-only; formatted/metric fields carry 2-decimal
        // values (e.g. 0.79″) so we scale them by 100, while plain spinbuttons
        // (table rows/cols) are integers (scale 1).
        SpinBox {
            id: sb
            // Decide integer vs 2-decimal from the step (counts use step 1;
            // measurements like margins use step 0.02), not the widget type —
            // table rows/cols are formattedfields but integer-valued.
            readonly property int factor: (root.node.step !== undefined &&
                                            !Number.isInteger(root.node.step)) ? 100 : 1
            from: root.node.min !== undefined ? Math.round(root.node.min * factor) : 0
            to: root.node.max !== undefined ? Math.round(root.node.max * factor) : 1000000
            value: root.node.value !== undefined ? Math.round(root.node.value * factor) : 0
            stepSize: root.node.step !== undefined ? Math.max(1, Math.round(root.node.step * factor)) : 1
            enabled: root.enabled_
            editable: true
            textFromValue: function (v) { return factor === 1 ? ("" + v) : (v / factor).toFixed(2); }
            valueFromText: function (txt) { return Math.round(parseFloat(txt) * factor); }
            onValueModified: root.host.send(root.nid, "spinfield", "value",
                                            factor === 1 ? ("" + value) : (value / factor).toFixed(2))
        }
    }

    Component {
        id: buttonComp
        Button {
            text: root.clean(root.node.text) || root.nid
            enabled: root.enabled_
            implicitHeight: 30
            contentItem: Label { text: parent.text; color: "#f0f0f0"; font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            background: Rectangle { radius: 4; color: parent.down ? "#3d5a8a" : (parent.hovered ? "#3a3a3a" : "#2f2f2f")
                border.color: "#555"; border.width: 1 }
            // dialog action buttons resolve as "responsebutton"; host maps id->response
            onClicked: root.host.send(root.nid, "responsebutton", "click", "")
        }
    }

    Component {
        id: tabComp
        ColumnLayout {
            id: tabCol
            spacing: 0
            // `tabs` carries the labels ({text,id}); `children` are the page bodies.
            property var tabs: (root.node && root.node.tabs) ? root.node.tabs : []
            property var pages: root.kids()
            function initialSel() {
                var s = root.node ? root.node.selected : "";
                for (var i = 0; i < tabs.length; ++i) if (("" + tabs[i].id) === ("" + s)) return i;
                return 0;
            }
            property int sel: initialSel()
            TabBar {
                id: bar
                Layout.fillWidth: true
                currentIndex: tabCol.sel
                Repeater {
                    model: tabCol.tabs
                    delegate: TabButton {
                        required property var modelData
                        required property int index
                        text: root.clean(modelData.text || modelData.id)
                        width: Math.max(72, implicitWidth)
                        onClicked: { tabCol.sel = index;
                            root.host.send(root.nid, "tabcontrol", "selecttab", "" + index) }
                    }
                }
            }
            StackLayout {
                Layout.fillWidth: true
                currentIndex: tabCol.sel
                Repeater { model: tabCol.pages; delegate: childComp }
            }
        }
    }

    Component {
        id: unknownComp
        Label { text: "[" + root.t + " " + root.nid + "]"; color: "#7a7a7a"; font.pixelSize: 10 }
    }
}
