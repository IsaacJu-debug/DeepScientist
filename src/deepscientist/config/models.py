from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


CONFIG_NAMES = ("config", "runners", "connectors", "plugins", "mcp_servers")
REQUIRED_CONFIG_NAMES = ("config", "runners", "connectors")
OPTIONAL_CONFIG_NAMES = ("plugins", "mcp_servers")


@dataclass(frozen=True)
class ConfigFileInfo:
    name: str
    path: Path
    required: bool
    exists: bool


def config_filename(name: str) -> str:
    return f"{name}.yaml"


def default_config(home: Path) -> dict:
    return {
        "home": str(home),
        "default_runner": "codex",
        "default_locale": "zh-CN",
        "daemon": {
            "session_restore_on_start": True,
            "max_concurrent_quests": 1,
            "ack_timeout_ms": 1000,
        },
        "ui": {
            "host": "127.0.0.1",
            "port": 20888,
            "auto_open_browser": True,
            "default_mode": "web",
        },
        "logging": {
            "level": "info",
            "console": True,
        },
        "git": {
            "auto_checkpoint": True,
            "auto_push": False,
            "default_remote": "origin",
            "graph_formats": ["svg", "png", "json"],
        },
        "skills": {
            "sync_global_on_init": True,
            "sync_quest_on_create": True,
        },
        "connectors": {
            "auto_ack": True,
            "milestone_push": True,
            "direct_chat_enabled": True,
        },
        "cloud": {
            "enabled": False,
            "base_url": "https://deepscientist.cc",
            "token": None,
            "token_env": "DEEPSCIENTIST_TOKEN",
            "verify_token_on_start": False,
            "sync_mode": "disabled",
        },
    }


def default_runners() -> dict:
    return {
        "codex": {
            "enabled": True,
            "binary": "codex",
            "model": "gpt-5.4",
            "approval_policy": "on-request",
            "sandbox_mode": "workspace-write",
        },
        "claude": {
            "enabled": False,
            "binary": "claude",
            "status": "reserved_todo",
        },
    }


def default_connectors() -> dict:
    return {
        "qq": {
            "enabled": False,
            "mode": "relay",
            "app_id": None,
            "app_secret": None,
            "public_callback_url": None,
            "relay_url": None,
            "main_chat_id": None,
            "require_at_in_groups": True,
        },
        "telegram": {"enabled": False},
        "discord": {"enabled": False},
        "slack": {"enabled": False},
    }


def default_plugins() -> dict:
    return {"search_paths": []}


def default_mcp_servers() -> dict:
    return {"servers": []}


def default_payload(name: str, home: Path) -> dict:
    if name == "config":
        return default_config(home)
    if name == "runners":
        return default_runners()
    if name == "connectors":
        return default_connectors()
    if name == "plugins":
        return default_plugins()
    if name == "mcp_servers":
        return default_mcp_servers()
    raise KeyError(name)
