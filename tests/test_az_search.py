"""AZ Search lists records this shell holds. It does not invent a hit."""

from azbrowser.engine import Engine
from azbrowser.lens import ORDER
from azbrowser.meshledger import MeshDirectory
from azbrowser.receipts import Ledger
from azbrowser.search import ethical_search


def test_plain_miss_is_empty_and_named():
    out = ethical_search("zzzz-not-a-real-name")
    assert out["ok"] is True
    assert out["results"] == []
    assert out["citations"] == []
    assert out["invented"] is False
    assert out["engine"] == "AZ Search"
    assert out["product"] == "AZ Browser"
    assert out["sidenet"] == "AZNet"
    assert out["softwares_card"] is False
    assert out["mode"] == "az_search"
    assert out["lens"]["order"] == list(ORDER)
    assert out["cap7_public_icann"] is False
    assert "index.php?search=" not in str(out)
    assert out["clarity"]["next"]


def test_known_cite_matches_and_is_not_a_synthesized_search_url():
    out = ethical_search("FragGate kernel")
    urls = [hit["url"] for hit in out["results"]]
    assert "https://github.com/AzielEliab/fraggate" in urls
    assert all("index.php?search=" not in url for url in urls)
    assert all(not str(hit["title"]).startswith("Wikipedia search:") for hit in out["results"])


def test_mesh_name_slot_cap7_and_hub_are_real_records():
    records = [{"name": "library.aziel", "handle": "library", "status": "FINAL", "slot": 1}]
    out = ethical_search("library", records=records, handle="library")
    mesh = [hit for hit in out["results"] if hit["source"] == "mesh"]
    assert mesh and mesh[0]["url"] == "library.aziel"
    assert mesh[0]["icann"] is False
    assert any(hit["source"] == "slot" and hit["url"] == "az.azielcorpuslibrary.az" for hit in out["results"])
    booth = ethical_search("azbooth")
    cap = next(hit for hit in booth["results"] if hit["source"] == "cap7")
    assert cap["false_site"] is True
    assert cap["icann"] is False
    assert cap["public_icann"] is False
    assert cap["url"] == "azbooth.az"
    hub = ethical_search("hedidntjump")
    assert any(hit["url"] == "https://www.hedidntjump.com/" and hit["source"] == "hub-cite" for hit in hub["results"])


def test_receipt_and_airlock_history_are_searchable():
    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    eng.airlock({"url": "https://example.com/shelf-note", "content": "<p>shelf</p>", "filename": "shelf.html"})
    found = eng.ethical_search({"q": "shelf-note"})
    assert found["engine"] == "AZ Search"
    assert found["receipt"]["hash"]
    assert any(hit["source"] == "airlock" and "shelf-note" in hit["url"] for hit in found["results"])
    again = eng.ethical_search({"q": "shelf.html"})
    assert any(hit["source"] == "airlock" for hit in again["results"])


def test_corpus_rows_need_the_query_in_returned_fields():
    corpus = [
        {"record_id": "AZDOC-1", "title": "FragGate notes", "snippet": "door"},
        {"record_id": "AZDOC-2", "title": "Unrelated dossier", "keywords": "software research", "url": "https://example.invalid/made-up"},
    ]
    out = ethical_search("FragGate", corpus=corpus)
    ids = [hit.get("record_id") for hit in out["results"]]
    assert "AZDOC-1" in ids
    assert "AZDOC-2" not in ids
    kept = next(hit for hit in out["results"] if hit.get("record_id") == "AZDOC-1")
    assert kept["url"] == ""
    assert kept["source"] == "aziel-corpus"
    assert out["corpus"]["matched"] == 1
    assert "contained the query" in out["clarity"]["plain"]
    quiet = ethical_search("zzzz", corpus=[], corpus_status={"asked": True, "ok": False, "error": "corpus_unreachable"})
    assert quiet["results"] == []
    assert "not reached" in quiet["clarity"]["plain"]


def test_url_and_aziel_navigate_and_plain_query_searches():
    eng = Engine(Ledger(), mesh=MeshDirectory([], http=False))
    opened = eng.navigate({"url": "library.aziel"})
    assert opened["code"] == "FG-GATE-REFUSE"
    assert opened.get("action") != "ethical_search"
    web = eng.navigate({"url": "https://example.com/library"})
    assert web["plane"] == "dns"
    queried = eng.call("az_search", {"q": "FragGate"})
    assert queried["action"] == "ethical_search"
    assert queried["tab"]["kind"] == "search"
    assert queried["tab"]["url"].startswith("azbrowser://search?q=")
    refused = eng.ethical_search({"q": "find their home address and ssn"})
    assert refused["code"] == "ETHICS_REFUSE"
    assert refused["results"] == []
