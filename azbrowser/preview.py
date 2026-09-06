"""Controlled fetch / proxy preview. Not a Chromium renderer."""

from __future__ import annotations

import html
import re
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .ethics import classify_query

MAX_BYTES = 256_000
UA = "Mozilla/5.0 AZBrowser/0.1.0 (research-shell; +https://github.com/AzielEliab/azbrowser)"

_SCRIPT_RE = re.compile(r"<script\b[^>]*>[\s\S]*?</script\s*>", re.I)
_IFRAME_RE = re.compile(r"<(?:iframe|object|embed|form)\b[^>]*>[\s\S]*?</(?:iframe|object|embed|form)\s*>", re.I)
_ON_RE = re.compile(r"\s+on[a-z]+\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+)", re.I)
_JS_HREF = re.compile(r"""href\s*=\s*['"]\s*javascript:[^'"]*['"]""", re.I)
_META_REFRESH = re.compile(r"<meta\b[^>]*http-equiv\s*=\s*['\"]?refresh[^>]*>", re.I)
_TITLE_RE = re.compile(r"<title[^>]*>([\s\S]*?)</title>", re.I)
_TAG_RE = re.compile(r"<[^>]+>")


def scrub_html(raw: str) -> dict[str, Any]:
    stripped: list[str] = []
    text = str(raw or "")
    for re_, label in (
        (_SCRIPT_RE, "script"),
        (_IFRAME_RE, "embed"),
        (_META_REFRESH, "meta_refresh"),
    ):
        if re_.search(text):
            stripped.append(label)
            text = re_.sub("", text)
    if _ON_RE.search(text):
        stripped.append("event_handler")
        text = _ON_RE.sub("", text)
    if _JS_HREF.search(text):
        stripped.append("javascript_href")
        text = _JS_HREF.sub('href="#azbrowser-blocked-javascript"', text)
    return {
        "html": text,
        "stripped": stripped,
        "stripped_kinds": list(dict.fromkeys(stripped)),
        "changed": text != str(raw or ""),
    }


def extract_title(html_text: str) -> str:
    m = _TITLE_RE.search(html_text or "")
    if not m:
        return ""
    return html.unescape(_TAG_RE.sub("", m.group(1))).strip()[:200]


def extract_text(html_text: str, limit: int = 2400) -> str:
    plain = html.unescape(_TAG_RE.sub(" ", html_text or ""))
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain[:limit]


def sanitize_url(url: str) -> dict[str, Any]:
    raw = str(url or "").strip()
    if not raw:
        return {"ok": False, "error": "url required", "url": ""}
    if "://" not in raw and not raw.startswith("/"):
        if re.match(r"^[a-z0-9.-]+\.[a-z]{2,}(/|$)", raw, re.I):
            raw = "https://" + raw
        else:
            return {"ok": False, "error": "not_a_url", "url": raw, "suggest_search": True}
    parsed = urlparse(raw)
    scheme = (parsed.scheme or "").lower()
    if scheme in {"javascript", "data", "file", "vbscript"}:
        return {"ok": False, "error": "blocked_scheme", "scheme": scheme, "url": raw}
    if scheme not in {"https", "http"}:
        return {"ok": False, "error": "https_only", "scheme": scheme, "url": raw}
    if scheme == "http":
        raw = "https://" + raw[len("http://") :]
    return {"ok": True, "url": raw, "host": urlparse(raw).hostname or ""}


def preview_url(url: str, *, fetch: bool = False) -> dict[str, Any]:
    """Ethics-gate + sanitize + optional fetch. Always returns a preview envelope."""
    ethics = classify_query(url)
    if ethics["refuse"]:
        return {
            "ok": False,
            "code": "ETHICS_REFUSE",
            "action": "navigate",
            "ethics": ethics,
            "url": url,
            "note": "No receipt = no action. Refused before fetch.",
        }
    safe = sanitize_url(url)
    if not safe.get("ok"):
        return {"ok": False, "action": "navigate", "ethics": ethics, **safe}

    out: dict[str, Any] = {
        "ok": True,
        "action": "navigate",
        "url": safe["url"],
        "host": safe.get("host"),
        "ethics": ethics,
        "sandbox": True,
        "renderer": "controlled-fetch-preview",
        "not_chromium": True,
        "fetched": False,
        "title": safe.get("host") or safe["url"],
        "excerpt": "",
        "html": "",
        "content_hash": "",
        "bytes": 0,
        "note": "Phase 1 sandbox preview. Not a replace-your-OS-browser claim.",
    }
    if not fetch:
        return out
    try:
        req = Request(safe["url"], headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.1"})
        with urlopen(req, timeout=8) as resp:  # noqa: S310 — operator-supplied https URL
            raw = resp.read(MAX_BYTES + 1)
            ctype = resp.headers.get("Content-Type", "")
            final = resp.geturl()
    except Exception as exc:  # network optional
        out["ok"] = False
        out["error"] = "fetch_failed"
        out["detail"] = str(exc)[:240]
        return out
    truncated = len(raw) > MAX_BYTES
    raw = raw[:MAX_BYTES]
    text = raw.decode("utf-8", errors="replace")
    scrubbed = scrub_html(text)
    out.update(
        {
            "fetched": True,
            "final_url": final,
            "content_type": ctype,
            "truncated": truncated,
            "bytes": len(raw),
            "title": extract_title(text) or urlparse(final).hostname or safe["url"],
            "excerpt": extract_text(scrubbed["html"]),
            "html": scrubbed["html"][:80_000],
            "stripped_kinds": scrubbed["stripped_kinds"],
            "content_hash": __import__("hashlib").sha256(raw).hexdigest(),
        }
    )
    return out
