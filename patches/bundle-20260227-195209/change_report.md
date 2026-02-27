# Change Report

## Affected repos
- abcdef-sim

## Base SHAs
- abcdef-sim: `e9ae0d34d17e8482b921a57696a776b834eb3132`

## Summary
### abcdef-sim
```
A  docs/adr/0007-lite-eco-0001-conventions-adoption.md
M  docs/adr/INDEX.md
```

## Apply instructions
```bash
for repo in abcdef-sim; do
  (cd deps/"$repo" && git apply ../../patches/bundle-20260227-195209/"$repo".patch)
done
```

## Tests
- Add commands used to validate this bundle here.
