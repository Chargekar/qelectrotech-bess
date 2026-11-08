# Load only the needed engineering context

| Task | Read | Machine assets |
|---|---|---|
| Meaning of terms/relationships | `ontology.md` | `assets/ontology/vocabulary.json`, `domain.schema.json` |
| Native symbol creation/QET behavior | `qet-authoring.md` | `assets/catalog.json`, `assets/library/elements/bess` |
| Raceway types, routes, fittings and support legends | `raceways.md` | `assets/raceways/types.json`, RacewaySpecification and RacewayRouteAnnotation definitions |
| PV source hierarchy, polarity, inverters and shutdown functions | `pv-assets.md` | `assets/pv/metadata-contracts.json`, PVSourceSpecification and PVShutdownRequirement definitions |
| Control, sensing, service assemblies and protection ratings | `interfaces.md` | `assets/interfaces/metadata-contracts.json`, ControlFunctionSpecification, SensorSpecification, ProtectionSpecification and DistributionAssemblySpecification definitions |
| Grounding/bonding roles, generator dependencies and transfer categories | `grounding-transfer.md` | `assets/grounding-transfer/metadata-contracts.json`, GroundingBondingSpecification, TransferSpecification, GeneratorSpecification, AvailabilityDependency and SourceTransition definitions |
| Location/roof/mounting graphics, physical frames, clearance envelopes and exposure markers | `location-assets.md` | `assets/location/geometry-contracts.json`, PhysicalCoordinateFrame, FootprintDefinition, MountingInterface, SpatialEnvelopeRequirement and EnvironmentalExposureRecord definitions |
| Fine schematic and sheet placement | `placement.md` | symbol geometry and terminal contracts |
| Native review title block, blank schedules and drawing-reference markers | `drawing-forms.md` | `assets/drafting`, SheetDefinition, DrawingOccurrence, ScheduleContract and AnnotationPlacement definitions |
| Geographic/code applicability | `california-review.md` and relevant jurisdiction profile | `assets/profiles/index.json` |
| Applicability decisions, note release and separate authority milestones | `applicability.md` | `assets/compliance/applicability-contracts.json`; AuthorityScope, RuleApplicability, ComplianceNoteInstance and ExternalAuthorizationRecord definitions |
| Mounting/location/coastal/corrosion | `constraints.md` physical/environment sections | typed PhysicalConstraint and EnvironmentConstraint definitions |
| Voltage/grounding compatibility | `constraints.md` electrical section | ElectricalConstraint definition |
| Autonomy/redundancy/future sizing inputs | `constraints.md` resilience/calculation sections | ResilienceRequirement and CalculationRequirement definitions |
| Reusable compliance notes | source register and applicable current official rules | `assets/notes/compliance-notes.json` |
| Code truth, formulas, relational DB, Draw.io export | `compliance-truth.md` | `assets/db/*.json`, `schema.sql`, `scripts/truth.py`, `build/bess.sqlite` |
| Truth seed change log, weekly source review | `watchtower.md` | `scripts/watchtower.py`, `watchtower/`, `assets/db/TRUTH_CHANGELOG.md` |
| Corpus expansion/provenance | `sources.md` | source IDs referenced by profiles/notes |
| Optional relational truth/vocabulary and Draw.io mappings | `compliance-truth.md` | `assets/db` and `assets/drawio`; new QET catalog IDs can use explicit basic-block fallbacks without invented stencils |

`US-BASE` is an unadopted vocabulary/reference profile, not enforceable US law. `US-CA` is a California starting profile requiring project edition/AHJ selection. Other states must receive their own verified adoption/profile; never fall back to California requirements silently.
