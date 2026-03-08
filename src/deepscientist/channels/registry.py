from __future__ import annotations

from typing import Callable


ChannelFactory = Callable[..., object]
_CHANNEL_FACTORIES: dict[str, ChannelFactory] = {}


def register_channel(name: str, factory: ChannelFactory) -> None:
    _CHANNEL_FACTORIES[name] = factory


def get_channel_factory(name: str) -> ChannelFactory:
    return _CHANNEL_FACTORIES[name]


def list_channel_names() -> list[str]:
    return sorted(_CHANNEL_FACTORIES)
