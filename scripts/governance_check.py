#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


ALLOWED_STATUS = {"experimental", "active", "deprecated"}
ALLOWED_MATURITY = {"scaffold", "production", "library", "governed"}
ALLOWED_REVIEW_CADENCE = {"monthly", "quarterly", "semiannual", "annual", "per-release"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_frontmatter(skill_md: Path) -> dict:
    if not skill_md.exists():
        return {}
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    payload = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip().strip("'\"")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check skill governance metadata and lifecycle readiness.")
    parser.add_argument("skill_dir")
    parser.add_argument("--require-manifest", action="store_true")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    manifest_path = root / "manifest.json"
    skill_md = root / "SKILL.md"
    failures = []
    warnings = []
    details = {"skill_dir": str(root), "manifest_present": manifest_path.exists()}

    frontmatter = read_frontmatter(skill_md)
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = load_json(manifest_path)
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid manifest.json: {exc}")
    elif args.require_manifest:
        failures.append("Missing manifest.json")
    else:
        warnings.append("No manifest.json; governance metadata is unavailable.")

    if manifest:
        required = ["name", "version", "owner", "updated_at", "review_cadence", "status", "maturity_tier", "lifecycle_stage"]
        missing = [field for field in required if not manifest.get(field)]
        if missing:
            failures.append(f"Missing manifest fields: {', '.join(missing)}")

        if manifest.get("status") and manifest["status"] not in ALLOWED_STATUS:
            failures.append(f"Invalid status: {manifest['status']}")
        if manifest.get("maturity_tier") and manifest["maturity_tier"] not in ALLOWED_MATURITY:
            failures.append(f"Invalid maturity_tier: {manifest['maturity_tier']}")
        if manifest.get("lifecycle_stage") and manifest["lifecycle_stage"] not in ALLOWED_MATURITY:
            failures.append(f"Invalid lifecycle_stage: {manifest['lifecycle_stage']}")
        if manifest.get("review_cadence") and manifest["review_cadence"] not in ALLOWED_REVIEW_CADENCE:
            failures.append(f"Invalid review_cadence: {manifest['review_cadence']}")
        if manifest.get("updated_at"):
            try:
                datetime.strptime(manifest["updated_at"], "%Y-%m-%d")
            except ValueError:
                failures.append("updated_at must use YYYY-MM-DD")

        if frontmatter.get("name") and manifest.get("name") and frontmatter["name"] != manifest["name"]:
            failures.append("manifest name does not match SKILL.md frontmatter name")

        if manifest.get("status") == "deprecated" and not manifest.get("deprecation_note"):
            warnings.append("Deprecated skill should include deprecation_note in manifest.json.")

    report = {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "details": {
            **details,
            "frontmatter_name": frontmatter.get("name"),
            "manifest_name": manifest.get("name"),
            "status": manifest.get("status"),
            "maturity_tier": manifest.get("maturity_tier"),
            "review_cadence": manifest.get("review_cadence"),
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
