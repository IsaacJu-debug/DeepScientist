from __future__ import annotations

import argparse
from typing import Any

from mcp.server.fastmcp import FastMCP

from ..artifact import ArtifactService
from ..memory import MemoryService
from .context import McpContext


def build_memory_server(context: McpContext) -> FastMCP:
    service = MemoryService(context.home)
    server = FastMCP(
        "memory",
        instructions="Quest-aware DeepScientist memory namespace. Prefer quest-local scope when quest context exists.",
        log_level="ERROR",
    )

    @server.tool(name="write", description="Write a Markdown memory card with YAML frontmatter.")
    def write(
        kind: str,
        title: str,
        body: str = "",
        markdown: str | None = None,
        scope: str = "quest",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resolved_scope = _resolve_scope(context, scope)
        quest_root = context.require_quest_root() if resolved_scope == "quest" else None
        return service.write_card(
            scope=resolved_scope,
            kind=kind,
            title=title,
            body=body,
            markdown=markdown,
            quest_root=quest_root,
            quest_id=context.quest_id,
            tags=tags,
            metadata=metadata,
        )

    @server.tool(name="read", description="Read a memory card by id or path.")
    def read(
        card_id: str | None = None,
        path: str | None = None,
        scope: str = "quest",
    ) -> dict[str, Any]:
        resolved_scope = _resolve_scope(context, scope)
        quest_root = context.require_quest_root() if resolved_scope == "quest" else None
        return service.read_card(card_id=card_id, path=path, scope=resolved_scope, quest_root=quest_root)

    @server.tool(name="search", description="Search memory cards by metadata or body text.")
    def search(
        query: str,
        scope: str = "quest",
        limit: int = 10,
        kind: str | None = None,
    ) -> dict[str, Any]:
        resolved_scope = _resolve_search_scope(context, scope)
        quest_root = context.quest_root if resolved_scope in {"quest", "both"} else None
        items = service.search(query, scope=resolved_scope, quest_root=quest_root, limit=limit, kind=kind)
        return {"ok": True, "count": len(items), "items": items}

    @server.tool(name="list_recent", description="List recent memory cards.")
    def list_recent(
        scope: str = "quest",
        limit: int = 10,
        kind: str | None = None,
    ) -> dict[str, Any]:
        resolved_scope = _resolve_search_scope(context, scope)
        if resolved_scope == "both":
            quest_items = service.list_recent(scope="quest", quest_root=context.require_quest_root(), limit=limit, kind=kind)
            global_items = service.list_recent(scope="global", limit=limit, kind=kind)
            items = (quest_items + global_items)[-limit:]
        else:
            quest_root = context.quest_root if resolved_scope == "quest" else None
            items = service.list_recent(scope=resolved_scope, quest_root=quest_root, limit=limit, kind=kind)
        return {"ok": True, "count": len(items), "items": items}

    @server.tool(name="promote_to_global", description="Promote a quest memory card into global memory.")
    def promote_to_global(card_id: str | None = None, path: str | None = None) -> dict[str, Any]:
        return service.promote_to_global(card_id=card_id, path=path, quest_root=context.require_quest_root())

    return server


def build_artifact_server(context: McpContext) -> FastMCP:
    service = ArtifactService(context.home)
    server = FastMCP(
        "artifact",
        instructions="Quest-aware DeepScientist artifact namespace. Git behavior is exposed through artifact only.",
        log_level="ERROR",
    )

    @server.tool(name="record", description="Write a structured artifact record under the current quest.")
    def record(payload: dict[str, Any]) -> dict[str, Any]:
        enriched = dict(payload)
        if context.run_id and "run_id" not in enriched:
            enriched["run_id"] = context.run_id
        if context.active_anchor and "anchor" not in enriched:
            enriched["anchor"] = context.active_anchor
        if context.agent_role:
            source = dict(enriched.get("source") or {})
            source.setdefault("kind", "agent")
            source.setdefault("role", context.agent_role)
            if context.run_id:
                source.setdefault("run_id", context.run_id)
            enriched["source"] = source
        return service.record(context.require_quest_root(), enriched)

    @server.tool(name="checkpoint", description="Create a Git checkpoint in the current quest repository.")
    def checkpoint(message: str, allow_empty: bool = False) -> dict[str, Any]:
        return service.checkpoint(context.require_quest_root(), message, allow_empty=allow_empty)

    @server.tool(name="prepare_branch", description="Prepare an idea or run branch and optional worktree.")
    def prepare_branch(
        run_id: str | None = None,
        idea_id: str | None = None,
        branch: str | None = None,
        branch_kind: str = "run",
        create_worktree_flag: bool = True,
        start_point: str | None = None,
    ) -> dict[str, Any]:
        return service.prepare_branch(
            context.require_quest_root(),
            run_id=run_id or context.run_id,
            idea_id=idea_id,
            branch=branch,
            branch_kind=branch_kind,
            create_worktree_flag=create_worktree_flag,
            start_point=start_point,
        )

    @server.tool(name="publish_baseline", description="Publish a quest baseline to the global baseline registry.")
    def publish_baseline(payload: dict[str, Any]) -> dict[str, Any]:
        enriched = dict(payload)
        enriched.setdefault("source", {"kind": "artifact_publish", "quest_id": context.quest_id, "quest_root": str(context.require_quest_root())})
        return service.publish_baseline(context.require_quest_root(), enriched)

    @server.tool(name="attach_baseline", description="Attach a published baseline to the current quest.")
    def attach_baseline(baseline_id: str, variant_id: str | None = None) -> dict[str, Any]:
        return service.attach_baseline(context.require_quest_root(), baseline_id, variant_id)

    @server.tool(name="refresh_summary", description="Refresh SUMMARY.md from recent artifact state.")
    def refresh_summary(reason: str | None = None) -> dict[str, Any]:
        return service.refresh_summary(context.require_quest_root(), reason=reason)

    @server.tool(name="render_git_graph", description="Render the quest Git graph to JSON, SVG, and PNG.")
    def render_git_graph() -> dict[str, Any]:
        return service.render_git_graph(context.require_quest_root())

    @server.tool(name="interact", description="Send a structured user-facing update and optionally fetch new inbound messages.")
    def interact(
        kind: str = "progress",
        message: str = "",
        response_phase: str = "ack",
        importance: str = "info",
        deliver_to_bound_conversations: bool = True,
        include_recent_inbound_messages: bool = True,
        recent_message_limit: int = 8,
        attachments: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return service.interact(
            context.require_quest_root(),
            kind=kind,
            message=message,
            response_phase=response_phase,
            importance=importance,
            deliver_to_bound_conversations=deliver_to_bound_conversations,
            include_recent_inbound_messages=include_recent_inbound_messages,
            recent_message_limit=recent_message_limit,
            attachments=attachments,
        )

    return server


def _resolve_scope(context: McpContext, scope: str) -> str:
    normalized = (scope or "quest").strip().lower()
    if normalized == "quest" and context.quest_root is None:
        raise ValueError("Quest-local memory call requires quest context.")
    if normalized not in {"quest", "global"}:
        raise ValueError("Scope must be `quest` or `global`.")
    return normalized


def _resolve_search_scope(context: McpContext, scope: str) -> str:
    normalized = (scope or "quest").strip().lower()
    if normalized in {"quest", "both"} and context.quest_root is None:
        return "global"
    if normalized not in {"quest", "global", "both"}:
        raise ValueError("Scope must be `quest`, `global`, or `both`.")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="DeepScientist built-in MCP server")
    parser.add_argument("--namespace", choices=("memory", "artifact"), required=True)
    args = parser.parse_args()
    context = McpContext.from_env()
    if args.namespace == "memory":
        build_memory_server(context).run("stdio")
    else:
        build_artifact_server(context).run("stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
