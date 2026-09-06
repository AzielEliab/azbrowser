"""Append-only integrity receipts. No receipt = no action."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ZERO = "0" * 64
KIND = "azbrowser.receipt"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def receipt_hash(seq: int, prev: str, action: str, payload_hash: str, ts: str) -> str:
    return sha256_text(f"{seq}|{prev}|{action}|{payload_hash}|{ts}")


class Ledger:
    """Hash-chained append-only receipt list. Verify walks the chain."""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path) if path else None
        self.entries: list[dict[str, Any]] = []
        if self.path and self.path.exists():
            self._load()

    def _load(self) -> None:
        self.entries = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            self.entries.append(json.loads(line))

    def _persist(self, row: dict[str, Any]) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    @property
    def tip(self) -> str:
        return self.entries[-1]["hash"] if self.entries else ZERO

    def append(self, action: str, payload: dict[str, Any] | None = None, *, tab_id: str | None = None) -> dict[str, Any]:
        if not action:
            raise ValueError("No receipt = no action: action required")
        payload = dict(payload or {})
        ts = _now()
        seq = len(self.entries) + 1
        prev = self.tip
        payload_hash = sha256_text(_canon(payload))
        digest = receipt_hash(seq, prev, action, payload_hash, ts)
        row = {
            "kind": KIND,
            "seq": seq,
            "ts": ts,
            "action": action,
            "tab_id": tab_id,
            "prev": prev,
            "payload_hash": payload_hash,
            "hash": digest,
            "payload": payload,
            "author": "Aziel Eliab",
        }
        self.entries.append(row)
        self._persist(row)
        return row

    def verify(self) -> dict[str, Any]:
        prev = ZERO
        for i, row in enumerate(self.entries, start=1):
            expected = receipt_hash(i, prev, row["action"], row["payload_hash"], row["ts"])
            if row.get("seq") != i or row.get("prev") != prev or row.get("hash") != expected:
                return {"ok": False, "broken_at": i, "tip": self.tip, "count": len(self.entries)}
            if row.get("payload") is not None:
                if sha256_text(_canon(row["payload"])) != row["payload_hash"]:
                    return {"ok": False, "broken_at": i, "reason": "payload_hash", "tip": self.tip}
            prev = row["hash"]
        return {"ok": True, "tip": self.tip, "count": len(self.entries), "kind": KIND}

    def list(self, limit: int = 64) -> list[dict[str, Any]]:
        return list(self.entries[-max(1, min(int(limit), 256)) :])
