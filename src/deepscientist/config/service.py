from __future__ import annotations

from pathlib import Path

from ..shared import read_text, read_yaml, run_command, sha256_text, utc_now, which, write_text, write_yaml
from .models import (
    CONFIG_NAMES,
    OPTIONAL_CONFIG_NAMES,
    REQUIRED_CONFIG_NAMES,
    ConfigFileInfo,
    config_filename,
    default_payload,
)


class ConfigManager:
    def __init__(self, home: Path) -> None:
        self.home = home
        self.config_root = home / "config"

    def path_for(self, name: str) -> Path:
        if name not in CONFIG_NAMES:
            raise KeyError(f"Unknown config name: {name}")
        return self.config_root / config_filename(name)

    def ensure_files(self) -> list[Path]:
        created: list[Path] = []
        for name in REQUIRED_CONFIG_NAMES:
            path = self.path_for(name)
            if not path.exists():
                write_yaml(path, default_payload(name, self.home))
                created.append(path)
        return created

    def ensure_optional_file(self, name: str) -> Path:
        if name not in OPTIONAL_CONFIG_NAMES:
            raise KeyError(f"{name} is not an optional config file")
        path = self.path_for(name)
        if not path.exists():
            write_yaml(path, default_payload(name, self.home))
        return path

    def list_files(self) -> list[ConfigFileInfo]:
        items: list[ConfigFileInfo] = []
        for name in CONFIG_NAMES:
            path = self.path_for(name)
            items.append(
                ConfigFileInfo(
                    name=name,
                    path=path,
                    required=name in REQUIRED_CONFIG_NAMES,
                    exists=path.exists(),
                )
            )
        return items

    def load_named(self, name: str, create_optional: bool = False) -> dict:
        path = self.path_for(name)
        if create_optional and name in OPTIONAL_CONFIG_NAMES and not path.exists():
            self.ensure_optional_file(name)
        return read_yaml(path, default_payload(name, self.home))

    def load_named_text(self, name: str, create_optional: bool = False) -> str:
        path = self.path_for(name)
        if create_optional and name in OPTIONAL_CONFIG_NAMES and not path.exists():
            self.ensure_optional_file(name)
        if path.exists():
            return read_text(path)
        payload = default_payload(name, self.home)
        write_yaml(path, payload)
        return read_text(path)

    def save_named_text(self, name: str, content: str) -> dict:
        validation = self.validate_named_text(name, content)
        if not validation["ok"]:
            return validation
        path = self.path_for(name)
        write_text(path, content)
        return {
            "ok": True,
            "document_id": name,
            "path": str(path),
            "saved_at": utc_now(),
            "revision": f"sha256:{sha256_text(content)}",
            "conflict": False,
            "warnings": validation["warnings"],
            "errors": [],
        }

    def validate_named_text(self, name: str, content: str) -> dict:
        try:
            from ..shared import require_yaml

            require_yaml()
            import yaml

            parsed = yaml.safe_load(content) if content.strip() else {}
        except Exception as exc:
            return {
                "ok": False,
                "warnings": [],
                "errors": [str(exc)],
                "name": name,
            }
        warnings: list[str] = []
        if parsed is None:
            parsed = {}
        if not isinstance(parsed, dict):
            return {
                "ok": False,
                "warnings": warnings,
                "errors": ["Top-level YAML value must be a mapping."],
                "name": name,
            }
        return {
            "ok": True,
            "warnings": warnings,
            "errors": [],
            "name": name,
            "parsed": parsed,
        }

    def validate_all(self) -> dict:
        results = []
        for info in self.list_files():
            if info.required and not info.exists:
                self.ensure_files()
            if not info.exists and not info.required:
                results.append(
                    {
                        "name": info.name,
                        "ok": True,
                        "warnings": ["Optional config file is missing and may be created lazily."],
                        "errors": [],
                    }
                )
                continue
            results.append(self.validate_named_text(info.name, self.load_named_text(info.name)))
        return {
            "ok": all(item["ok"] for item in results),
            "files": results,
        }

    def git_readiness(self) -> dict:
        git_binary = which("git")
        if git_binary is None:
            return {
                "ok": False,
                "installed": False,
                "user_name": "",
                "user_email": "",
                "warnings": [],
                "errors": ["`git` is not installed or not on PATH."],
                "guidance": [
                    "Install Git first.",
                ],
            }

        def get_value(key: str) -> str:
            try:
                result = run_command(["git", "config", "--get", key], check=False)
            except Exception:
                return ""
            return result.stdout.strip()

        user_name = get_value("user.name")
        user_email = get_value("user.email")
        warnings: list[str] = []
        guidance: list[str] = []
        if not user_name:
            warnings.append("Git user.name is missing.")
            guidance.append('git config --global user.name "Your Name"')
        if not user_email:
            warnings.append("Git user.email is missing.")
            guidance.append('git config --global user.email "you@example.com"')
        return {
            "ok": True,
            "installed": True,
            "user_name": user_name,
            "user_email": user_email,
            "warnings": warnings,
            "errors": [],
            "guidance": guidance,
        }
