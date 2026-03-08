from __future__ import annotations

from dataclasses import dataclass, field

from ..shared import utc_now


@dataclass
class QuestSession:
    quest_id: str
    bound_sources: set[str] = field(default_factory=set)
    updated_at: str = field(default_factory=utc_now)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, QuestSession] = {}

    def bind(self, quest_id: str, source: str) -> QuestSession:
        session = self._sessions.setdefault(quest_id, QuestSession(quest_id=quest_id))
        session.bound_sources.add(source)
        session.updated_at = utc_now()
        return session

    def snapshot(self) -> list[dict]:
        return [
            {
                "quest_id": session.quest_id,
                "bound_sources": sorted(session.bound_sources),
                "updated_at": session.updated_at,
            }
            for session in self._sessions.values()
        ]
