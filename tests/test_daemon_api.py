from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from urllib.request import Request, urlopen

from deepscientist.config import ConfigManager
from deepscientist.home import ensure_home_layout


def _get_json(url: str):
    with urlopen(url) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def test_daemon_serves_health_and_ui(temp_home: Path, project_root: Path, pythonpath_env) -> None:
    ensure_home_layout(temp_home)
    ConfigManager(temp_home).ensure_files()
    new_process = subprocess.run(
        [
            "python3",
            "-m",
            "deepscientist.cli",
            "--home",
            str(temp_home),
            "new",
            "daemon api quest",
        ],
        cwd=project_root,
        check=True,
        capture_output=True,
        text=True,
    )
    quest_id = json.loads(new_process.stdout)["quest_id"]

    server = subprocess.Popen(
        [
            "python3",
            "-m",
            "deepscientist.cli",
            "--home",
            str(temp_home),
            "daemon",
            "--host",
            "127.0.0.1",
            "--port",
            "20901",
        ],
        cwd=project_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        time.sleep(2)
        health = _get_json("http://127.0.0.1:20901/api/health")
        assert health["status"] == "ok"
        quest = _get_json(f"http://127.0.0.1:20901/api/quests/{quest_id}")
        assert quest["quest_id"] == quest_id
        root_request = Request("http://127.0.0.1:20901/")
        with urlopen(root_request) as response:  # noqa: S310
            html = response.read().decode("utf-8")
        assert "DeepScientist" in html
        assert "Copilot" in html
    finally:
        server.terminate()
        server.wait(timeout=10)
