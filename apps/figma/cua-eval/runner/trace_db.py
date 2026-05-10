"""Trace persistence backends for CUA attempts.

Backends:
- sqlite: local single-file DB (default)
- postgres-s3: hosted Postgres metadata + S3 artifacts
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from .runner import AttemptResult


def _now_ms() -> int:
    return int(time.time() * 1000)


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    raw = _read_text(path)
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _read_json_any(path: Path) -> Any:
    raw = _read_text(path)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _png_dimensions(payload: bytes) -> tuple[int | None, int | None]:
    if len(payload) < 24:
        return None, None
    if payload[:8] != b"\x89PNG\r\n\x1a\n":
        return None, None
    if payload[12:16] != b"IHDR":
        return None, None
    width = int.from_bytes(payload[16:20], "big")
    height = int.from_bytes(payload[20:24], "big")
    return width, height


def _ms_to_dt(ms: int | None) -> datetime | None:
    if not ms:
        return None
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)


def _guess_content_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".png":
        return "image/png"
    if ext == ".json":
        return "application/json"
    if ext == ".txt":
        return "text/plain; charset=utf-8"
    if ext == ".csv":
        return "text/csv; charset=utf-8"
    if ext == ".md":
        return "text/markdown; charset=utf-8"
    return "application/octet-stream"


class TraceStore(Protocol):
    def upsert_run(self, *, run_id: str, run_root: Path, config: dict[str, Any]) -> None: ...
    def ingest_attempt(
        self,
        *,
        run_id: str,
        provider: str,
        task_id: str,
        attempt_index: int,
        attempt_dir: Path,
        result: AttemptResult,
    ) -> None: ...
    def finalize_run(self, *, run_id: str, attempts: list[AttemptResult], extra: dict[str, Any]) -> None: ...
    def close(self) -> None: ...


class SqliteTraceStore:
    def __init__(self, db_path: Path, *, store_screenshot_bytes: bool = False) -> None:
        self.db_path = db_path
        self.store_screenshot_bytes = store_screenshot_bytes
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self._init_schema()

    def close(self) -> None:
        self.conn.close()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
              run_id TEXT PRIMARY KEY,
              run_root TEXT NOT NULL,
              status TEXT NOT NULL,
              created_at_ms INTEGER NOT NULL,
              ended_at_ms INTEGER,
              config_json TEXT NOT NULL,
              summary_json TEXT,
              attempt_count INTEGER NOT NULL DEFAULT 0,
              pass_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS attempts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT NOT NULL,
              provider TEXT NOT NULL,
              task_id TEXT NOT NULL,
              attempt_index INTEGER NOT NULL,
              attempt_dir TEXT NOT NULL,
              model TEXT,
              started_at_ms INTEGER,
              ended_at_ms INTEGER,
              elapsed_s REAL,
              turns INTEGER,
              stop_reason TEXT,
              error TEXT,
              passed INTEGER NOT NULL,
              final_score REAL,
              base_score REAL,
              max_score REAL,
              efficiency REAL,
              input_tokens INTEGER,
              output_tokens INTEGER,
              estimated_cost_usd REAL,
              log_session_id TEXT,
              meta_json TEXT,
              outcome_json TEXT,
              prompt_text TEXT,
              system_prompt_text TEXT,
              log_json TEXT,
              score_json TEXT,
              trajectory_json TEXT,
              created_at_ms INTEGER NOT NULL,
              updated_at_ms INTEGER NOT NULL,
              UNIQUE(run_id, provider, task_id, attempt_index),
              FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_attempts_run_id ON attempts(run_id);
            CREATE INDEX IF NOT EXISTS idx_attempts_provider_task ON attempts(provider, task_id);

            CREATE TABLE IF NOT EXISTS screenshots (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              attempt_id INTEGER NOT NULL,
              ordinal INTEGER NOT NULL,
              filename TEXT NOT NULL,
              path TEXT NOT NULL,
              sha256 TEXT NOT NULL,
              byte_size INTEGER NOT NULL,
              width INTEGER,
              height INTEGER,
              captured_at_ms INTEGER,
              image_blob BLOB,
              UNIQUE(attempt_id, ordinal),
              FOREIGN KEY(attempt_id) REFERENCES attempts(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_screenshots_attempt ON screenshots(attempt_id);
            """
        )
        self.conn.commit()

    def upsert_run(self, *, run_id: str, run_root: Path, config: dict[str, Any]) -> None:
        now_ms = _now_ms()
        self.conn.execute(
            """
            INSERT INTO runs(
              run_id, run_root, status, created_at_ms, config_json, attempt_count, pass_count
            ) VALUES(?, ?, 'running', ?, ?, 0, 0)
            ON CONFLICT(run_id) DO UPDATE SET
              run_root=excluded.run_root,
              status='running',
              config_json=excluded.config_json
            """,
            (
                run_id,
                str(run_root.resolve()),
                now_ms,
                json.dumps(config, ensure_ascii=False),
            ),
        )
        self.conn.commit()

    def ingest_attempt(
        self,
        *,
        run_id: str,
        provider: str,
        task_id: str,
        attempt_index: int,
        attempt_dir: Path,
        result: AttemptResult,
    ) -> None:
        meta_path = attempt_dir / "meta.json"
        outcome_path = attempt_dir / "outcome.json"
        prompt_path = attempt_dir / "prompt.txt"
        system_prompt_path = attempt_dir / "system_prompt.txt"
        log_path = attempt_dir / "log.json"
        score_path = attempt_dir / "score.json"
        trajectory_path = attempt_dir / "trajectory.json"
        screenshots_dir = attempt_dir / "screenshots"

        meta_json = _read_text(meta_path)
        outcome_json = _read_text(outcome_path)
        prompt_text = _read_text(prompt_path)
        system_prompt_text = _read_text(system_prompt_path)
        log_json = _read_text(log_path)
        score_json = _read_text(score_path)
        trajectory_json = _read_text(trajectory_path)

        meta = _read_json(meta_path)
        outcome = _read_json(outcome_path)

        started_at_ms = int(meta.get("started_at", 0) or 0) or None
        ended_at_ms = int(outcome.get("ended_at", 0) or 0) or None
        usage = result.usage or {}
        cost = result.cost_estimate or {}
        now_ms = _now_ms()

        self.conn.execute(
            """
            INSERT INTO attempts(
              run_id, provider, task_id, attempt_index, attempt_dir, model,
              started_at_ms, ended_at_ms, elapsed_s, turns, stop_reason, error, passed,
              final_score, base_score, max_score, efficiency, input_tokens, output_tokens,
              estimated_cost_usd, log_session_id, meta_json, outcome_json, prompt_text,
              system_prompt_text, log_json, score_json, trajectory_json,
              created_at_ms, updated_at_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id, provider, task_id, attempt_index) DO UPDATE SET
              attempt_dir=excluded.attempt_dir,
              model=excluded.model,
              started_at_ms=excluded.started_at_ms,
              ended_at_ms=excluded.ended_at_ms,
              elapsed_s=excluded.elapsed_s,
              turns=excluded.turns,
              stop_reason=excluded.stop_reason,
              error=excluded.error,
              passed=excluded.passed,
              final_score=excluded.final_score,
              base_score=excluded.base_score,
              max_score=excluded.max_score,
              efficiency=excluded.efficiency,
              input_tokens=excluded.input_tokens,
              output_tokens=excluded.output_tokens,
              estimated_cost_usd=excluded.estimated_cost_usd,
              log_session_id=excluded.log_session_id,
              meta_json=excluded.meta_json,
              outcome_json=excluded.outcome_json,
              prompt_text=excluded.prompt_text,
              system_prompt_text=excluded.system_prompt_text,
              log_json=excluded.log_json,
              score_json=excluded.score_json,
              trajectory_json=excluded.trajectory_json,
              updated_at_ms=excluded.updated_at_ms
            """,
            (
                run_id,
                provider,
                task_id,
                attempt_index,
                str(attempt_dir.resolve()),
                result.model,
                started_at_ms,
                ended_at_ms,
                float(result.elapsed_s),
                int(result.turns),
                result.stop_reason,
                result.error,
                1 if result.passed else 0,
                float(result.final_score),
                float(result.base_score),
                float(result.max_score),
                float(result.efficiency),
                int(usage.get("input_tokens", 0) or 0),
                int(usage.get("output_tokens", 0) or 0),
                float(cost.get("total_usd", 0.0) or 0.0),
                outcome.get("log_session_id"),
                meta_json,
                outcome_json,
                prompt_text,
                system_prompt_text,
                log_json,
                score_json,
                trajectory_json,
                now_ms,
                now_ms,
            ),
        )
        row = self.conn.execute(
            """
            SELECT id FROM attempts
            WHERE run_id=? AND provider=? AND task_id=? AND attempt_index=?
            """,
            (run_id, provider, task_id, attempt_index),
        ).fetchone()
        if row is None:
            self.conn.commit()
            return
        attempt_id = int(row[0])

        self.conn.execute("DELETE FROM screenshots WHERE attempt_id=?", (attempt_id,))
        if screenshots_dir.is_dir():
            screenshot_files = sorted(
                [p for p in screenshots_dir.iterdir() if p.is_file() and p.suffix.lower() == ".png"]
            )
            for ordinal, shot_path in enumerate(screenshot_files):
                blob = shot_path.read_bytes()
                width, height = _png_dimensions(blob)
                stat = shot_path.stat()
                self.conn.execute(
                    """
                    INSERT INTO screenshots(
                      attempt_id, ordinal, filename, path, sha256, byte_size,
                      width, height, captured_at_ms, image_blob
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        attempt_id,
                        ordinal,
                        shot_path.name,
                        str(shot_path.resolve()),
                        _sha256_hex(blob),
                        len(blob),
                        width,
                        height,
                        int(stat.st_mtime * 1000),
                        blob if self.store_screenshot_bytes else None,
                    ),
                )

        self.conn.commit()

    def finalize_run(self, *, run_id: str, attempts: list[AttemptResult], extra: dict[str, Any]) -> None:
        ended_at_ms = _now_ms()
        attempt_count = len(attempts)
        pass_count = sum(1 for a in attempts if a.passed)
        summary = {
            "attempt_count": attempt_count,
            "pass_count": pass_count,
            "pass_rate": (pass_count / attempt_count) if attempt_count else 0.0,
            "extra": extra,
            "attempts": [asdict(a) for a in attempts],
        }
        self.conn.execute(
            """
            UPDATE runs
            SET status='completed',
                ended_at_ms=?,
                attempt_count=?,
                pass_count=?,
                summary_json=?
            WHERE run_id=?
            """,
            (
                ended_at_ms,
                attempt_count,
                pass_count,
                json.dumps(summary, ensure_ascii=False),
                run_id,
            ),
        )
        self.conn.commit()


class PostgresS3TraceStore:
    def __init__(
        self,
        *,
        dsn: str,
        s3_bucket: str,
        s3_prefix: str = "cua-traces",
        aws_region: str | None = None,
        s3_endpoint_url: str | None = None,
    ) -> None:
        try:
            import psycopg  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Missing dependency: psycopg. Install requirements.txt") from exc
        try:
            import boto3  # type: ignore
        except ImportError as exc:
            raise RuntimeError("Missing dependency: boto3. Install requirements.txt") from exc

        self._psycopg = psycopg
        self.dsn = dsn
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix.strip("/") or "cua-traces"
        self.conn = psycopg.connect(dsn)
        self.conn.autocommit = False
        self.s3 = boto3.client("s3", region_name=aws_region, endpoint_url=s3_endpoint_url)
        self._init_schema()

    def close(self) -> None:
        self.conn.close()

    def _init_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                  run_id TEXT PRIMARY KEY,
                  run_root TEXT NOT NULL,
                  status TEXT NOT NULL,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                  ended_at TIMESTAMPTZ,
                  config_json JSONB NOT NULL,
                  summary_json JSONB,
                  attempt_count INTEGER NOT NULL DEFAULT 0,
                  pass_count INTEGER NOT NULL DEFAULT 0
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS attempts (
                  id BIGSERIAL PRIMARY KEY,
                  run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
                  provider TEXT NOT NULL,
                  task_id TEXT NOT NULL,
                  attempt_index INTEGER NOT NULL,
                  attempt_dir TEXT NOT NULL,
                  model TEXT,
                  started_at TIMESTAMPTZ,
                  ended_at TIMESTAMPTZ,
                  elapsed_s DOUBLE PRECISION,
                  turns INTEGER,
                  stop_reason TEXT,
                  error TEXT,
                  passed BOOLEAN NOT NULL,
                  final_score DOUBLE PRECISION,
                  base_score DOUBLE PRECISION,
                  max_score DOUBLE PRECISION,
                  efficiency DOUBLE PRECISION,
                  input_tokens INTEGER,
                  output_tokens INTEGER,
                  estimated_cost_usd DOUBLE PRECISION,
                  log_session_id TEXT,
                  meta_json JSONB,
                  outcome_json JSONB,
                  prompt_text TEXT,
                  system_prompt_text TEXT,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                  UNIQUE(run_id, provider, task_id, attempt_index)
                );
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_attempts_run_id ON attempts(run_id);
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_attempts_provider_task ON attempts(provider, task_id);
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                  id BIGSERIAL PRIMARY KEY,
                  attempt_id BIGINT NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
                  artifact_kind TEXT NOT NULL,
                  ordinal INTEGER,
                  filename TEXT NOT NULL,
                  relative_path TEXT NOT NULL,
                  storage_uri TEXT NOT NULL,
                  sha256 TEXT NOT NULL,
                  byte_size BIGINT NOT NULL,
                  content_type TEXT NOT NULL,
                  width INTEGER,
                  height INTEGER,
                  captured_at TIMESTAMPTZ,
                  metadata_json JSONB,
                  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                  UNIQUE(attempt_id, artifact_kind, filename)
                );
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_artifacts_attempt_id ON artifacts(attempt_id);
                """
            )
        self.conn.commit()

    def _upload_artifact(self, *, run_id: str, provider: str, task_id: str, attempt_index: int, path: Path, kind: str) -> dict[str, Any]:
        payload = path.read_bytes()
        sha = _sha256_hex(payload)
        key = (
            f"{self.s3_prefix}/run_id={run_id}/provider={provider}/task={task_id}/attempt={attempt_index}/"
            f"{kind}/{path.name}"
        )
        content_type = _guess_content_type(path)
        self.s3.put_object(
            Bucket=self.s3_bucket,
            Key=key,
            Body=payload,
            ContentType=content_type,
            Metadata={
                "run_id": run_id,
                "provider": provider,
                "task_id": task_id,
                "attempt_index": str(attempt_index),
                "artifact_kind": kind,
                "sha256": sha,
            },
        )
        width, height = (None, None)
        if content_type == "image/png":
            width, height = _png_dimensions(payload)
        stat = path.stat()
        return {
            "filename": path.name,
            "relative_path": str(path),
            "storage_uri": f"s3://{self.s3_bucket}/{key}",
            "sha256": sha,
            "byte_size": len(payload),
            "content_type": content_type,
            "width": width,
            "height": height,
            "captured_at": _ms_to_dt(int(stat.st_mtime * 1000)),
        }

    def upsert_run(self, *, run_id: str, run_root: Path, config: dict[str, Any]) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO runs(run_id, run_root, status, config_json, attempt_count, pass_count)
                VALUES (%s, %s, 'running', %s::jsonb, 0, 0)
                ON CONFLICT(run_id) DO UPDATE SET
                  run_root = EXCLUDED.run_root,
                  status = 'running',
                  config_json = EXCLUDED.config_json
                """,
                (run_id, str(run_root.resolve()), json.dumps(config, ensure_ascii=False)),
            )
        self.conn.commit()

    def ingest_attempt(
        self,
        *,
        run_id: str,
        provider: str,
        task_id: str,
        attempt_index: int,
        attempt_dir: Path,
        result: AttemptResult,
    ) -> None:
        meta_path = attempt_dir / "meta.json"
        outcome_path = attempt_dir / "outcome.json"
        prompt_path = attempt_dir / "prompt.txt"
        system_prompt_path = attempt_dir / "system_prompt.txt"
        log_path = attempt_dir / "log.json"
        score_path = attempt_dir / "score.json"
        trajectory_path = attempt_dir / "trajectory.json"
        trajectory_jsonl_path = attempt_dir / "trajectory.jsonl"
        screenshots_dir = attempt_dir / "screenshots"

        meta_obj = _read_json_any(meta_path)
        outcome_obj = _read_json_any(outcome_path)
        started_at_ms = None
        ended_at_ms = None
        if isinstance(meta_obj, dict):
            started_at_ms = int(meta_obj.get("started_at", 0) or 0) or None
        if isinstance(outcome_obj, dict):
            ended_at_ms = int(outcome_obj.get("ended_at", 0) or 0) or None
        usage = result.usage or {}
        cost = result.cost_estimate or {}

        prompt_text = _read_text(prompt_path)
        system_prompt_text = _read_text(system_prompt_path)

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO attempts(
                  run_id, provider, task_id, attempt_index, attempt_dir, model,
                  started_at, ended_at, elapsed_s, turns, stop_reason, error, passed,
                  final_score, base_score, max_score, efficiency,
                  input_tokens, output_tokens, estimated_cost_usd, log_session_id,
                  meta_json, outcome_json, prompt_text, system_prompt_text, updated_at
                ) VALUES (
                  %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s, %s, %s, %s,
                  %s, %s, %s, %s,
                  %s, %s, %s, %s,
                  %s::jsonb, %s::jsonb, %s, %s, now()
                )
                ON CONFLICT(run_id, provider, task_id, attempt_index) DO UPDATE SET
                  attempt_dir = EXCLUDED.attempt_dir,
                  model = EXCLUDED.model,
                  started_at = EXCLUDED.started_at,
                  ended_at = EXCLUDED.ended_at,
                  elapsed_s = EXCLUDED.elapsed_s,
                  turns = EXCLUDED.turns,
                  stop_reason = EXCLUDED.stop_reason,
                  error = EXCLUDED.error,
                  passed = EXCLUDED.passed,
                  final_score = EXCLUDED.final_score,
                  base_score = EXCLUDED.base_score,
                  max_score = EXCLUDED.max_score,
                  efficiency = EXCLUDED.efficiency,
                  input_tokens = EXCLUDED.input_tokens,
                  output_tokens = EXCLUDED.output_tokens,
                  estimated_cost_usd = EXCLUDED.estimated_cost_usd,
                  log_session_id = EXCLUDED.log_session_id,
                  meta_json = EXCLUDED.meta_json,
                  outcome_json = EXCLUDED.outcome_json,
                  prompt_text = EXCLUDED.prompt_text,
                  system_prompt_text = EXCLUDED.system_prompt_text,
                  updated_at = now()
                RETURNING id
                """,
                (
                    run_id,
                    provider,
                    task_id,
                    attempt_index,
                    str(attempt_dir.resolve()),
                    result.model,
                    _ms_to_dt(started_at_ms),
                    _ms_to_dt(ended_at_ms),
                    float(result.elapsed_s),
                    int(result.turns),
                    result.stop_reason,
                    result.error,
                    bool(result.passed),
                    float(result.final_score),
                    float(result.base_score),
                    float(result.max_score),
                    float(result.efficiency),
                    int(usage.get("input_tokens", 0) or 0),
                    int(usage.get("output_tokens", 0) or 0),
                    float(cost.get("total_usd", 0.0) or 0.0),
                    (outcome_obj.get("log_session_id") if isinstance(outcome_obj, dict) else None),
                    json.dumps(meta_obj if meta_obj is not None else {}, ensure_ascii=False),
                    json.dumps(outcome_obj if outcome_obj is not None else {}, ensure_ascii=False),
                    prompt_text,
                    system_prompt_text,
                ),
            )
            row = cur.fetchone()
            if row is None:
                self.conn.commit()
                return
            attempt_id = int(row[0])
            cur.execute("DELETE FROM artifacts WHERE attempt_id = %s", (attempt_id,))

            artifacts: list[tuple[str, Path, int | None]] = []
            if meta_path.is_file():
                artifacts.append(("meta_json", meta_path, None))
            if outcome_path.is_file():
                artifacts.append(("outcome_json", outcome_path, None))
            if prompt_path.is_file():
                artifacts.append(("prompt_text", prompt_path, None))
            if system_prompt_path.is_file():
                artifacts.append(("system_prompt_text", system_prompt_path, None))
            if log_path.is_file():
                artifacts.append(("log_json", log_path, None))
            if score_path.is_file():
                artifacts.append(("score_json", score_path, None))
            if trajectory_path.is_file():
                artifacts.append(("trajectory_json", trajectory_path, None))
            if trajectory_jsonl_path.is_file():
                artifacts.append(("trajectory_jsonl", trajectory_jsonl_path, None))
            if screenshots_dir.is_dir():
                screenshots = sorted([p for p in screenshots_dir.iterdir() if p.is_file() and p.suffix.lower() == ".png"])
                for idx, shot in enumerate(screenshots):
                    artifacts.append(("screenshot", shot, idx))

            for kind, art_path, ordinal in artifacts:
                uploaded = self._upload_artifact(
                    run_id=run_id,
                    provider=provider,
                    task_id=task_id,
                    attempt_index=attempt_index,
                    path=art_path,
                    kind=kind,
                )
                cur.execute(
                    """
                    INSERT INTO artifacts(
                      attempt_id, artifact_kind, ordinal, filename, relative_path,
                      storage_uri, sha256, byte_size, content_type, width, height,
                      captured_at, metadata_json
                    ) VALUES (
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb
                    )
                    """,
                    (
                        attempt_id,
                        kind,
                        ordinal,
                        uploaded["filename"],
                        uploaded["relative_path"],
                        uploaded["storage_uri"],
                        uploaded["sha256"],
                        int(uploaded["byte_size"]),
                        uploaded["content_type"],
                        uploaded["width"],
                        uploaded["height"],
                        uploaded["captured_at"],
                        json.dumps({}, ensure_ascii=False),
                    ),
                )

        self.conn.commit()

    def finalize_run(self, *, run_id: str, attempts: list[AttemptResult], extra: dict[str, Any]) -> None:
        attempt_count = len(attempts)
        pass_count = sum(1 for a in attempts if a.passed)
        summary = {
            "attempt_count": attempt_count,
            "pass_count": pass_count,
            "pass_rate": (pass_count / attempt_count) if attempt_count else 0.0,
            "extra": extra,
            "attempts": [asdict(a) for a in attempts],
        }
        with self.conn.cursor() as cur:
            cur.execute(
                """
                UPDATE runs
                SET status = 'completed',
                    ended_at = now(),
                    attempt_count = %s,
                    pass_count = %s,
                    summary_json = %s::jsonb
                WHERE run_id = %s
                """,
                (attempt_count, pass_count, json.dumps(summary, ensure_ascii=False), run_id),
            )
        self.conn.commit()


def create_trace_store(
    *,
    backend: str,
    sqlite_path: Path,
    sqlite_store_screenshot_bytes: bool,
    postgres_dsn: str | None,
    s3_bucket: str | None,
    s3_prefix: str,
    aws_region: str | None,
    s3_endpoint_url: str | None,
) -> TraceStore:
    if backend == "sqlite":
        return SqliteTraceStore(sqlite_path, store_screenshot_bytes=sqlite_store_screenshot_bytes)
    if backend == "postgres-s3":
        if not postgres_dsn:
            raise RuntimeError("trace backend postgres-s3 requires --trace-postgres-dsn or CUA_TRACE_POSTGRES_DSN")
        if not s3_bucket:
            raise RuntimeError("trace backend postgres-s3 requires --trace-s3-bucket or CUA_TRACE_S3_BUCKET")
        return PostgresS3TraceStore(
            dsn=postgres_dsn,
            s3_bucket=s3_bucket,
            s3_prefix=s3_prefix,
            aws_region=aws_region,
            s3_endpoint_url=s3_endpoint_url,
        )
    raise RuntimeError(f"Unsupported trace backend: {backend}")
