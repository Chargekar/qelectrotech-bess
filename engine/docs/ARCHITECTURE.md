# Architecture and data contracts

## Core rules

1. **As-built is immutable to agents:** existing equipment may not be changed with the proposal CLI. As-built corrections must be handled by a separate human-reviewed workflow in a future milestone.
2. **One source of truth:** equipment and connectivity live in the canonical Pydantic/JSON/YAML model, not in diagrams or in `.dss` files.
3. **Fail closed on unknown parameters:** model validation allows unknown line impedance/ampacity, but the OpenDSS compiler refuses to run a numerical study with those fields missing.
4. **Evidence is independent of confidence:** OCR text, source-page bounding boxes (planned), field measurement and human approval are different concepts.
5. **Deterministic and auditable:** structured patch proposals are validated against the schema, with a written audit and no mutation of input files.
6. **No automatic engineering sign-off:** neither solver convergence nor a passed CI check constitutes code compliance or professional approval.

## Current data graph

`Project` contains one `GridSource`, `Bus`, `Feeder`, `Load`, `PV`, `Battery`, and `Wind`. Global stable IDs are required. Feeders form a radial tree; all equipment connects to a known bus. Cross-voltage line connections are rejected pending transformer support. All modeled buses use three-phase ABC.

`status`: `existing` or `proposed`. `verified`: boolean and `evidence`: list are placeholders for a future full provenance system; consumers must not interpret `verified: false` as safe for final engineering use. The synthetic sample intentionally sets all entries unverified.

### Model compilation

`canonical YAML/JSON -> Pydantic parse -> graph validation -> study readiness -> OpenDSS script -> optional DSS-Python solve`.

Each `Line` uses positive/zero-sequence per-unit-length impedances and nominal ampacity. PV uses OpenDSS PVSystem at nominal full irradiance in `max-solar` only. Wind is represented by a disabled fixed generator until proper time-series support. Storage uses simplified `State=CHARGING/DISCHARGING/IDLING` at rated output. The `peak-load` scenario uses an illustrative 1.2x multiplier. These assumptions should be configurable and reviewed before any actual project is evaluated.

### Concept drawing generation

`canonical model -> radial hierarchy -> SVG/PDF/DXF`. This path currently provides only an annotated connectivity sketch. Protective devices, cable callouts, schedules and title blocks are not implemented. Outputs are clearly watermarked for review.

### Ingest

`PDF -> page text or OCR -> candidate tags -> source SHA -> review manifest`. No untrusted PDF text is sent to a shell command, and no LLM inference is performed in the current release. Future work must include visual symbol models, line-junction semantics, source bounding boxes, and a human reconciliation UI.

## Reference production architecture (future)

- Isolation: subprocess or container per PDF and simulation job, restricted filesystem, memory, execution time, no network by default.
- Evidence: object store for original documents; PostgreSQL metadata with immutable source hashes.
- Agent: typed tool calls exposed through CLI and MCP; patch proposals become versioned PRs with drawing and simulation diffs.
- Human gates: verify as-built, approve topology, approve engineering assumptions, independent checking, stamp/release outside the agent.
- Reproducibility: model SHA, engine/package versions, weather inputs, study parameters, and artifact hashes.

## Supported vs unsupported

| Feature | Milestone 0.1 |
|---|---|
| Schema validation / radial connectivity | Supported |
| Scripted OpenDSS steady-state export | Supported |
| Native OpenDSS execution | Implemented with optional dependency; integration unverified in initial environment |
| SVG/PDF/DXF concept drawing | Supported |
| PDF text/OCR evidence capture | Supported with optional dependencies |
| Full scanned-SLD graph reconstruction | Not implemented |
| Typed agent proposal operation | Supported |
| MCP server / autonomous agent loop | Not implemented |
| IEEE/ANSI breaker / protection coordination | Not implemented |
| NEC/CEC automated compliance checking | Not implemented |
| Certified construction drawing generation | Not implemented |
