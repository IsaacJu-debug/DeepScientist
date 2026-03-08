from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from ..artifact import ArtifactService
from ..gitops import export_git_graph
from ..prompts import PromptBuilder
from ..runtime_logs import JsonlLogger
from ..shared import append_jsonl, ensure_dir, read_yaml, utc_now, write_json, write_text
from .base import RunRequest, RunResult


def _iter_event_texts(event: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for key in ("text", "content", "message"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            texts.append(value)
    item = event.get("item")
    if isinstance(item, dict):
        for key in ("text", "content", "message"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                texts.append(value)
        content = item.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    value = block.get("text") or block.get("content")
                    if isinstance(value, str) and value.strip():
                        texts.append(value)
    delta = event.get("delta")
    if isinstance(delta, dict):
        for key in ("text", "content"):
            value = delta.get(key)
            if isinstance(value, str) and value.strip():
                texts.append(value)
    return texts


class CodexRunner:
    def __init__(
        self,
        *,
        home: Path,
        repo_root: Path,
        binary: str,
        logger: JsonlLogger,
        prompt_builder: PromptBuilder,
        artifact_service: ArtifactService,
    ) -> None:
        self.home = home
        self.repo_root = repo_root
        self.binary = binary
        self.logger = logger
        self.prompt_builder = prompt_builder
        self.artifact_service = artifact_service

    def run(self, request: RunRequest) -> RunResult:
        run_root = ensure_dir(request.quest_root / ".ds" / "runs" / request.run_id)
        history_root = ensure_dir(request.quest_root / ".ds" / "codex_history" / request.run_id)
        prompt = self.prompt_builder.build(
            quest_id=request.quest_id,
            skill_id=request.skill_id,
            user_message=request.message,
            model=request.model,
        )
        write_text(run_root / "prompt.md", prompt)

        codex_home = self._prepare_project_codex_home(
            request.quest_root,
            quest_id=request.quest_id,
            run_id=request.run_id,
        )
        command = self._build_command(request, prompt)
        write_json(run_root / "command.json", {"command": command, "codex_home": str(codex_home)})

        env = dict(**os.environ)
        env["CODEX_HOME"] = str(codex_home)
        env["DS_HOME"] = str(self.home)
        env["DS_QUEST_ID"] = request.quest_id
        env["DS_QUEST_ROOT"] = str(request.quest_root)
        env["DS_RUN_ID"] = request.run_id
        quest_yaml = read_yaml(request.quest_root / "quest.yaml", {})
        env["DS_ACTIVE_ANCHOR"] = str(quest_yaml.get("active_anchor", "baseline"))
        env["DS_CONVERSATION_ID"] = f"quest:{request.quest_id}"
        env["DS_AGENT_ROLE"] = request.skill_id
        env["DS_TEAM_MODE"] = "single"
        process = subprocess.Popen(
            command,
            cwd=str(request.quest_root),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert process.stdin is not None
        assert process.stdout is not None
        assert process.stderr is not None
        process.stdin.write(prompt)
        process.stdin.close()

        output_parts: list[str] = []
        history_events = history_root / "events.jsonl"
        stdout_events = run_root / "stdout.jsonl"

        for raw_line in process.stdout:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                payload = {"raw": line}
            append_jsonl(history_events, {"timestamp": utc_now(), "event": payload})
            append_jsonl(stdout_events, {"timestamp": utc_now(), "line": line})
            for chunk in _iter_event_texts(payload):
                output_parts.append(chunk)

        stderr_text = process.stderr.read()
        exit_code = process.wait()
        output_text = "\n".join(part.strip() for part in output_parts if part.strip()).strip()
        write_text(history_root / "assistant.md", (output_text or "") + ("\n" if output_text else ""))
        write_text(run_root / "stderr.txt", stderr_text)
        result_payload = {
            "ok": exit_code == 0,
            "run_id": request.run_id,
            "model": request.model,
            "exit_code": exit_code,
            "history_root": str(history_root),
            "run_root": str(run_root),
            "output_text": output_text,
            "stderr_text": stderr_text,
            "completed_at": utc_now(),
        }
        write_json(run_root / "result.json", result_payload)
        write_json(history_root / "meta.json", result_payload)
        self.logger.log(
            "info",
            "runner.codex.completed",
            quest_id=request.quest_id,
            run_id=request.run_id,
            model=request.model,
            exit_code=exit_code,
        )
        artifact_result = self.artifact_service.record(
            request.quest_root,
            {
                "kind": "run",
                "run_id": request.run_id,
                "run_kind": request.skill_id,
                "model": request.model,
                "summary": output_text[:1000],
                "history_root": str(history_root),
                "run_root": str(run_root),
                "exit_code": exit_code,
            },
        )
        export_git_graph(request.quest_root, request.quest_root / "artifacts" / "graphs")
        write_json(run_root / "artifact.json", artifact_result)
        return RunResult(
            ok=exit_code == 0,
            run_id=request.run_id,
            model=request.model,
            output_text=output_text,
            exit_code=exit_code,
            history_root=history_root,
            run_root=run_root,
            stderr_text=stderr_text,
        )

    def _build_command(self, request: RunRequest, prompt: str) -> list[str]:
        command = [
            shutil.which(self.binary) or self.binary,
            "exec",
            "--json",
            "--cd",
            str(request.quest_root),
            "--skip-git-repo-check",
            "--model",
            request.model,
        ]
        if request.approval_policy == "never":
            command.extend(["--ask-for-approval", "never"])
        elif request.approval_policy == "on-request":
            command.append("--full-auto")
        if request.sandbox_mode:
            command.extend(["--sandbox", request.sandbox_mode])
        command.append("-")
        return command

    def _prepare_project_codex_home(self, quest_root: Path, *, quest_id: str, run_id: str) -> Path:
        target = ensure_dir(quest_root / ".codex")
        source = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
        for filename in ("config.toml", "auth.json"):
            source_path = source / filename
            target_path = target / filename
            if source_path.exists() and not target_path.exists():
                shutil.copy2(source_path, target_path)
        ensure_dir(target / "skills")
        self._inject_built_in_mcp(target, quest_root=quest_root, quest_id=quest_id, run_id=run_id)
        return target

    def _inject_built_in_mcp(self, codex_home: Path, *, quest_root: Path, quest_id: str, run_id: str) -> None:
        config_path = codex_home / "config.toml"
        existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
        marker_start = "# BEGIN DEEPSCIENTIST BUILTINS"
        marker_end = "# END DEEPSCIENTIST BUILTINS"
        if marker_start in existing and marker_end in existing:
            prefix = existing.split(marker_start, 1)[0].rstrip()
        else:
            prefix = existing.rstrip()

        pythonpath = os.environ.get("PYTHONPATH", "")
        shared_env = {
            "DS_HOME": str(self.home),
            "DS_QUEST_ID": quest_id,
            "DS_QUEST_ROOT": str(quest_root),
            "DS_RUN_ID": run_id,
            "DS_ACTIVE_ANCHOR": str(read_yaml(quest_root / "quest.yaml", {}).get("active_anchor", "baseline")),
            "DS_CONVERSATION_ID": f"quest:{quest_id}",
            "DS_AGENT_ROLE": "pi",
            "DS_TEAM_MODE": "single",
        }
        if pythonpath:
            shared_env["PYTHONPATH"] = pythonpath

        block = "\n".join(
            [
                marker_start,
                self._mcp_block("memory", shared_env),
                "",
                self._mcp_block("artifact", shared_env),
                marker_end,
            ]
        ).strip()
        new_text = f"{prefix}\n\n{block}\n" if prefix else f"{block}\n"
        write_text(config_path, new_text)

    @staticmethod
    def _mcp_block(name: str, env: dict[str, str]) -> str:
        args = ["-m", "deepscientist.mcp.server", "--namespace", name]
        lines = [
            f"[mcp_servers.{name}]",
            f'command = "{sys.executable}"',
            f"args = [{', '.join(json.dumps(item) for item in args)}]",
            "",
            f"[mcp_servers.{name}.env]",
        ]
        for key, value in env.items():
            lines.append(f"{key} = {json.dumps(value)}")
        return "\n".join(lines)
