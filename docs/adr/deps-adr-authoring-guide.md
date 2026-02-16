# Guide: authoring repo-local ADRs in `deps/*`

This guide is for agents creating ADRs in dependency repos (for example `deps/cpa-sim/docs/adr/`).

## Why this exists

Two recurring problems were observed in patch ADRs:
1. Titles were verbose and repo-prefixed (example: `SIM-ADR-0001: Adopt ECO-0001 conventions and units policy in cpa-sim`).
2. Local ADRs only stated "ECO accepted" and did not preserve the local, actionable subset needed by agents working in that repo.

This guide standardizes a concise title format and a required "local instructions" section.

## Required naming format

For repo-local ADRs, use this format for both filename and top-level title:

- `ADR-XXXX-description`

Where:
- `XXXX` is a zero-padded local sequence number (`0001`, `0002`, ...)
- `description` is a short kebab-case summary of the local decision

### Examples

- `ADR-0007-units-and-symbol-contract`
- `ADR-0012-result-schema-adapter-for-phys-pipeline`

### Do not use

- Repo-prefixed IDs (`SIM-ADR-0001`, `TB-ADR-0003`, etc.)
- Titles that begin with `Adopt ECO-...` without describing the local policy

## What a local ECO-derived ADR must contain

A repo-local ADR that derives from an ecosystem ADR should be a **local operating contract**, not a copy of ecosystem governance text.

Required sections:

1. **Decision summary (local)**
   - One paragraph stating what this repo will do.

2. **Upstream reference**
   - Link to canonical ECO ADR(s).
   - Include a short "as of date/SHA" reference when available.

3. **Local instructions (required)**
   - Concrete rules agents/engineers should follow in this repo.
   - Include identifier-level guidance (module paths, symbols, naming/units rules, validation expectations).

4. **Applies to**
   - Enumerate directories/components/interfaces in scope.

5. **Out of scope for this repo**
   - Explicitly list ECO sections that do not apply locally.

6. **Acceptance checks**
   - Checklist of validations to run in the repo when changing affected code.

7. **Migration notes (if adopted mid-stream)**
   - Incremental rollout and compatibility steps for existing code.

## Content boundary vs ecosystem ADR

When writing local ADRs from ECO ADRs:
- **Include:** local implementation instructions, conventions, repo-specific acceptance criteria, impacted code locations.
- **Exclude:** broad ecosystem alternatives analysis, org-level governance rationale, and unrelated repo concerns.

If the local repo needs alternatives analysis for a repo-specific design choice, write a separate local ADR for that choice.

## Minimal template for deps ADRs

```md
# ADR-XXXX-description

## Status
Accepted | Proposed

## Upstream references
- ECO-000Y: <link>

## Decision summary (local)
<What this repo commits to doing>

## Local instructions
- <Rule 1 with file/module pointers>
- <Rule 2 with file/module pointers>
- <Validation requirement>

## Applies to
- <paths/modules>

## Out of scope for this repo
- <what from ECO is intentionally not restated here>

## Acceptance checks
- [ ] <check/command>
- [ ] <check/command>

## Migration notes
- <optional rollout notes>
```

## Review checklist for PR authors/reviewers

- [ ] Title and filename use `ADR-XXXX-description`.
- [ ] ADR contains actionable local instructions (not only "ECO accepted").
- [ ] Scope and out-of-scope are explicit for this repo.
- [ ] Validation checks are listed and repo-appropriate.
- [ ] Upstream ECO links are present and accurate.
