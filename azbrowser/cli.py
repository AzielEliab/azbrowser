"""AZBrowser CLI — local airlock, receipts, ethical search, loopback UI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .meta import AZNET, HOST, LIMITATION, __version__
from .doctor import doctor
from .engine import Engine
from .receipts import Ledger


def _engine(args: argparse.Namespace) -> Engine:
    path = getattr(args, "ledger", None) or os.environ.get("AZBROWSER_LEDGER") or "./azbrowser_receipts.jsonl"
    stub = os.environ.get("AZBROWSER_PAIR_STUB")
    paired = None
    if stub == "1":
        paired = True
    elif stub == "0":
        paired = False
    return Engine(Ledger(path), paired=paired)


def _print(obj: object) -> int:
    if isinstance(obj, dict) and obj.get("display"):
        d = obj["display"]
        print(d.get("title") or "AZBrowser")
        print(d.get("summary") or "")
        for row in d.get("fields") or []:
            print(f"  {row.get('label')}: {row.get('value')}")
        print()
    print(json.dumps(obj, indent=2, ensure_ascii=False))
    return 0 if (not isinstance(obj, dict) or obj.get("ok", True)) else 2


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="azbrowser", description="AZBrowser Phase 1 research shell. Author Aziel Eliab.")
    p.add_argument("--ledger", default=os.environ.get("AZBROWSER_LEDGER", "./azbrowser_receipts.jsonl"))
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version")
    sub.add_parser("doctor")
    sub.add_parser("ui")
    sub.add_parser("health")
    sub.add_parser("ops")
    sub.add_parser("pair-status")
    sub.add_parser("sidenet")

    n = sub.add_parser("navigate")
    n.add_argument("url")
    n.add_argument("--fetch", action="store_true")

    for name in ("back", "forward", "reload", "home"):
        sub.add_parser(name)

    s = sub.add_parser("search")
    s.add_argument("q")
    sub.add_parser("lamb-lens").add_argument("q")

    a = sub.add_parser("airlock")
    a.add_argument("--url", default="")
    a.add_argument("--file", default="")
    a.add_argument("--content", default="")
    a.add_argument("--fetch", action="store_true")

    sub.add_parser("receipts")
    sub.add_parser("verify")
    sub.add_parser("tabs")
    sub.add_parser("tab-new")
    e = sub.add_parser("ethics")
    e.add_argument("q")
    c = sub.add_parser("call")
    c.add_argument("op")
    c.add_argument("--payload", default="{}")

    args = p.parse_args(argv)
    if args.cmd == "version":
        print(f"AZBrowser {__version__}")
        print(LIMITATION)
        print("Worker:", HOST)
        print("AZNet sibling:", AZNET)
        return 0
    if args.cmd == "doctor":
        return doctor()
    if args.cmd == "ui":
        from .ui import serve

        return serve()

    eng = _engine(args)
    if args.cmd == "ops":
        return _print({"ok": True, "ops": list(__import__("azbrowser.engine", fromlist=["OPS"]).OPS)})
    if args.cmd == "health":
        return _print(eng.health({}))
    if args.cmd == "pair-status":
        return _print(eng.pair_status({}))
    if args.cmd == "sidenet":
        return _print(eng.sidenet_view({}))
    if args.cmd == "navigate":
        return _print(eng.navigate({"url": args.url, "fetch": args.fetch}))
    if args.cmd == "back":
        return _print(eng.back({}))
    if args.cmd == "forward":
        return _print(eng.forward({}))
    if args.cmd == "reload":
        return _print(eng.reload({}))
    if args.cmd == "home":
        return _print(eng.home({}))
    if args.cmd == "search":
        return _print(eng.ethical_search({"q": args.q}))
    if args.cmd == "lamb-lens":
        return _print(eng.ethical_search({"q": args.q}))
    if args.cmd == "airlock":
        content = None
        filename = ""
        if args.file:
            raw = Path(args.file).read_bytes()
            content = raw
            filename = Path(args.file).name
        elif args.content:
            content = args.content
        return _print(eng.airlock({"url": args.url, "content": content, "filename": filename, "fetch": args.fetch}))
    if args.cmd == "receipts":
        return _print(eng.receipts({}))
    if args.cmd == "verify":
        return _print(eng.receipt_verify({}))
    if args.cmd == "tabs":
        return _print(eng.tab_list({}))
    if args.cmd == "tab-new":
        return _print(eng.tab_new({}))
    if args.cmd == "ethics":
        return _print(eng.ethics_gate({"q": args.q}))
    if args.cmd == "call":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            print("payload must be JSON", file=sys.stderr)
            return 2
        return _print(eng.call(args.op, payload))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
