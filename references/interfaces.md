# Control, sensing, service and protection interfaces

Load `assets/interfaces/metadata-contracts.json` and the relevant typed definitions: ControlFunctionSpecification, SensorSpecification, ProtectionSpecification and DistributionAssemblySpecification. These are reusable input contracts, with no project ratings or control settings selected.

## Functional roles and terminal meaning

`power_conversion_system` converts power; `power_control_system` represents a limiting/control function. `energy_management_system` represents supervisory energy management. A controller name does not establish certified limiting performance, utility authorization or energy-code qualification. Resolve the exact hardware, firmware, measured boundary, controlled sources, setpoints, failure response and commissioning evidence. [UL's power-control overview](https://www.ul.com/services/power-control-systems-distributed-energy-resource-systems) is a starting source; evaluate the applicable edition and certified configuration for the project.

Solid terminal stubs represent power or protective bonding. Dashed control/sense stubs represent logical relationships. Select the line convention and legend for actual native conductors separately. Logical interfaces do not prescribe a cable, CT secondary pair, dry contact, voltage, communications protocol or redundant network. A `trip_coil` block is a trip function; the actual coil supply and circuit need a separate wiring detail. `ups_function` contains no runtime assertion.

CT, voltage-sensor and meter functions need measured-circuit references and explicit physical-interface evidence. Track ratio, polarity/orientation, accuracy/burden, secondary circuit, protection and auxiliary supply where applicable. Do not infer instrument-transformer wiring from a logical sense terminal. [Schneider's CT guidance](https://www.se.com/us/en/faqs/FA219147/) and [product-specific metering-ratio guidance](https://www.se.com/us/en/faqs/FA203246/) illustrate why the exact manual and field configuration matter; their product examples are not library defaults.

## Assemblies and distinct ratings

Switchboard, panelboard and combiner outlines are functional equipment boundaries. Their multiple ports do not assert an internal common bus, source interconnection method, selected breaker positions or neutral-to-ground bond. Create the actual internal topology and listing evidence only for a requested project. The service-disconnect asset does not establish service-equipment suitability.

Keep bus rating, breaker frame/trip current, interrupting rating, assembly SCCR, short-time withstand and available fault current as separate references. Retain exact voltage/configuration and any series-combination evidence. One rating does not substitute for another. [UL's panelboard guide](https://www.ul.com/thecodeauthority/knowledge/panelboards-guide) discusses assembly markings and conditional combinations; its cited code provisions require an edition/adoption check. [Eaton's commercial metering switchboard guide](https://www.eaton.com/content/dam/eaton/products/design-guides---consultant-audience/eaton-swbd-comm-metering-design-guide-dg015006en.pdf) supplies manufacturer-specific examples of these distinct attributes. No source dimensions, values or artwork are copied into these generic assets.

Switch-contact artwork is an identifying glyph, not a recorded operating position. Review status is a workflow record, jurisdiction is geographic, and device function is a component role. Keep each in its own namespace. A passed input contract or native-load check is not a protection-coordination result or engineering release.
