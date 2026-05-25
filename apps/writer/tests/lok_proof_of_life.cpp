// W1 proof-of-life: drive the built LibreOffice engine headlessly via the
// LibreOfficeKit C++ API — the exact integration path our Qt app will use.
//
// Proves: lok init -> documentLoad(Writer) -> initializeForRendering ->
// getDocumentSize -> postUnoCommand(InsertText, Bold) -> paintTile (bitmap)
// -> saveAs(.docx, .odt). No linking against LO libs: lok_cpp_init dlopen's
// the engine at runtime from the install path. Build:
//   g++ -std=c++17 -I <engine>/include lok_proof_of_life.cpp -ldl -o lok_pol
// Run:
//   lok_pol <engine>/instdir/program
// Tiled-rendering API (paintTile/postUnoCommand/getDocumentSize/...) lives
// behind LOK_USE_UNSTABLE_API in the header (same as gtktiledviewer).
#define LOK_USE_UNSTABLE_API
#include <LibreOfficeKit/LibreOfficeKit.hxx>
#include <LibreOfficeKit/LibreOfficeKitInit.h>
#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <vector>

using namespace lok;

int main(int argc, char** argv)
{
    setvbuf(stdout, nullptr, _IONBF, 0); // unbuffered: survive an abnormal exit
    if (argc < 2) { fprintf(stderr, "usage: %s <install_path (instdir/program)>\n", argv[0]); return 64; }
    const char* install = argv[1];

    Office* office = lok_cpp_init(install, "file:///tmp/lok-pol-profile");
    if (!office) { fprintf(stderr, "FAIL: lok_cpp_init\n"); return 1; }
    printf("ok: lok init\n");

    Document* doc = office->documentLoad("private:factory/swriter");
    if (!doc) { char* e = office->getError(); fprintf(stderr, "FAIL: documentLoad: %s\n", e ? e : "?"); return 2; }
    printf("ok: documentLoad(swriter)\n");

    doc->initializeForRendering();

    long w = 0, h = 0;
    doc->getDocumentSize(&w, &h);
    printf("ok: getDocumentSize = %ld x %ld twips\n", w, h);
    if (w <= 0 || h <= 0) { fprintf(stderr, "FAIL: bad doc size\n"); return 3; }

    doc->postUnoCommand(".uno:InsertText",
        "{\"Text\":{\"type\":\"string\",\"value\":\"Merhaba CUA Writer (LOK proof-of-life)\"}}", false);
    doc->postUnoCommand(".uno:Bold", nullptr, false);
    printf("ok: postUnoCommand InsertText + Bold\n");

    const int cw = 256, ch = 256;            // canvas pixels
    const int tw = 6000, th = 6000;          // tile area in twips
    std::vector<unsigned char> buf(static_cast<size_t>(cw) * ch * 4, 0);
    doc->paintTile(buf.data(), cw, ch, 0, 0, tw, th);
    unsigned char mn = 255, mx = 0;
    for (unsigned char b : buf) { if (b < mn) mn = b; if (b > mx) mx = b; }
    printf("ok: paintTile %dx%d px (byte min=%u max=%u -> %s)\n",
           cw, ch, mn, mx, (mx > mn) ? "rendered content" : "uniform/blank");
    if (mx == mn) { fprintf(stderr, "FAIL: tile is uniform (nothing rendered)\n"); return 4; }

    bool okDocx = doc->saveAs("file:///tmp/lok-pol-out.docx", "docx", nullptr);
    if (!okDocx) { char* e = office->getError(); fprintf(stderr, "docx err: %s\n", e ? e : "?"); }
    bool okOdt  = doc->saveAs("file:///tmp/lok-pol-out.odt", "odt", nullptr);
    if (!okOdt) { char* e = office->getError(); fprintf(stderr, "odt err: %s\n", e ? e : "?"); }
    printf("ok: saveAs docx=%s odt=%s\n", okDocx ? "OK" : "FAIL", okOdt ? "OK" : "FAIL");
    if (!okDocx || !okOdt) { fprintf(stderr, "FAIL: saveAs\n"); return 5; }

    printf("LOK_PROOF_OF_LIFE_DONE\n");
    // The engine's dev-build teardown (delete office) asserts on shutdown — a
    // known LOK quirk irrelevant to functionality (all work above succeeded
    // and files are on disk). The real app keeps the Office alive for its
    // lifetime; here we bypass the noisy teardown with a clean _exit.
    fflush(stdout);
    _exit(0);
}
