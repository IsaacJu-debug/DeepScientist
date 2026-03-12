from __future__ import annotations

import asyncio
from pathlib import Path

from deepscientist.artifact import ArtifactService
from deepscientist.config import ConfigManager
from deepscientist.home import ensure_home_layout, repo_root
from deepscientist.mcp.context import McpContext
from deepscientist.mcp.server import build_artifact_server, build_bash_exec_server, build_memory_server
from deepscientist.quest import QuestService
from deepscientist.skills import SkillInstaller


def _unwrap_tool_result(result):
    if isinstance(result, tuple) and len(result) == 2:
        return result[1]
    return result


def test_memory_mcp_server_tools_cover_core_flows(temp_home: Path) -> None:
    async def scenario() -> None:
        ensure_home_layout(temp_home)
        ConfigManager(temp_home).ensure_files()
        quest = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home)).create("mcp memory quest")
        quest_root = Path(quest["quest_root"])
        context = McpContext(
            home=temp_home,
            quest_id=quest["quest_id"],
            quest_root=quest_root,
            run_id="run-mcp-memory",
            active_anchor="baseline",
            conversation_id="quest:test",
            agent_role="baseline",
            worker_id="worker-main",
            worktree_root=None,
            team_mode="single",
        )
        server = build_memory_server(context)

        assert [tool.name for tool in await server.list_tools()] == [
            "write",
            "read",
            "search",
            "list_recent",
            "promote_to_global",
        ]

        write_result = _unwrap_tool_result(
            await server.call_tool(
                "write",
                {
                    "kind": "knowledge",
                    "title": "MCP Memory Demo",
                    "body": "memory body",
                    "tags": ["mcp"],
                },
            )
        )
        assert write_result["scope"] == "quest"
        assert Path(write_result["path"]).exists()

        read_result = _unwrap_tool_result(await server.call_tool("read", {"card_id": write_result["id"]}))
        assert read_result["id"] == write_result["id"]
        assert "memory body" in read_result["body"]

        search_result = _unwrap_tool_result(await server.call_tool("search", {"query": "memory", "scope": "quest"}))
        assert search_result["ok"] is True
        assert search_result["count"] >= 1
        assert any(item["id"] == write_result["id"] for item in search_result["items"])

        recent_result = _unwrap_tool_result(await server.call_tool("list_recent", {"scope": "both"}))
        assert recent_result["ok"] is True
        assert recent_result["count"] >= 1

        promote_result = _unwrap_tool_result(await server.call_tool("promote_to_global", {"card_id": write_result["id"]}))
        assert promote_result["scope"] == "global"
        assert Path(promote_result["path"]).exists()

    asyncio.run(scenario())


