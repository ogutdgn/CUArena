// DocumentCanvas — a QQuickPaintedItem that blits the LOK-rendered document
// bitmap. W2b first cut renders the whole document scaled to the item width;
// per-tile caching + scrolling + zoom come next. Exposed to QML as
// WriterApp.DocumentCanvas.
#pragma once

#include <QQuickPaintedItem>

class LokEngine;

class DocumentCanvas : public QQuickPaintedItem
{
    Q_OBJECT
    Q_PROPERTY(LokEngine* engine READ engine WRITE setEngine NOTIFY engineChanged)

public:
    explicit DocumentCanvas(QQuickItem* parent = nullptr);

    void paint(QPainter* painter) override;

    LokEngine* engine() const { return m_engine; }
    void setEngine(LokEngine* engine);

signals:
    void engineChanged();

private:
    LokEngine* m_engine = nullptr;
};
