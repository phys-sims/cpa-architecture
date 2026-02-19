# Change Report

## Affected repos
- cpa-testbench

## Base SHAs
- cpa-testbench: `2581e93167a663148811ec49136f20d1f8197b6f`

## Summary
### cpa-testbench
```
M .github/workflows/ci.yml
 M README.md
 M pyproject.toml
 M scripts/run_pipeline.py
 M src/cpa_testbench/__init__.py
A  src/cpa_testbench/cli.py
A  src/cpa_testbench/pipeline.py
 M tests/test_e2e.py
```

## Apply instructions
```bash
for repo in cpa-testbench; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260218-235846/"$repo".patch)
done
```

## Tests
- `python -m pip install -e .[dev]` (failed in this environment: proxy blocks fetching setuptools/other packages).
- `python -m pytest` (failed: missing `yaml` dependency due install failure).
