// W4 coverage audit: classify each dialog-target .uno command by how its dialog
// surfaces — JSDIALOG (full JSON widget tree, renderable natively) vs WINDOW
// (tiled/native window only => not in vcl/jsdialog/enabled.cxx => D6 patch
// candidate) vs NONE (no dialog / direct action). Feeds docs/architecture/
// W4_DIALOG_COVERAGE.md.
//
// Build: g++ -std=c++17 -DLOK_USE_UNSTABLE_API -I <engine>/include \
//        tests/dialog_audit.cpp -ldl -o /tmp/dialog_audit
// Run:   /tmp/dialog_audit <ABS instdir/program> <cmd-list-file>
#define LOK_USE_UNSTABLE_API
#include <LibreOfficeKit/LibreOfficeKit.hxx>
#include <LibreOfficeKit/LibreOfficeKitInit.h>
#include <LibreOfficeKit/LibreOfficeKitEnums.h>
#include <cstdio>
#include <dlfcn.h>
#include <fstream>
#include <unistd.h>
#include <string>
#include <vector>

using namespace lok;

static void (*g_pump)() = nullptr;
static bool g_jsTree = false, g_jsAny = false, g_winDialog = false;

static void cb(int type, const char* payload, void*)
{
    std::string p = payload ? payload : "";
    if (type == LOK_CALLBACK_JSDIALOG) {
        g_jsAny = true;
        if (p.find("\"children\"") != std::string::npos && p.find("\"type\": \"dialog\"") != std::string::npos)
            g_jsTree = true;
        if (p.find("\"type\": \"modelessdialog\"") != std::string::npos) g_jsTree = true;
    } else if (type == LOK_CALLBACK_WINDOW) {
        if (p.find("\"action\":\"created\"") != std::string::npos &&
            p.find("\"type\":\"dialog\"") != std::string::npos)
            g_winDialog = true;
    }
}
static void pump() { if (g_pump) g_pump(); }

int main(int argc, char** argv)
{
    setvbuf(stdout, nullptr, _IONBF, 0);
    if (argc < 3) { fprintf(stderr, "usage: %s <instdir/program> <cmd-list>\n", argv[0]); return 64; }
    Office* office = lok_cpp_init(argv[1], "file:///tmp/lok-audit-profile");
    if (!office) { fprintf(stderr, "FAIL init\n"); return 1; }
    g_pump = reinterpret_cast<void (*)()>(dlsym(RTLD_DEFAULT, "unit_lok_process_events_to_idle"));
    Document* doc = office->documentLoad("private:factory/swriter");
    if (!doc) { fprintf(stderr, "FAIL load\n"); return 2; }
    doc->initializeForRendering();
    doc->registerCallback(cb, nullptr);
    pump();
    doc->postUnoCommand(".uno:InsertText", "{\"Text\":{\"type\":\"string\",\"value\":\"audit text\"}}", false);
    pump();

    // One command per process invocation: a modal WINDOW-only dialog (e.g.
    // InsertTable) doesn't respond to .uno:Cancel and blocks every subsequent
    // command, so isolating each in a fresh process is the only reliable audit.
    std::string arg2 = argv[2];
    std::vector<std::string> cmds;
    if (arg2.rfind(".uno:", 0) == 0) {
        cmds.push_back(arg2);
    } else {
        std::ifstream f(argv[2]); std::string line;
        while (std::getline(f, line)) if (!line.empty()) cmds.push_back(line);
    }
    for (const auto& c : cmds) {
        g_jsTree = g_jsAny = g_winDialog = false;
        doc->postUnoCommand(c.c_str(), nullptr, true);
        pump();
        const char* verdict = g_jsTree ? "JSDIALOG"
                            : g_winDialog ? "WINDOW-only"
                            : g_jsAny ? "JSDIALOG-partial"
                            : "NONE";
        printf("%-30s %s\n", c.c_str(), verdict);
    }
    printf("AUDIT_DONE\n");
    fflush(stdout);
    _exit(0); // skip LO dev-build teardown abort
}
