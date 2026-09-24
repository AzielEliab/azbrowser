"""Human CLI and local chrome. Machine JSON stays available with --json."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout

import pytest

from azbrowser.cli import main
from azbrowser.engine import OPS
from azbrowser.meta import HOST, LIMITATION, __version__
from azbrowser.ui import _chrome, bind_message


def test_bare_command_welcomes():
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main([])
    text = buf.getvalue()
    assert code == 0
    assert f"AZBrowser {__version__}" in text
    assert "Aziel Eliab" in text
    assert "azbrowser ui" in text
    assert "http://127.0.0.1:8878/" in text
    assert "THIS IS NOT" not in text
    assert not text.lstrip().startswith("{")


def test_help_is_short():
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["--help"])
    text = buf.getvalue()
    assert code == 0
    assert "azbrowser ui" in text
    assert "Advanced" in text
    assert "Examples:" in text
    assert "--json" in text
    assert "changelog" not in text.lower()
    assert "THIS IS NOT" not in text


def test_unknown_command_names_the_next_step():
    err = io.StringIO()
    with redirect_stderr(err):
        with pytest.raises(SystemExit) as caught:
            main(["bogus"])
    assert caught.value.code == 2
    text = err.getvalue()
    assert 'Unknown command "bogus"' in text
    assert "azbrowser ui" in text
    assert "azbrowser --help" in text


def test_ui_help_stays_local():
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["ui", "--help"])
    assert code == 0
    assert "Open http://127.0.0.1:8878/" in buf.getvalue()


def test_bad_payload_and_missing_file():
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["call", "home", "--payload", "not-json"])
    assert code == 2
    assert "not JSON" in err.getvalue()
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(["airlock", "--file", "no-such-file-azbrowser.txt"])
    assert code == 2
    assert "Could not read" in err.getvalue()


def test_navigate_without_address():
    err = io.StringIO()
    with redirect_stderr(err):
        with pytest.raises(SystemExit) as caught:
            main(["navigate"])
    assert caught.value.code == 2
    assert "address" in err.getvalue().lower()
    assert "azbrowser navigate" in err.getvalue()


def test_human_health_is_text_and_json_flag_stays_machine(tmp_path):
    ledger = tmp_path / "receipts.jsonl"
    human = io.StringIO()
    with redirect_stdout(human):
        code = main(["--ledger", str(ledger), "health"])
    assert code == 0
    assert not human.getvalue().lstrip().startswith("{")
    assert "AZBrowser" in human.getvalue()

    machine = io.StringIO()
    with redirect_stdout(machine):
        code = main(["--ledger", str(ledger), "--json", "health"])
    assert code == 0
    payload = json.loads(machine.getvalue())
    assert payload["ok"] is True
    assert payload["version"] == __version__
    assert payload["author"] == "Aziel Eliab"
    assert payload["ops"] == list(OPS)
    assert payload["limitation"] == LIMITATION


def test_doctor_json_and_plain(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    plain = io.StringIO()
    with redirect_stdout(plain):
        code = main(["doctor"])
    assert code == 0
    assert "ok   health" in plain.getvalue()
    assert "THIS IS NOT" not in plain.getvalue()
    assert "No receipt = no action." in plain.getvalue()

    raw = io.StringIO()
    with redirect_stdout(raw):
        code = main(["doctor", "--json"])
    assert code == 0
    payload = json.loads(raw.getvalue())
    assert payload["ok"] is True
    assert payload["author"] == "Aziel Eliab"
    assert any(row["name"] == "lamb_lens" and row["ok"] for row in payload["checks"])


def test_bind_message_and_chrome():
    assert bind_message("127.0.0.1", 8878) == "Open http://127.0.0.1:8878/"
    html = _chrome()
    assert 'id="omnibox"' in html
    assert 'id="go"' in html
    assert 'id="startGo"' in html
    assert 'id="tabs"' in html
    assert ">Advanced<" in html
    assert 'id="sidePanel" hidden' in html
    assert 'id="designBtn"' in html
    assert "#c9a227" in html
    assert ":focus-visible" in html
    assert "max-width: 480px" in html
    assert "Search or enter a .aziel name or web address" in html
    assert "Live Nodes" in html
    assert "Mesh off" in html
    assert HOST in html
    assert LIMITATION not in html
    assert ", ".join(OPS) not in html
    assert "THIS IS NOT" not in html
    assert "QNM-BUILD-1.0" not in html
    assert "QNS-CD-1.0" not in html
