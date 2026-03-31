#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from context_sizer import estimate_tokens, read_text, TEXT_EXTS


OPTIONAL_DIRS = ("references", "scripts", "assets", "evals", "templates")
CANONICAL_PATHS = ("SKILL.md", "manifest.json", "agents", "references", "scripts", "assets", "evals", "templates")


def has_files(path: Path) -> bool:
    return path.exists() and any(child.is_file() for child in path.rglob("*"))


def iter_relevant_files(root: Path) -> list[Path]:
    files = []
    for entry in CANONICAL_PATHS:
        path = root / entry
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(file for file in path.rglob("*") if file.is_file()))
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether a skill package keeps resource boundaries under control.")
    parser.add_argument("skill_dir")
    parser.add_argument("--max-initial-tokens", type=int, default=1800)
    parser.add_argument("--warn-skill-body-tokens", type=int, default=1400)
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    skill_md = root / "SKILL.md"
    failures = []
    warnings = []

    if not skill_md.exists():
        failures.append("Missing SKILL.md")
        report = {"ok": False, "failures": failures, "warnings": warnings}
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(2)

    files = iter_relevant_files(root)
    skill_body_tokens = 0
    other_tokens = 0
    initial_load_tokens = 0
    total_text_tokens = 0
    for path in files:
        if path.suffix and path.suffix not in TEXT_EXTS and path.name != "SKILL.md":
            continue
        text = read_text(path)
        tokens = estimate_tokens(text)
        total_text_tokens += tokens
        rel = path.relative_to(root)
        if rel.name == "SKILL.md":
            skill_body_tokens += tokens
            initial_load_tokens += tokens
        else:
            other_tokens += tokens
            if rel.parts[0] in {"agents"}:
                initial_load_tokens += tokens

    if initial_load_tokens > args.max_initial_tokens:
        failures.append(
            f"Estimated initial-load tokens exceed budget: {initial_load_tokens} > {args.max_initial_tokens}"
        )
    if skill_body_tokens > args.warn_skill_body_tokens:
        warnings.append(f"SKILL.md is getting heavy: {skill_body_tokens} estimated tokens.")

    skill_text = skill_md.read_text(encoding="utf-8")
    for dirname in OPTIONAL_DIRS:
        path = root / dirname
        if path.exists() and not has_files(path):
            warnings.append(f"{dirname}/ exists but is empty.")
            continue
        if has_files(path) and dirname not in skill_text and dirname.capitalize() not in skill_text:
            warnings.append(f"{dirname}/ contains files but is not referenced explicitly in SKILL.md.")

    if other_tokens and skill_body_tokens / (skill_body_tokens + other_tokens) > 0.75:
        warnings.append("Most text still lives in SKILL.md; consider moving detail into references/ or scripts/.")

    report = {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "stats": {
            "skill_body_tokens": skill_body_tokens,
            "other_text_tokens": other_tokens,
            "estimated_initial_load_tokens": initial_load_tokens,
            "estimated_total_text_tokens": total_text_tokens,
            "relevant_file_count": len(files),
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
