// SessionLogger — the writer app's raw/semantic/outcome logger (W5).
//
// Because we own the dispatch + input + state seams (Boundary A, DECISIONS D7),
// every stream has a clean authoritative source in our layer — no engine
// instrumentation. Conforms to overview/log-contract.md (figma-parity):
//   raw[]      — input events (key/mouse/...), base fields per contract
//   semantic[] — .uno dispatches mapped to RL-friendly names + rawEventIdRange
//   outcome{}  — document state snapshot on a cadence; summary.semanticEventCount
//
// While live it writes three JSONL files under the session dir; a consolidator
// (tools/consolidate_log.py) merges them into the single figma-shaped
// session.json. See docs/architecture/LOGGING.md.
#pragma once

#include <QElapsedTimer>
#include <QFile>
#include <QJsonObject>
#include <QObject>
#include <QString>

class SessionLogger : public QObject
{
    Q_OBJECT
public:
    explicit SessionLogger(QObject* parent = nullptr);
    ~SessionLogger() override;

    // Create the session dir + open streams. Honours WRITER_LOG_DISABLE (off)
    // and WRITER_LOG_DIR (base dir; default ~/.writer-rl-logs). No-op if
    // disabled. unoNamesResource = qrc path to the .uno->name map.
    void start(const QString& unoNamesResource = QStringLiteral(":/resources/uno-names.json"));

    bool enabled() const { return m_enabled; }
    QString sessionId() const { return m_sessionId; }
    QString sessionDir() const { return m_dir; }
    int semanticEventCount() const { return m_semanticCount; }

    // raw[] — returns the emitted eventId (so callers needn't track it).
    QString logRaw(const QString& type, const QJsonObject& fields,
                   const QString& targetId = QString(),
                   const QJsonObject& modifiers = QJsonObject());

    // semantic[] — `cmd` is the raw .uno:* (mapped to an RL name via the
    // registry); `args` is the dispatch argument object (may be empty).
    void logSemantic(const QString& cmd, const QJsonObject& args = QJsonObject());

    // outcome{} — append a snapshot line; `document` is the per-app shape,
    // `summaryExtra` merges into summary alongside semanticEventCount.
    void writeOutcome(const QJsonObject& document,
                      const QJsonObject& summaryExtra = QJsonObject());

private:
    void writeLine(QFile& f, const QJsonObject& obj);
    QString nameFor(const QString& cmd) const;

    bool m_enabled = false;
    QString m_sessionId;
    QString m_dir;
    QElapsedTimer m_clock;
    QFile m_rawFile, m_semFile, m_outFile;

    int m_rawCount = 0;
    int m_semanticCount = 0;
    int m_outcomeCount = 0;

    // rawEventIdRange tracking: range = raw events since the previous semantic.
    QString m_mostRecentRawId;
    QString m_firstRawSinceSemantic;

    QHash<QString, QString> m_unoNames; // .uno:Cmd -> rl_name
};
