# Change Report

## Affected repos
- cpa-sim

## Base SHAs
- cpa-sim: `e1b0695ca9cce34ce5e278727bf638d0cd1b6df6`

## Summary
### cpa-sim
```
M src/cpa_sim/metrics.py
 M src/cpa_sim/stages/laser_gen/analytic.py
 M src/cpa_sim/stages/metrics/standard.py
 M tests/integration/test_tiny_chain.py
?? tests/unit/test_metrics.py
```

## Apply instructions
```bash
for repo in cpa-sim; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260218-225307/"$repo".patch)
done
```

## Tests
- Add commands used to validate this bundle here.
