"""Data ingestion airlock: download → scan → scrub → verify → vault."""

from __future__ import annotations

import hashlib
import re
from typing import Any
from urllib.parse import urlparse

from .ethics import classify_query
from .preview import MAX_BYTES, sanitize_url, scrub_html

STAGES = ("download", "scan", "scrub", "verify", "vault")

_SUSPICIOUS_EXT = {".exe", ".dll", ".scr", ".js", ".vbs", ".ps1", ".bat", ".cmd", ".apk", ".msi"}
_SUSPICIOUS_BYTES = (b"MZ", b"\x7fELF", b"PK\x03\x04")


def _scan(name: str, data: bytes, url: str) -> dict[str, Any]:
    flags: list[str] = []
    lower = (name or url).lower()
    for ext in _SUSPICIOUS_EXT:
        if lower.endswith(ext):
            flags.append("suspicious_extension:" + ext)
    head = data[:8]
    for magic in _SUSPICIOUS_BYTES:
        if head.startswith(magic):
            flags.append("suspicious_magic")
            break
    text = data[:4000].decode("utf-8", errors="ignore").lower()
    if "eval(" in text or "<script" in text:
        flags.append("script_like")
    if re.search(r"powershell|cmd\.exe|wget http", text):
        flags.append("shell_lure")
    risk = min(100, 20 * len(flags))
    verdict = "hold" if flags else "clean"
    if "suspicious_magic" in flags or any(f.startswith("suspicious_extension") for f in flags):
        verdict = "quarantine"
    return {"flags": flags, "risk": risk, "verdict": verdict, "advisory": True}


def airlock(
    *,
    url: str = "",
    content: str | bytes | None = None,
    filename: str = "",
    fetch: bool = False,
) -> dict[str, Any]:
    """Walk the airlock pipeline. Bytes stay local; hosted Worker stores metadata only."""
    ethics = classify_query(" ".join([url, filename, str(content)[:200] if content else ""]))
    stages: list[dict[str, Any]] = []

    def mark(name: str, **extra: Any) -> dict[str, Any]:
        row = {"stage": name, "ok": extra.pop("ok", True), **extra}
        if "hash" not in row:
            blob = repr(sorted(row.items())).encode("utf-8")
            row["hash"] = hashlib.sha256(blob).hexdigest()
        stages.append(row)
        return row

    if ethics["refuse"]:
        mark("download", ok=False, error="ETHICS_REFUSE", ethics=ethics)
        return {
            "ok": False,
            "code": "ETHICS_REFUSE",
            "stages": stages,
            "ethics": ethics,
            "pipeline": list(STAGES),
            "note": "No receipt = no action. Airlock refused before download.",
        }

    data = b""
    source = "inline"
    safe_url = ""
    if content is not None:
        data = content.encode("utf-8") if isinstance(content, str) else bytes(content)
        source = "inline"
        mark("download", source=source, bytes=len(data), filename=filename)
    elif url:
        safe = sanitize_url(url)
        if not safe.get("ok"):
            mark("download", ok=False, error=safe.get("error"), url=url)
            return {"ok": False, "stages": stages, "pipeline": list(STAGES), **safe}
        safe_url = safe["url"]
        if fetch:
            try:
                from urllib.request import Request, urlopen

                req = Request(safe_url, headers={"User-Agent": "Mozilla/5.0 AZBrowser/0.1.0"})
                with urlopen(req, timeout=8) as resp:  # noqa: S310
                    data = resp.read(MAX_BYTES + 1)
                    filename = filename or (urlparse(resp.geturl()).path.split("/")[-1] or "download.bin")
            except Exception as exc:
                mark("download", ok=False, error="fetch_failed", detail=str(exc)[:240], url=safe_url)
                return {"ok": False, "stages": stages, "pipeline": list(STAGES), "url": safe_url}
            truncated = len(data) > MAX_BYTES
            data = data[:MAX_BYTES]
            mark("download", source="fetch", url=safe_url, bytes=len(data), truncated=truncated, filename=filename)
        else:
            mark("download", source="url-only", url=safe_url, bytes=0, filename=filename, note="metadata preview; pass fetch=true or content=")
    else:
        mark("download", ok=False, error="url_or_content_required")
        return {"ok": False, "stages": stages, "pipeline": list(STAGES), "error": "url_or_content_required"}

    scan = _scan(filename, data, safe_url or url)
    mark("scan", **scan)

    scrubbed = {"html": "", "stripped_kinds": [], "changed": False}
    if data and (b"<" in data[:200] or (filename or "").endswith((".html", ".htm", ".svg"))):
        scrubbed = scrub_html(data.decode("utf-8", errors="replace"))
    mark("scrub", stripped_kinds=scrubbed.get("stripped_kinds") or [], changed=bool(scrubbed.get("changed")))

    digest = hashlib.sha256(data).hexdigest() if data else hashlib.sha256(b"").hexdigest()
    mark("verify", content_hash=digest, bytes=len(data), hash=digest)

    vault = {
        "held": scan["verdict"] != "clean",
        "verdict": scan["verdict"],
        "content_hash": digest,
        "filename": filename or "untitled",
        "stored_bytes": False,
        "note": "v0.1 vault is receipt + metadata. Bytes are not persisted on the hosted Worker.",
    }
    mark("vault", **vault)

    ok = all(s.get("ok", True) for s in stages) and scan["verdict"] != "quarantine"
    return {
        "ok": ok,
        "pipeline": list(STAGES),
        "stages": stages,
        "ethics": ethics,
        "scan": scan,
        "content_hash": digest,
        "filename": vault["filename"],
        "url": safe_url or url,
        "bytes": len(data),
        "vault": vault,
        "advisory": True,
        "note": "download → scan → scrub → verify → vault. No receipt = no action.",
    }
