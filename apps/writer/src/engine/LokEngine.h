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
#include <QJsonObject>
#include <QRect>
#include <QSize>
#include <QString>

#include "logging/SessionLogger.h"

namespace lok {
class Office;
class Document;
}
class QTimer;

class LokEngine : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool ready READ isReady NOTIFY readyChanged)
    Q_PROPERTY(QSize documentSize READ documentSizeTwips NOTIFY documentSizeChanged)

public:
    // Mirror LOK_KEYEVENT_* / LOK_MOUSEEVENT_* (asserted equal in the .cpp).
    enum KeyType { KeyInput = 0, KeyUp = 1 };
    enum MouseType { MouseDown = 0, MouseUp = 1, MouseMove = 2 };
    Q_ENUM(KeyType)
    Q_ENUM(MouseType)

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
    // Drive a JSDialog control back into the engine (W4). windowId = the
    // dialog's lokWindowId; argsJson = {"id":"<ctrl>","type":"<widget>",
    // "cmd":"<action>","data":"<value>"}. See docs/architecture/W4_*.
    Q_INVOKABLE void sendDialogEvent(qulonglong windowId, const QString& argsJson);
    Q_INVOKABLE void postKey(int type, int charCode, int keyCode);
    Q_INVOKABLE void typeText(const QString& text); // convenience: KEYINPUT+KEYUP per char
    Q_INVOKABLE void postMouse(int type, int xTwips, int yTwips, int count,
                               int buttons, int modifier);

signals:
    void readyChanged();
    void documentSizeChanged(QSize twips);
    void tilesInvalidated(QRect twips); // null/empty rect = whole document
    void unoStateChanged(QString payload); // ".uno:Bold=true"
    void jsDialog(QString payload);     // LOK_CALLBACK_JSDIALOG — JSON widget tree / update / action
    void windowEvent(QString payload);  // LOK_CALLBACK_WINDOW — created/close/destroy (tiled dialogs)

private:
    bool finishLoad();
    void refreshDocSize();
    void handleCallback(int type, const QByteArray& payload);
    static void callbackThunk(int type, const char* payload, void* data);
    void emitOutcome(); // build + write an outcome snapshot (logger cadence)
    // Pump LO's scheduler so edits lay out + invalidate + re-render (D9). Uses
    // the engine's exported unit_lok_process_events_to_idle (= Scheduler::
    // ProcessEventsToIdle); resolved via dlsym after lok init.
    void pumpScheduler();

    lok::Office* m_office = nullptr;
    lok::Document* m_doc = nullptr;
    QSize m_docSizeTwips;
    void (*m_pump)() = nullptr;

    // Logging (W5): raw from input, semantic from dispatch, outcome on a timer.
    SessionLogger m_logger;
    QTimer* m_outcomeTimer = nullptr;
    QJsonObject m_formatAtCursor;       // .uno toggle states from STATE_CHANGED
    QRect m_cursorTwips;                // from INVALIDATE_VISIBLE_CURSOR
};
