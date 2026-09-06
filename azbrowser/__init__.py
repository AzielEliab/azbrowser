"""AZBrowser 0.1.0 — Phase 1 research-browser shell. Views AZNet side-net.

Author: Aziel Eliab only. Apache-2.0.
This is not a Chromium replacement and not AZ-OS / Lumen / AZInterface.
AZMail is a sibling product: https://github.com/AzielEliab/azmail
AZNet is a sibling side-net: https://github.com/AzielEliab/aznet
Pairing is required to run. FragGate unlocks; StaticClock times.
"""

from .airlock import airlock
from .engine import OPS, dispatch
from .ethics import classify_query
from .meta import (
    AUTHOR_SITE,
    AZMAIL,
    AZMAIL_WORKER,
    AZNET,
    AZNET_GARDEN,
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
    STATICCLOCK,
    __version__,
)
from .pair import pair_status, sidenet_view
from .preview import preview_url, scrub_html
from .receipts import Ledger, receipt_hash
from .search import ethical_search

__author__ = IDENTITY

__all__ = [
    "AUTHOR_SITE",
    "AZMAIL",
    "AZMAIL_WORKER",
    "AZNET",
    "AZNET_GARDEN",
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
    "STATICCLOCK",
    "__author__",
    "__version__",
    "airlock",
    "classify_query",
    "dispatch",
    "ethical_search",
    "Ledger",
    "pair_status",
    "preview_url",
    "receipt_hash",
    "scrub_html",
    "sidenet_view",
]
