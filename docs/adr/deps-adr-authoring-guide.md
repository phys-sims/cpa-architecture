# Guide: authoring repo-local ADRs in `deps/*`

This guide is for agents creating ADRs in dependency repos (for example `deps/cpa-sim/docs/adr/`).

## Why this exists

Two recurring problems were observed in patch ADRs:
1. Titles were verbose and repo-prefixed (example: `SIM-ADR-0001: Adopt ECO-0001 conventions and units policy in cpa-sim`).
2. Local ADRs only stated "ECO accepted" and did not preserve the local, actionable subset needed by agents working in that repo.

This guide standardizes a concise title format and a required "local instructions" section.

## Default stance: keep local ADRs lean

Most repo-local ADRs are **not** derived from ecosystem ADRs and should stay concise.

For non-ECO ADRs, keep the doc short and focused on:
- the local decision,
- where it applies,
- how to validate it.

Do not add ecosystem-governance context unless it directly changes local implementation behavior.

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

## ECO-derived ADRs are an edge-case addendum

When (and only when) a repo ADR derives from an ecosystem ECO ADR, add a small, actionable addendum.

The goal is to avoid two failure modes:
1. Pointer ADRs that only say "ECO accepted".
2. Verbose near-copies of ecosystem ADRs.

## What an ECO-derived local ADR must contain

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

### Keep ECO-derived ADRs compact

To prevent verbosity, cap ECO-derived content to implementation-relevant deltas:
- Use short bullets, not long narrative.
- Summarize upstream clauses by reference (for example, "ECO-0001 §Convention contract #1-#3") instead of re-explaining rationale.
- Add only repo-local mappings (paths, symbols, checks).
- If a section has no repo-local adaptation, state "Adopted as-is" in one line.

## Content boundary vs ecosystem ADR

When writing local ADRs from ECO ADRs:
- **Include:** local implementation instructions, conventions, repo-specific acceptance criteria, impacted code locations.
- **Exclude:** broad ecosystem alternatives analysis, org-level governance rationale, and unrelated repo concerns.

If the local repo needs alternatives analysis for a repo-specific design choice, write a separate local ADR for that choice.

## Template usage policy

Use the existing ADR templates in each dependency repo (`deps/<repo>/docs/adr/`).

- Do **not** introduce a new global non-ECO template from this guide.
- For ECO-derived ADRs, start from the repo-local template and add the ECO-derived sections listed above.
- Keep the ECO-specific additions minimal and implementation-oriented.

## Review checklist for PR authors/reviewers

- [ ] Title and filename use `ADR-XXXX-description`.
- [ ] ADR contains actionable local instructions (not only "ECO accepted").
- [ ] Scope and out-of-scope are explicit for this repo.
- [ ] Validation checks are listed and repo-appropriate.
- [ ] Upstream ECO links are present and accurate (ECO-derived ADRs only).
- [ ] ADR remains compact and avoids duplicating ecosystem rationale.
