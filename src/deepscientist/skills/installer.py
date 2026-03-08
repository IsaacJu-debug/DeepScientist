from __future__ import annotations

import shutil
from pathlib import Path

from ..shared import ensure_dir
from .registry import discover_skill_bundles


class SkillInstaller:
    def __init__(self, repo_root: Path, home: Path) -> None:
        self.repo_root = repo_root
        self.home = home

    def discover(self):
        return discover_skill_bundles(self.repo_root)

    def sync_global(self) -> dict:
        codex_root = ensure_dir(Path.home() / ".codex" / "skills")
        ensure_dir(Path.home() / ".claude" / "agents")
        copied: list[str] = []
        for bundle in self.discover():
            target = codex_root / f"deepscientist-{bundle.skill_id}"
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(bundle.root, target)
            copied.append(str(target))
        return {
            "codex": copied,
            "claude": [],
            "notes": ["Claude sync is reserved for future work."],
        }

    def sync_quest(self, quest_root: Path) -> dict:
        codex_root = ensure_dir(quest_root / ".codex" / "skills")
        ensure_dir(quest_root / ".claude" / "agents")
        copied: list[str] = []
        for bundle in self.discover():
            target = codex_root / f"deepscientist-{bundle.skill_id}"
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(bundle.root, target)
            copied.append(str(target))
        return {
            "codex": copied,
            "claude": [],
            "notes": ["Claude sync is reserved for future work."],
        }
