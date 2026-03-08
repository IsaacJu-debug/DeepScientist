from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..shared import require_yaml


@dataclass(frozen=True)
class SkillBundle:
    skill_id: str
    name: str
    description: str
    root: Path
    skill_md: Path


def _parse_frontmatter(path: Path) -> dict:
    require_yaml()
    import yaml

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    _, frontmatter, _rest = text.split("---\n", 2)
    return yaml.safe_load(frontmatter) or {}


def discover_skill_bundles(repo_root: Path) -> list[SkillBundle]:
    skills_root = repo_root / "skills"
    bundles: list[SkillBundle] = []
    if not skills_root.exists():
        return bundles
    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        metadata = _parse_frontmatter(skill_md)
        skill_id = skill_md.parent.name
        bundles.append(
            SkillBundle(
                skill_id=skill_id,
                name=metadata.get("name", skill_id),
                description=metadata.get("description", ""),
                root=skill_md.parent,
                skill_md=skill_md,
            )
        )
    return bundles
