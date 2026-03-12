from __future__ import annotations

from pathlib import Path

from deepscientist.config import ConfigManager
from deepscientist.home import ensure_home_layout, repo_root
from deepscientist.prompts import PromptBuilder
from deepscientist.quest import QuestService
from deepscientist.skills import SkillInstaller, discover_skill_bundles


EXPECTED_STAGE_SKILLS = {
    "scout",
    "baseline",
    "idea",
    "experiment",
    "analysis-campaign",
    "write",
    "finalize",
    "decision",
}


def test_src_stage_skills_exist_and_are_nontrivial() -> None:
    root = repo_root() / "src" / "skills"
    for skill_id in EXPECTED_STAGE_SKILLS:
        path = root / skill_id / "SKILL.md"
        assert path.exists(), f"missing {path}"
        text = path.read_text(encoding="utf-8")
        assert len(text.splitlines()) >= 40, f"{path} is unexpectedly thin"


def test_skill_discovery_prefers_src_skills() -> None:
    bundles = discover_skill_bundles(repo_root())
    discovered = {bundle.skill_id for bundle in bundles}
    assert EXPECTED_STAGE_SKILLS.issubset(discovered)
    for bundle in bundles:
        if bundle.skill_id in EXPECTED_STAGE_SKILLS:
            assert Path(bundle.skill_md).is_relative_to(repo_root() / "src" / "skills")


def test_idea_skill_requires_memory_first_literature_survey() -> None:
    idea_skill = repo_root() / "src" / "skills" / "idea" / "SKILL.md"
    text = idea_skill.read_text(encoding="utf-8")
    assert "memory.search(...)" in text
    assert "arXiv" in text
    assert "artifact.arxiv(" in text
    assert "literature survey report" in text

    template = repo_root() / "src" / "skills" / "idea" / "references" / "literature-survey-template.md"
    assert template.exists()


def test_scout_skill_requires_memory_first_literature_report() -> None:
    scout_skill = repo_root() / "src" / "skills" / "scout" / "SKILL.md"
    text = scout_skill.read_text(encoding="utf-8")
    assert "memory.search(...)" in text
    assert "arXiv" in text
    assert "artifact.arxiv(" in text
    assert "literature scouting report" in text

    template = repo_root() / "src" / "skills" / "scout" / "references" / "literature-scout-template.md"
    assert template.exists()


def test_quest_creation_syncs_all_stage_skills(temp_home: Path) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    quest = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home)).create("skill sync quest")
    quest_root = Path(quest["quest_root"])

    codex_skills = sorted((quest_root / ".codex" / "skills").glob("deepscientist-*"))
    claude_skills = sorted((quest_root / ".claude" / "agents").glob("deepscientist-*.md"))

    assert {path.name.removeprefix("deepscientist-") for path in codex_skills} == EXPECTED_STAGE_SKILLS
    assert {path.stem.removeprefix("deepscientist-") for path in claude_skills} == EXPECTED_STAGE_SKILLS


def test_skill_resync_repairs_frontmatter_and_removes_stale_files(temp_home: Path) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    installer = SkillInstaller(repo_root(), temp_home)
    quest = QuestService(temp_home, skill_installer=installer).create("skill resync quest")
    quest_root = Path(quest["quest_root"])

    installed_skill = quest_root / ".codex" / "skills" / "deepscientist-idea" / "SKILL.md"
    stale_file = quest_root / ".codex" / "skills" / "deepscientist-idea" / "stale.tmp"
    stale_removed_codex = quest_root / ".codex" / "skills" / "deepscientist-alpharxiv-paper-loopup"
    stale_removed_claude = quest_root / ".claude" / "agents" / "deepscientist-alpharxiv-paper-loopup.md"

    installed_skill.write_text("broken skill body\n", encoding="utf-8")
    stale_file.write_text("remove me\n", encoding="utf-8")
    stale_removed_codex.mkdir(parents=True)
    (stale_removed_codex / "SKILL.md").write_text("legacy skill\n", encoding="utf-8")
    stale_removed_claude.write_text("legacy claude skill\n", encoding="utf-8")

    installer.sync_quest(quest_root)

    repaired = installed_skill.read_text(encoding="utf-8")
    assert repaired.startswith("---\n")
    assert "name:" in repaired
    assert not stale_file.exists()
    assert not stale_removed_codex.exists()
    assert not stale_removed_claude.exists()


