#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from context_sizer import estimate_tokens
from trigger_eval import (
    compare_reports,
    evaluate,
    extract_description,
    load_json,
    load_semantic_config,
)


def read_description(path: Path) -> str:
    return extract_description(path.read_text(encoding="utf-8")).strip()


def serial_join(items: list[str], conjunction: str = "or") -> str:
    items = [item.strip() for item in items if item and item.strip()]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"


def sentence(text: str) -> str:
    text = " ".join(text.split())
    if not text:
        return text
    if text.endswith("."):
        return text
    return f"{text}."


def build_candidates(current: str, config: dict) -> list[dict]:
    hints = config.get("optimizer_hints", {})
    capability = hints.get("capability") or current.split(".", 1)[0].strip()
    inputs = hints.get("inputs", [])
    trigger_actions = hints.get("trigger_actions", [])
    exclusions = hints.get("exclusions", [])
    artifacts = hints.get("artifacts", [])

    capability_sentence = sentence(capability)
    inputs_clause = f" from {serial_join(inputs)}" if inputs else ""
    trigger_clause = serial_join(trigger_actions[:3], "or")
    exclusion_clause = serial_join(exclusions[:3], "or")
    artifact_clause = serial_join(artifacts[:4], "or")

    raw_candidates = [
        {
            "id": "current",
            "label": "Current",
            "description": sentence(current),
            "strategy": "current",
        },
    ]

    if capability and trigger_clause:
        raw_candidates.extend(
            [
                {
                    "id": "balanced",
                    "label": "Balanced",
                    "description": sentence(f"{capability}{inputs_clause}. Use when asked to {trigger_clause}"),
                    "strategy": "balanced_template",
                },
                {
                    "id": "boundary",
                    "label": "Boundary",
                    "description": sentence(
                        f"{capability}{inputs_clause}. Use when asked to {trigger_clause}. Do not use for {exclusion_clause}"
                    )
                    if exclusion_clause
                    else sentence(f"{capability}{inputs_clause}. Use when asked to {trigger_clause}"),
                    "strategy": "boundary_template",
                },
                {
                    "id": "minimal",
                    "label": "Minimal",
                    "description": sentence(f"{capability}. Use when asked to {trigger_clause}"),
                    "strategy": "minimal_template",
                },
            ]
        )

    if capability and artifact_clause and trigger_clause:
        raw_candidates.append(
            {
                "id": "artifact_aware",
                "label": "Artifact Aware",
                "description": sentence(
                    f"{capability}{inputs_clause}. Trigger when requests mention {artifact_clause} and the job is to {trigger_clause}"
                ),
                "strategy": "artifact_template",
            }
        )

    if capability and exclusion_clause:
        raw_candidates.append(
            {
                "id": "guardrail",
                "label": "Guardrail",
                "description": sentence(f"{capability}{inputs_clause}. Do not use for {exclusion_clause}"),
                "strategy": "guardrail_template",
            }
        )

    deduped = []
    seen = set()
    for candidate in raw_candidates:
        normalized = candidate["description"].lower()
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(candidate)
    return deduped


def objective_key(report: dict, token_count: int) -> tuple:
    bucket_stats = report.get("bucket_stats", {})
    near_rate = bucket_stats.get("near_neighbor", {}).get("pass_rate") or 0
    negative_rate = bucket_stats.get("should_not_trigger", {}).get("pass_rate") or 0
    precision = report.get("precision") or 0
    recall = report.get("recall") or 0
    return (
        report["false_positives"],
        report["false_negatives"],
        -near_rate,
        -negative_rate,
        -precision,
        -recall,
        token_count,
    )


def summarize_candidate(candidate: dict, dev_report: dict, holdout_report: dict | None) -> dict:
    token_count = estimate_tokens(candidate["description"])
    summary = {
        **candidate,
        "estimated_tokens": token_count,
        "dev": {
            "false_positives": dev_report["false_positives"],
            "false_negatives": dev_report["false_negatives"],
            "precision": dev_report["precision"],
            "recall": dev_report["recall"],
            "near_neighbor_pass_rate": dev_report["bucket_stats"]["near_neighbor"]["pass_rate"],
            "should_not_trigger_pass_rate": dev_report["bucket_stats"]["should_not_trigger"]["pass_rate"],
        },
        "selection_key": objective_key(dev_report, token_count),
    }
    if holdout_report:
        summary["holdout"] = {
            "false_positives": holdout_report["false_positives"],
            "false_negatives": holdout_report["false_negatives"],
            "precision": holdout_report["precision"],
            "recall": holdout_report["recall"],
            "near_neighbor_pass_rate": holdout_report["bucket_stats"]["near_neighbor"]["pass_rate"],
            "should_not_trigger_pass_rate": holdout_report["bucket_stats"]["should_not_trigger"]["pass_rate"],
        }
    return summary


