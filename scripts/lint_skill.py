#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint a skill package for basic structure issues.")
    parser.add_argument("skill_dir")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    failures = []
    warnings = []

    if root.name.lower() != root.name:
        warnings.append("Skill directory is not lowercase.")
    if " " in root.name:
        failures.append("Skill directory contains spaces.")

    skill_md = root / "SKILL.md"
    if skill_md.exists():
        lines = skill_md.read_text(encoding="utf-8").splitlines()
        if len(lines) > 300:
            warnings.append("SKILL.md is getting long; consider moving detail into references/.")

    print(json.dumps({"ok": not failures, "failures": failures, "warnings": warnings}, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
