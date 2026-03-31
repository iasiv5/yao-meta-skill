# Governance Model

This project treats important skills as governed assets rather than one-shot prompt files.

## Goals

- keep shared skills trustworthy over time
- make ownership explicit
- avoid stale or oversized skill packages
- define when a skill should evolve, split, or retire

## Required Governance Metadata

For reusable or library-grade skills, `manifest.json` should include:

- `name`
- `version`
- `owner`
- `updated_at`
- `review_cadence`
- `status`
- `maturity_tier`
- `lifecycle_stage`

## Allowed Values

### `status`

- `experimental`
- `active`
- `deprecated`

### `maturity_tier`

- `scaffold`
- `production`
- `library`
- `governed`

### `lifecycle_stage`

- `scaffold`
- `production`
- `library`
- `governed`

### `review_cadence`

- `monthly`
- `quarterly`
- `semiannual`
- `annual`
- `per-release`

## Governance Rules

### 1. Owner Required

Any skill meant for reuse must have a named owner or owning team.

### 2. Review Cadence Required

If a skill is shared, it must declare how often it should be reviewed.

### 3. Maturity Should Match Rigor

- `scaffold`: lightweight, personal, low-governance
- `production`: reusable team skill with validation
- `library`: curated shared skill with explicit packaging and evals
- `governed`: critical or meta-level skill with regression, maintenance, and review expectations

### 4. Deprecated Skills Need Explicit Intent

Deprecated skills should include a deprecation note or replacement reference in adjacent documentation or manifest extensions.

### 5. Drift Must Be Observable

Important skills should keep:

- a regression history
- visible evaluation results
- known anti-patterns or failure modes

## Governance Actions

Use governance review to decide whether a skill should:

- stay as-is
- tighten trigger boundaries
- split into sibling skills
- move detail into `references/`
- move brittle logic into `scripts/`
- be deprecated or replaced

## Why This Matters

Most skill systems stop at creation. World-class skill systems also manage:

- ownership
- drift
- maturity
- deprecation
- evidence of ongoing quality
