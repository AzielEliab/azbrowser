"""Ordered FED-MESH name-read. Dead relays are skipped. .aziel is not DNS.

Mocks only. No public Worker, no LAN peer, no ICANN lookup.
"""

from __future__ import annotations

import argparse
import json
import socket
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse

from azbrowser.cli import _engine
from azbrowser.engine import Engine
from azbrowser.meshledger import MeshDirectory, mesh_relay_bases, read_public_relay
from azbrowser.meta import MESH_RELAYS_ENV, RUNTIME
from azbrowser.receipts import Ledger
from azbrowser.ui import ENGINE
from tests.test_mesh_browser import signed_record

L0 = RUNTIME.rstrip("/")
ROW = {
    "name": "shelf.aziel",
    "owner": "shelf",
    "status": "pending",
    "statement_hash": "aa" * 32,
}


class _Body:
    def __init__(self, doc: dict, status: int = 200) -> None:
        self.status = status
        self._raw = json.dumps(doc).encode("utf-8")

    def read(self, _n: int = -1) -> bytes:
        return self._raw

    def __enter__(self) -> "_Body":
        return self

    def __exit__(self, *_args: object) -> bool:
        return False


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def test_unset_list_is_l0_only(monkeypatch):
    monkeypatch.delenv(MESH_RELAYS_ENV, raising=False)
    assert MESH_RELAYS_ENV == "AZBROWSER_MESH_RELAYS"
    assert mesh_relay_bases() == [L0]
    assert mesh_relay_bases("") == [L0]


def test_operator_list_keeps_order_dedupes_and_appends_l0():
    bases = mesh_relay_bases(
        "http://127.0.0.1:8780/v1/mesh/relay, http://127.0.0.1:8780/v1/mesh/relay\nhttp://10.0.0.8:8783"
    )
    assert bases == ["http://127.0.0.1:8780", "http://10.0.0.8:8783", L0]
    again = mesh_relay_bases(f"{L0}/v1/mesh/relay,http://127.0.0.1:8780/v1/mesh/relay")
    assert again == [L0, "http://127.0.0.1:8780"]


def test_aziel_relay_host_is_dropped():
    bases = mesh_relay_bases("https://library.aziel/v1/mesh/relay,http://127.0.0.1:8783/v1/mesh/relay")
    assert bases[0] == "http://127.0.0.1:8783"
    assert bases[-1] == L0
    assert all(not _host(base).endswith(".aziel") for base in bases)


