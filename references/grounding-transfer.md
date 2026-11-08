# Grounding, transfer and generator assets

Use `assets/grounding-transfer/metadata-contracts.json` and the GroundingBondingSpecification, TransferSpecification, GeneratorSpecification and AvailabilityDependency definitions. Load the existing SourceTransition contract for later sequence work. These modules contain no connected design, fuel selection, sizing result or default performance value.

## Grounding and terminal roles

Keep neutral/grounded circuit conductors, equipment grounding conductors (EGC), grounding electrode conductors (GEC), electrodes and bonding jumpers distinct. A neutral bar has individual AC-conductor ports and no implicit protective-earth connection. A grounding bar has protective-bond ports. Their declared common connection applies only within that domain; native artwork is not a general circuit solver.

MBJ, SBJ and EBJ identify different bonding functions. Assign their actual endpoints, permitted neutral/bonding connection, system grounding arrangement and installation location through a reviewed grounding detail. Do not interpret two generic bonding ports as permission to bond any neutral to an enclosure. Determine separately-derived-system status from the complete source/transfer/neutral arrangement and applicable rules. [Cummins T-011](https://www.cummins.com/sites/default/files/2024-08/t011-Transfer-switch-application-manual.pdf) illustrates why neutral treatment affects system grounding; its 2014 code citations require an adoption/edition check.

The rod glyph identifies one electrode type without selecting rod length, count, spacing, soil conditions or the complete electrode system. Product qualification, terminations, materials, corrosion and continuity/fault-path evidence remain project inputs. [UL's grounding component overview](https://www.ul.com/services/grounding-and-lightning-protection-component-evaluations) is a qualification starting point; a generic symbol does not carry a listing.

GEC/EGC callouts are graphic markers with no electrical terminals. Place them as annotations beside the actual native conductor/path. AC/DC terminal blocks represent individual conductors, without selecting phase, polarity, neutral or internal product topology. The CT test block represents physical individual secondary conductors. Its shorting arrangement, test sequence and wiring must come from the exact manufacturer detail; do not replace this detail with logical sense lines. See [Schneider's CT guidance](https://www.se.com/us/en/faqs/FA219147/).

## Transfer category, observed position and availability

Open/closed transition describe equipment/sequence categories. Observed switch position belongs in SwitchPosition, with its mode/time/evidence context. Manual/automatic operation and neutral treatment are separate attributes. Generic functional transfer blocks do not select poles, timing, synchronization, protection or a permitted source-parallel duration. Closed-transition artwork establishes neither utility authorization nor uninterrupted power. Bypass/isolation behavior requires the exact internal topology, interlocks and interruption evidence; product implementations vary. [Cummins T-011](https://www.cummins.com/sites/default/files/2024-08/t011-Transfer-switch-application-manual.pdf) provides manufacturer examples, not universal project defaults.

Represent transition guards, source quality, control supply, commanded switch actions and failure response with SourceTransition and related evidence. The interlock asset represents a logical relationship; verify the actual mechanical/electrical implementation and approved combination separately. Generator connection cabinets require explicit source isolation, connector configuration and neutral/bonding review. Load banks and auxiliary heater/charger/start-energy blocks are separate functions, with no capacity or runtime assertion.

Generator application class is a regulatory/design classification, not its present condition or a geographic jurisdiction. Use ComponentCondition for available/degraded/failed/maintenance observations and jurisdiction records for the governing location. AvailabilityDependency captures later starting-energy, fuel, auxiliary power, cooling, controls, transfer-path and common-cause review. Counting sources alone does not establish redundancy or five-day autonomy. No such project case is instantiated here.

## Fuel and environmental permissions

Fuel/exhaust legends have non-electrical annotation anchors only. They do not select fuel quantity, tank construction, discharge location or clearance. Future autonomy work needs usable fuel, duty/consumption evidence, refill assumptions and concurrent dependencies, alongside the electrical load boundary.

California generator review may involve CARB and the actual air district, plus fire, environmental, noise and utility requirements. [CARB's backup-generator page](https://ww2.arb.ca.gov/our-work/programs/emergency-backup-generators/about) and [Bay Area engine permitting](https://www.baaqmd.gov/permits/apply-for-a-permit/engine-permits) are source starting points. Bay Area requirements are local; they are not statewide or USA defaults. Record applicability, permit conditions, source revision and reviewer before an operational claim. No operating-hour allowance or universal permit exemption is encoded.
