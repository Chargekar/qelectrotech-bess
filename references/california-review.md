# California project review and release

Research date: 2026-11-06. Recheck sources for each project. These are review topics, not a complete rule engine. Exact sections, exceptions, thresholds and amendments must be read in the adopted edition and recorded in project requirements.

## Establish applicability before drafting compliance notes

The 2025 California Electrical Code adopts the 2023 NEC with California amendments, effective January 1, 2026 [CA-CEC]. Select the edition by the actual permit/vesting basis and AHJ, including applicable supplements/errata. Do not choose an edition just because a historic example uses it. The current model-code publication is not necessarily the adopted code.

Record building and fire authorities, local amendments, occupancy, installation setting (indoor/outdoor/garage/roof), energy quantity/chemistry, flood/WUI/seismic context, and whether DSA/HCAI or other special jurisdiction applies. Residential provisions and commercial/container installations are separate review paths. NFPA 855 edition/applicability must be established from adopted references and AHJ requirements; never assume the newest edition is adopted statewide.

For utility interconnection, identify the actual utility and tariff. CPUC Rule 21 addresses applicable IOU interconnections; municipal utilities and wholesale/CAISO arrangements require their own basis [CPUC-R21]. Obtain project-specific approved interconnection and control settings.

## Electrical review topics

| Topic | Evidence/drawing outcome | Starting code topics to verify |
|---|---|---|
| Existing service and point of connection | field survey, utility/service data, existing/demo/proposed relationship | CEC 110, 230, 705 |
| Bus/interconnection method | explicit selected method and calculation, main/bus ratings, source placement | CEC 705; do not default every case to a 120% rule |
| Conductors/raceways | load/source current, ampacity/correction/adjustment, terminals, fill, voltage drop, length | CEC 110, 210/215 as applicable, 240, 300, 310, Chapter 9 |
| Overcurrent and equipment withstand | available fault current, SCCR/AIC, device settings, protection/coordination | CEC 110, 240, applicable equipment articles |
| PV | maximum cold Voc, source circuits, string limits, RSD, disconnects, routing/marking | CEC 690 and 705 |
| ESS/converter | actual product combination, energy/power/current, charging/discharging, isolation | CEC 706 and applicable 480 provisions |
| Power controls | approved/listed scope, sensing/polarity, control supply, setpoints/failure behavior | CEC 705 power-control provisions; utility requirements |
| Grounding/bonding | EGC/GEC/bond/neutral locations; derived-system and switching analysis | CEC 250 and source-specific provisions |
| Backup/islanding | separation, switching/neutral, source forming/following, protection, reconnection | CEC 702/705/706; 700/701/708 only when applicable |
| Working space/signage | actual dimensions, service access, source directories, warning/identification | CEC 110 and source-specific labeling |

Use manufacturer current ratings rather than calculating output solely from kW/nominal voltage where nameplate data governs. Do not implement a blanket continuous-current multiplier or use export limitation as a universal exemption from conductor/bus requirements.

## Fire, spatial and structural review

- Determine applicable CFC ESS provisions (including Section 1207 where applicable) or adopted residential provisions. Verify the current edition's numbering and residential limits. Do not reuse obsolete R328 notes by habit.
- Verify exact ESS system certification/listing, battery and inverter compatibility, installation manual revision, and environmental/location restrictions. UL 9540 is a system safety/certification basis; UL 9540A is a fire-propagation test method, not a product listing [UL-SYSTEM, UL-TEST]. A test report is not an automatic spacing waiver.
- Resolve quantity/energy limits, unit/group separation, property/building/opening exposures, egress and responder access, detection/suppression, ventilation/gas/explosion controls, emergency shutdown, signage and emergency response/commissioning plans as applicable.
- Obtain measured/site-supported footprints, equipment service faces/doors, dimensioned working space, conduit routes, roof access/pathways/ridges, clearances, accessible routes, fences/gates, vehicle impact exposure and protection.
- Identify equipment weights, mounting elevations, anchorage, pad/roof load path and required seismic/wind/geotechnical/structural calculations. Generic pad/anchor graphics are not engineered details.

Use San Diego's current bulletin only for San Diego scope [SD-301]. Other AHJs can impose different application paths. The starter does not encode numerical fire/working clearances as universal California defaults.

## Release checklist

Record each item as an explicit requirement with an owner and disposition. Automation may flag missing data; it does not supply professional approval.

1. Confirm site/scope/survey and current AHJ/utility/code basis.
2. Resolve equipment nameplate, certification, installation and compatibility evidence.
3. Complete service/interconnection, load/demand, ampacity, raceway, fault/protection, grounding, PV and applicable storage/control calculations.
4. Resolve each operating mode, export policy, isolation/reconnection, control/auxiliary failure behavior and required commissioning verification.
5. Resolve fire, spatial, structural, architectural/accessibility and utility review requirements.
6. Cross-check all sheets, tags, counts, circuits, schedules, notes, calculations and evidence revisions. Remove obsolete or contradictory details.
7. Inspect native-rendered sheets at final print size. Check issue/revision/date, sheet index, scales, north, legible annotations, references, and blank seal area.
8. Complete responsible professional review under the applicable California practice law and AHJ rules [CA-PE]. The actual licensee controls signing/sealing; no generated stamp or signature.
9. Record AHJ acceptance, utility authorization to operate/energize and field/commissioning requirements as distinct milestones. A building approval alone is not utility permission.

Never silently remove an unresolved requirement to make a package appear complete.
