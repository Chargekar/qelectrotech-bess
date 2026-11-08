# Reusable PV source and shutdown assets

This family provides original generic module/string/combiner/optimizer/junction-box blocks, AC-module and inverter functions, shutdown equipment/initiator functions and a graphic-only PV boundary. The blocks contain no selected equipment, source count, voltage, current, conductor size or calculated output.

## Levels and port meaning

Keep cell/module, string and array levels explicit. A module block exposes individual positive/negative conductor terminals. A bundled string source exposes one aggregate circuit port; the alternative polarized string block exposes two individual conductors. Tiny module marks in a string glyph are illustrative and never a series-count instruction. Native QET does not enforce this semantic distinction automatically.

An AC-module block represents an assembly's externally exposed AC/bond interfaces. A microinverter is a DC-to-AC function, not an assumed backup/grid-forming system. A dual-input inverter shows conceptual input functions; independent MPPT channels, permitted string combinations and limits require the selected product evidence. An optimizer block does not automatically establish shutdown capability.

## Shutdown and hazard-control semantics

The shutdown equipment and initiating function are separate assets. A logical command port identifies a control relationship, not a mandated dedicated wire. Actual signal transport, operating configuration and compatible equipment/system listing must be documented. The original PV boundary marker is a declared project legend and carries no dimensional, voltage/time, fire-access or compliance proof.

Use `PVSourceSpecification` for rated conditions, product/topology references, temperature-dependent input data, physical/environmental constraints and review. Use `PVShutdownRequirement` for applicability/approach, exact compatible equipment, initiating and activation method, system evidence, boundary/criteria references and verification. These are input/evidence contracts only; no sizing or shutdown calculation runs during asset creation.

Manufacturer shutdown documentation demonstrates why exact compatibility and configuration are separate evidence fields. It is not permission to apply one product's instructions to another product or to replace the actual adopted electrical code. Select the governing PV/shutdown provisions and exceptions for the project/AHJ before drafting a compliance statement. The source register links the inspected primary references; no manufacturer drawing artwork is copied.
