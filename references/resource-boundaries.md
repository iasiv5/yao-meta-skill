# Resource Boundary Spec

This spec defines where information belongs inside a skill package.

## Principle

Keep the main skill small enough to route and execute clearly. Move detail out of `SKILL.md` as soon as it stops helping routing or branch selection.

## Placement Rules

### Put content in `SKILL.md` when it is:

- part of the trigger surface
- part of the core execution skeleton
- part of the output contract
- necessary for branch selection or safe defaults

### Put content in `references/` when it is:

- domain guidance
- long examples
- policy material
- schemas or templates humans or agents may read on demand

### Put content in `scripts/` when it is:

- deterministic
- repetitive
- brittle if rewritten from prose
- easier to validate as code than as instructions

### Put content in `evals/` when:

- the skill is reused enough that routing mistakes matter
- near-neighbor confusion is likely
- quality claims should be reproducible

### Put content in `assets/` when:

- the package includes output artifacts, examples, or static files that should not bloat prompt context

## Anti-Patterns

Avoid these:

- storing long policy text directly in `SKILL.md`
- adding `references/` with no files that are actually used
- adding `scripts/` for logic that is still best expressed in prose
- adding `evals/` for one-off or disposable skills
- creating every folder by default even when empty

## Heuristics

### `SKILL.md`

- should stay focused
- should not become the full knowledge base
- should mention any optional directory that materially affects execution

### `references/`

- should earn their keep
- should usually be named and discoverable from `SKILL.md`

### `scripts/`

- should exist only when deterministic logic or formatting logic is real
- should be referenced explicitly from `SKILL.md` when required for execution

### `evals/`

- should exist when routing or quality claims need to be defended
- should be skipped for disposable personal drafts

## Quality Intent

The best skill is not the one with the most files. The best skill is the smallest package that still makes the recurring job reliable, reusable, and auditable.
