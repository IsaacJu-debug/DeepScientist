from __future__ import annotations

from pathlib import Path

from ..memory.frontmatter import load_markdown_document
from ..quest import QuestService
from ..shared import read_text
from ..skills import discover_skill_bundles


class PromptBuilder:
    def __init__(self, repo_root: Path, home: Path) -> None:
        self.repo_root = repo_root
        self.home = home
        self.quest_service = QuestService(home)

    def build(
        self,
        *,
        quest_id: str,
        skill_id: str,
        user_message: str,
        model: str,
    ) -> str:
        snapshot = self.quest_service.snapshot(quest_id)
        quest_root = Path(snapshot["quest_root"])
        skill_block = self._skill_block(skill_id)
        skill_index = self._skill_index()
        brief = read_text(quest_root / "brief.md").strip()
        plan = read_text(quest_root / "plan.md").strip()
        status = read_text(quest_root / "status.md").strip()
        summary = read_text(quest_root / "SUMMARY.md").strip()
        codex_skill_root = quest_root / ".codex" / "skills"
        return "\n\n".join(
            [
                "You are DeepScientist Core running a quest-local Codex turn.",
                f"quest_id: {quest_id}",
                f"quest_root: {quest_root}",
                f"runner_name: codex",
                f"model: {model}",
                f"active_anchor: {snapshot.get('active_anchor')}",
                "",
                "Rules:",
                "- Keep all durable outputs inside quest_root.",
                "- Use the built-in MCP namespaces `memory` and `artifact` instead of inventing ad hoc ledgers.",
                "- Use Markdown + YAML frontmatter files for memory-style notes.",
                "- Use structured artifacts for decisions, milestones, runs, reports, and graph refreshes.",
                "- Every decision must include an explicit reason.",
                "- If you change direction, update plan.md or explain why the plan is unchanged.",
                "- Preserve long-horizon continuity in files, not only in ephemeral chat.",
                "- Prefer `memory.write` for durable notes, paper summaries, and lessons learned.",
                "- Prefer `artifact.record` or `artifact.interact` for user-facing progress and decisions.",
                "- Use `artifact.prepare_branch` before risky idea or run divergence.",
                "- Use `artifact.checkpoint` for meaningful Git milestones.",
                "- Use `artifact.render_git_graph` whenever the graph view should be refreshed.",
                "- If you need the latest user messages during a long turn, call `artifact.interact(include_recent_inbound_messages=true)`.",
                "",
                "Git contract:",
                f"- quest branch: quest/{quest_id}",
                f"- idea branch: idea/{quest_id}-<idea_id>",
                "- run branch: run/<run_id>",
                "- worktree root: <quest_root>/.ds/worktrees/<run_id>/",
                "",
                "Quest context:",
                brief,
                plan,
                status,
                summary,
                "",
                "Available first-party skills:",
                skill_index,
                "",
                "Installed skill roots:",
                f"- quest local: {codex_skill_root}",
                f"- repo canonical: {self.repo_root / 'skills'}",
                "",
                f"Active skill: {skill_id}",
                skill_block,
                "",
                "Built-in MCP operations you can call:",
                "- memory.write(kind, title, body/markdown, tags, scope)",
                "- memory.read(card_id/path)",
                "- memory.search(query, scope, limit)",
                "- memory.list_recent(scope, limit)",
                "- memory.promote_to_global(card_id/path)",
                "- artifact.record(payload)",
                "- artifact.interact(kind, message, response_phase, importance, ...)",
                "- artifact.checkpoint(message)",
                "- artifact.prepare_branch(run_id/idea_id/branch_kind)",
                "- artifact.publish_baseline(payload)",
                "- artifact.attach_baseline(baseline_id, variant_id)",
                "- artifact.refresh_summary(reason)",
                "- artifact.render_git_graph()",
                "",
                "Operational examples:",
                "- After finishing a paper read, call memory.write(kind='papers', ...).",
                "- After choosing an idea, call artifact.record(kind='decision', action='launch_experiment', reason='...').",
                "- After a main run ends, call artifact.record(kind='run', run_kind='main', metrics={...}, metric_deltas={...}).",
                "- After analysis is complete, call artifact.record(kind='report', report_type='analysis_campaign_summary', reason='...').",
                "",
                "Current user request:",
                user_message.strip(),
            ]
        ).strip() + "\n"

    def _skill_index(self) -> str:
        lines = []
        for bundle in discover_skill_bundles(self.repo_root):
            lines.append(f"- {bundle.skill_id}: {bundle.description}")
        return "\n".join(lines)

    def _skill_block(self, skill_id: str) -> str:
        skill_md = self.repo_root / "skills" / skill_id / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"Unknown skill: {skill_id}")
        text = skill_md.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            _metadata, body = self._split_frontmatter(skill_md)
            return body.strip()
        return text.strip()

    @staticmethod
    def _split_frontmatter(path: Path) -> tuple[dict, str]:
        metadata, body = load_markdown_document(path)
        return metadata, body
