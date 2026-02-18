# Change Report

## Affected repos
- cpa-testbench

## Base SHAs
- cpa-testbench: `2581e93167a663148811ec49136f20d1f8197b6f`

## Summary
### cpa-testbench
```
A  configs/lab/components.yaml
A  configs/lab/experiment_matrix.yaml
A  configs/lab/optimization.yaml
A  docs/agent/cpa-sim-adaptation-context.md
A  docs/agent/lab-meeting-graph-playbook.md
A  docs/agent/phys-sims-utils-optimization-context.md
```

## Apply instructions
```bash
for repo in cpa-testbench; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260218-231506/"$repo".patch)
done
```

## Tests
- Add commands used to validate this bundle here.
