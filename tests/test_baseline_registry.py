from __future__ import annotations

from pathlib import Path

from deepscientist.artifact import ArtifactService
from deepscientist.config import ConfigManager
from deepscientist.home import ensure_home_layout, repo_root
from deepscientist.quest import QuestService
from deepscientist.registries import BaselineRegistry
from deepscientist.skills import SkillInstaller


def test_baseline_publish_and_attach(temp_home: Path) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    quest = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home)).create("baseline quest")
    quest_root = Path(quest["quest_root"])
    artifact = ArtifactService(temp_home)
    result = artifact.record(
        quest_root,
        {
            "kind": "baseline",
            "publish_global": True,
            "baseline_id": "baseline-demo",
            "name": "Demo baseline",
            "primary_metric": {"name": "accuracy", "value": 0.9},
            "metrics_summary": {"accuracy": 0.9},
            "baseline_variants": [{"variant_id": "main", "label": "Main"}],
            "default_variant_id": "main",
        },
    )
    assert result["ok"] is True
    registry = BaselineRegistry(temp_home)
    entry = registry.get("baseline-demo")
    assert entry is not None
    attachment = registry.attach(quest_root, "baseline-demo", "main")
    assert attachment["source_baseline_id"] == "baseline-demo"
    assert attachment["source_variant_id"] == "main"
