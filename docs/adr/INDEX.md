# CPA Ecosystem ADR Index

This index lists **ecosystem-level ADRs** (prefix `ECO-`) that define cross-repo contracts and policies for the CPA ecosystem in the phys-sims org.

Repo-local ADRs live in each repo’s `docs/adr/` folder. Private/internal ADRs live in private repos (e.g., `cpa-workspace` and private testbenches).

---

## How to add a new ecosystem ADR

1. Create a new file in this folder named: `ECO-####-short-title.md`
2. Use the template in this folder (see “Templates” below).
3. Choose the next available `ECO-####` number.
4. Add a row to the table below.
5. Prefer linking from repo-local ADRs to the ecosystem ADR rather than duplicating content.

---

## Templates

- `_template-full.md`
- `_template-lite.md`
- `_template-amend.md`

(These should include **Scope**, **Visibility**, **Canonical ADR**, **Impacted repos**, and **Related ecosystem ADRs** fields.)

---

## Ecosystem ADRs

| ID | Title | Status | Date | Impacted repos |
|---|---|---|---|---|
| ECO-0001 | _TBD_ | Draft | YYYY-MM-DD | phys-pipeline, abcdef-sim, glnse-sim |
| ECO-0002 | _TBD_ | Draft | YYYY-MM-DD | _TBD_ |
| ECO-0003 | _TBD_ | Draft | YYYY-MM-DD | _TBD_ |

> Tip: keep each ADR focused on one decision. If it starts turning into a handbook, split it.
