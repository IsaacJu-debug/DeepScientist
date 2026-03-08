from __future__ import annotations

from pathlib import Path

from deepscientist.artifact import ArtifactService
from deepscientist.config import ConfigManager
from deepscientist.home import ensure_home_layout, repo_root
from deepscientist.prompts import PromptBuilder
from deepscientist.quest import QuestService
from deepscientist.runners import CodexRunner, RunRequest
from deepscientist.runtime_logs import JsonlLogger
from deepscientist.skills import SkillInstaller


def test_codex_runner_creates_history_and_run_outputs(temp_home: Path, monkeypatch) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    quest_service = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home))
    quest = quest_service.create("runner quest")
    quest_root = Path(quest["quest_root"])

    fake_bin_root = temp_home / "bin"
    fake_bin_root.mkdir(parents=True, exist_ok=True)
    fake_codex = fake_bin_root / "codex"
    fake_codex.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json, sys",
                "sys.stdin.read()",
                "print(json.dumps({'item': {'text': 'fake codex response'}}))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)
    import os

    monkeypatch.setenv("PATH", f"{fake_bin_root}:{os.environ.get('PATH', '')}")

    runner = CodexRunner(
        home=temp_home,
        repo_root=repo_root(),
        binary="codex",
        logger=JsonlLogger(temp_home / "logs", level="debug"),
        prompt_builder=PromptBuilder(repo_root(), temp_home),
        artifact_service=ArtifactService(temp_home),
    )
    result = runner.run(
        RunRequest(
            quest_id=quest["quest_id"],
            quest_root=quest_root,
            run_id="run-test-001",
            skill_id="decision",
            message="Respond briefly.",
            model="gpt-5.4",
            approval_policy="never",
            sandbox_mode="workspace-write",
        )
    )
    assert result.ok is True
    assert "fake codex response" in result.output_text
    assert (result.history_root / "assistant.md").exists()
    assert (result.run_root / "prompt.md").exists()
    assert (result.run_root / "result.json").exists()
    config_text = (quest_root / ".codex" / "config.toml").read_text(encoding="utf-8")
    assert "[mcp_servers.memory]" in config_text
    assert "[mcp_servers.artifact]" in config_text
