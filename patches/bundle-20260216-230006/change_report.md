# Change Report

## Affected repos
- cpa-sim

## Base SHAs
- cpa-sim: `263d7f67bd86f702e1ac6110c424e4c6db3fef94`

## Summary
### cpa-sim
```
A  docs/agent/phys-pipeline-context.md
```

## Apply instructions
```bash
for repo in cpa-sim; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260216-230006/"$repo".patch)
done
```

## Tests
- Add commands used to validate this bundle here.
