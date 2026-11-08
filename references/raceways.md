# Raceway and installation legend assets

This family contains original generic NTS graphics for eight raceway type identifiers and routing/fitting/support annotations. They are drafting blocks, not manufactured details. The eight type records remain in `assets/raceways/types.json`.

The catalog declares `view_kind: installation-legend`, zero electrical ports and `connection_semantics: non-electrical-annotation`. Optional annotation anchors align physical route graphics; they must never become native electrical terminals. A raceway contains or supports circuits, but it is not a substitute for the conductors/circuit connections represented on an SLD.

## Blocks and intended use

- EMT, IMC, RMC, FMC, LFMC, LFNC, PVC and RTRC identifiers: identify a selected raceway type. Neither the line artwork nor the abbreviation supplies trade size, material/coating or environmental suitability.
- Elbow and offset: indicate routing intent. Specify actual bend radius, cumulative bends and pulling constraints from the selected installation/design evidence.
- UP/DN, UG/OH: project legend markers for a riser direction or route condition. These are original conventions, not a claim of universally standardized plan symbols. Define them in the project's legend and provide actual elevation/clearance/burial information separately.
- Sleeve and firestop: mark a referenced penetration treatment. A firestop glyph does not identify a tested assembly or establish a fire rating. Reference the applicable assembly, penetrants, wall/floor and installation conditions.
- Expansion fitting, support, conduit body, pull box and transition: locate a function requiring a selected compatible product/detail. No stroke, support spacing, box sizing, bonding adequacy, attachment strength or listed compatibility is embedded in the geometry.

## Future project input contract

Resolve type/trade size, material/coating, route/exposure, compatible fitting listing, support and expansion details, bonding, fill/pulling/bending calculations, access, penetrations, actual adopted rule edition/locator, manufacturer restrictions and reviewer. `RacewaySpecification` and `RacewayRouteAnnotation` in the domain schema keep these data separate from electrical ports and geographic/operating states.

The manufacturer references in the source register establish product families and the importance of type/material/installation selection. They do not authorize applying a particular manufacturer's detail to another product or overriding the adopted electrical code. No source artwork is copied into this library.
