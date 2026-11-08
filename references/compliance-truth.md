# Compliance truth layer and relational model

The model has five linked domains in one SQLite database (`python scripts/build_db.py`, output `build/bess.sqlite`):

| Domain | Tables | Changes when |
|---|---|---|
| Truth | standard, edition, clause, clause_lineage, formula, formula_term, constant, code_table, code_table_row | A new code cycle, errata or verification. Never edited in place. |
| Vocabulary | equipment_family, equipment_class, class_alias, rating_param, class_param, symbol, drawio_shape, note_template, layout_convention, location_kind, raceway_type | Library work (new symbol, new class) |
| Topology | project, project_edition, equipment, port, connection, operating_mode, mode_connection | Per project |
| Ratings | fact | Per project, as datasheets and surveys arrive |
| Placement / evidence | location, placement, clearance, drawing_occurrence, requirement, evidence, calculation | Per project |

## Why truth is separate

Equipment ratings are facts about one product and change with selection. A clause, its formula and its constants are fixed for an adopted edition. The database enforces this: triggers block updates and deletes of truth content, so errata or a new cycle is a new edition row plus a `clause_lineage` link (example: NEC 2017 705.60 renumbered to 705.28 in 2020). Only `verification`, `verified_by`, `verified_on` can change, and `verified` requires both.

## Status of the seed

Physics rows are definitions. Every code locator, constant and table row is `needs-verification` until checked against the adopted text; `truth.py eval` labels any result built on such rows PRELIMINARY. Title 24 Tables 140.10-A/B and NEC 310.16, 250.122, Chapter 9 Table 8 are declared (key schema only) and must be transcribed from the purchased/adopted text, not from memory. 240.6(A) and 110.26(A)(1) rows are seeded and still need a verifier.

## Rules that the schema enforces

- A requirement can only cite a clause in the project's selected editions (or their model basis and physics).
- `pass` needs a reviewer and at least one evidence row; `not-applicable` needs a reason.
- A connection's domain must match both port domains (control never merges with power).
- A `verified` fact needs a source; `unknown` facts may hold null.
- Every Draw.io stencil must exist in `drawio_shape` (extracted from jgraph/drawio Sidebar-Electrical.js, commit in `assets/drawio/stencil_inventory.json`).

## Use

```
python scripts/build_db.py
python scripts/truth.py editions --date 2026-03-01 --jurisdiction US-CA
python scripts/truth.py formulas --topic interconnection
python scripts/truth.py eval "F-NEC-2023-705.30-OMIN" I_cont=<A>
python scripts/truth.py sql "SELECT * FROM v_symbol_gaps"
python scripts/build_drawio.py          # A grid-tied, B backup, Legend pages
```

To verify a row: read the adopted text, then add `{"row": "<clause/formula/constant/table id>", "by": "<name>", "on": "<date>"}` to `verifications` in `assets/db/truth_seed.json` and rebuild. Correcting a wrong value means a new edition or clause row, never an edit.

Every seed change is classified and logged by the watchtower; see [watchtower](watchtower.md).
