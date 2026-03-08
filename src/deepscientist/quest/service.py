from __future__ import annotations

from pathlib import Path

from ..gitops import current_branch, export_git_graph, head_commit, init_repo
from ..home import repo_root
from ..shared import append_jsonl, ensure_dir, generate_id, read_json, read_jsonl, read_text, read_yaml, sha256_text, utc_now, write_text, write_yaml
from ..skills import SkillInstaller
from .layout import (
    QUEST_DIRECTORIES,
    gitignore,
    initial_brief,
    initial_plan,
    initial_quest_yaml,
    initial_status,
    initial_summary,
)


class QuestService:
    def __init__(self, home: Path, skill_installer: SkillInstaller | None = None) -> None:
        self.home = home
        self.quests_root = home / "quests"
        self.skill_installer = skill_installer

    def _quest_root(self, quest_id: str) -> Path:
        return self.quests_root / quest_id

    def create(self, goal: str, quest_id: str | None = None, runner: str = "codex") -> dict:
        quest_id = quest_id or generate_id("q")
        quest_root = self._quest_root(quest_id)
        if quest_root.exists():
            raise FileExistsError(f"Quest already exists: {quest_id}")
        ensure_dir(quest_root)
        for relative in QUEST_DIRECTORIES:
            ensure_dir(quest_root / relative)
        write_yaml(quest_root / "quest.yaml", initial_quest_yaml(quest_id, goal, quest_root, runner))
        write_text(quest_root / "brief.md", initial_brief(goal))
        write_text(quest_root / "plan.md", initial_plan())
        write_text(quest_root / "status.md", initial_status())
        write_text(quest_root / "SUMMARY.md", initial_summary())
        write_text(quest_root / ".gitignore", gitignore())
        init_repo(quest_root)
        if self.skill_installer is not None:
            self.skill_installer.sync_quest(quest_root)
        from ..gitops import checkpoint_repo

        checkpoint_repo(quest_root, f"quest: initialize {quest_id}", allow_empty=False)
        export_git_graph(quest_root, ensure_dir(quest_root / "artifacts" / "graphs"))
        return self.snapshot(quest_id)

    def list_quests(self) -> list[dict]:
        items: list[dict] = []
        if not self.quests_root.exists():
            return items
        for quest_yaml in sorted(self.quests_root.glob("*/quest.yaml")):
            quest_id = quest_yaml.parent.name
            items.append(self.snapshot(quest_id))
        return sorted(items, key=lambda item: item.get("updated_at", ""), reverse=True)

    def snapshot(self, quest_id: str) -> dict:
        quest_root = self._quest_root(quest_id)
        quest_yaml = read_yaml(quest_root / "quest.yaml", {})
        graph_dir = quest_root / "artifacts" / "graphs"
        graph_svg = graph_dir / "git-graph.svg"
        history = read_jsonl(quest_root / ".ds" / "conversations" / "main.jsonl")
        artifacts = []
        recent_runs = []
        memory_cards = list((quest_root / "memory").glob("*/*.md"))
        pending_decisions = []
        latest_metric = None
        active_baseline_id = None
        active_baseline_variant_id = None
        artifacts_root = quest_root / "artifacts"
        if artifacts_root.exists():
            for folder in sorted(artifacts_root.iterdir()):
                if not folder.is_dir():
                    continue
                for path in sorted(folder.glob("*.json")):
                    item = read_json(path, {})
                    artifacts.append({"kind": folder.name, "path": str(path), "payload": item})
                    if folder.name == "decisions":
                        pending_decisions.append(item.get("id") or path.stem)
                    metrics_summary = item.get("metrics_summary")
                    if latest_metric is None and isinstance(metrics_summary, dict) and metrics_summary:
                        key = next(iter(metrics_summary))
                        latest_metric = {"key": key, "value": metrics_summary.get(key)}
        codex_history_root = quest_root / ".ds" / "codex_history"
        if codex_history_root.exists():
            for meta_path in sorted(codex_history_root.glob("*/meta.json")):
                run_data = read_json(meta_path, {})
                if run_data:
                    recent_runs.append(run_data)
                    if latest_metric is None and run_data.get("summary"):
                        latest_metric = {"key": "summary", "value": run_data.get("summary")}
        attachment_path = quest_root / "baselines" / "imported"
        if attachment_path.exists():
            attachments = sorted(attachment_path.glob("*/attachment.yaml"))
            if attachments:
                attachment = read_yaml(attachments[-1], {})
                active_baseline_id = attachment.get("source_baseline_id")
                active_baseline_variant_id = attachment.get("source_variant_id")
        status_line = "Quest created."
        status_text = read_text(quest_root / "status.md").strip().splitlines()
        if status_text:
            for line in status_text:
                line = line.strip().lstrip("#").strip()
                if line:
                    status_line = line
                    break
        paths = {
            "brief": str(quest_root / "brief.md"),
            "plan": str(quest_root / "plan.md"),
            "status": str(quest_root / "status.md"),
            "summary": str(quest_root / "SUMMARY.md"),
            "git_graph_svg": str(graph_svg) if graph_svg.exists() else None,
        }
        counts = {
            "memory_cards": len(memory_cards),
            "artifacts": len(artifacts),
            "pending_decision_count": len(pending_decisions),
            "analysis_run_count": sum(
                1
                for item in recent_runs
                if str(item.get("run_id", "")).startswith("analysis")
                or item.get("run_kind") == "analysis-campaign"
            ),
        }
        return {
            "quest_id": quest_yaml.get("quest_id", quest_id),
            "title": quest_yaml.get("title", quest_id),
            "quest_root": str(quest_root.resolve()),
            "status": quest_yaml.get("status", "idle"),
            "active_anchor": quest_yaml.get("active_anchor", "baseline"),
            "runner": quest_yaml.get("default_runner", "codex"),
            "active_baseline_id": active_baseline_id,
            "active_baseline_variant_id": active_baseline_variant_id,
            "active_idea_id": None,
            "active_run_id": recent_runs[-1]["run_id"] if recent_runs else None,
            "active_analysis_campaign_id": None,
            "pending_decisions": pending_decisions,
            "bound_conversations": (read_json(quest_root / ".ds" / "bindings.json", {}).get("sources") or ["local:default"]),
            "created_at": quest_yaml.get("created_at"),
            "updated_at": quest_yaml.get("updated_at"),
            "branch": current_branch(quest_root),
            "head": head_commit(quest_root),
            "graph_svg_path": str(graph_svg) if graph_svg.exists() else None,
            "summary": {
                "status_line": status_line,
                "latest_metric": latest_metric,
            },
            "paths": paths,
            "counts": counts,
            "team": {"mode": "single", "active_workers": []},
            "cloud": {"linked": False, "base_url": "https://deepscientist.cc"},
            "history_count": len(history),
            "artifact_count": len(artifacts),
            "recent_artifacts": artifacts[-5:],
            "recent_runs": recent_runs[-5:],
        }

    def append_message(self, quest_id: str, role: str, content: str, source: str = "local") -> dict:
        quest_root = self._quest_root(quest_id)
        timestamp = utc_now()
        record = {
            "id": generate_id("msg"),
            "role": role,
            "content": content,
            "source": source,
            "created_at": timestamp,
        }
        append_jsonl(quest_root / ".ds" / "conversations" / "main.jsonl", record)
        if role == "user":
            from ..shared import write_json

            bindings_path = quest_root / ".ds" / "bindings.json"
            bindings = read_json(bindings_path, {"sources": []})
            normalized_source = self._normalize_binding_source(source)
            sources = list(bindings.get("sources") or [])
            if normalized_source not in sources:
                sources.append(normalized_source)
                bindings["sources"] = sources
                write_json(bindings_path, bindings)
        append_jsonl(
            quest_root / ".ds" / "events.jsonl",
            {
                "type": "conversation.message",
                "quest_id": quest_id,
                "role": role,
                "source": source,
                "created_at": timestamp,
            },
        )
        quest_data = read_yaml(quest_root / "quest.yaml", {})
        quest_data["updated_at"] = timestamp
        write_yaml(quest_root / "quest.yaml", quest_data)
        return record

    def set_status(self, quest_id: str, status: str) -> dict:
        quest_root = self._quest_root(quest_id)
        quest_data = read_yaml(quest_root / "quest.yaml", {})
        quest_data["status"] = status
        quest_data["updated_at"] = utc_now()
        write_yaml(quest_root / "quest.yaml", quest_data)
        return self.snapshot(quest_id)

    def history(self, quest_id: str, limit: int = 100) -> list[dict]:
        return read_jsonl(self._quest_root(quest_id) / ".ds" / "conversations" / "main.jsonl")[-limit:]

    def list_documents(self, quest_id: str) -> list[dict]:
        quest_root = self._quest_root(quest_id)
        documents = []
        for relative in ("brief.md", "plan.md", "status.md", "SUMMARY.md"):
            path = quest_root / relative
            documents.append(
                {
                    "document_id": relative,
                    "title": relative,
                    "path": str(path),
                    "kind": "markdown",
                    "writable": True,
                    "source_scope": "quest",
                }
            )
        for path in sorted((quest_root / "memory").glob("*/*.md")):
            relative = path.relative_to(quest_root / "memory").as_posix()
            documents.append(
                {
                    "document_id": f"memory::{relative}",
                    "title": path.name,
                    "path": str(path),
                    "kind": "markdown",
                    "writable": True,
                    "source_scope": "quest_memory",
                }
            )
        for skill_md in sorted((repo_root() / "skills").glob("*/SKILL.md")):
            relative = skill_md.relative_to(repo_root() / "skills").as_posix()
            documents.append(
                {
                    "document_id": f"skill::{relative}",
                    "title": relative,
                    "path": str(skill_md),
                    "kind": "markdown",
                    "writable": False,
                    "source_scope": "skill",
                }
            )
        return documents

    def open_document(self, quest_id: str, document_id: str) -> dict:
        quest_root = self._quest_root(quest_id)
        path, writable, scope, source_kind = self._resolve_document(quest_root, document_id)
        content = read_text(path)
        return {
            "document_id": document_id,
            "quest_id": quest_id,
            "title": path.name if "::" in document_id else document_id,
            "path": str(path),
            "kind": "markdown" if path.suffix == ".md" else "text",
            "scope": scope,
            "writable": writable,
            "encoding": "utf-8",
            "source_scope": source_kind,
            "content": content,
            "revision": f"sha256:{sha256_text(content)}",
            "updated_at": utc_now(),
            "meta": {
                "tags": [path.stem],
                "source_kind": source_kind,
                "renderer_hint": "markdown" if path.suffix == ".md" else "text",
            },
        }

    def save_document(self, quest_id: str, document_id: str, content: str, previous_revision: str | None = None) -> dict:
        current = self.open_document(quest_id, document_id)
        if not current.get("writable", False):
            return {
                "ok": False,
                "conflict": False,
                "message": "Document is read-only.",
                "document_id": document_id,
                "saved_at": utc_now(),
                "updated_payload": current,
            }
        current_revision = current["revision"]
        if previous_revision and previous_revision != current_revision:
            return {
                "ok": False,
                "conflict": True,
                "message": "Document changed since it was opened.",
                "current_revision": current_revision,
                "document_id": document_id,
                "saved_at": utc_now(),
                "updated_payload": current,
            }
        path = Path(current["path"])
        write_text(path, content)
        new_revision = f"sha256:{sha256_text(content)}"
        return {
            "ok": True,
            "document_id": document_id,
            "quest_id": quest_id,
            "conflict": False,
            "path": str(path),
            "saved_at": utc_now(),
            "revision": new_revision,
            "updated_payload": self.open_document(quest_id, document_id),
        }

    @staticmethod
    def _normalize_binding_source(source: str) -> str:
        normalized = (source or "local").strip().lower()
        if normalized in {"web", "cli", "api", "command", "local", "local-ui"}:
            return "local:default"
        if ":" in normalized:
            return normalized
        return f"{normalized}:default"

    @staticmethod
    def _resolve_document(quest_root: Path, document_id: str) -> tuple[Path, bool, str, str]:
        if document_id.startswith("memory::"):
            relative = document_id.split("::", 1)[1]
            if relative.startswith("."):
                raise ValueError("Document ID must stay within quest memory.")
            root = (quest_root / "memory").resolve()
            path = (root / relative).resolve()
            if path != root and root not in path.parents:
                raise ValueError("Document ID escapes quest memory.")
            return path, True, "quest_memory", "quest_memory"
        if document_id.startswith("skill::"):
            relative = document_id.split("::", 1)[1]
            root = (repo_root() / "skills").resolve()
            path = (root / relative).resolve()
            if path != root and root not in path.parents:
                raise ValueError("Document ID escapes skills root.")
            return path, False, "skill", "skill"
        if "/" in document_id or document_id.startswith("."):
            raise ValueError("Document ID must be a simple curated file name.")
        return quest_root / document_id, True, "quest", "quest_file"
