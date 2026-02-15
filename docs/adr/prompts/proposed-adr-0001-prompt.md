# Prompt: Write Proposed ADR-0001 (Conventions & Units)

You are drafting an ecosystem ADR in `cpa-architecture`.

## Task
Create a **proposed** ADR for conventions/units as:
- `docs/adr/ECO-0001-conventions-units.md`

Use the ADR template structure already used in this repo (Title/ADR ID/Status/Date/Context/Options/Decision/Consequences/etc.).

## Required source context (must read before writing)
From this repo:
- `docs/adr/cpa-adr-writing-context.md` (ADR-0001 section + placeholders)
- `docs/adr/_template-full.md`
- `docs/adr/ECO-0004-repository-roles-boundaries.md`

From dependency repos (must reference concretely in rationale):
- `deps/cpa-sim/src/cpa_sim/pipeline.py`
- `deps/cpa-sim/src/cpa_sim/data_models/laser.py`
- `deps/cpa-sim/src/cpa_sim/stages/free_space/treacy_grating.py`
- `deps/cpa-sim/src/cpa_sim/stages/fiber/fiber_sim.py`
- `deps/phys-pipeline/src/phys_pipeline/types.py`
- `deps/phys-pipeline/docs/adr/0011-policybag.md`
- `deps/phys-sims-utils/docs/adr/0001-canonical-result-contracts.md`
- `deps/cpa-testbench/configs/pipeline.yaml`

## Decision constraints
The ADR must explicitly lock:
1. Internal unit system (`fs`, `um`, `rad`) and conversion policy.
2. Boundary-unit strategy and schema-level declaration (`unit_system` + metric suffix policy).
3. Envelope normalization (`|E|^2` meaning, energy integral units).
4. FFT convention + scaling convention + shift policy.
5. Chirp and dispersion sign conventions (including beta2/GDD mapping statement).
6. Free-space grating coordinate/sign convention (vendor-neutral).

## Validation section requirements
Include a "How we validate" section with concrete tests mapped to repos:
- fast invariant tests in `cpa-sim`
- contract checks in `phys-sims-utils`
- end-to-end sanity in `cpa-testbench`

## Output quality bar
- Status: **Proposed**.
- Include at least 3 options considered with explicit trade-offs.
- Include a migration plan that explains adoption order across repos.
- Include a short glossary for beam terminology.
- Include a short list of open questions only if truly unresolved.
