#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a skill package.")
    parser.add_argument("skill_dir")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    failures = []
    skill_md = root / "SKILL.md"
    interface = root / "agents" / "interface.yaml"

    if not skill_md.exists():
        failures.append("Missing SKILL.md")
    if not interface.exists():
        failures.append("Missing agents/interface.yaml")

    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            failures.append("SKILL.md missing frontmatter")
        else:
            parts = text.split("---", 2)
            data = yaml.safe_load(parts[1]) or {}
            for field in ("name", "description"):
                if not data.get(field):
                    failures.append(f"Missing frontmatter field: {field}")

    if interface.exists():
        data = yaml.safe_load(interface.read_text(encoding="utf-8")) or {}
        meta = data.get("interface", {})
        for field in ("display_name", "short_description", "default_prompt"):
            if not meta.get(field):
                failures.append(f"Missing interface field: {field}")

    print(json.dumps({"ok": not failures, "failures": failures}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
