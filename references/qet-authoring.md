# QElectroTech asset authoring

Use the catalog as the semantic/terminal contract and `build_assets.py` as the original geometry source. Do not hand-edit generated copies without reconciling the generator. The library uses plain XML .elmt and .qet for portability; an application may offer other save formats.

## Local tool discovery and native checks

On this workspace's Windows host, the development wrapper is:

```powershell
& "$env:LOCALAPPDATA\Programs\QElectroTech\qet.cmd" --check-elements "<element-directory>"
& "$env:LOCALAPPDATA\Programs\QElectroTech\qet.cmd" --info "<gallery.qet>" "<info.json>"
& "$env:LOCALAPPDATA\Programs\QElectroTech\qet.cmd" --export-png "<gallery.qet>" "<output-directory>"
```

Discover paths/flags again on another machine. The installed stable 0.100 and development 0.200.1 builds are separate. The wrapper uses isolated CLI settings and the packaged Windows Qt platform plugin. This Windows development package does not include the offscreen plugin; do not blindly set `QT_QPA_PLATFORM=offscreen` from Linux examples. `--version` was unsuitable as a headless probe on this package; use a documented CLI operation with a timeout.

The official automation reference documents project inspection and export verbs. A zero exit code and count report establish native load/export behavior, not electrical correctness. Native output should be inspected. Keep batch settings and GUI preferences separate; use copies for resave compatibility checks.

## XML contracts that matter

- `.elmt` has a definition, names, provenance information, graphical description and real terminal primitives. Terminal positions/orientations must agree with the catalog. Stable UUIDs are deterministic in the generator.
- A terminal's `representation` in the catalog distinguishes circuit bundle from individual conductor, protective bond or functional signal. AC/DC alone is insufficient. Native QET artwork does not enforce this semantic distinction for the user.
- A project contains direct `diagram` children. Embedded definitions live under its collection. A placed element references the embedded location and has terminal records, metadata, position and orientation.
- Real electrical connections require native conductors referencing actual terminals. Drawn lines inside a symbol do not create a general circuit solver, nor prove protection or topology. In particular, a drawn multiport bus has a semantic internal-common contract, while QET's potential export may not model that internal relation.
- The included gallery deliberately has no connected conductors and no equipment selection: it is an unconnected review index. Free terminals are expected there.
- Installation legend assets deliberately have no electrical terminals. The development CLI reports a zero-terminal warning for each such file even when it loads successfully. Reconcile those warnings against the catalog's annotation contract; do not add fake terminals or suppress unrelated warnings to make the report look clean.

## Collections and data preservation

Build into a dedicated output folder. For a user collection install, copy this library into a distinct `bess` subfolder of the selected user's collection. Never overwrite unrelated user symbols. Installed stable/development profiles and their user collections are separate. Keep generated library assets and source catalog/scripts together when distributing the skill.

Current file edits are one-way. Reconcile GUI changes back into the source model/catalog before rebuilding. Do not silently regenerate over edited project work.

When the optional relational/Draw.io vocabulary is present, new catalog IDs also need explicit mappings. `python scripts/sync_catalog_mappings.py` reports missing entries; `--write` appends clearly labelled basic rectangle fallbacks and preserves existing verified stencil mappings. A fallback is not a claimed artwork conversion. Validate database construction using a fresh `--output` path; preserve a live/user-populated database and existing Draw.io project templates rather than overwriting them during asset-only work.