def test_dead_relay_is_skipped_and_the_next_answers(monkeypatch):
    real = socket.getaddrinfo

    def guarded(host, *args, **kwargs):
        if str(host).lower().endswith(".aziel"):
            raise AssertionError(host)
        return real(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", guarded)
    calls: list[str] = []

    def opener(req, timeout=2.5):
        url = req.full_url
        calls.append(url)
        host = _host(url)
        assert not host.endswith(".aziel")
        if host == "127.0.0.1" and urlparse(url).port == 8780:
            raise TimeoutError("relay down")
        if "vibelock.workers.dev" in host:
            raise URLError("cf down")
        if urlparse(url).port == 8783:
            return _Body({"record": ROW})
        raise URLError("unexpected " + url)

    bases = mesh_relay_bases("http://127.0.0.1:8780/v1/mesh/relay,http://127.0.0.1:8783/v1/mesh/relay")
    found = read_public_relay("shelf.aziel", bases=bases, opener=opener)
    assert found["found"] is True
    assert found["row"]["name"] == "shelf.aziel"
    assert found["dns"] is False
    assert found["icann"] is False
    assert found["aznet_replaces_internet"] is False
    assert found["public_l1_live"] is False
    assert found["l1_configured"] is True
    assert "l1_live" not in found
    assert found["l0_fallback"] is False
    assert ":8783" in found["endpoint"]
    assert "name=shelf.aziel" in found["endpoint"]
    assert _host(found["endpoint"]) == "127.0.0.1"
    assert any(":8780" in url for url in found["skipped"])
    assert all("vibelock" not in url for url in calls)

    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    eng.mesh.relay_read = lambda name: read_public_relay(name, bases=bases, opener=opener)
    opened = eng.navigate({"url": "shelf.aziel"})
    assert opened["ok"] is True
    assert opened["name_status"] == "PENDING"
    assert opened["dns"] is False
    assert opened["icann"] is False
    assert opened["source"] == "fed-mesh-relay"
    assert opened["public_l1_live"] is False
    assert opened["aznet_replaces_internet"] is False
    assert "l1_live" not in opened
    assert ":8783" in opened["relay_endpoint"]


def test_clean_miss_continues_and_http_500_is_dead():
    calls: list[str] = []

    def opener(req, timeout=2.5):
        url = req.full_url
        calls.append(url)
        if ":8780" in url:
            return _Body({"ok": False, "code": "FED-MESH-NO-NAME"})
        if ":8783" in url:
            raise HTTPError(url, 503, "down", hdrs=None, fp=None)
        return _Body({"record": ROW})

    bases = ["http://127.0.0.1:8780", "http://127.0.0.1:8783", L0]
    found = read_public_relay("shelf.aziel", bases=bases, opener=opener)
    assert found["found"] is True
    assert found["l0_fallback"] is True
    assert _host(found["endpoint"]) == "aziel-runtime.vibelock.workers.dev"
    assert len(calls) == 3
    assert found["public_l1_live"] is False
    assert found["aznet_replaces_internet"] is False


def test_isolation_stops_the_list():
    calls: list[str] = []

    def opener(req, timeout=2.5):
        calls.append(req.full_url)
        return _Body({"ok": False, "code": "FED-MESH-ISOLATED", "reason": "policy", "evidence_hash": "ab" * 32})

    found = read_public_relay(
        "shelf.aziel",
        bases=["http://127.0.0.1:8780", "http://127.0.0.1:8783"],
        opener=opener,
    )
    assert found["isolated"] is True
    assert len(calls) == 1
    assert found["dns"] is False


def test_every_relay_dead_refuses_without_dns():
    def opener(req, timeout=2.5):
        assert not _host(req.full_url).endswith(".aziel")
        raise URLError("down")

    bases = mesh_relay_bases("http://127.0.0.1:8780/v1/mesh/relay")
    missed = read_public_relay("missing-name.aziel", bases=bases, opener=opener)
    assert missed["found"] is False
    assert missed["unread"] is True
    assert missed["dns"] is False
    assert missed["public_l1_live"] is False
    assert missed["aznet_replaces_internet"] is False
    assert missed["l1_configured"] is True
    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    eng.mesh.relay_read = lambda name: read_public_relay(name, bases=bases, opener=opener)
    opened = eng.navigate({"url": "missing-name.aziel"})
    assert opened["code"] == "FG-GATE-REFUSE"
    assert opened["reason"] == "name_not_in_ledger"
    assert opened["dns"] is False
    assert opened["icann"] is False
    assert opened["relay_unread"] is True
    assert opened["public_l1_live"] is False
    assert opened["aznet_replaces_internet"] is False
    assert "l1_live" not in opened
    assert all(not _host(url).endswith(".aziel") for url in opened["relays_tried"])


def test_unconfigured_read_is_not_painted_live():
    calls: list[str] = []

    def opener(req, timeout=2.5):
        calls.append(req.full_url)
        return _Body({"ok": False, "code": "FED-MESH-NO-NAME"})

    missed = read_public_relay("library.aziel", bases=mesh_relay_bases(""), opener=opener)
    assert calls == [L0 + "/v1/mesh/relay/name?name=library.aziel"]
    assert missed["found"] is False
    assert missed["unread"] is False
    assert missed["l1_configured"] is False
    assert missed["public_l1_live"] is False
    assert missed["l0_fallback"] is False
    assert missed["aznet_replaces_internet"] is False
    assert "l1_live" not in missed


def test_local_ledger_wins_when_relays_are_dead():
    record = signed_record()
    calls: list[str] = []

    def opener(req, timeout=2.5):
        calls.append(req.full_url)
        raise URLError("cf down")

    bases = mesh_relay_bases("http://127.0.0.1:8780/v1/mesh/relay")
    eng = Engine(Ledger(), mesh=MeshDirectory([record], http=False))
    eng.mesh.relay_read = lambda name: read_public_relay(name, bases=bases, opener=opener)
    out = eng.navigate({"url": "library.aziel"})
    assert out["ok"] is True
    assert out["owner_handle"] == "library"
    assert out.get("dns") is not True
    assert out["icann"] is False
    assert out.get("reason") != "name_not_in_ledger"
    assert out["ledger_source"] == "local-ledger"
    assert out["public_l1_live"] is False
    assert out["aznet_replaces_internet"] is False
    assert calls
    assert all(not _host(url).endswith(".aziel") for url in calls)


def test_local_qnm_resolves_when_the_runtime_is_unread():
    record = signed_record()
    posts: list[str] = []

    def post(url, body, timeout):
        posts.append(str(url))
        if str(url).endswith("/local/resolve"):
            return record
        if str(url).endswith("/local/connect"):
            return {"ok": True, "connected": False, "mode": "direct", "peer": "library"}
        return {"ok": False}

    directory = MeshDirectory([], http=True, post=post, qnm_url="http://127.0.0.1:8891")
    eng = Engine(Ledger(), mesh=directory)
    eng.mesh.relay_read = lambda name: {
        "found": False,
        "unread": True,
        "dns": False,
        "tried": [L0 + "/v1/mesh/relay/name?name=" + name],
        "skipped": [L0 + "/v1/mesh/relay/name?name=" + name],
        "l1_configured": False,
        "aznet_replaces_internet": False,
    }
    out = eng.navigate({"url": "library.aziel"})
    assert out["ok"] is True
    assert out["owner_handle"] == "library"
    assert out.get("dns") is not True
    assert out["icann"] is False
    assert out.get("reason") != "name_not_in_ledger"
    assert any(url.endswith("/local/resolve") for url in posts)
    assert out["ledger_source"] == "local-ledger"
    assert out["public_l1_live"] is False


def test_cap7_does_not_walk_the_relay_list():
    calls: list[str] = []
    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    eng.mesh.relay_read = lambda name: calls.append(name)
    out = eng.navigate({"url": "azgrid.az"})
    assert out["plane"] == "cap7"
    assert out["icann"] is False
    assert calls == []


def test_shells_use_the_reader_and_doctor_engine_does_not():
    assert ENGINE.mesh.relay_read is read_public_relay
    args = argparse.Namespace(ledger="/tmp/azbrowser-relay-test-receipts.jsonl")
    assert _engine(args).mesh.relay_read is read_public_relay
    assert Engine(Ledger()).mesh.relay_read is None
