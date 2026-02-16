# Change Report

## Affected repos
- cpa-sim

## Base SHAs
- cpa-sim: `c394a3554e187b0515f31c431d8198625e434553`

## Summary
### cpa-sim
```
A  docs/adr/ADR-0001-conventions-units-sign.md
A  docs/adr/ADR-0002-stage-interface-and-provenance.md
A  docs/adr/ADR-0003-validation-tiers-and-tolerances.md
M  docs/adr/INDEX.md
M  docs/adr/_template-amend.md
M  docs/adr/_template-full.md
M  docs/adr/template-lite.md
```

## Apply instructions
```bash
for repo in cpa-sim; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260216-180342/"$repo".patch)
done
```

## Tests
- `python -m pre_commit run -a` (failed: `No module named pre_commit` in environment)
- `python -m pytest -q -m "not slow and not physics" --durations=10` (failed: existing `pyproject.toml` parse error)
- `python -m mypy src` (passed; also reported same existing `pyproject.toml` parse warning)
