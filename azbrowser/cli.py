"""AZBrowser CLI — local airlock, receipts, ethical search, loopback UI."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from .meta import AZNET, HOST, __version__
from .doctor import doctor
from .engine import Engine
from .peer import ABSENT_LINE, SEEN_LINE, aznet_answers
from .receipts import Ledger

HELP = f"""azbrowser — local research browser

Search, open a .aziel name, or type a web address. The app runs on this machine.
Author: Aziel Eliab. Version {__version__}.

Usage:
  azbrowser
  azbrowser <command> [options]

Start:
  azbrowser                 Welcome and the next step
  azbrowser ui              Open the app at http://127.0.0.1:8878/
  azbrowser doctor          Check this install
  azbrowser --help          Show this help

Everyday:
  azbrowser search TEXT
  azbrowser navigate URL
  azbrowser home
  azbrowser tabs
  azbrowser tab-new

Advanced:
  azbrowser back
  azbrowser forward
  azbrowser reload
  azbrowser lamb-lens TEXT
  azbrowser airlock [--url URL] [--file PATH] [--content TEXT] [--fetch]
  azbrowser receipts
  azbrowser verify
  azbrowser ethics TEXT
  azbrowser health
  azbrowser ops
  azbrowser version
  azbrowser call OP [--payload JSON]

Options:
  --ledger PATH             Receipt file. Default: ./azbrowser_receipts.jsonl
  --json                    Print machine JSON for a command
  -h, --help                Show this help

Examples:
  azbrowser ui
  azbrowser search library
  azbrowser navigate https://www.azieleliab.com/
  azbrowser doctor
