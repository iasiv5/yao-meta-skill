# Client Compatibility

This skill package uses a neutral source-of-truth file:

- `agents/interface.yaml`

That file is the canonical metadata source for:

- display metadata
- adapter targets
- activation mode
- execution context
- shell expectations
- trust boundaries
- degradation rules

## Compatibility Strategy

Use a two-layer model:

1. **Canonical source**
   - Keep brand-neutral metadata in `agents/interface.yaml`.
   - Keep behavior in `SKILL.md`, `references/`, and `scripts/`.
   - Keep activation, execution, and trust declarations in neutral metadata rather than target-specific files.

2. **Adapter outputs**
   - Generate client-specific metadata only when exporting or packaging.
   - Do not keep vendor-specific metadata files in the source tree unless a client strictly requires them.
   - Preserve neutral execution and trust semantics inside generated adapters.

## Supported Targets

The current adapter flow is designed for:

- OpenAI-compatible clients
- Claude-compatible clients
- generic Agent Skills clients

## Compatibility Rules

- Keep `SKILL.md` as the primary behavior definition.
- Keep client metadata minimal but semantically meaningful.
- Avoid putting client-specific logic in the main workflow.
- Prefer packaging-time conversion over source-tree duplication.
- Prefer one neutral portability profile over multiple divergent vendor trees.
- Declare how remote or untrusted environments should behave before exporting adapters.
