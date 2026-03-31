---
name: yao-meta-skill
description: Create, refactor, evaluate, and package agent skills from workflows, prompts, transcripts, docs, or notes. Use when asked to create a skill, turn a repeated process into a reusable skill, improve an existing skill, add evals, or package a skill for team reuse.
metadata:
  author: Yao Team
  philosophy: "structured design, evaluation loop, template ergonomics, operational packaging"
---

# Yao Meta Skill

Build reusable skill packages, not long prompts.

## Router Rules

- Route by the frontmatter `description` first; it is the main trigger surface.
- Keep `SKILL.md` as router plus execution skeleton only.
- Put long guidance in `references/`, deterministic logic in `scripts/`, static artifacts in `assets/`, and generated evidence in `reports/`.
- Use the lightest process that still makes the skill reliable.
- Package for reuse only when reuse is real.

## Use Cases

- create a new skill
- turn a workflow, runbook, or prompt set into a skill
- improve a skill's boundary, evals, or packaging
- design a team skill template or standard
- migrate a skill toward the open format

## Modes

- `Scaffold`: personal or exploratory; deliver `SKILL.md`, `agents/interface.yaml`, and only clearly needed folders.
- `Production`: reusable team skill; add focused `references/`, `scripts/`, and `evals/` only when they earn their keep.
- `Library`: important shared or meta skill; add trigger matrices, packaging guidance, and maintenance metadata.

Detailed mode rules: [Operating Modes](references/operating-modes.md), [QA Ladder](references/qa-ladder.md), [Resource Boundary Spec](references/resource-boundaries.md).

## Compact Workflow

1. Capture the recurring job, outputs, trigger phrases, and risk.
2. Set one coherent boundary: one capability family, one trigger surface, one workflow.
3. Write the `description` early and add positives, negatives, and near neighbors for important skills.
4. Generate only the folders that earn their keep. Start from the basic template unless complexity is real.
5. Run the smallest useful gates: `context_sizer.py`, `resource_boundary_check.py`, `governance_check.py`, `trigger_eval.py`, `cross_packager.py`.

Detailed playbooks: [Operating Modes](references/operating-modes.md) and [Trigger And Eval Playbook](references/eval-playbook.md).

## Output Contract

Unless the user asks otherwise, produce:

1. a working skill directory
2. a trigger-aware `SKILL.md`
3. aligned `agents/interface.yaml`
4. references, scripts, evals, reports, and `manifest.json` only when justified
5. a short summary of boundary, exclusions, gates, and next steps

## Reference Map

- [Operating Modes](references/operating-modes.md)
- [QA Ladder](references/qa-ladder.md)
- [Governance Model](references/governance.md)
- [Resource Boundary Spec](references/resource-boundaries.md)
- [Skill Design Guidelines](references/skill_design_guidelines.md)
- [Client Compatibility](references/client-compatibility.md)
- [Comparative Analysis](references/comparative-analysis.md)
- [Meta-Skill Rubric](references/design-rubric.md)
- [Skill Template](references/skill-template.md)
- [Trigger And Eval Playbook](references/eval-playbook.md)
