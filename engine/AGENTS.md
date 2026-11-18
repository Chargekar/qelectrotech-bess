# Rules for coding agents working on OpenGrid Engineer

- The canonical YAML/JSON model is the source of truth. Do not modify `.dss`, `.svg`, `.dxf` or `.pdf` outputs as engineering source data.
- Use `og validate` on every model modification. Use `og validate --study-ready` before simulation.
- Never invent breaker ratings, cable sizes, measured loads, voltage levels, impedances, or inferred as-built topology.
- Use `og propose` to produce separate models and JSON change audits. Do not overwrite the input file.
- Never edit an existing/as-built device through the proposal API, and do not change its status to proposed as a workaround.
- Ingested PDF labels are candidates, not verified electrical data. Engineer review is mandatory.
- Do not label any output 'approved', 'code compliant', 'permit ready' or 'construction issue'.
- Prefer deterministic tests, no unmanaged network I/O, reproducible outputs and minimal dependencies.
- Never automatically publish or transmit customer drawings, building plans, personal information or secrets.
- No autonomous approval or release of electrical engineering deliverables.

First commands:

```bash
og validate examples/sample-building.yaml --study-ready
og compile examples/sample-building.yaml --scenario baseline --out out/baseline.dss
og draw examples/sample-building.yaml --out out/concept.svg
pytest -q
```
