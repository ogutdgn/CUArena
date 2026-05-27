// DocumentCanvas — a QQuickPaintedItem that blits the LOK-rendered document
// bitmap. W2b first cut renders the whole document scaled to the item width;
// per-tile caching + scrolling + zoom come next. Exposed to QML as
// WriterApp.DocumentCanvas.
#pragma once

#include <QQuickPaintedItem>

class LokEngine;
class QTimer;

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

protected:
    void keyPressEvent(QKeyEvent* event) override;
    void keyReleaseEvent(QKeyEvent* event) override;
    void mousePressEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void mouseDoubleClickEvent(QMouseEvent* event) override;

private:
    double twipsPerPixel() const; // current uniform scale (whole-page-to-width)
    double pxPerTwip() const;     // inverse: twip -> canvas px

    LokEngine* m_engine = nullptr;
    QTimer* m_blink = nullptr;    // caret blink
    bool m_caretOn = true;
    bool m_mouseDown = false;     // drag-select in progress
};
