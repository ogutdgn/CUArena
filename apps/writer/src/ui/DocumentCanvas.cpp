#include "DocumentCanvas.h"
#include "engine/LokEngine.h"

#include <QPainter>

DocumentCanvas::DocumentCanvas(QQuickItem* parent) : QQuickPaintedItem(parent)
{
    setOpaquePainting(true);
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
