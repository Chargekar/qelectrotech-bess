# Watchtower for the compliance-truth seed

The watchtower records, classifies and flags changes around `assets/db/truth_seed.json`. It never edits the seed: promoting a row to verified, or adding a new edition, stays a human decision.

## Three loops

| Loop | Trigger | Writes |
|---|---|---|
| Change log | You edit the seed, then run `watchtower.py log` | `assets/db/TRUTH_CHANGELOG.md`, `watchtower/changelog.jsonl` |
| Guard | Every push and pull request (GitHub Actions `truth-watch`) | Nothing. Fails the build on violations or a missing changelog entry |
| Weekly review | Scheduled cloud run, opens a pull request | `watchtower/state.json`, `REVIEW_QUEUE.md`, `ledger.jsonl`, `reports/` |

## Change classes

| Class | Meaning | Allowed |
|---|---|---|
| addition | New standard, edition, clause, formula, constant, table row, lineage or source | Yes |
| promotion | Verification record added (row checked against adopted text by a named reviewer) | Yes |
| metadata | Non-normative field (edition `effective_to`, formula name or note, constant meaning, clause `applies_to`) | Yes |
| demotion | Verification record removed or altered | Fails guard |
| violation | Normative content edited, or a truth row deleted | Fails guard |

To correct a wrong value, restore the original row, add a new edition or clause row with the corrected value, and add a `lineage` entry linking them.

## Your workflow

```
# 1. edit assets/db/truth_seed.json (add rows or verifications)
python scripts/watchtower.py diff                     # preview the classification
python scripts/watchtower.py log --by "Harshwardhan Wadikar" --note "why"
python scripts/build_db.py
git commit -am "truth: <what changed>" && git push
```

## Weekly review (what the scheduled run does)

1. `watchtower.py report --write` for the current state.
2. For each source in `watchtower/sources.json`, read the official page and record what it shows with `watchtower.py observe`. A changed value raises a queue item listing the affected clauses.
3. `watchtower.py rotation --n 5` picks the least recently reviewed unverified rows; each is checked against an official source and recorded with `watchtower.py finding` (consistent, discrepancy or unable). A discrepancy raises a queue item.
4. Opens a pull request titled `watchtower: weekly review <date>`. Merge it to keep the record; act on queue items by editing the seed yourself.

Close a queue item by setting its `status` in `watchtower/state.json` to `resolved` or `dismissed` and adding a `resolution` note.
