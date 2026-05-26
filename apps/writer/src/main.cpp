// Writer — modern native Qt6/QML Word-like CUA app entry point.
// W2 skeleton: opens the application shell. The LOK engine binding + tile
// canvas land next (see docs/execution-map.md "Next: W2").
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include <QUrl>

int main(int argc, char* argv[])
{
    QGuiApplication app(argc, argv);
    app.setApplicationName(QStringLiteral("Writer"));
    app.setOrganizationName(QStringLiteral("cua-bench"));

    // Basic style is fully stylable from QML (we paint our own Word-like chrome).
    QQuickStyle::setStyle(QStringLiteral("Basic"));

    QQmlApplicationEngine engine;
    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreationFailed, &app,
        []() { qFatal("Writer: QML root failed to load"); }, Qt::QueuedConnection);
    engine.load(QUrl(QStringLiteral("qrc:/src/ui/qml/Main.qml")));
    if (engine.rootObjects().isEmpty())
        return -1;

    return app.exec();
}
