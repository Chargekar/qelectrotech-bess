# Development roadmap

## Milestone 0.1 — repository foundation (this release)

- [x] CLI package, strict JSON errors, synthetic reference project
- [x] Pydantic radial electrical model with validation
- [x] Typed proposed-equipment patch and audit
- [x] OpenDSS script compilation and optional solver interface
- [x] Concept DXF/SVG/PDF export from model
- [x] PDF text extraction / OCR evidence manifest
- [x] Unit tests and GitHub Actions CI
- [ ] Native DSS-Python live integration test in environment with solver installed

## Milestone 0.2 — trustworthy engineering core

- [ ] Add transformers, switchgear, circuit breakers, terminals and connectivity types
- [ ] Represent unbalanced one-/two-/three-phase systems, neutrals and explicit grounding
- [ ] Import measured load profiles and device catalogs with verified electrical specifications
- [ ] Independent IEEE test feeders and voltage/current regression fixtures
- [ ] Test against multiple published reference power-flow cases and verify numerical tolerances
- [ ] Model state separated into verified as-built, proposal, and released revisions
- [ ] Add equipment names, ratings, schedules, drawing legend and line styles

## Milestone 0.3 — source evidence and CAD

- [ ] Import digital/vector SLD geometry with source bounding boxes
- [ ] OCR, line detection, junction and symbol recognition on representative scanned drawings
- [ ] Manual side-by-side PDF/model reviewer with uncertain annotations
- [ ] Multi-sheet CAD generator, legends, symbols, title blocks, schedules, PDF quality checks
- [ ] Reject ambiguous line crossings, unverified breaker ratings and missing feeder paths

## Milestone 0.4 — advanced studies

- [ ] pvlib/weather-based solar profiles, windpowerlib turbine curves
- [ ] PyPSA or other dispatch optimizer, coupled to time-series electrical feasibility checks
- [ ] Energy metering, utility tariffs, battery degradation assumptions, outage scenarios
- [ ] Documented IEEE/ANSI short-circuit and protection workflows if validated

## Milestone 0.5 — agent and commercial readiness

- [ ] MCP read/propose/study/draw tool server
- [ ] Least-privilege roles, reviewed PR workflow, reproducible CI studies
- [ ] Threat model, unsafe document handling controls, audit event retention
- [ ] Engineering validation report with solver versions and source evidence
- [ ] Production packaging, deployment, authorization, and SBOM/license audit

**Release criterion:** No commercial-grade marketing or professional engineering release until validated study coverage, reviewed equipment catalog, evidence tracing, and an engineer sign-off workflow are implemented and tested.
