// W4 research probe: capture real LOK_CALLBACK_JSDIALOG (46) payloads so we can
// design the native JSON->QML dialog renderer against the actual widget-tree
// schema (ARCHITECTURE §5, DECISIONS D6). Triggers a set of Writer dialog
// commands one at a time, pumps the scheduler, and dumps any JSDIALOG / WINDOW
// callbacks. Tells us which dialogs already flow through jsdialog/enabled.cxx
// and which are silent (need an enabled.cxx patch).
//
// Build: g++ -std=c++17 -DLOK_USE_UNSTABLE_API -I <engine>/include \
//        tests/dialog_probe.cpp -ldl -o /tmp/dialog_probe
// Run:   /tmp/dialog_probe <engine>/instdir/program
#define LOK_USE_UNSTABLE_API
#include <LibreOfficeKit/LibreOfficeKit.hxx>
#include <LibreOfficeKit/LibreOfficeKitInit.h>
#include <LibreOfficeKit/LibreOfficeKitEnums.h>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <string>
#include <vector>

using namespace lok;

static void (*g_pump)() = nullptr;
static const char* g_label = "";

static void cb(int type, const char* payload, void*)
{
    // Only the dialog-relevant callbacks; ignore the render/cursor noise.
    if (type == LOK_CALLBACK_JSDIALOG || type == LOK_CALLBACK_WINDOW) {
        const char* name = (type == LOK_CALLBACK_JSDIALOG) ? "JSDIALOG" : "WINDOW";
        std::string p = payload ? payload : "";
        printf("\n[%s] %s (%zu bytes):\n%s\n", g_label, name, p.size(),
               p.size() > 1200 ? (p.substr(0, 1200) + " …(truncated)").c_str() : p.c_str());
        // Dump full widget trees untruncated to a per-command file so we can
        // design the renderer against the real schema.
        if (type == LOK_CALLBACK_JSDIALOG &&
            p.find("\"children\"") != std::string::npos && p.size() > 1500) {
            std::string cmd = g_label;
            std::string base = cmd.substr(cmd.find(':') + 1);
            std::string path = "/tmp/jsdlg_" + base + ".json";
            if (FILE* f = fopen(path.c_str(), "w")) { fwrite(p.data(), 1, p.size(), f); fclose(f); }
        }
    }
}

static void pump() { if (g_pump) g_pump(); }

int main(int argc, char** argv)
{
    setvbuf(stdout, nullptr, _IONBF, 0);
    if (argc < 2) { fprintf(stderr, "usage: %s <instdir/program>\n", argv[0]); return 64; }

    Office* office = lok_cpp_init(argv[1], "file:///tmp/lok-dlgprobe-profile");
    if (!office) { fprintf(stderr, "FAIL: lok_cpp_init\n"); return 1; }
    g_pump = reinterpret_cast<void (*)()>(dlsym(RTLD_DEFAULT, "unit_lok_process_events_to_idle"));
    printf("ok: lok init (pump=%s)\n", g_pump ? "yes" : "NO");

    Document* doc = office->documentLoad("private:factory/swriter");
    if (!doc) { fprintf(stderr, "FAIL: documentLoad\n"); return 2; }
    doc->initializeForRendering();
    doc->registerCallback(cb, nullptr);
    pump();

    // Type a little text so dialogs that need a selection/content have it.
    doc->postUnoCommand(".uno:InsertText",
        "{\"Text\":{\"type\":\"string\",\"value\":\"probe text\"}}", false);
    pump();

    const char* dialogs[] = {
        ".uno:InsertTable", ".uno:PageDialog", ".uno:FontDialog",
        ".uno:SearchDialog", ".uno:ParagraphDialog", ".uno:InsertSymbol",
        ".uno:HyperlinkDialog", ".uno:WordCountDialog", ".uno:InsertField",
    };
    for (const char* d : dialogs) {
        g_label = d;
        printf("\n==== post %s ====", d);
        doc->postUnoCommand(d, nullptr, true);   // notify=true
        pump();
        // close anything that opened so the next probe is clean
        doc->postUnoCommand(".uno:Cancel", nullptr, false);
        pump();
    }
    printf("\nPROBE_DONE\n");
    return 0;
}
