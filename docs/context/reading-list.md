# `cpa-sim` dependency context reading order

Agents should read in this order:

1. `docs/context/README.md` (system purpose + rules)
2. `docs/context/deps/phys-pipeline.md`
3. `docs/context/deps/abcdef-sim.md`
4. `docs/context/deps/phys-sim-utils.md`
5. `docs/context/deps/cpa-testbench.md`
6. Relevant upstream snapshots under `docs/context/snapshots/`