def test_paper_reading_stage_skills_use_artifact_arxiv_and_legacy_skill_is_removed() -> None:
    root = repo_root() / "src" / "skills"
    for skill_id in ("baseline", "scout", "idea", "write", "finalize"):
        text = (root / skill_id / "SKILL.md").read_text(encoding="utf-8")
        assert "artifact.arxiv(" in text
        assert "alpharxiv-paper-loopup" not in text

    assert not (root / "alpharxiv-paper-loopup" / "SKILL.md").exists()


def test_baseline_skill_documents_confirm_or_waive_gate() -> None:
    text = (repo_root() / "src" / "skills" / "baseline" / "SKILL.md").read_text(encoding="utf-8")
    assert "artifact.confirm_baseline(...)" in text
    assert "artifact.waive_baseline(...)" in text
    assert "do not open the downstream gate" in text
    assert "requested_baseline_ref" in text
    assert "default to reuse-and-verify" in text


def test_decision_skill_requires_reuse_baseline_to_land_on_attach_and_confirm() -> None:
    text = (repo_root() / "src" / "skills" / "decision" / "SKILL.md").read_text(encoding="utf-8")
    assert "artifact.attach_baseline(...)" in text
    assert "artifact.confirm_baseline(...)" in text
    assert "explicit blocker or waiver" in text


def test_prompt_builder_skill_paths_only_reference_existing_files(temp_home: Path) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    quest = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home)).create("skill prompt quest")
    builder = PromptBuilder(repo_root(), temp_home)

    prompt = builder.build(
        quest_id=quest["quest_id"],
        skill_id="finalize",
        user_message="Please summarize the quest and stop cleanly.",
        model="gpt-5.4",
    )

    finalize_primary = str((repo_root() / "src" / "skills" / "finalize" / "SKILL.md").resolve())
    assert "Fallback mirrored skills root:" not in prompt
    assert f"- finalize: primary={finalize_primary}" in prompt


def test_all_stage_skills_document_blocking_decision_request_options_and_timeout() -> None:
    root = repo_root() / "src" / "skills"
    for skill_id in EXPECTED_STAGE_SKILLS:
        text = (root / skill_id / "SKILL.md").read_text(encoding="utf-8")
        assert "1 to 3 concrete options" in text
        assert "wait up to 1 day" in text


def test_all_stage_skills_require_stage_start_memory_retrieval_and_stage_end_memory_write() -> None:
    root = repo_root() / "src" / "skills"
    for skill_id in ("scout", "baseline", "idea", "experiment", "analysis-campaign", "write", "finalize"):
        text = (root / skill_id / "SKILL.md").read_text(encoding="utf-8")
        assert "Stage-start requirement:" in text
        assert "memory.list_recent(scope='quest', limit=5)" in text
        assert "memory.search(...)" in text
        assert "Stage-end requirement:" in text
        assert "memory.write(...)" in text


def test_experiment_skill_requires_outcome_status_in_memory_writes() -> None:
    text = (repo_root() / "src" / "skills" / "experiment" / "SKILL.md").read_text(encoding="utf-8")
    assert "`success`, `partial`, or `failure`" in text
    assert "`idea_id`, `branch`, and `run_id`" in text


def test_idea_skill_requires_review_of_prior_ideas_and_experiment_outcomes() -> None:
    text = (repo_root() / "src" / "skills" / "idea" / "SKILL.md").read_text(encoding="utf-8")
    assert "review prior quest idea records and experiment outcomes" in text
    assert "reference material, not as the active idea contract" in text
