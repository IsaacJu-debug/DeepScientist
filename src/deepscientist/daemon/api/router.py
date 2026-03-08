from __future__ import annotations

import re


ROUTES: list[tuple[str, re.Pattern[str], str]] = [
    ("GET", re.compile(r"^/$"), "root"),
    ("GET", re.compile(r"^/ui/(?P<ui_path>.+)$"), "ui_asset"),
    ("GET", re.compile(r"^/api/health$"), "health"),
    ("GET", re.compile(r"^/api/connectors$"), "connectors"),
    ("GET", re.compile(r"^/api/quests$"), "quests"),
    ("POST", re.compile(r"^/api/quests$"), "quest_create"),
    ("GET", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)$"), "quest"),
    ("GET", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/history$"), "history"),
    ("GET", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/graph$"), "graph"),
    ("GET", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/runs$"), "runs"),
    ("GET", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/memory$"), "quest_memory"),
    ("GET", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/documents$"), "documents"),
    ("POST", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/documents/open$"), "document_open"),
    ("PUT", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/documents/(?P<document_id>[^/]+)$"), "document_save"),
    ("POST", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/chat$"), "chat"),
    ("POST", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/commands$"), "command"),
    ("POST", re.compile(r"^/api/quests/(?P<quest_id>[^/]+)/runs$"), "run_create"),
    ("GET", re.compile(r"^/api/memory$"), "memory"),
    ("GET", re.compile(r"^/api/config/files$"), "config_files"),
    ("GET", re.compile(r"^/api/config/(?P<name>[^/]+)$"), "config_show"),
    ("PUT", re.compile(r"^/api/config/(?P<name>[^/]+)$"), "config_save"),
    ("POST", re.compile(r"^/api/config/validate$"), "config_validate"),
    ("GET", re.compile(r"^/assets/(?P<asset_path>.+)$"), "asset"),
]


def match_route(method: str, path: str) -> tuple[str | None, dict]:
    for route_method, pattern, name in ROUTES:
        if route_method != method:
            continue
        match = pattern.match(path)
        if match:
            return name, match.groupdict()
    return None, {}
