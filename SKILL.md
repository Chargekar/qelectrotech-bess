---
name: qelectrotech-bess
description: Build reusable QElectroTech PV/BESS engineering assets, native electrical symbols, equipment-location graphics, compliance-note templates and compact ontologies for California and other US jurisdictions. Use for .elmt/.qet asset libraries and coordinated engineering drawings; professional review and sealing remain with the responsible licensee.
---

Develop editable drawing packages from an explicit project model. Start with the ontology, then assets, then drawings. A polished drawing or successful XML check is not engineering verification.

## Model first

Read [the ontology](references/ontology.md), then load only the relevant module from [the retrieval index](references/INDEX.md). Use [the typed domain contract](assets/ontology/domain.schema.json) to distinguish jurisdiction, operating mode, component condition, and review status. Do not use a bare `state` property. Keep unknown inputs null.

For asset-only requests, build reusable components, metadata contracts and note templates. Do not invent project scenarios, choose project equipment, or perform specific calculations. Autonomy duration, redundancy/failure cases, voltage configuration, environmental exposure, and future sizing inputs belong in the ontology until a project calculation is requested.

Maintain stable equipment, port, circuit, location, requirement, and source IDs. Physical placement and schematic layout are different coordinate systems. Power, protective earth, sensing, and control are distinct domains. Resolve whether PCS means power conversion system or power control system.

Read [California review](references/california-review.md) for compliance work. Verify current official AHJ, utility, adopted-code, certification, and manufacturer sources for real projects. [The source register](references/sources.md) is a starting corpus. Historical plans inform drafting; they establish neither current requirements nor reuse rights.

For rule-scope and compliance-note work, read [applicability](references/applicability.md). Keep applicability decisions, evidence review and external authorizations separate; jurisdiction profiles supply research starting points, not automatic project defaults.

For relational-model work, run `python scripts/build_db.py --output <fresh-qa-path>` first; the builder replaces its target, so preserve live/user-populated databases. Query clauses with `python scripts/truth.py`; evaluate formulas only when calculations are requested. Results built on unverified truth rows are PRELIMINARY. See [compliance truth](references/compliance-truth.md). Regenerate Draw.io templates with `python scripts/build_drawio.py` only when that output is requested, preserving existing user drawings; use verified stencils or explicitly declared generic fallbacks.

## Assets and native authoring

Use [the catalog](assets/catalog.json) to select original generic symbols and terminal contracts. Run `python scripts/build_assets.py --output <folder>` to regenerate the library and contact sheet. Electrical symbols need named terminals, domains, stable UUIDs, hotspots, and provenance. Do not substitute decorative lines for native conductors or claim the generic library is exact IEEE/IEC artwork or a manufacturer-certified design.

Read [QET authoring](references/qet-authoring.md) before native XML changes or CLI use and [placement conventions](references/placement.md) for symbol/annotation/detail spacing. Discover executable/version and flags; stable and development builds differ. Separate GUI and batch settings, and resave copies. QET does not perform conductor sizing, protection coordination, structural analysis, or fire analysis.

## Drawings and verification

1. Run `python scripts/validate_library.py`. Fix catalog, ontology, metadata, resource-link and native asset errors.
2. Run `python scripts/build_gallery.py --output <folder>` to create a native symbol gallery for review. It is an asset index, not an electrical design scenario. Use the catalog, note templates and profile modules to author project drawings only when requested.
3. Expand sheets to fit scope: cover/code basis, site/roof/equipment locations, existing/demo/proposed SLD, grounding, controls/sequence, calculations, placards, mounting/anchorage, and product documents. Reuse the same asset IDs across views.
4. Native-load and export the QET; inspect every sheet for legibility at printed size, continuity, real terminals, junctions/crossings, collisions, title blocks/revisions, scale/north/dimensions, and schedule agreement. CLI inspection checks structure only and does not establish engineering correctness.
5. Deliver editable drawings/model, readable exports, schedules, source references, and open issues. Report the checks actually run and limitations. Keep PRELIMINARY / NOT FOR CONSTRUCTION until an authorized engineering release. Leave the seal area blank; never synthesize a PE seal, signature, or approval.

Use the release checklist in `references/california-review.md` for California, and select the actual adopted rules for other US jurisdictions. A passed requirement needs project-specific evidence and a reviewer. Distinguish consistency checks, calculations, AHJ acceptance, utility authorization, and professional sign-off. Unresolved inputs must not become “compliant,” “permit ready,” or “PE approved.” A symbol or note template does not calculate ratings, fault current, export performance, fire separation or anchorage.

The model is canonical for regeneration. Reconcile GUI edits into it before rebuilding: this starter does not merge native changes back into JSON.
