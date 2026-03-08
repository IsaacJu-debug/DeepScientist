from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ..artifact import ArtifactService
from ..channels import LocalChannel, QQRelayChannel, register_channel
from ..cloud import CloudLinkService
from ..config import ConfigManager
from ..home import repo_root
from ..memory import MemoryService
from ..prompts import PromptBuilder
from ..quest import QuestService
from ..runners import CodexRunner, register_runner
from ..runtime_logs import JsonlLogger
from ..skills import SkillInstaller
from ..team import SingleTeamService
from .api import ApiHandlers, match_route
from .sessions import SessionStore


class DaemonApp:
    def __init__(self, home: Path) -> None:
        self.home = home
        self.repo_root = repo_root()
        self.config_manager = ConfigManager(home)
        self.runners_config = self.config_manager.load_named("runners")
        self.skill_installer = SkillInstaller(self.repo_root, home)
        self.quest_service = QuestService(home, skill_installer=self.skill_installer)
        self.memory_service = MemoryService(home)
        self.artifact_service = ArtifactService(home)
        self.team_service = SingleTeamService(home)
        self.cloud_service = CloudLinkService(home)
        config = self.config_manager.load_named("config")
        self.logger = JsonlLogger(home / "logs", level=config.get("logging", {}).get("level", "info"))
        self.prompt_builder = PromptBuilder(self.repo_root, home)
        self.codex_runner = CodexRunner(
            home=home,
            repo_root=self.repo_root,
            binary=self.runners_config.get("codex", {}).get("binary", "codex"),
            logger=self.logger,
            prompt_builder=self.prompt_builder,
            artifact_service=self.artifact_service,
        )
        register_runner("codex", lambda **_: self.codex_runner)
        register_channel("local", lambda **_: LocalChannel(home))
        register_channel("qq", lambda **_: QQRelayChannel(home))
        self.channels = {
            "local": LocalChannel(home),
            "qq": QQRelayChannel(home),
        }
        self.sessions = SessionStore()
        self.handlers = ApiHandlers(self)

    def serve(self, host: str, port: int) -> None:
        app = self

        class RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, format: str, *args) -> None:
                return

            def do_GET(self) -> None:  # noqa: N802
                self._dispatch("GET")

            def do_POST(self) -> None:  # noqa: N802
                self._dispatch("POST")

            def do_PUT(self) -> None:  # noqa: N802
                self._dispatch("PUT")

            def _dispatch(self, method: str) -> None:
                parsed = urlparse(self.path)
                route_name, params = match_route(method, parsed.path)
                if route_name is None:
                    self._write_json(404, {"ok": False, "message": "Not Found"})
                    return

                content_length = int(self.headers.get("Content-Length", "0"))
                raw_body = self.rfile.read(content_length) if content_length else b""
                body = {}
                if raw_body and self.headers.get("Content-Type", "").startswith("application/json"):
                    body = app.handlers.parse_body(raw_body)

                try:
                    result = getattr(app.handlers, route_name)
                    if route_name == "asset":
                        status, headers, content = result(**params)
                        self.send_response(status)
                        for key, value in headers.items():
                            self.send_header(key, value)
                        self.end_headers()
                        self.wfile.write(content)
                        return
                    if method == "GET":
                        payload = result(**params) if params else result()
                    elif route_name in {"document_open", "chat", "command", "config_save", "quest_create", "run_create"}:
                        payload = result(**params, body=body)
                    elif route_name == "config_validate":
                        payload = result(body)
                    elif method == "PUT":
                        payload = result(**params, body=body)
                    elif route_name == "memory":
                        payload = result(app.handlers.parse_query(self.path))
                    else:
                        payload = result(**params) if params else result()
                except Exception as exc:
                    self._write_json(500, {"ok": False, "message": str(exc)})
                    return

                if isinstance(payload, tuple) and len(payload) == 3:
                    status, headers, content = payload
                    self.send_response(status)
                    for key, value in headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    if isinstance(content, str):
                        self.wfile.write(content.encode("utf-8"))
                    else:
                        self.wfile.write(content)
                    return
                self._write_json(200, payload)

            def _write_json(self, code: int, payload: dict | list) -> None:
                encoded = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
                self.send_response(code)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

        server = ThreadingHTTPServer((host, port), RequestHandler)
        print(f"DeepScientist daemon listening on http://{host}:{port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
