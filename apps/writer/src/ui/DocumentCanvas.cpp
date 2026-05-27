#include "DocumentCanvas.h"
#include "engine/LokEngine.h"

#include <QKeyEvent>
#include <QMouseEvent>
#include <QPainter>
#include <QTimer>

// Qt key -> LibreOffice awt::Key code for non-printable keys (printable chars
// go through the event text). Values from offapi/com/sun/star/awt/Key.idl.
static int qtKeyToLok(int qtKey)
{
    switch (qtKey) {
    case Qt::Key_Return:
    case Qt::Key_Enter:    return 1280; // RETURN
    case Qt::Key_Escape:   return 1281;
    case Qt::Key_Tab:      return 1282;
    case Qt::Key_Backspace:return 1283;
    case Qt::Key_Delete:   return 1286;
    case Qt::Key_Down:     return 1024;
    case Qt::Key_Up:       return 1025;
    case Qt::Key_Left:     return 1026;
    case Qt::Key_Right:    return 1027;
    case Qt::Key_Home:     return 1028;
    case Qt::Key_End:      return 1029;
    case Qt::Key_PageUp:   return 1030;
    case Qt::Key_PageDown: return 1031;
    case Qt::Key_Insert:   return 1285;
    default:               return 0;
    }
}

DocumentCanvas::DocumentCanvas(QQuickItem* parent) : QQuickPaintedItem(parent)
{
    setOpaquePainting(true);
    setAcceptedMouseButtons(Qt::AllButtons);
    setFlag(QQuickItem::ItemAcceptsInputMethod, true);
    setActiveFocusOnTab(true);

    m_blink = new QTimer(this);
    m_blink->setInterval(530); // Word-ish caret blink
    connect(m_blink, &QTimer::timeout, this, [this]() { m_caretOn = !m_caretOn; update(); });
    m_blink->start();
}

double DocumentCanvas::twipsPerPixel() const
{
    if (!m_engine || width() <= 0)
        return 0.0;
    const QSize d = m_engine->documentSizeTwips();
    if (d.isEmpty())
        return 0.0;
    return static_cast<double>(d.width()) / width(); // uniform: page scaled to width
}

double DocumentCanvas::pxPerTwip() const
{
    const double tpp = twipsPerPixel();
    return tpp > 0.0 ? 1.0 / tpp : 0.0;
}

void DocumentCanvas::setEngine(LokEngine* engine)
{
    if (m_engine == engine)
        return;
    if (m_engine)
        m_engine->disconnect(this);
    m_engine = engine;
    if (m_engine) {
        connect(m_engine, &LokEngine::tilesInvalidated, this, [this]() { update(); });
        connect(m_engine, &LokEngine::documentSizeChanged, this, [this]() { update(); });
        connect(m_engine, &LokEngine::readyChanged, this, [this]() { update(); });
        // Caret/selection overlays: reset the blink so the caret is solid right
        // after it moves (Word feel), then repaint.
        connect(m_engine, &LokEngine::cursorChanged, this, [this]() {
            m_caretOn = true; if (m_blink) m_blink->start(); update();
        });
        connect(m_engine, &LokEngine::selectionChanged, this, [this]() { update(); });
    }
    emit engineChanged();
    update();
}