def test_artifact_mcp_server_tools_cover_core_flows(temp_home: Path) -> None:
    async def scenario() -> None:
        ensure_home_layout(temp_home)
        ConfigManager(temp_home).ensure_files()
        quest = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home)).create("mcp artifact quest")
        quest_root = Path(quest["quest_root"])
        context = McpContext(
            home=temp_home,
            quest_id=quest["quest_id"],
            quest_root=quest_root,
            run_id="run-mcp-artifact",
            active_anchor="baseline",
            conversation_id="quest:test",
            agent_role="pi",
            worker_id="worker-main",
            worktree_root=None,
            team_mode="single",
        )
        server = build_artifact_server(context)

        assert [tool.name for tool in await server.list_tools()] == [
            "record",
            "checkpoint",
            "prepare_branch",
            "submit_idea",
            "record_main_experiment",
            "create_analysis_campaign",
            "record_analysis_slice",
            "publish_baseline",
            "attach_baseline",
            "confirm_baseline",
            "waive_baseline",
            "arxiv",
            "refresh_summary",
            "render_git_graph",
            "interact",
        ]

        record_result = _unwrap_tool_result(
            await server.call_tool(
                "record",
                {
                    "payload": {
                        "kind": "report",
                        "status": "completed",
                        "report_type": "mcp-test",
                        "summary": "artifact record ok",
                    }
                },
            )
        )
        assert record_result["ok"] is True
        assert record_result["record"]["source"]["role"] == "pi"
        assert record_result["record"]["run_id"] == "run-mcp-artifact"
        assert Path(record_result["path"]).exists()

        checkpoint_result = _unwrap_tool_result(
            await server.call_tool(
                "checkpoint",
                {
                    "message": "mcp artifact checkpoint",
                    "allow_empty": True,
                },
            )
        )
        assert checkpoint_result["ok"] is True
        assert "head" in checkpoint_result

        branch_result = _unwrap_tool_result(
            await server.call_tool(
                "prepare_branch",
                {
                    "run_id": "run-branch-001",
                    "branch_kind": "run",
                    "create_worktree_flag": False,
                },
            )
        )
        assert branch_result["ok"] is True
        assert branch_result["branch"].startswith("run/")

        publish_result = _unwrap_tool_result(
            await server.call_tool(
                "publish_baseline",
                {
                    "payload": {
                        "baseline_id": "mcp-baseline",
                        "name": "MCP Baseline",
                        "summary": "published from mcp server test",
                        "primary_metric": {"name": "accuracy", "value": 0.9},
                        "metrics_summary": {"accuracy": 0.9},
                        "baseline_variants": [{"variant_id": "main", "label": "Main"}],
                        "default_variant_id": "main",
                    }
                },
            )
        )
        assert publish_result["ok"] is True
        assert publish_result["baseline_registry_entry"]["baseline_id"] == "mcp-baseline"
        baseline_root = quest_root / "baselines" / "local" / "mcp-baseline"
        baseline_root.mkdir(parents=True, exist_ok=True)
        (baseline_root / "README.md").write_text("# MCP Baseline\n", encoding="utf-8")

        attach_result = _unwrap_tool_result(
            await server.call_tool(
                "attach_baseline",
                {
                    "baseline_id": "mcp-baseline",
                    "variant_id": "main",
                },
            )
        )
        assert attach_result["ok"] is True
        assert attach_result["attachment"]["source_variant_id"] == "main"

        confirm_result = _unwrap_tool_result(
            await server.call_tool(
                "confirm_baseline",
                {
                    "baseline_path": "baselines/imported/mcp-baseline",
                    "baseline_id": "mcp-baseline",
                    "variant_id": "main",
                    "summary": "MCP baseline confirmed",
                },
            )
        )
        assert confirm_result["ok"] is True
        assert confirm_result["baseline_gate"] == "confirmed"
        assert confirm_result["confirmed_baseline_ref"]["baseline_id"] == "mcp-baseline"

        idea_result = _unwrap_tool_result(
            await server.call_tool(
                "submit_idea",
                {
                    "mode": "create",
                    "title": "Adapter route",
                    "problem": "Baseline saturates.",
                    "hypothesis": "A lightweight adapter helps.",
                    "mechanism": "Insert a residual adapter.",
                    "decision_reason": "Promote the strongest current idea.",
                },
            )
        )
        assert idea_result["ok"] is True
        assert idea_result["branch"].startswith(f"idea/{quest['quest_id']}-")
        assert Path(idea_result["worktree_root"]).exists()

        main_result = _unwrap_tool_result(
            await server.call_tool(
                "record_main_experiment",
                {
                    "run_id": "main-mcp-001",
                    "title": "Main MCP run",
                    "hypothesis": "Adapter improves accuracy.",
                    "setup": "Use baseline recipe.",
                    "execution": "Ran full validation.",
                    "results": "Accuracy improved.",
                    "conclusion": "Ready for follow-up.",
                    "metric_rows": [{"metric_id": "accuracy", "value": 0.93}],
                },
            )
        )
        assert main_result["ok"] is True
        assert Path(main_result["result_json_path"]).exists()
        assert main_result["progress_eval"]["breakthrough"] is True

        campaign_result = _unwrap_tool_result(
            await server.call_tool(
                "create_analysis_campaign",
                {
                    "campaign_title": "Ablation suite",
                    "campaign_goal": "Stress-test the promoted idea.",
                    "slices": [
                        {
                            "slice_id": "ablation",
                            "title": "Adapter ablation",
                            "goal": "Disable the adapter and compare.",
                            "required_changes": "Disable adapter only.",
                            "metric_contract": "Report full validation metrics.",
                        }
                    ],
                },
            )
        )
        assert campaign_result["ok"] is True
        assert campaign_result["campaign_id"]
        assert Path(campaign_result["slices"][0]["worktree_root"]).exists()

        slice_result = _unwrap_tool_result(
            await server.call_tool(
                "record_analysis_slice",
                {
                    "campaign_id": campaign_result["campaign_id"],
                    "slice_id": "ablation",
                    "setup": "Disable the adapter only.",
                    "execution": "Ran the full validation sweep.",
                    "results": "Accuracy dropped as expected.",
                    "metric_rows": [{"name": "acc", "value": 0.84}],
                    "evidence_paths": ["experiments/analysis/ablation/result.json"],
                },
            )
        )
        assert slice_result["ok"] is True
        assert slice_result["completed"] is True
        assert slice_result["returned_to_branch"] == idea_result["branch"]

        summary_result = _unwrap_tool_result(await server.call_tool("refresh_summary", {"reason": "mcp test"}))
        assert summary_result["ok"] is True
        assert Path(summary_result["summary_path"]).exists()

        graph_result = _unwrap_tool_result(await server.call_tool("render_git_graph", {}))
        assert graph_result["ok"] is True
        assert Path(graph_result["graph"]["json_path"]).exists()

        interact_result = _unwrap_tool_result(
            await server.call_tool(
                "interact",
                {
                    "kind": "progress",
                    "message": "mcp interact ok",
                    "deliver_to_bound_conversations": False,
                },
            )
        )
        assert interact_result["status"] == "ok"
        assert interact_result["delivered"] is False

    asyncio.run(scenario())


