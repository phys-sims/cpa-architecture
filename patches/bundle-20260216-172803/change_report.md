# Change Report

## Affected repos
- cpa-sim

## Base SHAs
- cpa-sim: `c394a3554e187b0515f31c431d8198625e434553`

## Summary
### cpa-sim
```
M  docs/adr/INDEX.md
A  docs/adr/SIM-ADR-0001-eco-0001-conventions-units-adoption.md
A  docs/adr/SIM-ADR-0002-eco-0002-result-schema-adoption.md
A  docs/adr/SIM-ADR-0003-eco-0003-validation-ci-adoption.md
A  docs/adr/SIM-ADR-0004-eco-0004-boundaries-ownership-adoption.md
```

## Apply instructions
```bash
for repo in cpa-sim; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260216-172803/"$repo".patch)
done
```

## Tests
- Add commands used to validate this bundle here.
