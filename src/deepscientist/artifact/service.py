from __future__ import annotations

from pathlib import Path
from typing import Any

from ..gitops import (
    canonical_worktree_root,
    checkpoint_repo,
    create_worktree,
    current_branch,
    ensure_branch,
    export_git_graph,
    head_commit,
)
from ..registries import BaselineRegistry
from ..shared import (
    append_jsonl,
    ensure_dir,
    generate_id,
    read_json,
    read_jsonl,
    read_text,
    read_yaml,
    utc_now,
    write_json,
    write_text,
    write_yaml,
)
from .schemas import ARTIFACT_DIRS, guidance_for_kind, validate_artifact_payload


class ArtifactService:
    def __init__(self, home: Path) -> None:
        self.home = home
        self.baselines = BaselineRegistry(home)

    def record(self, quest_root: Path, payload: dict, *, checkpoint: bool | None = None) -> dict:
        errors = validate_artifact_payload(payload)
        if errors:
            return {
                "ok": False,
                "errors": errors,
                "warnings": [],
            }

        record = self._build_record(quest_root, payload)
        artifact_id = record["artifact_id"]
        artifact_path = self._artifact_path(quest_root, record["kind"], artifact_id)
        write_json(artifact_path, record)
        append_jsonl(quest_root / "artifacts" / "_index.jsonl", self._index_line(record, artifact_path))
        append_jsonl(
            quest_root / ".ds" / "events.jsonl",
            {
                "type": "artifact.recorded",
                "quest_id": record["quest_id"],
                "artifact_id": artifact_id,
                "kind": record["kind"],
                "recorded_at": record["updated_at"],
                "status": record.get("status"),
            },
        )

        should_checkpoint = self._should_checkpoint(record["kind"]) if checkpoint is None else checkpoint
        checkpoint_result = None
        if should_checkpoint:
            checkpoint_result = checkpoint_repo(quest_root, f"artifact: {record['kind']} {artifact_id}", allow_empty=False)
        graph_manifest = None
        if record["kind"] in {"baseline", "decision", "milestone", "run", "report", "approval", "graph"}:
            graph_manifest = export_git_graph(quest_root, ensure_dir(quest_root / "artifacts" / "graphs"))
        self._touch_quest_updated_at(quest_root)

        baseline_registry_entry = None
        if record["kind"] == "baseline" and record.get("publish_global"):
            baseline_registry_entry = self.baselines.publish(
                {
                    "baseline_id": record.get("baseline_id", artifact_id),
                    "name": record.get("name", record.get("baseline_id", artifact_id)),
                    "source": record.get(
                        "source",
                        {
                            "kind": "artifact_publish",
                            "quest_id": record["quest_id"],
                            "quest_root": str(quest_root),
                            "git_commit": head_commit(quest_root),
                        },
                    ),
                    "path": record.get(
                        "path",
                        str(quest_root / "baselines" / "local" / record.get("baseline_id", artifact_id)),
                    ),
                    "baseline_kind": record.get("baseline_kind", "reproduced"),
                    "task": record.get("task"),
                    "dataset": record.get("dataset"),
                    "primary_metric": record.get("primary_metric"),
                    "metrics_summary": record.get("metrics_summary", {}),
                    "environment": record.get("environment", {}),
                    "tags": record.get("tags", []),
                    "summary": record.get("summary", ""),
                    "codebase_id": record.get("codebase_id"),
                    "codebase_root_path": record.get("codebase_root_path"),
                    "default_variant_id": record.get("default_variant_id"),
                    "baseline_variants": record.get("baseline_variants", []),
                    "metric_objectives": record.get("metric_objectives", []),
                    "baseline_metrics_path": record.get("baseline_metrics_path"),
                    "baseline_results_index_path": record.get("baseline_results_index_path"),
                }
            )

        return {
            "ok": True,
            "artifact_id": artifact_id,
            "path": str(artifact_path),
            "guidance": guidance_for_kind(record["kind"]),
            "graph": graph_manifest,
            "recorded": record["kind"],
            "record": record,
            "checkpoint": checkpoint_result,
            "baseline_registry_entry": baseline_registry_entry,
        }

    def checkpoint(self, quest_root: Path, message: str, *, allow_empty: bool = False) -> dict:
        result = checkpoint_repo(quest_root, message, allow_empty=allow_empty)
        self._touch_quest_updated_at(quest_root)
        return {
            "ok": True,
            "message": message,
            "guidance": "Checkpoint created. Continue from the updated quest branch state.",
            **result,
        }

    def prepare_branch(
        self,
        quest_root: Path,
        *,
        run_id: str | None = None,
        idea_id: str | None = None,
        branch: str | None = None,
        branch_kind: str = "run",
        create_worktree_flag: bool = True,
        start_point: str | None = None,
    ) -> dict:
        branch_name = branch or self._default_branch_name(quest_root, run_id=run_id, idea_id=idea_id, branch_kind=branch_kind)
        branch_result = ensure_branch(quest_root, branch_name, start_point=start_point, checkout=False)
        worktree_result = None
        worktree_root = None
        if create_worktree_flag:
            worktree_root = canonical_worktree_root(quest_root, run_id or branch_name)
            worktree_result = create_worktree(
                quest_root,
                branch=branch_name,
                worktree_root=worktree_root,
                start_point=start_point,
            )
        artifact_result = self.record(
            quest_root,
            {
                "kind": "decision",
                "status": "prepared",
                "verdict": "prepared",
                "action": "prepare_branch",
                "reason": f"Prepared branch `{branch_name}` for the next quest step.",
                "branch": branch_name,
                "run_id": run_id,
                "idea_id": idea_id,
                "worktree_root": str(worktree_root) if worktree_root else None,
                "source": {"kind": "system", "role": "artifact"},
            },
            checkpoint=False,
        )
        return {
            "ok": True,
            "branch": branch_name,
            "branch_result": branch_result,
            "worktree": worktree_result,
            "worktree_root": str(worktree_root) if worktree_root else None,
            "guidance": "Use this branch/worktree for the isolated idea or run. Keep durable outputs under quest_root.",
            "artifact": artifact_result,
        }

    def publish_baseline(self, quest_root: Path, payload: dict) -> dict:
        data = dict(payload)
        data["kind"] = "baseline"
        data["publish_global"] = True
        return self.record(quest_root, data)

    def attach_baseline(self, quest_root: Path, baseline_id: str, variant_id: str | None = None) -> dict:
        attachment = self.baselines.attach(quest_root, baseline_id, variant_id)
        artifact = self.record(
            quest_root,
            {
                "kind": "report",
                "status": "completed",
                "report_type": "baseline_attachment",
                "report_id": generate_id("report"),
                "summary": f"Attached baseline `{baseline_id}`.",
                "reason": "Baseline reuse avoids repeating an already stable reproduction.",
                "baseline_id": baseline_id,
                "baseline_variant_id": attachment.get("source_variant_id"),
                "paths": {
                    "attachment_yaml": str(quest_root / "baselines" / "imported" / baseline_id / "attachment.yaml"),
                },
                "source": {"kind": "system", "role": "artifact"},
            },
        )
        return {
            "ok": True,
            "attachment": attachment,
            "artifact": artifact,
            "guidance": "Reuse the attached baseline metadata and metrics before deciding whether a new reproduction is necessary.",
        }

    def refresh_summary(self, quest_root: Path, *, reason: str | None = None) -> dict:
        recent = self.recent(quest_root, limit=20)
        latest_runs = [item for item in recent if item.get("kind") == "runs"][-5:]
        latest_decisions = [item for item in recent if item.get("kind") == "decisions"][-5:]
        lines = [
            "# Quest Summary",
            "",
            f"- Updated at: {utc_now()}",
            f"- Branch: `{current_branch(quest_root)}`",
            f"- Head: `{head_commit(quest_root) or 'none'}`",
        ]
        if reason:
            lines.extend(["", f"- Refresh reason: {reason}"])
        if latest_decisions:
            lines.extend(["", "## Recent decisions"])
            for item in latest_decisions:
                payload = read_json(Path(item["path"]), {})
                lines.append(f"- `{payload.get('artifact_id')}`: {payload.get('reason', 'No reason provided.')}")
        if latest_runs:
            lines.extend(["", "## Recent runs"])
            for item in latest_runs:
                payload = read_json(Path(item["path"]), {})
                summary = payload.get("summary") or "No summary provided."
                lines.append(f"- `{payload.get('run_id') or payload.get('artifact_id')}`: {summary}")
        summary_path = quest_root / "SUMMARY.md"
        write_text(summary_path, "\n".join(lines).rstrip() + "\n")
        artifact = self.record(
            quest_root,
            {
                "kind": "report",
                "status": "completed",
                "report_type": "summary_refresh",
                "report_id": generate_id("report"),
                "summary": "Quest summary refreshed from recent artifacts.",
                "reason": reason or "Summary refreshed after artifact updates.",
                "paths": {"summary_md": str(summary_path)},
                "source": {"kind": "system", "role": "artifact"},
            },
        )
        return {
            "ok": True,
            "summary_path": str(summary_path),
            "artifact": artifact,
            "guidance": "Use the refreshed SUMMARY.md as the compact quest state for the next turn.",
        }

    def render_git_graph(self, quest_root: Path) -> dict:
        graph_manifest = export_git_graph(quest_root, ensure_dir(quest_root / "artifacts" / "graphs"))
        artifact = self.record(
            quest_root,
            {
                "kind": "graph",
                "status": "generated",
                "graph_id": generate_id("graph"),
                "graph_type": "git_history",
                "summary": "Quest git graph exported.",
                "branch_summary": [graph_manifest.get("branch")],
                "head_commit": graph_manifest.get("head"),
                "commit_count": len(graph_manifest.get("lines", [])),
                "paths": {
                    "svg": graph_manifest.get("svg_path"),
                    "png": graph_manifest.get("png_path"),
                    "json": graph_manifest.get("json_path"),
                },
                "source": {"kind": "daemon"},
            },
            checkpoint=False,
        )
        return {
            "ok": True,
            "guidance": "Share the graph preview when you need to explain the research history or branching state.",
            "graph": graph_manifest,
            "artifact": artifact,
        }

    def interact(
        self,
        quest_root: Path,
        *,
        kind: str = "progress",
        message: str = "",
        response_phase: str = "ack",
        importance: str = "info",
        deliver_to_bound_conversations: bool = True,
        include_recent_inbound_messages: bool = True,
        recent_message_limit: int = 8,
        attachments: list[dict[str, Any]] | None = None,
    ) -> dict:
        durable_kind = {
            "progress": "progress",
            "milestone": "milestone",
            "decision_request": "decision",
            "approval_result": "approval",
        }.get(kind, "progress")
        payload: dict[str, Any] = {
            "kind": durable_kind,
            "status": "active" if durable_kind == "progress" else "completed",
            "message": message,
            "summary": message,
            "interaction_phase": "request" if kind == "decision_request" else response_phase,
            "importance": importance,
            "attachments": attachments or [],
            "source": {"kind": "agent", "role": "pi"},
        }
        if durable_kind == "decision":
            payload.update(
                {
                    "verdict": "pending_user",
                    "action": "continue",
                    "reason": message or "Decision request emitted for user review.",
                }
            )
        if durable_kind == "approval":
            payload.setdefault("reason", message or "Approval result emitted.")
        artifact = self.record(
            quest_root,
            payload,
            checkpoint=durable_kind in {"milestone", "decision", "approval"},
        )
        delivery_targets: list[str] = []
        delivered = False
        if deliver_to_bound_conversations:
            targets = self._bound_conversations(quest_root)
            for target in targets:
                channel_name = self._normalize_channel_name(target)
                payload = {
                    "quest_root": str(quest_root),
                    "quest_id": self._quest_id(quest_root),
                    "conversation_id": target,
                    "kind": kind,
                    "message": message,
                    "response_phase": response_phase,
                    "importance": importance,
                    "artifact_id": artifact.get("artifact_id"),
                    "attachments": attachments or [],
                }
                if self._send_to_channel(channel_name, payload):
                    delivery_targets.append(target)
                    delivered = True

        recent_messages: list[dict[str, Any]] = []
        if include_recent_inbound_messages:
            recent_messages = self._recent_inbound_messages(quest_root, limit=recent_message_limit)

        return {
            "status": "ok",
            "artifact_id": artifact.get("artifact_id"),
            "delivered": delivered,
            "response_phase": response_phase,
            "delivery_targets": delivery_targets,
            "recent_inbound_messages": recent_messages,
            "guidance": "Reply to the newest user message if it changes direction; otherwise continue and refresh plan.md only when needed.",
        }

    def recent(self, quest_root: Path, limit: int = 20) -> list[dict]:
        items: list[dict] = []
        for folder in sorted((quest_root / "artifacts").glob("*")):
            if not folder.is_dir():
                continue
            for path in sorted(folder.glob("*.json")):
                items.append({"path": str(path), "name": path.name, "kind": folder.name})
        return items[-limit:]

    def _build_record(self, quest_root: Path, payload: dict) -> dict:
        timestamp = utc_now()
        kind = payload["kind"]
        artifact_id = payload.get("artifact_id") or payload.get("id") or generate_id(kind)
        quest_id = payload.get("quest_id") or self._quest_id(quest_root)
        status = payload.get("status") or self._default_status(kind)
        source = payload.get("source") or {"kind": "agent"}
        return {
            "kind": kind,
            "schema_version": 1,
            "artifact_id": artifact_id,
            "id": artifact_id,
            "quest_id": quest_id,
            "created_at": payload.get("created_at", timestamp),
            "updated_at": timestamp,
            "source": source,
            "status": status,
            **payload,
        }

    def _artifact_path(self, quest_root: Path, kind: str, artifact_id: str) -> Path:
        directory = ensure_dir(quest_root / "artifacts" / ARTIFACT_DIRS[kind])
        return directory / f"{artifact_id}.json"

    @staticmethod
    def _index_line(record: dict, artifact_path: Path) -> dict:
        return {
            "artifact_id": record.get("artifact_id"),
            "kind": record.get("kind"),
            "status": record.get("status"),
            "quest_id": record.get("quest_id"),
            "path": str(artifact_path),
            "summary": record.get("summary") or record.get("message"),
            "updated_at": record.get("updated_at"),
        }

    @staticmethod
    def _default_status(kind: str) -> str:
        return {
            "progress": "active",
            "decision": "pending",
            "approval": "accepted",
            "graph": "generated",
        }.get(kind, "completed")

    @staticmethod
    def _should_checkpoint(kind: str) -> bool:
        return kind in {"baseline", "decision", "milestone", "run", "report", "approval"}

    def _touch_quest_updated_at(self, quest_root: Path) -> None:
        quest_path = quest_root / "quest.yaml"
        quest_data = read_yaml(quest_path, {})
        quest_data["updated_at"] = utc_now()
        write_yaml(quest_path, quest_data)

    def _quest_id(self, quest_root: Path) -> str:
        quest_yaml = read_yaml(quest_root / "quest.yaml", {})
        return str(quest_yaml.get("quest_id") or quest_root.name)

    def _default_branch_name(
        self,
        quest_root: Path,
        *,
        run_id: str | None,
        idea_id: str | None,
        branch_kind: str,
    ) -> str:
        quest_id = self._quest_id(quest_root)
        if branch_kind == "idea" and idea_id:
            return f"idea/{quest_id}-{idea_id}"
        if branch_kind == "quest":
            return f"quest/{quest_id}"
        return f"run/{run_id or generate_id('run')}"

    def _bound_conversations(self, quest_root: Path) -> list[str]:
        state_path = quest_root / ".ds" / "bindings.json"
        payload = read_json(state_path, {"sources": ["local:default"]})
        sources = payload.get("sources") or ["local:default"]
        return [str(item) for item in sources]

    @staticmethod
    def _normalize_channel_name(target: str) -> str:
        source = (target or "local:default").split(":", 1)[0].strip().lower()
        if source in {"web", "cli", "api", "command", "local", "local-ui"}:
            return "local"
        return source or "local"

    def _send_to_channel(self, channel_name: str, payload: dict[str, Any]) -> bool:
        if channel_name == "local":
            append_jsonl(self.home / "logs" / "connectors" / "local" / "outbox.jsonl", {"sent_at": utc_now(), **payload})
            return True
        if channel_name == "qq":
            append_jsonl(self.home / "logs" / "connectors" / "qq" / "outbox.jsonl", {"sent_at": utc_now(), **payload})
            return True
        return False

    def _recent_inbound_messages(self, quest_root: Path, *, limit: int) -> list[dict]:
        conversation_path = quest_root / ".ds" / "conversations" / "main.jsonl"
        state_path = quest_root / ".ds" / "interaction_state.json"
        cursor = read_json(state_path, {})
        last_seen_id = cursor.get("last_seen_user_message_id")
        messages = [item for item in read_jsonl(conversation_path) if item.get("role") == "user"]
        unseen: list[dict] = []
        if last_seen_id:
            seen = False
            for item in messages:
                if seen:
                    unseen.append(item)
                elif item.get("id") == last_seen_id:
                    seen = True
            if not seen:
                unseen = messages[-limit:]
        else:
            unseen = messages[-limit:]
        if unseen:
            cursor["last_seen_user_message_id"] = unseen[-1].get("id")
            write_json(state_path, cursor)
        return unseen[-limit:]
