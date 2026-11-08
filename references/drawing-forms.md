# Blank drawing forms, title block and annotation placement

Use `assets/drafting/forms.json`, `assets/drafting/placement-conventions.json`, the six native form elements and header-only CSVs, and `assets/drafting/titleblocks/renewable-original-review.titleblock`. `blank-forms.qet` is a six-sheet asset gallery with empty schedules and an embedded title block. It contains no project equipment, selected ratings or connected design.

Run `python scripts/build_drafting.py` to regenerate these original assets, then `python scripts/build_drafting.py --validate`. `build_assets.py` and `build_gallery.py` regenerate the smaller catalog markers separately. Reconcile native edits into the source before regeneration. Blank forms are generic artwork, not a live database query or automatically populated schedule.

## Native title block

The title block contains project/site identifiers, sheet title/number, revision, scale, drawn/checked/date and source-basis fields. It has a preliminary/not-for-construction banner and an empty rightmost professional area. No logo, professional identity, seal or signature is generated. The blank-forms gallery embeds the template and initializes custom variables to blank; portable use does not depend on another machine's user collection.

The layout and variable syntax follow [QET's native title-block documentation](https://github.com/qelectrotech/qelectrotech-source-mirror/wiki/title_blocks). The artwork/layout is original. Native collection location and blank-variable behavior differ across versions; inspect the actual installed build. Select actual paper size and scale, fill custom project fields from evidence, and inspect the final exported/printed result. A blank scale field is not permission to infer physical dimensions from drawing pixels.

Native `rowspan`/`colspan` values count additional cells: zero means one cell. The builder accepts total-cell spans and converts them. Its validator checks full grid coverage, bounds and overlap; native render inspection remains necessary.

## Schedules and cross-view identity

Equipment, conductor/raceway, control/sensing interfaces, requirement/evidence, sheet index and revision/issue forms are separate. CSV files contain machine-readable headers only; native form rows are blank. Do not interpret blank cells as zero, not-applicable, verified or approved.

Use stable equipment/circuit/interface/requirement/sheet/revision IDs as row keys. Reconcile each row to model records, source revisions, units and the same identities shown on related views. Keep bundle/individual-conductor representation explicit in conductor data. Ratings and calculations require their actual evidence; a schedule heading supplies no engineering value or approved mapping.

Use SheetDefinition, DrawingOccurrence, ScheduleContract and AnnotationPlacement to link views and forms. A drawing occurrence is not a new equipment instance. SLD topology and physical geometry references are independent. Preserve work scope (existing/new/remove/relocate), operating mode, component condition, revision and evidence-review status as separate concepts.

## Fine placement

The placement JSON supplies editable local drawing-unit conventions. They are layout aids, not electrical/fire distances, statutory font limits or physical mounting dimensions. Keep the equipment tag nearest the symbol; use secondary annotations for function/verified rating and refer longer model/evidence text to schedules. Align labels on clear baselines, reserve space for later revisions, and keep leaders/text out of terminal, contact, junction and conductor-bend areas.

Marker placeholders such as `EQ-?`, `N?`, `D?` and `S?` require coordinated native annotation values. A marker leader, flow arrow, match line or continuation outline has no electrical terminals. Cross-sheet electrical continuity must use actual native conductor/report topology. The control marker identifies a logical relation and does not specify wire type or protocol.

Check actual text bounds, leader crossings, sheet/detail-reference targets, longer real IDs, monochrome legibility and print scale. Preserve distinct door/service/electrical/fire envelopes on physical views; annotation offsets do not substitute for those requirements. Review the actual sheet index and revision issue before release, with professional execution and authority permissions tracked independently.
