from __future__ import annotations

import json
from urllib.request import urlopen


def _get_json(url: str):
    with urlopen(url) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def render_tui(base_url: str) -> str:
    quests = _get_json(f"{base_url}/api/quests")
    connectors = _get_json(f"{base_url}/api/connectors")
    lines = [
        "DeepScientist TUI",
        "=" * 24,
        "",
        "Quests:",
    ]
    for quest in quests:
        lines.extend(
            [
                f"- {quest['quest_id']} :: {quest['title']}",
                f"  status={quest['status']} anchor={quest['active_anchor']} branch={quest['branch']}",
                f"  artifacts={quest['artifact_count']} history={quest['history_count']}",
            ]
        )
    lines.extend(["", "Connectors:"])
    for connector in connectors:
        lines.append(
            f"- {connector['name']} ({connector['display_mode']}) inbox={connector['inbox_count']} outbox={connector['outbox_count']}"
        )
    return "\n".join(lines) + "\n"
