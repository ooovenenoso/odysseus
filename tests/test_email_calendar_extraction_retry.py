import ast
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "routes" / "email_pollers.py"
SOURCE_TEXT = MODULE_PATH.read_text(encoding="utf-8")


def _load_record_helper():
    tree = ast.parse(SOURCE_TEXT)
    helper = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_record_calendar_extraction"
    )
    ns = {
        "SCHEDULED_DB": "",
        "datetime": datetime,
        "logger": logging.getLogger("test_email_calendar_extraction_retry"),
    }
    ast.fix_missing_locations(helper)
    exec(compile(ast.Module(body=[helper], type_ignores=[]), str(MODULE_PATH), "exec"), ns)
    return ns


def test_record_calendar_extraction_persists_success(tmp_path):
    ns = _load_record_helper()
    db_path = tmp_path / "scheduled.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE email_calendar_extractions ("
        "message_id TEXT PRIMARY KEY, uid TEXT, events_created INTEGER, created_at TEXT)"
    )
    conn.commit()
    conn.close()
    ns["SCHEDULED_DB"] = str(db_path)

    existing = set()
    ns["_record_calendar_extraction"]("msg-1", b"42", 2, existing)

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT message_id, uid, events_created FROM email_calendar_extractions"
    ).fetchone()
    conn.close()

    assert row == ("msg-1", "42", 2)
    assert "msg-1" in existing


def test_calendar_extraction_cache_is_after_llm_success_path():
    source = ast.parse(SOURCE_TEXT)

    for node in ast.walk(source):
        if not isinstance(node, ast.Try):
            continue
        handler_text = "\n".join(
            ast.get_source_segment(SOURCE_TEXT, h) or "" for h in node.handlers
        )
        if "Meeting extraction LLM call failed" not in handler_text:
            continue

        else_text = "\n".join(
            ast.get_source_segment(SOURCE_TEXT, stmt) or "" for stmt in node.orelse
        )
        assert "_record_calendar_extraction" not in handler_text
        assert "_record_calendar_extraction" in else_text
        return

    raise AssertionError("calendar extraction LLM try/except block not found")
