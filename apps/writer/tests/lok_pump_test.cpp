// D9 probe (visual): does pumping LO's scheduler via the exported
// unit_lok_process_events_to_idle make an edit render? Renders the top region
// of the page before edit / after insert+pump, saves PNGs to inspect, and
// reports dark-pixel counts. Built as the writer_pump_test CMake target.
#define LOK_USE_UNSTABLE_API
#include <LibreOfficeKit/LibreOfficeKit.hxx>
#include <LibreOfficeKit/LibreOfficeKitInit.h>

#include <QGuiApplication>
#include <QImage>

#include <cstdio>
#include <dlfcn.h>
#include <unistd.h>

using namespace lok;
using pump_t = void (*)();

int main(int argc, char** argv)
{
    qputenv("SAL_USE_VCLPLUGIN", "svp");
    qputenv("LO_RL_LOG_DISABLE", "1");
    qputenv("QT_QPA_PLATFORM", "offscreen");
    QGuiApplication app(argc, argv);
    if (argc < 2) { printf("usage\n"); return 64; }

    Office* office = lok_cpp_init(argv[1], "file:///tmp/lok-pump-profile");
    if (!office) { printf("FAIL init\n"); return 1; }
    Document* doc = office->documentLoad("private:factory/swriter");
    if (!doc) { printf("FAIL load\n"); return 2; }
    doc->initializeForRendering();
    auto pump = reinterpret_cast<pump_t>(dlsym(RTLD_DEFAULT, "unit_lok_process_events_to_idle"));
    printf("pump symbol: %p\n", reinterpret_cast<void*>(pump));

    long w = 0, h = 0;
    doc->getDocumentSize(&w, &h);
    // Top region of the page (~4000 twips tall) at high resolution.
    const int topTwips = 4000;
    const int wp = 1200;
    const int hp = static_cast<int>(double(wp) * topTwips / w);

    auto renderTop = [&](const char* file) -> long {
        QImage img(wp, hp, QImage::Format_ARGB32_Premultiplied);
        img.fill(Qt::white);
        doc->paintTile(img.bits(), wp, hp, 0, 0, static_cast<int>(w), topTwips);
        if (doc->getTileMode() == LOK_TILEMODE_RGBA) img = img.rgbSwapped();
        long dark = 0;
        for (int y = 0; y < img.height(); ++y)
            for (int x = 0; x < img.width(); ++x)
                if (qGray(img.pixel(x, y)) < 100) ++dark;
        img.save(file);
        printf("%-22s dark=%ld saved=%s\n", file, dark, "ok");
        return dark;
    };

    renderTop("/tmp/pump-before.png");

    // A) typing via postKeyEvent (the app's real path via the canvas)
    const char* typed = "KEYEVENT TYPING 999";
    for (const char* p = typed; *p; ++p) {
        doc->postKeyEvent(LOK_KEYEVENT_KEYINPUT, *p, 0);
        doc->postKeyEvent(LOK_KEYEVENT_KEYUP, *p, 0);
    }
    if (pump) pump();
    renderTop("/tmp/pump-after-keyevent.png");

    // B) then a paragraph break + .uno:InsertText on the next line
    doc->postUnoCommand(".uno:InsertPara", nullptr, false);
    doc->postUnoCommand(".uno:InsertText",
        "{\"Text\":{\"type\":\"string\",\"value\":\"UNO INSERTTEXT 888\"}}", false);
    if (pump) pump();
    renderTop("/tmp/pump-after-both.png");

    fflush(stdout);
    _exit(0);
}
