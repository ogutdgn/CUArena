// Writer shell — Word-like window: data-driven ribbon (W3) over the LOK tile
// canvas (W2). The ribbon is built from ribbonData (resources/ribbon.json,
// exposed by main.cpp); commands dispatch through lokEngine.postUno and toggle
// state streams back via STATE_CHANGED -> unoStateChanged.
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import WriterApp

ApplicationWindow {
    id: win
    width: 1200
    height: 800
    visible: true
    title: "Document1 — Writer"
    color: "#1f1f1f"

    // .uno: toggle/enabled state streamed from the engine (STATE_CHANGED),
    // e.g. ".uno:Bold=true". Reassigned (not mutated) so QML bindings re-eval.
    property var unoState: ({})
    Connections {
        target: lokEngine
        function onUnoStateChanged(payload) {
            var eq = payload.indexOf("=");
            if (eq <= 0) return;
            var s = win.unoState;
            s[payload.substring(0, eq)] = payload.substring(eq + 1);
            win.unoState = s;
        }
    }

    header: Ribbon {
        ribbonModel: ribbonData
        engine: lokEngine
        stateMap: win.unoState
        currentTab: typeof initialTab !== "undefined" ? initialTab : 0
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
