# qelectrotech-bess

Reusable engineering assets for PV and battery energy storage (BESS) single line diagrams: native QElectroTech symbols, Draw.io templates, compliance note templates, and a relational model that keeps code knowledge separate from project data.

Author: Harshwardhan Wadikar. Licensed under the BSD 2-Clause License (see `LICENSE`).

## What is here

| Path | Purpose |
|---|---|
| `assets/library/` | Original QElectroTech `.elmt` symbols and a review gallery |
| `assets/db/` | Relational schema, compliance-truth seed, glossary seed, truth changelog |
| `assets/drawio/` | Draw.io SLD templates (grid-tied and backup) and the verified stencil inventory |
| `watchtower/` | Watched code sources, review queue, observation ledger, weekly reports |
| `scripts/` | Builders, validators, `truth.py` query tool, `watchtower.py` |
| `references/` | Ontology, placement, QET authoring, California review notes |

## Quick start

```
python scripts/build_db.py            # build build/bess.sqlite
python scripts/truth.py formulas      # list code formulas and their verification state
python scripts/build_drawio.py        # regenerate Draw.io templates
python scripts/validate_library.py    # check symbols, schema and links
```

## Compliance truth and the watchtower

`assets/db/truth_seed.json` holds standards, editions, clauses, formulas, constants and code tables. Rows are constant for an edition: errata or a new code cycle are added as new rows with a lineage link, never edited in place. Every change is recorded in `assets/db/TRUTH_CHANGELOG.md`, and CI rejects edits that alter normative content. A weekly review checks official code sources and flags anything that may affect the seed. Details: `references/watchtower.md`.

## Status and limits

Seeded code rows are marked `needs-verification` until a named reviewer checks them against the adopted text. Drawings produced from these assets are preliminary and are not a substitute for review and sealing by a responsible licensed engineer. Code text is paraphrased, not reproduced.
