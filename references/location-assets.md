# Physical location, mounting and environment assets

Load `assets/location/geometry-contracts.json` and the PhysicalCoordinateFrame, FootprintDefinition, MountingInterface, SpatialEnvelopeRequirement and EnvironmentalExposureRecord definitions. These extend the existing PhysicalConstraint and EnvironmentConstraint contracts. The native blocks are visibly marked NTS previews, with no selected equipment, site layout or physical dimensions.

## Geometry and identity

Keep physical model coordinates, sheet/paper coordinates and symbol-preview coordinates in separate frames. Declare physical units, origin, axes, horizontal reference, vertical datum and north basis as applicable. QET glyph coordinates are drawing units; dragging or stretching the icon does not establish an equipment dimension or survey. The normalized unit-box primitive is an abstract ratio: apply sourced width/depth and an explicit transform only when later project data exists.

For dimensioned use, obtain actual product/measured/engineered geometry, revision/configuration and dimensional evidence. Rebuild the physical outline from that data; place text, line weights, door geometry, service face and clearance envelopes separately. Resolve every geometry/frame/source reference before export. A schema-valid reference string does not prove that its target exists or uses compatible units. No source dimensions or engineering capacities are supplied by this library.

Link each physical occurrence to the same equipment identity/tag used on the SLD and schedules. Keep footprint, door sweep, service envelope, electrical working space and fire-exposure separation as separate objects. Dimension from named faces/surfaces to actual obstructions, property lines, openings and routes. [San Diego IB 301](https://www.sandiego.gov/development-services/forms-publications/information-bulletins/301) and [IB 122](https://www.sandiego.gov/development-services/forms-publications/information-bulletins/122) are local examples of location/roof/site information; apply the actual receiving agency's requirements. Their numerical prescriptions and source artwork are not copied into these assets.

## Mounting and access

Wall/roof/rack/pad sections identify relationships, not designed connections. Replace schematic supports with the approved detail and calculations for the actual substrate, equipment mass/center of gravity, load path, wind/seismic basis, anchors/fasteners, corrosion compatibility, bonding and waterproofing. A target marker references an anchorage detail; it supplies no anchor pattern or capacity. A bollard marker supplies no impact rating or foundation design.

Door/gate arcs and PV grids are illustrative; do not read an opening angle, leaf count, module count, array tilt or roof slope from them. Source actual geometry before using it to assess movement or clearance. The route marker does not prove an accessible route, egress or fire-access path. [US Access Board guidance](https://www.access-board.gov/ada/guides/chapter-4-accessible-routes/) provides a federal starting point; determine applicable California/local/occupancy requirements independently. No universal path width, slope or separation is encoded.

Clearance graphics use distinct monochrome patterns and purpose labels. Preserve a legend and separate applicability/evidence records even when two envelopes overlap. Equipment service access, electrical working space, fire separation, roof pathways and accessible circulation can all apply concurrently; one boundary cannot stand in for the others.

## Exposure and geographic jurisdiction

Physical salt/corrosion/flood markers attach to exposure evidence and actual location/elevation records. Verify enclosure, material, coating, fasteners, galvanic interfaces, ingress, maintenance and manufacturer restrictions for the specific exposure. An enclosure label alone does not establish the complete installation's corrosion suitability; see the NEMA/manufacturer starting sources in `sources.md`.

California's Coastal Zone is a legal/geographic boundary. [Coastal Commission maps](https://www.coastal.ca.gov/maps/czb/) describe their use limits and potential need for a formal boundary determination. They do not establish a site's salt spray, corrosive environment or survey accuracy. Keep that jurisdiction record separate from EnvironmentalExposureRecord and EnvironmentConstraint. Likewise, a graphic water line is not a flood elevation: require the actual hazard study, datum and equipment/site elevation evidence.

The north arrow needs an actual true/grid/project/magnetic basis and orientation reference. A generic roof edge, fence or plan symbol does not verify a surveyed boundary. No PE/surveyor seal or signature is generated.
