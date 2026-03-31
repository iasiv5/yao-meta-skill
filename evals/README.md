# Evals

This directory makes trigger quality and packaging quality more reproducible.

Contents:

- `trigger_cases.json`: positive, negative, and near-neighbor prompts
- `train/`, `dev/`, `holdout/`: split trigger suites for iterative tuning and final verification
- `semantic_config.json`: local semantic-intent concepts, exclusions, and weights
- `baseline_description.txt`: intentionally weaker trigger description
- `improved_description.txt`: current stronger trigger description
- `sample_trigger_report.json`: example comparison output using the current recommended threshold
- `failure-cases.md`: current weak spots and regression targets
- `packaging_expectations.json`: required packaging behaviors for supported targets

Use:

```bash
python3 scripts/trigger_eval.py --description-file evals/improved_description.txt --cases evals/trigger_cases.json
python3 scripts/trigger_eval.py --description-file evals/improved_description.txt --cases evals/trigger_cases.json --baseline-description-file evals/baseline_description.txt
python3 scripts/run_eval_suite.py
python3 scripts/cross_packager.py . --platform openai --platform claude --expectations evals/packaging_expectations.json --zip
python3 tests/verify_packager_failures.py
```

Regression scope now includes:

- direct positives
- direct negatives
- near neighbors
- long-context positives
- mixed-intent negatives
- explicit "do not build a skill" negatives
- semantic exclusion cases such as one-off, document-only, and future-outline prompts
- holdout verification
