# Constraint ontology and asset-selection contracts

Use this only for the relevant domain. Do not instantiate a design case or calculate a size for an asset-library request. The schema's definitions are reusable contracts for later project data.

## Physical and environmental

An equipment symbol, its physical footprint, its required clearances and its engineered support detail are four different assets. Link them by IDs. Store mounting method (wall/floor/pad/rack/roof/pole), installation location, supporting material, service/door faces, footprint/height/weight, permitted orientation, attachment/anchor/load-path references and restrictions. Keep manufacturer limits, measured site facts and engineered limits distinct.

For exposure, record coastal/salt-spray evidence, corrosion mechanism/category, enclosure/material/coating selection, compatible fasteners/galvanic isolation, wet/damp ingress qualification, ambient/altitude limits, UV, condensation, contaminants, maintenance and warranty restrictions. Do not infer corrosion suitability solely from a Type 4X or IP label. A coastal-jurisdiction permit requirement is a separate jurisdiction fact from salt exposure.

A conduit asset has a raceway type, trade size, material/coating, allowed installation/support/bend/joint/fitting conditions, transition/expansion/bonding details and source/review fields. Raceway type alone does not establish fill, wet-location conductor suitability, burial depth, corrosion protection or ampacity. Reusable choices include EMT, IMC, RMC, FMC, LFMC, LFNC, PVC/RNC and RTRC; project applicability remains open until verified.

## Electrical

Model a service voltage as quantity plus basis/configuration: AC/DC, nominal/range V, line-to-line/line-to-neutral, phases, wire/neutral availability, frequency, topology, grounding and source evidence. Equipment ports reference this system and their own permissible range/configuration. A nominal 480 V declaration alone must leave wye/delta, neutral and grounding unknown.

Treat current, trip/frame, withstand/SCCR, interrupting rating and fault contribution as separate quantities. Conductor/raceway assets require material/insulation/wet rating, temperature/termination basis, circuit grouping, route/exposure, quantities/neutral/EGC, length, installation constraints and subsequent calculations. Symbol proximity cannot supply these inputs.

## Resilience and source transitions

Declare autonomy duration and its supply boundary: BESS-only, coordinated island system, or another explicitly defined basis. Include critical-load time series/units/intervals, outage windows, allowable interruption/unserved energy, energy/power basis, initial SOC, usable SOC window, end-of-life/temperature derating, efficiency and auxiliary loads. Record whether PV/resource uncertainty can be credited; a favorable daily average is not an outage proof.

Source roles (normal, alternate, fallback) and source health are separate from operating mode. Define events/guards/actions for grid loss, BESS failure/low energy, generator start/failure, transfer/retransfer, emergency shutdown and controls/communications loss. Include transfer/isolation devices, auxiliary/control power, neutral/grounding behavior, backfeed prevention, synchronization/permitted parallel operation and common points of failure.

Represent N+k with N definition, function/load served, unit capacities, k, failure set, independence/common-cause dependencies, duration and verification reference. Preserve an owner's label as `claimed_label`; use `unverified` until the defined claim is checked. Do not equate mains+BESS+generator with proved N+2.

## Calculation and energy-code requirements

Store a CalculationRequirement with purpose, jurisdiction/rule edition/errata, required inputs, units and capacity basis, method/software version, assumptions, calculation artifact, result, reviewer and disposition. A missing input is null/open, not zero. No default numerical factors or code table values are encoded in this first ontology increment.

For California Part 6, determine occupancy/building scope, new/alteration status, compliance path, climate zone, relevant floor/solar access areas, applicability/exceptions, approved software/forms, current rule/errata and JA12 equipment/control requirements as applicable. For other US jurisdictions select their own adopted energy-code basis. The code compliance result, product qualification, physical fit, electrical compatibility and resilience result are independent selection predicates.

The CEC's published 2025 guidance identifies corrections to BESS capacity tables; retrieve the current adopted/errata-adjusted source before later numerical implementation. This is why a copied historical formula/table is not an asset-level constant.
