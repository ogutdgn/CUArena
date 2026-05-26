// Writer — modern native Qt6/QML Word-like CUA app entry point.
// W2: opens the shell, starts the LOK engine, loads a blank Writer document
// and renders it on the canvas. See docs/architecture/ARCHITECTURE.md.
#include <QGuiApplication>
#include <QImage>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QQuickStyle>
#include <QQuickWindow>
#include <QTimer>
#include <QUrl>
#include <QtQml>

#include "engine/LokEngine.h"
#include "ui/DocumentCanvas.h"

#ifndef WRITER_ENGINE_INSTALL
#define WRITER_ENGINE_INSTALL "" // set by CMake to <engine>/instdir/program
#endif

int main(int argc, char* argv[])
{
    // Drive the embedded LO engine headless; use our own logger, not the
    // engine's built-in rllogger (DECISIONS D7).
    qputenv("SAL_USE_VCLPLUGIN", "svp");
    qputenv("LO_RL_LOG_DISABLE", "1");

    QGuiApplication app(argc, argv);
    app.setApplicationName(QStringLiteral("Writer"));
    app.setOrganizationName(QStringLiteral("cua-bench"));
    QQuickStyle::setStyle(QStringLiteral("Basic"));

    LokEngine lok;
    if (lok.initialize(QStringLiteral(WRITER_ENGINE_INSTALL),
                       QStringLiteral("file:///tmp/writer-lok-profile"))) {
        lok.loadBlankWriter();
    }

    qmlRegisterType<DocumentCanvas>("WriterApp", 1, 0, "DocumentCanvas");
    qmlRegisterUncreatableType<LokEngine>("WriterApp", 1, 0, "LokEngine",
                                          QStringLiteral("provided as the lokEngine context property"));

    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty(QStringLiteral("lokEngine"), &lok);
    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreationFailed, &app,
        []() { qFatal("Writer: QML root failed to load"); }, Qt::QueuedConnection);
    engine.load(QUrl(QStringLiteral("qrc:/src/ui/qml/Main.qml")));
    if (engine.rootObjects().isEmpty())
        return -1;

    // Headless verification / CI: WRITER_SHOT=<png> grabs the window once the
    // first frame + LOK page have rendered, then quits. (Useful for the RL /
    // Docker headless flow too.)
    if (qEnvironmentVariableIsSet("WRITER_SHOT")) {
        const QString shot = qEnvironmentVariable("WRITER_SHOT");
        auto* win = qobject_cast<QQuickWindow*>(engine.rootObjects().constFirst());
        QTimer::singleShot(1800, win, [win, shot]() {
            if (win) {
                const QImage img = win->grabWindow();
                img.save(shot);
            }
            QCoreApplication::quit();
        });
    }

    return app.exec();
}
