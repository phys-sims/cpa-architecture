# Change Report

## Affected repos
- cpa-sim

## Base SHAs
- cpa-sim: `c394a3554e187b0515f31c431d8198625e434553`

## Summary
### cpa-sim
```
M  STATUS.md
A  docs/adr/ADR-0001-conventions-units.md
A  docs/adr/ADR-0002-result-schema-contract.md
A  docs/adr/ADR-0003-validation-tiers-ci-policy.md
A  docs/adr/ADR-0004-stage-domain-boundaries.md
M  docs/adr/INDEX.md
```

## Apply instructions
```bash
for repo in cpa-sim; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260216-211009/"$repo".patch)
done
```

## Tests
- `python -m pre_commit run -a` *(fails: pre_commit not installed in environment)*
- `python -m mypy src` *(passes)*
- `python -m pytest -q -m "not slow and not physics" --durations=10` *(fails due existing `pyproject.toml` parse error in repo baseline)*
