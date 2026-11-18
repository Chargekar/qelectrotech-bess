# OpenGrid Engineer — QElectroTech BESS integration

**CLI-first, agent-friendly electrical engineering foundation** for building distribution, solar PV, wind, and battery storage. Open source under Apache-2.0.

> **Status: Milestone 0.1 / engineering prototype. NOT FOR CONSTRUCTION OR SAFETY-CRITICAL DESIGN.**
> The repository generates illustrative drawings and simplified OpenDSS steady-state models. No NEC/CEC or interconnection compliance assessment is implemented. No arc-flash, protective coordination, conductor sizing, grounding study, or approved protection model is provided. A qualified electrical engineer must validate all inputs and outputs before design use.

## What works now

- Typed, versioned Pydantic schema for radial **balanced three-phase, single-voltage** networks: utility equivalent, buses, feeders, loads, PV, storage, and wind.
- Strict schema/topology validation and simulation gating when feeder impedances or ampacity are unknown.
- Scenario-specific OpenDSS text generation (`baseline`, `peak-load`, `max-solar`, `bess-charging`, `bess-discharging`). Optional OpenDSS-DSS-Python execution (requires the `[sim]` dependency).
- SVG/PDF/DXF **concept** single-line output from the same electrical model. These are not construction documents.
- Conservative PDF intake: embedded text extraction or optional Tesseract OCR and source SHA-256. **Does not** infer electrical circuit topology or verify SLD connections.
- Agent-compatible JSON CLI and `propose` patch operation for *proposed* equipment only; input model remains unchanged with JSON audit output.
- Unit/CLI tests and GitHub Actions CI.

## Setup (Linux / macOS / WSL2)

Requires Python 3.11 or newer. For full functionality, `tesseract` is optional system software for scanned PDF OCR.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[all]'
```

For just model editing, validation, and OpenDSS export: `pip install -e .`.

## Try the end-to-end sample

```bash
og validate examples/sample-building.yaml --study-ready
og compile examples/sample-building.yaml --scenario max-solar --out out/max-solar.dss
og draw examples/sample-building.yaml --out out/concept.svg
og draw examples/sample-building.yaml --out out/concept.pdf
og draw examples/sample-building.yaml --out out/concept.dxf
og propose examples/sample-building.yaml examples/upgrade-proposal.yaml \
  --out out/proposed.yaml --audit out/change-audit.json
og validate out/proposed.yaml --study-ready
og study out/proposed.yaml --scenario bess-charging --out out/charging.json
```

`og study` requires DSS-Python (`pip install -e '.[sim]'`) and currently models one steady-state operating point, not a time-series battery dispatch optimization. The sample uses **synthetic illustrative values, not field measurements**. The solver dependency was unavailable in the environment where this initial repository was authored, so the optional native `og study` path has not yet passed an integration test; the OpenDSS compiler and other modules have automated tests.

### PDF evidence intake

```bash
og ingest path/to/asbuilt.pdf --out out/asbuilt-evidence.json
```

The manifest contains page-level text, tentative tags, extraction method, source hash, and a mandatory manual review flag. A scanned drawing is **not** automatically converted into a circuit yet. This safeguard is intentional.

### CLI for agents

All normal command output is JSON; failures return a nonzero exit status. Agents should edit proposed models only through `og propose` (or generate and validate a separate proposal), never rewrite an approved as-built file. Refer to [AGENTS.md](AGENTS.md).

```yaml
# proposals are lists; this is examples/upgrade-proposal.yaml
- op: update
  collection: pv
  id: PV_250
  changes:
    ac_kw: 200
```

This produces a separate proposal file and change audit. No proposal is automatically approved.

## Architectural choices

- **Authoritative source:** Canonical, reviewable YAML/JSON engineering topology with stable object IDs.
- **Simulation:** Compiler emits native OpenDSS text. A DSS-Python backend may run power flow when installed.
- **Drawings:** Programmatically generated SVG, PDF and DXF; no freehand agent manipulation of linework.
- **PDF intake:** Evidence extraction first; OCR does not imply topology or rating truth.
- **Safety:** No silently inferred ratings, no updating existing as-built assets via agent patch, no released-drawing pathway yet.

Detailed documentation: [ARCHITECTURE.md](docs/ARCHITECTURE.md) · [ROADMAP.md](docs/ROADMAP.md) · [SECURITY.md](SECURITY.md).

## Limits of 0.1

1. Only radial, 3-phase, single nominal voltage networks are supported. There are no explicit breakers, transformers, conductor geometries, grounding, or neutral current models yet.
2. The numerical OpenDSS and battery models are simplified steady-state equivalents, without inverter controls, wind time series, or realistic battery dispatch.
3. SVG/PDF/DXF output is a topology sketch, not professional permit-ready sheet drafting.
4. PDF OCR text and extracted tags are unverified; circuit reconstruction and symbol recognition remain future work.
5. `verified` metadata is tracked but not yet required for all studies; engineers must not treat simulations as verified as-built data.
6. Integration with MCP, pvlib, windpowerlib, PyPSA, and CI full solver validation is on the roadmap—not delivered in 0.1.

## Contributing

```bash
pip install -e '.[dev,draw,ingest]'
pytest -q
```

By contributing you acknowledge the engineering use limitations above. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Integration with the existing QElectroTech asset library

This engine lives in `engine/` within the existing `qelectrotech-bess` repository.
The original `assets/catalog.json`, `.elmt` symbols, ontology, truth seed,
Draw.io generators, existing CI, and compliance watchtower remain unchanged.

From repository root, after installing with `pip install -e './engine[all]'`:

```bash
og symbols assets/catalog.json --id pv_inverter
og validate engine/examples/sample-building.yaml --catalog assets/catalog.json --study-ready
og compile engine/examples/sample-building.yaml --scenario max-solar --out engine/out/max-solar.dss
og draw engine/examples/sample-building.yaml --out engine/out/concept.svg
```

Catalog validation checks symbol IDs and AC-domain port metadata. It does **not**
validate engineering suitability or turn a concept drawing into native QET.
The catalog currently lacks a dedicated wind-turbine symbol, which the bridge
explicitly reports rather than substituting an unrelated generator symbol.

`docs/` covers the CLI model and limitations, while repository-level `SKILL.md`
and `references/` remain authoritative for the existing QET asset conventions.

**Security:** This repository is public. Never add customer as-builts,
site coordinates, utility identifiers, real equipment schedules, or secrets.
Use synthetic example data only until the user establishes a private project store.