void DocumentCanvas::paint(QPainter* painter)
{
    painter->fillRect(boundingRect(), QColor(0x3a, 0x3a, 0x3a));
    if (!m_engine || !m_engine->isReady())
        return;

    const QSize docTwips = m_engine->documentSizeTwips();
    if (docTwips.isEmpty())
        return;

    // First cut: scale the whole document to the item width.
    const int wPx = qMax(1, static_cast<int>(width()));
    const double scale = static_cast<double>(wPx) / docTwips.width();
    const int hPx = qMax(1, static_cast<int>(docTwips.height() * scale));

    const QImage img = m_engine->renderTile(0, 0, docTwips.width(), docTwips.height(), wPx, hPx);
    if (!img.isNull())
        painter->drawImage(QPointF(0, 0), img);

    // Editor overlays (twips -> px with the same uniform scale).
    painter->setRenderHint(QPainter::Antialiasing, false);

    // Text selection — translucent highlight over the selected runs.
    const QVector<QRect> sel = m_engine->selectionTwips();
    if (!sel.isEmpty()) {
        const QColor hi(0x2b, 0x57, 0x97, 0x55);
        for (const QRect& r : sel)
            painter->fillRect(QRectF(r.x() * scale, r.y() * scale,
                                     r.width() * scale, r.height() * scale), hi);
    }

    // Caret — a thin vertical bar at the cursor rect (blinks; hidden during a
    // ranged selection, like Word).
    if (sel.isEmpty() && m_engine->cursorVisible() && m_caretOn) {
        const QRect c = m_engine->cursorTwips();
        if (c.height() > 0) {
            const double x = c.x() * scale;
            const double y = c.y() * scale;
            const double h = c.height() * scale;
            const double w = qMax(1.0, c.width() * scale);
            painter->fillRect(QRectF(x, y, w, h), QColor(0x10, 0x10, 0x10));
        }
    }
}

void DocumentCanvas::keyPressEvent(QKeyEvent* event)
{
    if (!m_engine) { QQuickPaintedItem::keyPressEvent(event); return; }
    const QString t = event->text();
    const int ch = (!t.isEmpty() && t.at(0).isPrint()) ? t.at(0).unicode() : 0;
    m_engine->postKey(LokEngine::KeyInput, ch, qtKeyToLok(event->key()));
    event->accept();
}

void DocumentCanvas::keyReleaseEvent(QKeyEvent* event)
{
    if (!m_engine) { QQuickPaintedItem::keyReleaseEvent(event); return; }
    const QString t = event->text();
    const int ch = (!t.isEmpty() && t.at(0).isPrint()) ? t.at(0).unicode() : 0;
    m_engine->postKey(LokEngine::KeyUp, ch, qtKeyToLok(event->key()));
    event->accept();
}

void DocumentCanvas::mousePressEvent(QMouseEvent* event)
{
    forceActiveFocus();
    const double s = twipsPerPixel();
    if (m_engine && s > 0.0) {
        m_mouseDown = true;
        m_engine->postMouse(LokEngine::MouseDown, int(event->position().x() * s),
                            int(event->position().y() * s), 1, 1, 0);
    }
    event->accept();
}

void DocumentCanvas::mouseMoveEvent(QMouseEvent* event)
{
    // Forward drag as MOUSEMOVE so the engine extends the text selection.
    const double s = twipsPerPixel();
    if (m_engine && m_mouseDown && s > 0.0) {
        m_engine->postMouse(LokEngine::MouseMove, int(event->position().x() * s),
                            int(event->position().y() * s), 1, 1, 0);
    }
    event->accept();
}

void DocumentCanvas::mouseReleaseEvent(QMouseEvent* event)
{
    const double s = twipsPerPixel();
    if (m_engine && s > 0.0) {
        m_engine->postMouse(LokEngine::MouseUp, int(event->position().x() * s),
                            int(event->position().y() * s), 1, 1, 0);
    }
    m_mouseDown = false;
    event->accept();
}

void DocumentCanvas::mouseDoubleClickEvent(QMouseEvent* event)
{
    // count=2 selects the word under the cursor (LO mouse-event semantics).
    const double s = twipsPerPixel();
    if (m_engine && s > 0.0) {
        m_engine->postMouse(LokEngine::MouseDown, int(event->position().x() * s),
                            int(event->position().y() * s), 2, 1, 0);
        m_engine->postMouse(LokEngine::MouseUp, int(event->position().x() * s),
                            int(event->position().y() * s), 2, 1, 0);
    }
    event->accept();
}
