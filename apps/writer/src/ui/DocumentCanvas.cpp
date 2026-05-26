#include "DocumentCanvas.h"
#include "engine/LokEngine.h"

#include <QKeyEvent>
#include <QMouseEvent>
#include <QPainter>

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
        m_engine->postMouse(LokEngine::MouseDown, int(event->position().x() * s),
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
    event->accept();
}
