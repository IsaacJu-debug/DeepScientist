from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from urllib.parse import parse_qs

from ...gitops import export_git_graph
from ...shared import generate_id, read_text, resolve_within
from ...runners import RunRequest


class ApiHandlers:
    def __init__(self, app: "DaemonApp") -> None:
        self.app = app

    def root(self) -> tuple[int, dict, str]:
        html = (self.app.repo_root / "ui" / "index.html").read_text(encoding="utf-8")
        return 200, {"Content-Type": "text/html; charset=utf-8"}, html

    def ui_asset(self, ui_path: str) -> tuple[int, dict, bytes]:
        ui_root = self.app.repo_root / "ui"
        path = resolve_within(ui_root, ui_path)
        if not path.exists() or not path.is_file():
            return 404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not Found"
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return 200, {"Content-Type": mime_type}, path.read_bytes()

    def health(self) -> dict:
        return {
            "status": "ok",
            "home": str(self.app.home),
            "sessions": self.app.sessions.snapshot(),
        }

    def connectors(self) -> list[dict]:
        return [channel.status() for channel in self.app.channels.values()]

    def quests(self) -> list[dict]:
        return self.app.quest_service.list_quests()

    def quest_create(self, body: dict) -> dict:
        goal = body.get("goal", "").strip()
        if not goal:
            return {"ok": False, "message": "Quest goal is required."}
        snapshot = self.app.quest_service.create(goal=goal)
        return {"ok": True, "snapshot": snapshot}

    def quest(self, quest_id: str) -> dict:
        return self.app.quest_service.snapshot(quest_id)

    def history(self, quest_id: str) -> list[dict]:
        return self.app.quest_service.history(quest_id)

    def graph(self, quest_id: str) -> dict:
        quest_root = self.app.quest_service._quest_root(quest_id)
        return export_git_graph(quest_root, quest_root / "artifacts" / "graphs")

    def runs(self, quest_id: str) -> list[dict]:
        return self.app.quest_service.snapshot(quest_id).get("recent_runs", [])

    def quest_memory(self, quest_id: str) -> list[dict]:
        return self.app.memory_service.list_cards(
            scope="quest",
            quest_root=self.app.quest_service._quest_root(quest_id),
        )

    def documents(self, quest_id: str) -> list[dict]:
        return self.app.quest_service.list_documents(quest_id)

    def document_open(self, quest_id: str, body: dict) -> dict:
        return self.app.quest_service.open_document(quest_id, body["document_id"])

    def document_save(self, quest_id: str, document_id: str, body: dict) -> dict:
        return self.app.quest_service.save_document(
            quest_id,
            document_id,
            body["content"],
            previous_revision=body.get("revision"),
        )

    def chat(self, quest_id: str, body: dict) -> dict:
        text = body.get("text", "").strip()
        if not text:
            return {"ok": False, "message": "Empty message."}
        self.app.sessions.bind(quest_id, body.get("source", "api"))
        message = self.app.quest_service.append_message(
            quest_id,
            role="user",
            content=text,
            source=body.get("source", "api"),
        )
        return {
            "ok": True,
            "ack": f"Received for {quest_id}. Stored and ready for plan refresh.",
            "message": message,
        }

    def command(self, quest_id: str, body: dict) -> dict:
        command = body.get("command", "").strip()
        if command in {"/status", "status"}:
            return {"ok": True, "type": "status", "snapshot": self.quest(quest_id)}
        if command in {"/graph", "graph"}:
            return {"ok": True, "type": "graph", "graph": self.graph(quest_id)}
        if command.startswith("/note "):
            note = command.split(" ", 1)[1]
            self.app.quest_service.append_message(quest_id, role="user", content=note, source="command")
            return {"ok": True, "type": "ack", "message": "Note stored."}
        return {
            "ok": True,
            "type": "ack",
            "message": f"Command `{command}` is accepted by the skeleton but not fully implemented yet.",
        }

    def run_create(self, quest_id: str, body: dict) -> dict:
        quest_root = self.app.quest_service._quest_root(quest_id)
        runners = self.app.config_manager.load_named("runners")
        codex_cfg = runners.get("codex", {})
        request = RunRequest(
            quest_id=quest_id,
            quest_root=quest_root,
            run_id=body.get("run_id") or generate_id("run"),
            skill_id=body.get("skill_id", "decision"),
            message=body.get("message", "").strip(),
            model=body.get("model") or codex_cfg.get("model", "gpt-5.4"),
            approval_policy=codex_cfg.get("approval_policy", "on-request"),
            sandbox_mode=codex_cfg.get("sandbox_mode", "workspace-write"),
        )
        result = self.app.codex_runner.run(request)
        if result.output_text:
            self.app.quest_service.append_message(
                quest_id,
                role="assistant",
                content=result.output_text,
                source="codex",
            )
        return {
            "ok": result.ok,
            "run_id": result.run_id,
            "model": result.model,
            "exit_code": result.exit_code,
            "history_root": str(result.history_root),
            "run_root": str(result.run_root),
            "output_text": result.output_text,
            "stderr_text": result.stderr_text,
        }

    def memory(self, query: dict[str, list[str]]) -> list[dict]:
        term = (query.get("q") or [""])[0]
        if not term:
            return self.app.memory_service.list_cards(scope="global")
        return self.app.memory_service.search(term, scope="global")

    def config_files(self) -> list[dict]:
        return [
            {
                "name": item.name,
                "path": str(item.path),
                "required": item.required,
                "exists": item.exists,
            }
            for item in self.app.config_manager.list_files()
        ]

    def config_show(self, name: str) -> dict:
        content = self.app.config_manager.load_named_text(name, create_optional=True)
        path = self.app.config_manager.path_for(name)
        from ...shared import sha256_text, utc_now

        return {
            "document_id": name,
            "title": path.name,
            "path": str(path),
            "kind": "code",
            "scope": "config",
            "writable": True,
            "encoding": "utf-8",
            "source_scope": "config",
            "content": content,
            "revision": f"sha256:{sha256_text(content)}",
            "updated_at": utc_now(),
            "meta": {
                "tags": [name],
                "source_kind": "config_file",
                "renderer_hint": "code",
            },
        }

    def config_save(self, name: str, body: dict) -> dict:
        return self.app.config_manager.save_named_text(name, body.get("content", ""))

    def config_validate(self, body: dict | None = None) -> dict:
        if body and "name" in body and "content" in body:
            return self.app.config_manager.validate_named_text(body["name"], body["content"])
        return self.app.config_manager.validate_all()

    def asset(self, asset_path: str) -> tuple[int, dict, bytes]:
        asset_root = self.app.repo_root / "assets"
        path = resolve_within(asset_root, asset_path)
        if not path.exists() or not path.is_file():
            return 404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not Found"
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return 200, {"Content-Type": mime_type}, path.read_bytes()

    @staticmethod
    def parse_query(path: str) -> dict[str, list[str]]:
        if "?" not in path:
            return {}
        return parse_qs(path.split("?", 1)[1], keep_blank_values=True)

    @staticmethod
    def parse_body(raw: bytes) -> dict:
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    @staticmethod
    def error(message: str, code: int = 400) -> tuple[int, dict]:
        return code, {"ok": False, "message": message}