def optimize(
    current_description: str,
    dev_cases: dict,
    holdout_cases: dict | None,
    config: dict,
    baseline_description: str | None = None,
) -> dict:
    dev_threshold = dev_cases.get("recommended_threshold", 0.48)
    holdout_threshold = holdout_cases.get("recommended_threshold", dev_threshold) if holdout_cases else dev_threshold

    candidates = []
    for candidate in build_candidates(current_description, config):
        dev_report = evaluate(candidate["description"], dev_cases, dev_threshold, config)
        holdout_report = evaluate(candidate["description"], holdout_cases, holdout_threshold, config) if holdout_cases else None
        candidates.append(
            {
                "candidate": summarize_candidate(candidate, dev_report, holdout_report),
                "dev_report": dev_report,
                "holdout_report": holdout_report,
            }
        )

    candidates.sort(key=lambda item: item["candidate"]["selection_key"])
    winner = candidates[0]
    current = next(item for item in candidates if item["candidate"]["id"] == "current")

    baseline = None
    if baseline_description:
        baseline_dev = evaluate(baseline_description, dev_cases, dev_threshold, config)
        baseline_holdout = evaluate(baseline_description, holdout_cases, holdout_threshold, config) if holdout_cases else None
        baseline = {
            "description": sentence(baseline_description),
            "estimated_tokens": estimate_tokens(sentence(baseline_description)),
            "dev": baseline_dev,
            "holdout": baseline_holdout,
        }

    report = {
        "current_description": sentence(current_description),
        "current_candidate": current["candidate"],
        "baseline": baseline,
        "winner": winner["candidate"],
        "winner_dev_report": winner["dev_report"],
        "winner_holdout_report": winner["holdout_report"],
        "current_dev_report": current["dev_report"],
        "current_holdout_report": current["holdout_report"],
        "candidates": [item["candidate"] for item in candidates],
        "selection_logic": {
            "priority": [
                "fewest false positives",
                "fewest false negatives",
                "highest near-neighbor pass rate",
                "highest negative pass rate",
                "highest precision",
                "highest recall",
                "shortest description",
            ]
        },
        "comparison": {
            "winner_vs_current_dev": compare_reports(current["dev_report"], winner["dev_report"]),
            "winner_vs_current_holdout": compare_reports(current["holdout_report"], winner["holdout_report"])
            if current["holdout_report"] and winner["holdout_report"]
            else None,
            "winner_vs_baseline_dev": compare_reports(baseline["dev"], winner["dev_report"]) if baseline else None,
            "winner_vs_baseline_holdout": compare_reports(baseline["holdout"], winner["holdout_report"])
            if baseline and baseline["holdout"] and winner["holdout_report"]
            else None,
        },
    }
    report["summary"] = {
        "winner_label": report["winner"]["label"],
        "winner_tokens": report["winner"]["estimated_tokens"],
        "current_tokens": report["current_candidate"]["estimated_tokens"],
        "winner_dev_total_errors": report["winner"]["dev"]["false_positives"] + report["winner"]["dev"]["false_negatives"],
        "current_dev_total_errors": report["current_candidate"]["dev"]["false_positives"]
        + report["current_candidate"]["dev"]["false_negatives"],
        "winner_holdout_total_errors": report["winner"]["holdout"]["false_positives"] + report["winner"]["holdout"]["false_negatives"]
        if report["winner"].get("holdout")
        else None,
        "current_holdout_total_errors": report["current_candidate"]["holdout"]["false_positives"]
        + report["current_candidate"]["holdout"]["false_negatives"]
        if report["current_candidate"].get("holdout")
        else None,
        "candidate_count": len(report["candidates"]),
    }
    if baseline:
        report["summary"]["baseline_tokens"] = baseline["estimated_tokens"]
        report["summary"]["baseline_dev_total_errors"] = baseline["dev"]["false_positives"] + baseline["dev"]["false_negatives"]
        report["summary"]["baseline_holdout_total_errors"] = (
            baseline["holdout"]["false_positives"] + baseline["holdout"]["false_negatives"]
            if baseline.get("holdout")
            else None
        )
    return report


def render_markdown(report: dict, title: str) -> str:
    lines = [
        f"# {title}",
        "",
        f"Winner: `{report['winner']['label']}`",
        "",
        f"- current tokens: `{report['current_candidate']['estimated_tokens']}`",
        f"- winner tokens: `{report['winner']['estimated_tokens']}`",
    ]
    if report["baseline"]:
        lines.append(f"- baseline tokens: `{report['baseline']['estimated_tokens']}`")
    lines.extend(
        [
            "",
            "## Winner",
            "",
            report["winner"]["description"],
            "",
            "## Candidate Ranking",
            "",
            "| Candidate | Tokens | Dev FP | Dev FN | Dev Near | Holdout FP | Holdout FN |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for candidate in report["candidates"]:
        holdout = candidate.get("holdout", {})
        lines.append(
            f"| `{candidate['label']}` | {candidate['estimated_tokens']} | {candidate['dev']['false_positives']} | {candidate['dev']['false_negatives']} | {candidate['dev']['near_neighbor_pass_rate']} | {holdout.get('false_positives', '-')} | {holdout.get('false_negatives', '-')} |"
        )

    lines.extend(
        [
            "",
            "## Selection Logic",
            "",
            "Ordered by:",
        ]
    )
    for item in report["selection_logic"]["priority"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and score description candidates on dev and holdout suites.")
    parser.add_argument("--description-file", required=True)
    parser.add_argument("--baseline-description-file")
    parser.add_argument("--dev-cases", required=True)
    parser.add_argument("--holdout-cases")
    parser.add_argument("--semantic-config", required=True)
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--title", default="Description Optimization Report")
    args = parser.parse_args()

    current_description = read_description(Path(args.description_file))
    baseline_description = read_description(Path(args.baseline_description_file)) if args.baseline_description_file else None
    dev_cases = load_json(Path(args.dev_cases))
    holdout_cases = load_json(Path(args.holdout_cases)) if args.holdout_cases else None
    config = load_semantic_config(Path(args.semantic_config))

    report = optimize(current_description, dev_cases, holdout_cases, config, baseline_description)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(rendered + "\n", encoding="utf-8")
    if args.output_md:
        Path(args.output_md).write_text(render_markdown(report, args.title), encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
