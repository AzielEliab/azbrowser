"""Whether AZNet's loopback port answers.

This is a short look at 127.0.0.1:8771. It does not write a pair receipt
and it does not claim a handshake. Pairing stays in AZNet.

Author: Aziel Eliab only.
"""

from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .meta import AZNET
from .sidenet import pair_view

AZNET_HOST = "127.0.0.1"
AZNET_PORT = 8771
SEEN_LINE = "AZNet seen on this machine"
ABSENT_LINE = "AZNet not running on :8771"


def aznet_answers(host: str = AZNET_HOST, port: int = AZNET_PORT, timeout: float = 0.4) -> bool:
    """True only when that host:port returns an HTTP response."""
    url = f"http://{host}:{int(port)}/"
    req = Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"})
    try:
        with urlopen(req, timeout=timeout) as res:  # noqa: S310 — loopback AZNet port only
            res.read(64)
        return True
    except HTTPError:
        return True
    except (URLError, TimeoutError, OSError, ValueError):
        return False


def aznet_report(host: str = AZNET_HOST, port: int = AZNET_PORT, timeout: float = 0.4) -> dict[str, Any]:
    seen = aznet_answers(host, port, timeout)
    pairing = pair_view()
    status = str(pairing.get("pair_status") or "unknown")
    if status == "PAIRED":
        line = "AZNet paired on this machine. The pair token stays on the AZNet ledger."
    elif seen:
        line = SEEN_LINE + ". Pair token was not read from the ledger."
    else:
        line = ABSENT_LINE
    return {
        "seen": seen,
        "host": host,
        "port": int(port),
        "line": line,
        "install": AZNET,
        "pair_status": status,
        "unlock_status": pairing.get("unlock_status"),
        "pair_token_present": bool(pairing.get("pair_token_present")),
        "pair_token_echoed": False,
        "wrote": False,
        "products_merged": False,
        "resolver": pairing.get("resolver"),
    }
