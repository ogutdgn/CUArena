// LokEngine — our binding over LibreOfficeKit. Owns the lok::Office (kept
// alive for the app's whole lifetime to avoid the dev-build teardown abort)
// and the current lok::Document. This is the seam where rendering, command
// dispatch, logging and (later) MCP all hook in — see ARCHITECTURE.md.
//
// W2b simplification: LOK is driven from the GUI thread; callbacks (which may
// arrive on a LOK-internal thread) are marshalled back to this object's thread
// via a queued invocation. A dedicated engine thread can come later if
// paintTile latency on the GUI thread becomes a problem.
#pragma once

#include <QObject>
#include <QImage>
#include <QRect>
#include <QSize>
#include <QString>

namespace lok {
class Office;
class Document;
}

class LokEngine : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool ready READ isReady NOTIFY readyChanged)

public:
    explicit LokEngine(QObject* parent = nullptr);
    ~LokEngine() override;

    // Initialise the engine from a built instdir/program path. Returns false
    // if LOK could not start. Safe to call once.
    bool initialize(const QString& installPath, const QString& userProfileUrl);

    bool loadBlankWriter();
    bool loadDocument(const QString& fileUrl);
    bool save(const QString& fileUrl, const QString& format);

    bool isReady() const { return m_doc != nullptr; }
    QSize documentSizeTwips() const { return m_docSizeTwips; }

    // Render a twip rectangle of the document into an (wPx x hPx) image.
    QImage renderTile(int posXTwips, int posYTwips, int wTwips, int hTwips,
                      int wPx, int hPx);

    // Input + command dispatch (the logger/MCP seam).
    Q_INVOKABLE void postUno(const QString& command, const QString& argsJson = QString());
    Q_INVOKABLE void postKey(int type, int charCode, int keyCode);
    Q_INVOKABLE void postMouse(int type, int xTwips, int yTwips, int count,
                               int buttons, int modifier);

signals:
    void readyChanged();
    void documentSizeChanged(QSize twips);
    void tilesInvalidated(QRect twips); // null/empty rect = whole document
    void unoStateChanged(QString payload); // ".uno:Bold=true"

private:
    bool finishLoad();
    void refreshDocSize();
    void handleCallback(int type, const QByteArray& payload);
    static void callbackThunk(int type, const char* payload, void* data);

    lok::Office* m_office = nullptr;
    lok::Document* m_doc = nullptr;
    QSize m_docSizeTwips;
};
