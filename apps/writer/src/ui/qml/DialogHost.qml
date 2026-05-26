// In-app modal host for LOK JSDialogs (W4). Listens to the engine's jsDialog /
// windowEvent streams, maintains the widget-tree model, and renders it as a
// native overlay (our own UI — not an OS window — consistent with Boundary A
// and capturable in headless screenshots). All control interactions go back to
// the engine through send() -> lokEngine.sendDialogEvent.
//
// Event protocol (from vcl/jsdialog/executor.cxx + desktop/.../init.cxx):
//   sendDialogEvent(windowId, {"id":<controlId>,"type":<widget>,"cmd":<action>,"data":<value>})
//   windowId = the dialog tree root's lokWindowId.
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts

Item {
    id: host
    property var engine
    anchors.fill: parent

    property var rootNode: null
    property real windowId: 0
    property string dlgTitle: ""
    visible: rootNode !== null

    readonly property var closeIds: ["ok", "cancel", "close"]

    // ---- engine streams ----------------------------------------------------
    Connections {
        target: host.engine
        function onJsDialog(payload) { host.handle(payload) }
        function onWindowEvent(payload) {
            if (payload.indexOf("\"close\"") >= 0 || payload.indexOf("\"destroy\"") >= 0)
                host.dismiss();
        }
    }

    // ---- outbound seam -----------------------------------------------------
    function send(id, type, cmd, data) {
        if (!engine || windowId === undefined) return;
        engine.sendDialogEvent(windowId, JSON.stringify({ id: id, type: type, cmd: cmd, data: data || "" }));
        // Optimistic close so the UI stays responsive even if the ack is async.
        if (cmd === "click" && host.closeIds.indexOf(("" + id).toLowerCase()) >= 0)
            host.dismiss();
    }
    function dismiss() { rootNode = null; dlgTitle = ""; }

    // ---- inbound payload handling -----------------------------------------
    function handle(payload) {
        var msg;
        try { msg = JSON.parse(payload); } catch (e) { return; }

        // Full widget tree (initial render or full refresh).
        if (msg.children !== undefined && msg.type !== undefined &&
            (msg.type === "dialog" || msg.type === "modelessdialog" ||
             msg.type === "messagedialog")) {
            host.windowId = (msg.lokWindowId !== undefined) ? msg.lokWindowId : parseInt(msg.id);
            host.dlgTitle = msg.text ? ("" + msg.text).replace(/~/g, "") : "";
            host.rootNode = msg;
            return;
        }

        // Incremental messages: {"jsontype":"dialog","action":"update"|"action"|"close",...}
        if (msg.jsontype === "dialog") {
            if (msg.action === "close") { host.dismiss(); return; }
            if (!host.rootNode) return;
            if (msg.action === "update" && msg.control) {
                host.patchNode(msg.control.id, function (n) {
                    for (var k in msg.control) n[k] = msg.control[k];
                });
            } else if (msg.action === "action" && msg.data) {
                var d = msg.data;
                host.patchNode(d.control_id, function (n) {
                    switch (d.action_type) {
                    case "hide": n.visible = false; break;
                    case "show": n.visible = true; break;
                    case "enable": n.enabled = true; break;
                    case "disable": n.enabled = false; break;
                    case "setText": if (d.text !== undefined) n.text = d.text; break;
                    }
                });
            }
        }
    }

    // Find node by id, mutate via fn, then reassign rootNode to re-render.
    function patchNode(id, fn) {
        function walk(n) {
            if (!n || typeof n !== "object") return false;
            if (("" + n.id) === ("" + id)) { fn(n); return true; }
            var ch = n.children || [];
            for (var i = 0; i < ch.length; ++i) if (walk(ch[i])) return true;
            return false;
        }
        if (walk(host.rootNode)) {
            var r = host.rootNode; host.rootNode = null; host.rootNode = r; // force re-render
        }
    }

    // ---- UI -----------------------------------------------------------------
    Rectangle {                       // dimmed backdrop, swallows clicks
        anchors.fill: parent
        color: "#99000000"
        MouseArea { anchors.fill: parent; onClicked: {} }
    }

    Rectangle {                       // dialog panel
        id: panel
        anchors.centerIn: parent
        color: "#262626"
        radius: 8
        border.color: "#454545"; border.width: 1
        width: Math.min(host.width * 0.8, Math.max(360, content.implicitWidth + 32))
        height: Math.min(host.height * 0.85, titleBar.height + content.implicitHeight + 28)

        // title bar
        Rectangle {
            id: titleBar
            anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right
            height: 38; radius: 8
            color: "#2f2f2f"
            Label {
                anchors.verticalCenter: parent.verticalCenter; anchors.left: parent.left; anchors.leftMargin: 14
                text: host.dlgTitle; color: "#f0f0f0"; font.pixelSize: 13; font.bold: true
            }
            Button {
                anchors.verticalCenter: parent.verticalCenter; anchors.right: parent.right; anchors.rightMargin: 8
                width: 24; height: 24
                background: Rectangle { radius: 4; color: parent.hovered ? "#c0392b" : "transparent" }
                contentItem: Label { text: "✕"; color: "#e8e8e8"; horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter }
                onClicked: { host.send("cancel", "responsebutton", "click", ""); host.dismiss(); }
            }
        }

        // body
        Flickable {
            id: bodyFlick
            anchors.top: titleBar.bottom; anchors.left: parent.left; anchors.right: parent.right
            anchors.bottom: parent.bottom; anchors.margins: 14
            contentWidth: width; contentHeight: content.implicitHeight; clip: true
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

            DialogWidget {
                id: content
                width: bodyFlick.width
                node: host.rootNode ? host.rootNode : ({ type: "container", children: [] })
                host: host
            }
        }
    }
}
