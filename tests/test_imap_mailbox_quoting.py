"""Regression coverage for IMAP mailbox names that contain spaces.

imaplib does not quote mailbox arguments for SELECT/APPEND/MOVE/COPY, so callers
must quote names such as "[Gmail]/All Mail" or "Sent Items" themselves.
"""

from pathlib import Path

import pytest

pytest.importorskip("mcp")

import mcp_servers.email_server as es


class FakeListConn:
    def __init__(self):
        self.calls = []

    def select(self, folder, readonly=False):
        self.calls.append(("select", folder, readonly))
        return "OK", []

    def uid(self, command, *args):
        self.calls.append(("uid", command, *args))
        if command == "SEARCH":
            return "OK", [b""]
        return "OK", []

    def logout(self):
        self.calls.append(("logout",))


def test_mcp_list_emails_quotes_spaced_folder_on_select(monkeypatch):
    conn = FakeListConn()
    monkeypatch.setattr(es, "_imap_connect", lambda account=None: conn)

    assert es._list_emails(folder="Sent Items") == []

    assert conn.calls[0] == ("select", '"Sent Items"', True)


def test_mcp_quote_helper_handles_spaced_and_quoted_mailboxes():
    assert es._q("Sent Items") == '"Sent Items"'
    assert es._q('[Gmail]/All Mail') == '"[Gmail]/All Mail"'
    assert es._q('Label "Needs Reply"') == '"Label \\"Needs Reply\\""'


def test_known_imap_mailbox_call_sites_are_quoted():
    mcp = Path("mcp_servers/email_server.py").read_text()
    assert "conn.select(folder" not in mcp
    assert "conn.select(source_folder" not in mcp
    assert "imap.append(sent_folder" not in mcp

    pollers = Path("routes/email_pollers.py").read_text()
    assert "conn.select(sent_name" not in pollers
    assert "imap.append(sent_folder" not in pollers

    document_routes = Path("routes/document_routes.py").read_text()
    assert "conn.select(doc.source_email_folder" not in document_routes
