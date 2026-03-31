#!/usr/bin/env python3
import json
from pathlib import Path

from optimize_description import optimize, read_description, render_markdown
from trigger_eval import load_json, load_semantic_config


ROOT = Path(__file__).resolve().parent.parent


TARGETS = [
    {
        "name": "yao-meta-skill",
        "title": "Root Description Optimization",
        "description_file": ROOT / "SKILL.md",
        "baseline_file": ROOT / "evals" / "baseline_description.txt",
        "dev_cases": ROOT / "evals" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "evals" / "holdout" / "trigger_cases.json",
        "semantic_config": ROOT / "evals" / "semantic_config.json",
        "output_json": ROOT / "reports" / "description_optimization.json",
        "output_md": ROOT / "reports" / "description_optimization.md",
    },
    {
        "name": "team-frontend-review",
        "title": "Frontend Review Description Optimization",
        "description_file": ROOT / "examples" / "team-frontend-review" / "generated-skill" / "SKILL.md",
        "baseline_file": ROOT / "examples" / "team-frontend-review" / "optimization" / "baseline_description.txt",
        "dev_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "examples" / "team-frontend-review" / "optimization" / "holdout" / "trigger_cases.json",
        "semantic_config": ROOT / "examples" / "team-frontend-review" / "optimization" / "semantic_config.json",
        "output_json": ROOT / "examples" / "team-frontend-review" / "optimization" / "reports" / "description_optimization.json",
        "output_md": ROOT / "examples" / "team-frontend-review" / "optimization" / "reports" / "description_optimization.md",
    },
    {
        "name": "governed-incident-command",
        "title": "Governed Incident Description Optimization",
        "description_file": ROOT / "examples" / "governed-incident-command" / "generated-skill" / "SKILL.md",
        "baseline_file": ROOT / "examples" / "governed-incident-command" / "optimization" / "baseline_description.txt",
        "dev_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "dev" / "trigger_cases.json",
        "holdout_cases": ROOT / "examples" / "governed-incident-command" / "optimization" / "holdout" / "trigger_cases.json",
        "semantic_config": ROOT / "examples" / "governed-incident-command" / "optimization" / "semantic_config.json",
        "output_json": ROOT / "examples" / "governed-incident-command" / "optimization" / "reports" / "description_optimization.json",
        "output_md": ROOT / "examples" / "governed-incident-command" / "optimization" / "reports" / "description_optimization.md",
    },
]


def report_errors(report: dict) -> tuple[int, int]:
    return (
        report["holdout"]["false_positives"] if report.get("holdout") else report["dev"]["false_positives"],
        report["holdout"]["false_negatives"] if report.get("holdout") else report["dev"]["false_negatives"],
    )


def main() -> None:
    summary = {"targets": [], "ok": True}
    for target in TARGETS:
        current_description = read_description(target["description_file"])
        baseline_description = read_description(target["baseline_file"])
        dev_cases = load_json(target["dev_cases"])
        holdout_cases = load_json(target["holdout_cases"])
        config = load_semantic_config(target["semantic_config"])

        report = optimize(current_description, dev_cases, holdout_cases, config, baseline_description)
        target["output_json"].parent.mkdir(parents=True, exist_ok=True)
        target["output_json"].write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        target["output_md"].write_text(render_markdown(report, target["title"]), encoding="utf-8")

        winner_fp, winner_fn = report_errors(report["winner"])
        current_fp, current_fn = report_errors(report["current_candidate"])
        baseline_fp, baseline_fn = report_errors(report["baseline"])

        target_ok = (
            (winner_fp, winner_fn) <= (current_fp, current_fn)
            and (winner_fp, winner_fn) <= (baseline_fp, baseline_fn)
        )
        summary["targets"].append(
            {
                "name": target["name"],
                "winner_label": report["winner"]["label"],
                "winner_description": report["winner"]["description"],
                "winner_tokens": report["winner"]["estimated_tokens"],
                "current_tokens": report["current_candidate"]["estimated_tokens"],
                "winner_holdout_fp": winner_fp,
                "winner_holdout_fn": winner_fn,
                "current_holdout_fp": current_fp,
                "current_holdout_fn": current_fn,
                "baseline_holdout_fp": baseline_fp,
                "baseline_holdout_fn": baseline_fn,
                "ok": target_ok,
            }
        )
        if not target_ok:
            summary["ok"] = False

    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    (ROOT / "reports" / "description_optimization_suite.json").write_text(rendered + "\n", encoding="utf-8")
    lines = [
        "# Description Optimization Suite",
        "",
        "| Target | Winner | Winner Tokens | Holdout FP | Holdout FN | Current FP | Current FN | Baseline FP | Baseline FN | Status |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for target in summary["targets"]:
        lines.append(
            f"| `{target['name']}` | `{target['winner_label']}` | {target['winner_tokens']} | {target['winner_holdout_fp']} | {target['winner_holdout_fn']} | {target['current_holdout_fp']} | {target['current_holdout_fn']} | {target['baseline_holdout_fp']} | {target['baseline_holdout_fn']} | {'ok' if target['ok'] else 'fail'} |"
        )
    (ROOT / "reports" / "description_optimization_suite.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(rendered)
    if not summary["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
