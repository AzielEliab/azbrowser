"""In-process tab isolation (UX + agent ops). Not a process sandbox."""

from __future__ import annotations

import uuid
from typing import Any


def _id() -> str:
    return "tab-" + uuid.uuid4().hex[:10]


class TabSession:
    def __init__(self) -> None:
        home = self._blank("Home")
        self.tabs: dict[str, dict[str, Any]] = {home["id"]: home}
        self.active: str = home["id"]

    def _blank(self, title: str = "New Tab") -> dict[str, Any]:
        return {
            "id": _id(),
            "title": title,
            "url": "azbrowser://newtab",
            "history": ["azbrowser://newtab"],
            "index": 0,
            "kind": "newtab",
        }

    def list(self) -> dict[str, Any]:
        return {"ok": True, "active": self.active, "tabs": list(self.tabs.values())}

    def new(self, title: str = "New Tab") -> dict[str, Any]:
        tab = self._blank(title)
        self.tabs[tab["id"]] = tab
        self.active = tab["id"]
        return {"ok": True, "tab": tab, "active": self.active}

    def close(self, tab_id: str) -> dict[str, Any]:
        if tab_id not in self.tabs:
            return {"ok": False, "error": "unknown_tab", "tab_id": tab_id}
        if len(self.tabs) == 1:
            return {"ok": False, "error": "last_tab"}
        del self.tabs[tab_id]
        if self.active == tab_id:
            self.active = next(iter(self.tabs))
        return {"ok": True, "active": self.active, "tabs": list(self.tabs.values())}

    def switch(self, tab_id: str) -> dict[str, Any]:
        if tab_id not in self.tabs:
            return {"ok": False, "error": "unknown_tab", "tab_id": tab_id}
        self.active = tab_id
        return {"ok": True, "tab": self.tabs[tab_id], "active": self.active}

    def current(self) -> dict[str, Any]:
        return self.tabs[self.active]

    def push(self, url: str, title: str, kind: str = "preview") -> dict[str, Any]:
        tab = self.current()
        hist = tab["history"][: tab["index"] + 1]
        hist.append(url)
        tab["history"] = hist[-32:]
        tab["index"] = len(tab["history"]) - 1
        tab["url"] = url
        tab["title"] = title
        tab["kind"] = kind
        return tab

    def back(self) -> dict[str, Any]:
        tab = self.current()
        if tab["index"] <= 0:
            return {"ok": False, "error": "no_back", "tab": tab}
        tab["index"] -= 1
        tab["url"] = tab["history"][tab["index"]]
        return {"ok": True, "tab": tab}

    def forward(self) -> dict[str, Any]:
        tab = self.current()
        if tab["index"] >= len(tab["history"]) - 1:
            return {"ok": False, "error": "no_forward", "tab": tab}
        tab["index"] += 1
        tab["url"] = tab["history"][tab["index"]]
        return {"ok": True, "tab": tab}

    def home(self) -> dict[str, Any]:
        tab = self.current()
        return self.push("azbrowser://newtab", "Home", "newtab") if tab else self.new("Home")