def test_artifact_mcp_server_arxiv_tool_calls_service(temp_home: Path, monkeypatch) -> None:
    async def scenario() -> None:
        ensure_home_layout(temp_home)
        ConfigManager(temp_home).ensure_files()
        quest = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home)).create("mcp arxiv quest")
        quest_root = Path(quest["quest_root"])
        context = McpContext(
            home=temp_home,
            quest_id=quest["quest_id"],
            quest_root=quest_root,
            run_id="run-mcp-arxiv",
            active_anchor="scout",
            conversation_id="quest:test",
            agent_role="scout",
            worker_id="worker-main",
            worktree_root=None,
            team_mode="single",
        )
        calls: list[tuple[str, bool]] = []

        def fake_arxiv(self, paper_id: str, *, full_text: bool = False) -> dict[str, object]:  # noqa: ANN001
            calls.append((paper_id, full_text))
            return {
                "ok": True,
                "paper_id": paper_id,
                "requested_full_text": full_text,
                "content_mode": "overview",
                "source": "test",
                "content": "# Fake Paper",
            }

        monkeypatch.setattr(ArtifactService, "arxiv", fake_arxiv)
        server = build_artifact_server(context)
        result = _unwrap_tool_result(
            await server.call_tool(
                "arxiv",
                {
                    "paper_id": "2010.11929",
                    "full_text": True,
                },
            )
        )

        assert result["ok"] is True
        assert result["paper_id"] == "2010.11929"
        assert calls == [("2010.11929", True)]

    asyncio.run(scenario())


def test_bash_exec_mcp_server_supports_detach_read_list_and_kill(temp_home: Path) -> None:
    async def scenario() -> None:
        ensure_home_layout(temp_home)
        ConfigManager(temp_home).ensure_files()
        quest = QuestService(temp_home, skill_installer=SkillInstaller(repo_root(), temp_home)).create("mcp bash quest")
        quest_root = Path(quest["quest_root"])
        context = McpContext(
            home=temp_home,
            quest_id=quest["quest_id"],
            quest_root=quest_root,
            run_id="run-mcp-bash",
            active_anchor="experiment",
            conversation_id=f"quest:{quest['quest_id']}",
            agent_role="pi",
            worker_id="worker-main",
            worktree_root=None,
            team_mode="single",
        )
        server = build_bash_exec_server(context)

        assert [tool.name for tool in await server.list_tools()] == ["bash_exec"]

        detached = _unwrap_tool_result(
            await server.call_tool(
                "bash_exec",
                {
                    "command": "printf 'alpha\\n'; sleep 5; printf 'omega\\n'",
                    "mode": "detach",
                },
            )
        )
        assert detached["status"] == "running"
        bash_id = detached["bash_id"]
        await asyncio.sleep(0.8)

        listing = _unwrap_tool_result(await server.call_tool("bash_exec", {"mode": "list"}))
        assert listing["count"] >= 1
        assert any(item["bash_id"] == bash_id for item in listing["items"])

        read_back = _unwrap_tool_result(await server.call_tool("bash_exec", {"mode": "read", "id": bash_id}))
        assert read_back["bash_id"] == bash_id
        assert "alpha" in read_back["log"]

        stopped = _unwrap_tool_result(
            await server.call_tool(
                "bash_exec",
                {
                    "mode": "kill",
                    "id": bash_id,
                    "reason": "pytest-stop",
                },
            )
        )
        assert stopped["bash_id"] == bash_id
        assert stopped["status"] in {"terminating", "terminated"}

        awaited = _unwrap_tool_result(
            await server.call_tool("bash_exec", {"mode": "await", "id": bash_id, "timeout_seconds": 10})
        )
        assert awaited["bash_id"] == bash_id
        assert awaited["status"] == "terminated"
        assert Path(quest_root / awaited["log_path"]).exists()

    asyncio.run(scenario())
