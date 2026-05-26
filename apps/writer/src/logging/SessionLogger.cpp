#include "SessionLogger.h"

#include <QDateTime>
#include <QDir>
#include <QJsonArray>
#include <QJsonDocument>
#include <QStandardPaths>
#include <QUuid>

SessionLogger::SessionLogger(QObject* parent) : QObject(parent) {}

SessionLogger::~SessionLogger()
{
    if (m_rawFile.isOpen()) m_rawFile.close();
    if (m_semFile.isOpen()) m_semFile.close();
    if (m_outFile.isOpen()) m_outFile.close();
}

void SessionLogger::start(const QString& unoNamesResource)
{
    if (qEnvironmentVariableIsSet("WRITER_LOG_DISABLE")) {
        m_enabled = false;
        return;
    }

    QString base = qEnvironmentVariableIsSet("WRITER_LOG_DIR")
                       ? qEnvironmentVariable("WRITER_LOG_DIR")
                       : QDir::homePath() + "/.writer-rl-logs";

    m_sessionId = QUuid::createUuid().toString(QUuid::WithoutBraces);
    m_dir = base + "/" + m_sessionId;
    if (!QDir().mkpath(m_dir)) {
        qWarning() << "SessionLogger: cannot create" << m_dir << "- logging off";
        return;
    }

    m_rawFile.setFileName(m_dir + "/raw.jsonl");
    m_semFile.setFileName(m_dir + "/semantic.jsonl");
    m_outFile.setFileName(m_dir + "/outcome.jsonl");
    if (!m_rawFile.open(QIODevice::WriteOnly | QIODevice::Text) ||
        !m_semFile.open(QIODevice::WriteOnly | QIODevice::Text) ||
        !m_outFile.open(QIODevice::WriteOnly | QIODevice::Text)) {
        qWarning() << "SessionLogger: cannot open stream files - logging off";
        return;
    }

    // Load the .uno -> RL-name registry (generated from the command catalog).
    if (QFile nf(unoNamesResource); nf.open(QIODevice::ReadOnly)) {
        const QJsonObject o = QJsonDocument::fromJson(nf.readAll()).object();
        for (auto it = o.begin(); it != o.end(); ++it)
            m_unoNames.insert(it.key(), it.value().toString());
    }

    m_clock.start();
    m_enabled = true;
    qInfo() << "SessionLogger: session" << m_sessionId << "->" << m_dir;
}

void SessionLogger::writeLine(QFile& f, const QJsonObject& obj)
{
    f.write(QJsonDocument(obj).toJson(QJsonDocument::Compact));
    f.write("\n");
    f.flush();
}

QString SessionLogger::nameFor(const QString& cmd) const
{
    if (const auto it = m_unoNames.constFind(cmd); it != m_unoNames.constEnd())
        return it.value();
    // Fallback: strip ".uno:" so an uncatalogued command still has a stable name.
    return cmd.startsWith(QStringLiteral(".uno:")) ? cmd.mid(5) : cmd;
}

QString SessionLogger::logRaw(const QString& type, const QJsonObject& fields,
                              const QString& targetId, const QJsonObject& modifiers)
{
    if (!m_enabled)
        return QString();
    const QString id = QStringLiteral("raw-%1").arg(++m_rawCount);
    const qint64 now = QDateTime::currentMSecsSinceEpoch();
    QJsonObject mods = modifiers;
    if (mods.isEmpty())
        mods = QJsonObject{{"alt", false}, {"shift", false}, {"ctrl", false}, {"meta", false}};

    writeLine(m_rawFile, QJsonObject{
        {"eventId", id},
        {"type", type},
        {"timestamp", static_cast<double>(now)},
        {"sessionTime", static_cast<double>(m_clock.elapsed())},
        {"targetId", targetId.isEmpty() ? QJsonValue(QJsonValue::Null) : QJsonValue(targetId)},
        {"modifiers", mods},
        {"fields", fields},
    });

    m_mostRecentRawId = id;
    if (m_firstRawSinceSemantic.isEmpty())
        m_firstRawSinceSemantic = id;
    return id;
}

void SessionLogger::logSemantic(const QString& cmd, const QJsonObject& args)
{
    if (!m_enabled)
        return;
    ++m_semanticCount;

    // rawEventIdRange = the raw events emitted since the previous semantic.
    QJsonValue range = QJsonValue::Null;
    if (!m_mostRecentRawId.isEmpty()) {
        const QString start = m_firstRawSinceSemantic.isEmpty() ? m_mostRecentRawId
                                                                : m_firstRawSinceSemantic;
        range = QJsonArray{start, m_mostRecentRawId};
    }
    m_firstRawSinceSemantic.clear();

    writeLine(m_semFile, QJsonObject{
        {"schemaVersion", 1},
        {"sessionId", m_sessionId},
        {"eventId", QStringLiteral("sem-%1").arg(m_semanticCount)},
        {"timestamp", static_cast<double>(QDateTime::currentMSecsSinceEpoch())},
        {"docId", QStringLiteral("writer")},
        {"rawEventIdRange", range},
        {"name", nameFor(cmd)},
        {"command", cmd},
        {"args", args},
    });
}

void SessionLogger::writeOutcome(const QJsonObject& document, const QJsonObject& summaryExtra)
{
    if (!m_enabled)
        return;
    ++m_outcomeCount;
    QJsonObject summary = summaryExtra;
    summary.insert("semanticEventCount", m_semanticCount);

    writeLine(m_outFile, QJsonObject{
        {"schemaVersion", 1},
        {"sessionId", m_sessionId},
        {"capturedAt", static_cast<double>(QDateTime::currentMSecsSinceEpoch())},
        {"summary", summary},
        {"document", document},
    });
}
