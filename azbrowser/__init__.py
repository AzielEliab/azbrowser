"""AZBrowser 0.1.0 — Phase 1 research-browser shell + Lamb Lens ethical search.

Author: Aziel Eliab only. Apache-2.0.
This is not a Chromium replacement and not AZ-OS / Lumen / AZInterface.
AZMail is a sibling: https://github.com/AzielEliab/azmail
AZNet is a sibling functional pair: https://github.com/AzielEliab/aznet
"""

from .airlock import airlock
from .engine import OPS, dispatch
from .ethics import classify_query
from .meta import (
    AUTHOR_SITE,
    AZMAIL,
    AZMAIL_WORKER,
    AZNET,
    AZNET_WORKER,
    FRAGGATE,
    FRAGGATE_CALL,
    FRAGGATE_MCP,
    GITHUB,
    GODLOCK,
    HOST,
    IDENTITY,
    LIBRARY,
    LIMITATION,
    RUNTIME,
    SIGIL,
    SPEC,
    __version__,
)
from .preview import preview_url, scrub_html
from .receipts import Ledger, receipt_hash
from .search import ethical_search

__author__ = IDENTITY

__all__ = [
    "AUTHOR_SITE",
    "AZMAIL",
    "AZMAIL_WORKER",
    "AZNET",
    "AZNET_WORKER",
    "FRAGGATE",
    "FRAGGATE_CALL",
    "FRAGGATE_MCP",
    "GITHUB",
    "GODLOCK",
    "HOST",
    "IDENTITY",
    "LIBRARY",
    "LIMITATION",
    "OPS",
    "RUNTIME",
    "SIGIL",
    "SPEC",
    "__author__",
    "__version__",
    "airlock",
    "classify_query",
    "dispatch",
    "ethical_search",
    "Ledger",
    "preview_url",
    "receipt_hash",
    "scrub_html",
]
