from __future__ import annotations

import json
from pathlib import Path

from deepscientist.artifact import ArtifactService
from deepscientist.config import ConfigManager
from deepscientist.home import ensure_home_layout, repo_root
from deepscientist.memory import MemoryService
from deepscientist.quest import QuestService
from deepscientist.skills import SkillInstaller


def test_memory_documents_and_promotion(temp_home: Path) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    quest_service = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home))
    quest = quest_service.create("memory quest")
    quest_root = Path(quest["quest_root"])
    memory = MemoryService(temp_home)

    card = memory.write_card(
        scope="quest",
        kind="ideas",
        title="Reusable idea",
        body="A compact durable note.",
        quest_root=quest_root,
        quest_id=quest["quest_id"],
        tags=["test"],
    )
    assert Path(card["path"]).exists()

    documents = quest_service.list_documents(quest["quest_id"])
    memory_doc = next(item for item in documents if item["document_id"].startswith("memory::"))
    opened = quest_service.open_document(quest["quest_id"], memory_doc["document_id"])
    assert opened["writable"] is True
    assert "A compact durable note." in opened["content"]

    promoted = memory.promote_to_global(path=card["path"], quest_root=quest_root)
    assert Path(promoted["path"]).exists()
    assert promoted["scope"] == "global"

    skill_doc = next(item for item in documents if item["document_id"].startswith("skill::"))
    skill_opened = quest_service.open_document(quest["quest_id"], skill_doc["document_id"])
    assert skill_opened["writable"] is False


def test_artifact_interact_and_prepare_branch(temp_home: Path) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    quest_service = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home))
    quest = quest_service.create("artifact quest")
    quest_root = Path(quest["quest_root"])
    artifact = ArtifactService(temp_home)

    quest_service.append_message(quest["quest_id"], role="user", content="请先告诉我 baseline 情况。", source="web")
    result = artifact.interact(
        quest_root,
        kind="progress",
        message="Baseline is ready; I am summarizing the current metrics.",
        deliver_to_bound_conversations=True,
        include_recent_inbound_messages=True,
    )
    assert result["status"] == "ok"
    assert result["delivered"] is True
    assert result["recent_inbound_messages"]

    outbox = temp_home / "logs" / "connectors" / "local" / "outbox.jsonl"
    assert outbox.exists()
    records = [json.loads(line) for line in outbox.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert any("Baseline is ready" in (item.get("message") or "") for item in records)

    branch = artifact.prepare_branch(quest_root, run_id="run-main-001")
    assert branch["ok"] is True
    assert branch["branch"] == "run/run-main-001"
    assert Path(branch["worktree_root"]).exists()
