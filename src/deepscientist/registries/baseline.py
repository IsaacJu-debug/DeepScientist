from __future__ import annotations

from pathlib import Path

from ..shared import append_jsonl, ensure_dir, read_jsonl, read_yaml, utc_now, write_yaml


class BaselineRegistry:
    def __init__(self, home: Path) -> None:
        self.home = home
        self.root = ensure_dir(home / "config" / "baselines")
        self.entries_root = ensure_dir(self.root / "entries")
        self.index_path = self.root / "index.jsonl"

    def list_entries(self) -> list[dict]:
        return read_jsonl(self.index_path)

    def get(self, baseline_id: str) -> dict | None:
        path = self.entries_root / f"{baseline_id}.yaml"
        if path.exists():
            return read_yaml(path, {})
        for item in self.list_entries():
            if item.get("baseline_id") == baseline_id or item.get("entry_id") == baseline_id:
                return item
        return None

    def publish(self, entry: dict) -> dict:
        timestamp = utc_now()
        baseline_id = entry.get("baseline_id") or entry.get("entry_id")
        if not baseline_id:
            raise ValueError("Baseline entry requires baseline_id or entry_id")
        normalized = {
            "registry_kind": "baseline",
            "schema_version": 1,
            "entry_id": baseline_id,
            "baseline_id": baseline_id,
            "status": entry.get("status", "active"),
            "created_at": entry.get("created_at", timestamp),
            "updated_at": timestamp,
            **entry,
        }
        write_yaml(self.entries_root / f"{baseline_id}.yaml", normalized)
        append_jsonl(self.index_path, normalized)
        return normalized

    def attach(self, quest_root: Path, baseline_id: str, variant_id: str | None = None) -> dict:
        entry = self.get(baseline_id)
        if not entry:
            raise FileNotFoundError(f"Unknown baseline: {baseline_id}")
        selected_variant = None
        variants = entry.get("baseline_variants") or []
        if variant_id:
            for variant in variants:
                if variant.get("variant_id") == variant_id:
                    selected_variant = variant
                    break
            if selected_variant is None:
                raise FileNotFoundError(f"Unknown baseline variant: {variant_id}")
        elif variants:
            selected_variant = next(
                (item for item in variants if item.get("variant_id") == entry.get("default_variant_id")),
                variants[0],
            )

        attachment_root = ensure_dir(quest_root / "baselines" / "imported" / baseline_id)
        attachment = {
            "attached_at": utc_now(),
            "source_baseline_id": baseline_id,
            "source_variant_id": selected_variant.get("variant_id") if selected_variant else None,
            "entry": entry,
            "selected_variant": selected_variant,
        }
        write_yaml(attachment_root / "attachment.yaml", attachment)
        return attachment
