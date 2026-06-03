"""Regression tests for MCP email archive mailbox quoting.

Gmail folder names such as [Gmail]/All Mail contain spaces. The GUI email
routes quote destination mailboxes before UID MOVE/COPY; the MCP email server
must do the same or Gmail returns BAD "Could not parse command".
"""

import pytest

pytest.importorskip("mcp")

import mcp_servers.email_server as es


class FakeImap:
    def __init__(self):
        self.calls = []

    def select(self, folder, readonly=False):
        self.calls.append(("select", folder, readonly))
        return "OK", []

    def uid(self, command, *args):
        self.calls.append(("uid", command, *args))
        if command == "FETCH":
            return "OK", [b"1 (UID 123)"]
        if command == "MOVE":
            return "OK", []
        return "BAD", []

    def logout(self):
        self.calls.append(("logout",))


def test_move_message_quotes_gmail_archive_folder(monkeypatch):
    conn = FakeImap()
    monkeypatch.setattr(es, "_imap_connect", lambda account=None: conn)
    monkeypatch.setattr(es, "_resolve_folder", lambda conn, dest, role: "[Gmail]/All Mail")

    assert es._move_message("123", "INBOX", "Archive", role="archive") is True

    move_calls = [call for call in conn.calls if call[:2] == ("uid", "MOVE")]
    assert move_calls == [("uid", "MOVE", b"123", '"[Gmail]/All Mail"')]


def test_bulk_move_quotes_gmail_archive_folder(monkeypatch):
    conn = FakeImap()
    monkeypatch.setattr(es, "_imap_connect", lambda account=None: conn)
    monkeypatch.setattr(es, "_resolve_folder", lambda conn, dest, role: "[Gmail]/All Mail")

    assert es._bulk_move(["123", "124"], "INBOX", "Archive", role="archive") == 1

    move_calls = [call for call in conn.calls if call[:2] == ("uid", "MOVE")]
    assert move_calls == [("uid", "MOVE", b"123,124", '"[Gmail]/All Mail"')]
