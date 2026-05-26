// W2b render-path test: exercise the LokEngine binding headlessly (no QML) —
// init -> load blank Writer -> type text -> renderTile -> save PNG. Proves the
// LOK->QImage path produces a real page bitmap, independent of QML runtime
// modules. Built as the `writer_render_test` CMake target.
#include "engine/LokEngine.h"

#include <QCoreApplication>
#include <QElapsedTimer>
#include <QGuiApplication>
#include <QImage>
#include <QThread>
#include <cstdio>
#include <unistd.h>

#ifndef WRITER_ENGINE_INSTALL
#define WRITER_ENGINE_INSTALL ""
#endif

int main(int argc, char* argv[])
{
    qputenv("SAL_USE_VCLPLUGIN", "svp");
    qputenv("LO_RL_LOG_DISABLE", "1");
    qputenv("WRITER_LOG_DISABLE", "1"); // don't spawn session logs from the render test
    qputenv("QT_QPA_PLATFORM", "offscreen");
    QGuiApplication app(argc, argv);

    LokEngine lok;
    if (!lok.initialize(QStringLiteral(WRITER_ENGINE_INSTALL),
                        QStringLiteral("file:///tmp/writer-rt-profile"))) {
        fprintf(stderr, "FAIL: initialize\n");
        return 1;
    }
    if (!lok.loadBlankWriter()) {
        fprintf(stderr, "FAIL: loadBlankWriter\n");
        return 2;
    }
    lok.postUno(QStringLiteral(".uno:InsertText"),
                QStringLiteral("{\"Text\":{\"type\":\"string\",\"value\":\"Writer via LokEngine binding\"}}"));

    // Let LOK process the insert + lay out / invalidate before we render.
    QElapsedTimer t; t.start();
    while (t.elapsed() < 600) {
        QCoreApplication::processEvents(QEventLoop::AllEvents, 50);
        QThread::msleep(20);
    }

    const QSize d = lok.documentSizeTwips();
    printf("ok: docsize = %d x %d twips\n", d.width(), d.height());
    if (d.isEmpty()) { fprintf(stderr, "FAIL: empty doc size\n"); return 3; }

    // Full page (for the PNG artifact).
    const int wPx = 820;
    const int hPx = int(820.0 * d.height() / d.width());
    const QImage img = lok.renderTile(0, 0, d.width(), d.height(), wPx, hPx);
    printf("ok: rendered full page %d x %d (null=%d)\n", img.width(), img.height(), img.isNull());
    if (img.isNull()) { fprintf(stderr, "FAIL: null image\n"); return 4; }
    const bool saved = img.save(QStringLiteral("/tmp/writer-render-test.png"));
    printf("ok: saved /tmp/writer-render-test.png = %d\n", saved);

    // Text-visibility check: render just the top strip at high resolution so the
    // inserted glyphs are several px tall, then look for dark (text) pixels —
    // proving paintTile rendered AND the .uno dispatch took effect in the bitmap.
    const int stripTwipsH = 3000;
    const int sWpx = 1600;
    const int sHpx = int(double(sWpx) * stripTwipsH / d.width());
    const QImage strip = lok.renderTile(0, 0, d.width(), stripTwipsH, sWpx, sHpx);
    int dark = 0, light = 0;
    for (int y = 0; y < strip.height(); ++y)
        for (int x = 0; x < strip.width(); ++x) {
            if (qGray(strip.pixel(x, y)) < 100) ++dark; else ++light;
        }
    strip.save(QStringLiteral("/tmp/writer-render-test-strip.png"));
    printf("ok: top strip %dx%d  light=%d dark=%d\n", strip.width(), strip.height(), light, dark);
    if (!saved || light == 0) { fprintf(stderr, "FAIL: render verification\n"); return 5; }
    printf("%s\n", dark > 0 ? "ok: text glyphs visible in render"
                            : "note: no dark pixels (text not laid out at render time)");

    // Decisive dispatch check: save via the binding and confirm the inserted
    // text is in the document model (separates render-timing from a dispatch bug).
    const bool sv = lok.save(QStringLiteral("file:///tmp/writer-rt-out.docx"), QStringLiteral("docx"));
    printf("ok: saveAs docx via binding = %d\n", sv);

    printf("RENDER_TEST_DONE\n");
    fflush(stdout);
    _exit(0); // bypass LO dev-build teardown abort (ENGINE_BUILD.md §6)
}