"""

COMMAND_HELP = {
    "ui": "azbrowser ui\nOpen the local app on this machine.\nPrints: Open http://127.0.0.1:8878/\n",
    "doctor": "azbrowser doctor [--json]\nCheck this install. One pass or fail line per check.\n",
    "version": "azbrowser version [--json]\nPrint the version and author.\n",
    "search": "azbrowser search TEXT [--json]\nLamb Lens search. Example: azbrowser search library\n",
    "navigate": "azbrowser navigate URL [--fetch] [--json]\nOpen an address. Example: azbrowser navigate https://www.azieleliab.com/\n",
    "home": "azbrowser home [--json]\nOpen the home tab.\n",
    "tabs": "azbrowser tabs [--json]\nList open tabs.\n",
    "tab-new": "azbrowser tab-new [--json]\nOpen a new tab.\n",
    "back": "azbrowser back [--json]\nGo back in the active tab.\n",
    "forward": "azbrowser forward [--json]\nGo forward in the active tab.\n",
    "reload": "azbrowser reload [--json]\nReload the active tab.\n",
    "lamb-lens": "azbrowser lamb-lens TEXT [--json]\nSame search as azbrowser search.\n",
    "airlock": "azbrowser airlock [--url URL] [--file PATH] [--content TEXT] [--fetch] [--json]\nRun the receipted airlock on text, a file, or an address.\n",
    "receipts": "azbrowser receipts [--json]\nList local receipts.\n",
    "verify": "azbrowser verify [--json]\nWalk the local receipt chain.\n",
    "ethics": "azbrowser ethics TEXT [--json]\nCheck text with the ethics gate.\n",
    "health": "azbrowser health [--json]\nStatus of this install.\n",
    "ops": "azbrowser ops [--json]\nList operation names.\n",
    "call": 'azbrowser call OP [--payload JSON] [--json]\nRun one operation. Example: azbrowser call home --payload "{}"\n',
    "help": HELP,
}


class FriendlyParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print(_plain_error(self.prog, message), file=sys.stderr)
        raise SystemExit(2)


def _plain_error(prog: str, message: str) -> str:
    choice = re.search(r"invalid choice: '([^']*)'", message)
    if choice:
        bad = choice.group(1) or "that"
        return f'Unknown command "{bad}". Try: azbrowser ui   or   azbrowser --help'
    if "required" in message:
        if prog.endswith(" navigate"):
            return "An address is required. Try: azbrowser navigate https://www.azieleliab.com/"
        if prog.endswith(" search") or prog.endswith(" lamb-lens"):
            return "Words to search are required. Try: azbrowser search library"
        if prog.endswith(" ethics"):
            return "Text to check is required. Try: azbrowser ethics library"
        if prog.endswith(" call"):
            return "An operation name is required. Try: azbrowser call home"
        return "That command needs more detail. Try: azbrowser --help"
    if "unrecognized arguments" in message:
        return f"Unrecognized option. Try: azbrowser --help"
    return "That command could not run. Try: azbrowser --help"


def _welcome() -> str:
    if aznet_answers():
        peer = SEEN_LINE + "."
    else:
        peer = f"{ABSENT_LINE}. Install: {AZNET}"
    return (
        f"AZBrowser {__version__} is a local research browser for search, tabs, and .aziel names.\n"
        "Author: Aziel Eliab.\n"
        f"{peer}\n"
        "\n"
        "Open the app:\n"
        "  azbrowser ui\n"
        "\n"
        "Then go to http://127.0.0.1:8878/\n"
        "\n"
        "Also:\n"
        "  azbrowser doctor\n"
        "  azbrowser --help\n"
    )


def _engine(args: argparse.Namespace) -> Engine:
    path = getattr(args, "ledger", None) or os.environ.get("AZBROWSER_LEDGER") or "./azbrowser_receipts.jsonl"
    return Engine(Ledger(path))


def _emit(obj: object, as_json: bool) -> int:
    ok = not isinstance(obj, dict) or obj.get("ok", True)
    if as_json:
        print(json.dumps(obj, indent=2, ensure_ascii=False))
        return 0 if ok else 2
    if isinstance(obj, dict):
        code = str(obj.get("code") or "")
        clarity = obj.get("clarity") if isinstance(obj.get("clarity"), dict) else {}
        display = obj.get("display") if isinstance(obj.get("display"), dict) else {}
        if ok is False or code in {"FG-GATE-REFUSE", "ETHICS_REFUSE", "FG-HALLUC-TOOL"}:
            plain = clarity.get("plain") or display.get("summary") or obj.get("error") or obj.get("reason") or "Refused."
            nxt = clarity.get("next") or "Try: azbrowser --help"
            print(plain)
            print(nxt)
            if code:
                print(code)
            return 2 if ok is False else 0
        if obj.get("ops") and not display:
            print("Operations")
            for name in obj["ops"]:
                print(f"  {name}")
            return 0
        title = display.get("title") or "AZBrowser"
        summary = display.get("summary") or ""
        print(title)
        if summary:
            print(summary)
        for row in display.get("fields") or []:
            label = row.get("label")
            value = row.get("value")
            print(f"  {label}: {value}")
        if clarity.get("next") and clarity.get("next") not in summary:
            print(clarity["next"])
        return 0 if ok else 2
    print(obj)
    return 0 if ok else 2


def _build() -> FriendlyParser:
    common = argparse.ArgumentParser(add_help=False)
    # SUPPRESS so a subparser default does not wipe a flag set before the command.
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    common.add_argument("-h", "--help", action="store_true", default=argparse.SUPPRESS)

    p = FriendlyParser(prog="azbrowser", add_help=False, parents=[common])
    p.add_argument("--ledger", default=os.environ.get("AZBROWSER_LEDGER", "./azbrowser_receipts.jsonl"))
    sub = p.add_subparsers(dest="cmd")

    for name in (
        "version",
        "doctor",
        "ui",
        "health",
        "ops",
        "back",
        "forward",
        "reload",
        "home",
        "receipts",
        "verify",
        "tabs",
        "tab-new",
        "help",
    ):
        sub.add_parser(name, add_help=False, parents=[common])

    n = sub.add_parser("navigate", add_help=False, parents=[common])
    n.add_argument("url")
    n.add_argument("--fetch", action="store_true")

    s = sub.add_parser("search", add_help=False, parents=[common])
    s.add_argument("q")
    sub.add_parser("lamb-lens", add_help=False, parents=[common]).add_argument("q")

    a = sub.add_parser("airlock", add_help=False, parents=[common])
    a.add_argument("--url", default="")
    a.add_argument("--file", default="")
    a.add_argument("--content", default="")
    a.add_argument("--fetch", action="store_true")

    e = sub.add_parser("ethics", add_help=False, parents=[common])
    e.add_argument("q")
    c = sub.add_parser("call", add_help=False, parents=[common])
    c.add_argument("op")
    c.add_argument("--payload", default="{}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build().parse_args(argv)
    args.help = bool(getattr(args, "help", False))
    args.json = bool(getattr(args, "json", False))
    if args.help or args.cmd == "help":
        print(COMMAND_HELP.get(args.cmd or "", HELP) if args.cmd not in (None, "help") else HELP)
        return 0
    if not args.cmd:
        print(_welcome())
        return 0
    if args.cmd == "version":
        if args.json:
            return _emit(
                {"ok": True, "name": "AZBrowser", "version": __version__, "author": "Aziel Eliab", "host": HOST},
                True,
            )
        print(f"AZBrowser {__version__}")
        print("Author: Aziel Eliab")
        return 0
    if args.cmd == "doctor":
        return doctor(as_json=bool(args.json))
    if args.cmd == "ui":
        from .ui import serve

        return serve()

    eng = _engine(args)
    as_json = bool(args.json)
    if args.cmd == "ops":
        return _emit({"ok": True, "ops": list(__import__("azbrowser.engine", fromlist=["OPS"]).OPS)}, as_json)
    if args.cmd == "health":
        return _emit(eng.health({}), as_json)
    if args.cmd == "navigate":
        return _emit(eng.navigate({"url": args.url, "fetch": args.fetch}), as_json)
    if args.cmd == "back":
        return _emit(eng.back({}), as_json)
    if args.cmd == "forward":
        return _emit(eng.forward({}), as_json)
    if args.cmd == "reload":
        return _emit(eng.reload({}), as_json)
    if args.cmd == "home":
        return _emit(eng.home({}), as_json)
    if args.cmd == "search":
        return _emit(eng.ethical_search({"q": args.q}), as_json)
    if args.cmd == "lamb-lens":
        return _emit(eng.ethical_search({"q": args.q}), as_json)
    if args.cmd == "airlock":
        content = None
        filename = ""
        if args.file:
            try:
                raw = Path(args.file).read_bytes()
            except OSError:
                print(f'Could not read "{args.file}". Check the path and try again.', file=sys.stderr)
                return 2
            content = raw
            filename = Path(args.file).name
        elif args.content:
            content = args.content
        return _emit(
            eng.airlock({"url": args.url, "content": content, "filename": filename, "fetch": args.fetch}),
            as_json,
        )
    if args.cmd == "receipts":
        return _emit(eng.receipts({}), as_json)
    if args.cmd == "verify":
        return _emit(eng.receipt_verify({}), as_json)
    if args.cmd == "tabs":
        return _emit(eng.tab_list({}), as_json)
    if args.cmd == "tab-new":
        return _emit(eng.tab_new({}), as_json)
    if args.cmd == "ethics":
        return _emit(eng.ethics_gate({"q": args.q}), as_json)
    if args.cmd == "call":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError:
            print('That payload is not JSON. Try: azbrowser call home --payload "{}"', file=sys.stderr)
            return 2
        if not isinstance(payload, dict):
            print('The payload must be a JSON object. Try: azbrowser call home --payload "{}"', file=sys.stderr)
            return 2
        return _emit(eng.call(args.op, payload), as_json)
    print(f'Unknown command "{args.cmd}". Try: azbrowser ui   or   azbrowser --help', file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
