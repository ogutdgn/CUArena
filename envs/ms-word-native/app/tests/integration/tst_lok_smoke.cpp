// Type-B test: headless LOK integration through our binding — load -> dispatch -> save ->
// reload, asserting REAL document content survives (never "did not crash", never on a blank doc).
//
// Plain C++ (no Qt): a QCoreApplication fights LibreOffice's own VCL application singleton, so
// this drives the binding directly on the main thread, exactly as a LOK client/converter does.
// Returns 0 on success; std::_Exit bypasses LO's fragile at-exit shutdown. CMake injects
// MW_LOK_INSTDIR and MW_FIXTURE_FODT.

#include <cstdio>
#include <cstdlib>
#include <string>

#include "engine/LokEngine.h"

namespace {
int g_fail = 0;
std::string fileUrl(const char* p) { return std::string("file://") + p; }
const char* kExpected = "quick brown fox";

void check(bool cond, const char* what) {
    std::fprintf(stderr, "%s: %s\n", cond ? "ok " : "FAIL", what);
    if (!cond) ++g_fail;
}
}  // namespace

int main() {
    mw::LokEngine eng;
    check(eng.init(MW_LOK_INSTDIR, "file:///tmp/mw-lok-profile"), "LOK init");
    if (g_fail) { std::fflush(stderr); std::_Exit(2); }  // can't test anything without the engine

    // Load a real-content fixture; SelectAll must surface the actual body text (proves the
    // load + dispatch path against the real engine, not a blank document).
    check(eng.loadDocument(fileUrl(MW_FIXTURE_FODT)), "load fixture .fodt");
    eng.dispatch(".uno:SelectAll");
    const std::string sel = eng.selectedText();
    std::fprintf(stderr, "  selection: '%s'\n", sel.c_str());
    check(sel.find(kExpected) != std::string::npos, "SelectAll surfaces real content");

    // Round-trip: save the doc as .docx through the real engine, reload it, confirm content
    // survived (exercises the .docx export + import filters).
    check(eng.loadDocument(fileUrl(MW_FIXTURE_FODT)), "reload fixture");
    std::remove("/tmp/mw-lok-out.docx");
    check(eng.saveAs(fileUrl("/tmp/mw-lok-out.docx"), "docx"), "saveAs .docx");
    check(eng.loadDocument(fileUrl("/tmp/mw-lok-out.docx")), "load saved .docx");
    eng.dispatch(".uno:SelectAll");
    check(eng.selectedText().find(kExpected) != std::string::npos,
          "content round-trips through .docx");

    std::fprintf(stderr, "%s\n", g_fail ? "B-TEST FAILED" : "B-TEST PASSED");
    std::fflush(stdout);
    std::fflush(stderr);
    std::_Exit(g_fail ? 1 : 0);
}
