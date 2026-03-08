from __future__ import annotations

from typing import Callable


RunnerFactory = Callable[..., object]
_RUNNER_FACTORIES: dict[str, RunnerFactory] = {}


def register_runner(name: str, factory: RunnerFactory) -> None:
    _RUNNER_FACTORIES[name] = factory


def get_runner_factory(name: str) -> RunnerFactory:
    return _RUNNER_FACTORIES[name]


def list_runner_names() -> list[str]:
    return sorted(_RUNNER_FACTORIES)
