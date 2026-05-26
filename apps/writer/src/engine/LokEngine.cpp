#include "LokEngine.h"

// LOK_USE_UNSTABLE_API (gates paintTile/postUnoCommand/... — ENGINE_BUILD.md §6)
// is defined globally by CMake for this target.
#include <LibreOfficeKit/LibreOfficeKit.hxx>
#include <LibreOfficeKit/LibreOfficeKitInit.h>

#include <QByteArray>
#include <QDebug>
#include <QMetaObject>

LokEngine::LokEngine(QObject* parent) : QObject(parent) {}

LokEngine::~LokEngine()
{
    // Deliberately do NOT delete m_doc / m_office: the LO dev-build teardown
    // asserts on shutdown (ENGINE_BUILD.md §6). The process exits anyway.
}

bool LokEngine::initialize(const QString& installPath, const QString& userProfileUrl)
{
    if (m_office)
        return true;
    m_office = lok::lok_cpp_init(installPath.toUtf8().constData(),
                                 userProfileUrl.isEmpty() ? nullptr
                                                          : userProfileUrl.toUtf8().constData());
    if (!m_office) {
        qWarning() << "LokEngine: lok_cpp_init failed for" << installPath;
        return false;
    }
    return true;
}

bool LokEngine::loadBlankWriter()
{
    if (!m_office)
        return false;
    m_doc = m_office->documentLoad("private:factory/swriter");
    return finishLoad();
}

bool LokEngine::loadDocument(const QString& fileUrl)
{
    if (!m_office)
        return false;
    m_doc = m_office->documentLoad(fileUrl.toUtf8().constData());
    return finishLoad();
}

bool LokEngine::finishLoad()
{
    if (!m_doc) {
        char* err = m_office ? m_office->getError() : nullptr;
        qWarning() << "LokEngine: documentLoad failed:" << (err ? err : "?");
        return false;
    }
    m_doc->initializeForRendering();
    m_doc->registerCallback(&LokEngine::callbackThunk, this);
    refreshDocSize();
    emit readyChanged();
    return true;
}

bool LokEngine::save(const QString& fileUrl, const QString& format)
{
    if (!m_doc)
        return false;
    return m_doc->saveAs(fileUrl.toUtf8().constData(), format.toUtf8().constData(), nullptr);
}

void LokEngine::refreshDocSize()
{
    if (!m_doc)
        return;
    long w = 0, h = 0;
    m_doc->getDocumentSize(&w, &h);
    const QSize s(static_cast<int>(w), static_cast<int>(h));
    if (s != m_docSizeTwips) {
        m_docSizeTwips = s;
        emit documentSizeChanged(s);
    }
}

QImage LokEngine::renderTile(int posXTwips, int posYTwips, int wTwips, int hTwips,
                             int wPx, int hPx)
{
    if (!m_doc || wPx <= 0 || hPx <= 0)
        return {};

    // LOK paints premultiplied 32-bit pixels. On little-endian, BGRA maps
    // directly to QImage::Format_ARGB32_Premultiplied; RGBA needs a swap.
    QImage img(wPx, hPx, QImage::Format_ARGB32_Premultiplied);
    img.fill(Qt::white);
    m_doc->paintTile(img.bits(), wPx, hPx, posXTwips, posYTwips, wTwips, hTwips);

    if (m_doc->getTileMode() == LOK_TILEMODE_RGBA)
        img = img.rgbSwapped();
    return img;
}

void LokEngine::postUno(const QString& command, const QString& argsJson)
{
    if (!m_doc)
        return;
    const QByteArray cmd = command.toUtf8();
    const QByteArray args = argsJson.toUtf8();
    m_doc->postUnoCommand(cmd.constData(), argsJson.isEmpty() ? nullptr : args.constData(), false);
}

void LokEngine::postKey(int type, int charCode, int keyCode)
{
    if (m_doc)
        m_doc->postKeyEvent(type, charCode, keyCode);
}

void LokEngine::postMouse(int type, int xTwips, int yTwips, int count, int buttons, int modifier)
{
    if (m_doc)
        m_doc->postMouseEvent(type, xTwips, yTwips, count, buttons, modifier);
}

// static — may run on a LOK-internal thread; marshal to this object's thread.
void LokEngine::callbackThunk(int type, const char* payload, void* data)
{
    auto* self = static_cast<LokEngine*>(data);
    const QByteArray p = payload ? QByteArray(payload) : QByteArray();
    QMetaObject::invokeMethod(
        self, [self, type, p]() { self->handleCallback(type, p); }, Qt::QueuedConnection);
}

void LokEngine::handleCallback(int type, const QByteArray& payload)
{
    switch (type) {
    case LOK_CALLBACK_INVALIDATE_TILES: {
        if (payload.isEmpty() || payload == "EMPTY") {
            emit tilesInvalidated(QRect());
        } else {
            const auto parts = payload.split(',');
            if (parts.size() >= 4)
                emit tilesInvalidated(QRect(parts[0].trimmed().toInt(), parts[1].trimmed().toInt(),
                                            parts[2].trimmed().toInt(), parts[3].trimmed().toInt()));
            else
                emit tilesInvalidated(QRect());
        }
        break;
    }
    case LOK_CALLBACK_DOCUMENT_SIZE_CHANGED:
        refreshDocSize();
        break;
    case LOK_CALLBACK_STATE_CHANGED:
        emit unoStateChanged(QString::fromUtf8(payload));
        break;
    default:
        break;
    }
}
