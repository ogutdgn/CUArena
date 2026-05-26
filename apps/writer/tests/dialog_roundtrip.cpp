// W4 round-trip proof: open a modal JSDialog (Page Style), capture its window
// id from the widget-tree root, then close it via sendDialogEvent and confirm
// the engine acknowledges with a JSDIALOG `action:"close"`. This is the exact
// path DialogHost.qml uses. Proves JSDIALOG -> native UI -> sendDialogEvent.
//
// Confirmed protocol (see docs/architecture/W4_DIALOG_COVERAGE.md):
//   windowId = the dialog tree root's "lokWindowId".
//   event    = {"id":"<controlId>","type":"<widget>","cmd":"<action>","data":"<v>"}
//   a dialog action button (ok/cancel/close/apply) => type "responsebutton",
//   cmd "click"; the engine replies {"jsontype":"dialog","action":"close","id":N}.
//
// Build: g++ -std=c++17 -DLOK_USE_UNSTABLE_API -I <ABS engine>/include \
//        tests/dialog_roundtrip.cpp -ldl -o /tmp/dialog_roundtrip
// Run (ABSOLUTE instdir/program path):  /tmp/dialog_roundtrip <instdir/program>
#define LOK_USE_UNSTABLE_API
#include <LibreOfficeKit/LibreOfficeKit.hxx>
#include <LibreOfficeKit/LibreOfficeKitInit.h>
#include <LibreOfficeKit/LibreOfficeKitEnums.h>
#include <cstdio>
#include <cstdlib>
#include <dlfcn.h>
#include <string>
#include <unistd.h>

using namespace lok;

static void (*g_pump)() = nullptr;
static long long g_windowId = -1;
static bool g_closed = false;

static long long lokWindowId(const std::string& p)
{
    auto k = p.find("\"lokWindowId\":");
    return (k == std::string::npos) ? -1 : atoll(p.c_str() + k + 14);
}

static void cb(int type, const char* payload, void*)
{
    std::string p = payload ? payload : "";
    if (type != LOK_CALLBACK_JSDIALOG)
        return;
    // initial full tree of the modal dialog: {"id":"...","type":"dialog","children":[...]}
    if (g_windowId < 0 && p.find("\"type\": \"dialog\"") != std::string::npos &&
        p.find("\"children\"") != std::string::npos) {
        g_windowId = lokWindowId(p);
        printf("  [tree] dialog windowId=%lld\n", g_windowId);
    }
    if (p.find("\"action\": \"close\"") != std::string::npos) {
        g_closed = true;
        printf("  [ack] %s\n", p.substr(0, 120).c_str());
    }
}
static void pump() { if (g_pump) g_pump(); }

int main(int argc, char** argv)
{
    setvbuf(stdout, nullptr, _IONBF, 0);
    if (argc < 2) { fprintf(stderr, "usage: %s <instdir/program>\n", argv[0]); return 64; }
    Office* office = lok_cpp_init(argv[1], "file:///tmp/lok-rt-profile");
    if (!office) { fprintf(stderr, "FAIL init (use an ABSOLUTE path)\n"); return 1; }
    g_pump = reinterpret_cast<void (*)()>(dlsym(RTLD_DEFAULT, "unit_lok_process_events_to_idle"));
    Document* doc = office->documentLoad("private:factory/swriter");
    if (!doc) { fprintf(stderr, "FAIL load\n"); return 2; }
    doc->initializeForRendering();
    doc->registerCallback(cb, nullptr);
    pump();

    printf("== open .uno:PageDialog ==\n");
    doc->postUnoCommand(".uno:PageDialog", nullptr, true);
    pump();
    if (g_windowId < 0) { fprintf(stderr, "FAIL: no window id\n"); return 3; }

    printf("== sendDialogEvent: cancel (responsebutton click) on windowId=%lld ==\n", g_windowId);
    doc->sendDialogEvent(static_cast<unsigned long long>(g_windowId),
                         "{\"id\":\"cancel\",\"type\":\"responsebutton\",\"cmd\":\"click\"}");
    pump();

    printf("%s\n", g_closed ? "ROUNDTRIP_OK: engine acknowledged close" : "ROUNDTRIP_FAIL");
    printf("DONE\n");
    fflush(stdout);
    _exit(g_closed ? 0 : 5); // skip LO dev-build teardown abort (ENGINE_BUILD.md §6)
}
