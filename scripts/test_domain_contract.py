"""Behavioral contract checks; no project scenario or sizing calculation. Requires jsonschema."""
import json
from pathlib import Path
try:
    from jsonschema import Draft202012Validator
except ImportError:
    raise SystemExit('Install jsonschema in the chosen Python environment to run domain-contract tests.')

ROOT=Path(__file__).resolve().parents[1]
schema=json.loads((ROOT/'assets/ontology/domain.schema.json').read_text(encoding='utf-8'))
Draft202012Validator.check_schema(schema)
def check(name,document,valid):
    errors=list(Draft202012Validator(schema).iter_errors({'ontology_version':'1.1.0',**document}))
    assert bool(errors)!=valid, f'{name}: expected valid={valid}, errors={[e.message for e in errors]}'

cases=[
    ('jurisdiction namespace accepts US-CA',{'jurisdiction':{'country':'US','subdivision_code':'US-CA'}},True),
    ('mode namespace accepts operating mode',{'operating_modes':[{'id':'type-check-only','mode':'grid-parallel'}]},True),
    ('geography cannot be operating mode',{'operating_modes':[{'id':'type-check-only','mode':'US-CA'}]},False),
    ('operating mode cannot be geography',{'jurisdiction':{'country':'US','subdivision_code':'grid-parallel'}},False),
    ('bare state forbidden',{'state':'California'},False),
    ('nested bare state forbidden',{'jurisdiction':{'country':'US','subdivision_code':'US-CA','state':'islanded'}},False),
    ('health cannot be geographic',{'component_conditions':[{'equipment_ref':'type-check-only','condition':'US-CA'}]},False),
    ('SOC has fraction bounds',{'battery_soc_records':[{'equipment_ref':'type-check-only','soc_fraction':2}]},False),
    ('unknown voltage accepts null',{'electrical_constraints':[{'id':'type-check-only','subject_class_or_ref':'class-only','current_kind':'unresolved','voltage':{'value':None,'unit':'V','evidence_status':'unknown'},'review':{'status':'open'}}]},True),
    ('energy cannot be voltage',{'electrical_constraints':[{'id':'type-check-only','subject_class_or_ref':'class-only','current_kind':'unresolved','voltage':{'value':None,'unit':'kWh','evidence_status':'unknown'},'review':{'status':'open'}}]},False),
    ('energy cannot be autonomy time',{'resilience_requirements':[{'id':'type-check-only','autonomy_duration':{'value':None,'unit':'kWh','evidence_status':'unknown'},'review':{'status':'open'}}]},False),
    ('pass needs evidence/reviewer',{'physical_constraints':[{'id':'type-check-only','subject_class_or_ref':'class-only','review':{'status':'pass'}}]},False),
    ('not-applicable needs reason',{'physical_constraints':[{'id':'type-check-only','subject_class_or_ref':'class-only','review':{'status':'not-applicable'}}]},False),
    ('verified quantity cannot remain unknown',{'electrical_constraints':[{'id':'type-check-only','subject_class_or_ref':'class-only','current_kind':'unresolved','voltage':{'value':None,'unit':'V','evidence_status':'verified','source_refs':['type-check-only']},'review':{'status':'open'}}]},False)
]
cases.extend([
    ('raceway specification is physical containment',{'raceway_specifications':[{'id':'type-check-only','type_id':'unresolved','review':{'status':'open'}}]},True),
    ('route annotation cannot define electrical ports',{'raceway_route_annotations':[{'id':'type-check-only','raceway_specification_ref':'class-only','ports':[{'domain':'ac'}],'review':{'status':'open'}}]},False),
    ('raceway type is not an operating state',{'raceway_specifications':[{'id':'type-check-only','type_id':'grid-parallel','review':{'status':'open'}}]},False),
    ('route cannot use geographic state as installation condition',{'raceway_route_annotations':[{'id':'type-check-only','raceway_specification_ref':'class-only','installation_condition':'US-CA','review':{'status':'open'}}]},False)
])
cases.extend([
    ('PV source can retain unresolved level and representation',{'pv_source_specifications':[{'id':'type-check-only','source_level':'unresolved','terminal_representation':'unresolved','review':{'status':'open'}}]},True),
    ('PV source level is not operating mode',{'pv_source_specifications':[{'id':'type-check-only','source_level':'grid-parallel','terminal_representation':'circuit-bundle','review':{'status':'open'}}]},False),
    ('PV module count cannot be zero',{'pv_source_specifications':[{'id':'type-check-only','source_level':'string','terminal_representation':'circuit-bundle','series_module_count':0,'review':{'status':'open'}}]},False),
    ('PV representation cannot use a current domain value',{'pv_source_specifications':[{'id':'type-check-only','source_level':'module','terminal_representation':'dc','review':{'status':'open'}}]},False),
    ('shutdown approach cannot use geographic jurisdiction',{'pv_shutdown_requirements':[{'id':'type-check-only','approach':'US-CA','review':{'status':'open'}}]},False)
])
cases.extend([
    ('control role can remain unresolved',{'control_function_specifications':[{'id':'type-check-only','function_type':'unresolved','review':{'status':'open'}}]},True),
    ('control role cannot be geographic',{'control_function_specifications':[{'id':'type-check-only','function_type':'US-CA','review':{'status':'open'}}]},False),
    ('control role is distinct from power conversion',{'control_function_specifications':[{'id':'type-check-only','function_type':'power-conversion','review':{'status':'open'}}]},False),
    ('logical measurement is an explicit sensor basis',{'sensor_specifications':[{'id':'type-check-only','sensed_quantity':'current','interface_basis':'logical-measurement','review':{'status':'open'}}]},True),
    ('sensor basis is not an operating mode',{'sensor_specifications':[{'id':'type-check-only','sensed_quantity':'current','interface_basis':'islanded','review':{'status':'open'}}]},False),
    ('protection pass still requires evidence and reviewer',{'protection_specifications':[{'id':'type-check-only','device_function':'fuse','review':{'status':'pass'}}]},False),
    ('assembly role is not geographic jurisdiction',{'distribution_assembly_specifications':[{'id':'type-check-only','assembly_class':'US-CA','review':{'status':'open'}}]},False),
    ('bare assembly state remains forbidden',{'distribution_assembly_specifications':[{'id':'type-check-only','assembly_class':'panelboard','state':'islanded','review':{'status':'open'}}]},False)
])
cases.extend([
    ('neutral conductor role remains explicit',{'grounding_bonding_specifications':[{'id':'type-check-only','role':'neutral-circuit-conductor','subject_class_or_ref':'class-only','review':{'status':'open'}}]},True),
    ('grounding role cannot be operating mode',{'grounding_bonding_specifications':[{'id':'type-check-only','role':'islanded','subject_class_or_ref':'class-only','review':{'status':'open'}}]},False),
    ('unresolved transfer retains neutral decision',{'transfer_specifications':[{'id':'type-check-only','operation_type':'unresolved','transition_type':'unresolved','neutral_treatment':'unresolved','review':{'status':'open'}}]},True),
    ('transfer category is not observed motion',{'transfer_specifications':[{'id':'type-check-only','operation_type':'unresolved','transition_type':'transitioning','neutral_treatment':'unresolved','review':{'status':'open'}}]},False),
    ('neutral treatment cannot be geographic',{'transfer_specifications':[{'id':'type-check-only','operation_type':'unresolved','transition_type':'unresolved','neutral_treatment':'US-CA','review':{'status':'open'}}]},False),
    ('transfer pole count cannot be zero',{'transfer_specifications':[{'id':'type-check-only','operation_type':'unresolved','transition_type':'unresolved','neutral_treatment':'unresolved','controlled_pole_count':0,'review':{'status':'open'}}]},False),
    ('generator classification can remain unknown',{'generator_specifications':[{'id':'type-check-only','application_class':'unresolved','engine_technology':'unresolved','fuel_type':'unresolved','review':{'status':'open'}}]},True),
    ('generator class is not health observation',{'generator_specifications':[{'id':'type-check-only','application_class':'failed','engine_technology':'unresolved','fuel_type':'unresolved','review':{'status':'open'}}]},False),
    ('dependency kind is not geographic jurisdiction',{'availability_dependencies':[{'id':'type-check-only','subject_class_or_ref':'class-only','dependency_kind':'US-CA','review':{'status':'open'}}]},False),
    ('dependency pass requires reviewer and evidence',{'availability_dependencies':[{'id':'type-check-only','subject_class_or_ref':'class-only','dependency_kind':'fuel','review':{'status':'pass'}}]},False)
])
cases.extend([
    ('physical frame declares a physical unit',{'physical_coordinate_frames':[{'id':'type-check-only','frame_kind':'physical-model','unit':'mm','review':{'status':'open'}}]},True),
    ('physical frame cannot use glyph units',{'physical_coordinate_frames':[{'id':'type-check-only','frame_kind':'physical-model','unit':'drawing-unit','review':{'status':'open'}}]},False),
    ('glyph frame cannot silently use inches',{'physical_coordinate_frames':[{'id':'type-check-only','frame_kind':'symbol-preview','unit':'in','review':{'status':'open'}}]},False),
    ('north basis is not jurisdiction',{'physical_coordinate_frames':[{'id':'type-check-only','frame_kind':'symbol-preview','unit':'drawing-unit','north_basis':'US-CA','review':{'status':'open'}}]},False),
    ('NTS footprint retains unresolved geometry',{'footprint_definitions':[{'id':'type-check-only','subject_class_or_ref':'class-only','drawing_use':'NTS-symbol','geometry_basis':'NTS-preview','geometry_ref':None,'review':{'status':'open'}}]},True),
    ('dimensioned footprint needs geometry and evidence',{'footprint_definitions':[{'id':'type-check-only','subject_class_or_ref':'class-only','drawing_use':'dimensioned-outline','geometry_basis':'product-drawing','review':{'status':'open'}}]},False),
    ('NTS art cannot become dimensioned by label alone',{'footprint_definitions':[{'id':'type-check-only','subject_class_or_ref':'class-only','drawing_use':'dimensioned-outline','geometry_basis':'NTS-preview','physical_frame_ref':'type-check-only','geometry_ref':'type-check-only','dimension_source_refs':['type-check-only'],'review':{'status':'open'}}]},False),
    ('mounting method is not operating mode',{'mounting_interfaces':[{'id':'type-check-only','subject_class_or_ref':'class-only','mounting_method':'grid-parallel','review':{'status':'open'}}]},False),
    ('envelope purpose is not geographic jurisdiction',{'spatial_envelope_requirements':[{'id':'type-check-only','subject_class_or_ref':'class-only','purpose':'US-CA','review':{'status':'open'}}]},False),
    ('physical hazard is not California jurisdiction',{'environmental_exposure_records':[{'id':'type-check-only','subject_class_or_ref':'class-only','hazard':'US-CA','exposure_basis':'unresolved','review':{'status':'open'}}]},False),
    ('exposure basis is not operating mode',{'environmental_exposure_records':[{'id':'type-check-only','subject_class_or_ref':'class-only','hazard':'coastal-salt','exposure_basis':'grid-parallel','review':{'status':'open'}}]},False),
    ('envelope pass still requires evidence and reviewer',{'spatial_envelope_requirements':[{'id':'type-check-only','subject_class_or_ref':'class-only','purpose':'electrical-working','review':{'status':'pass'}}]},False)
])
cases.extend([
    ('authority role cannot be operating mode',{'authority_scopes':[{'id':'type-check-only','authority_kind':'grid-parallel','review':{'status':'open'}}]},False),
    ('rule applicability can remain undetermined',{'rule_applicability_decisions':[{'id':'type-check-only','rule_or_requirement_ref':'type-check-only','subject_class_or_ref':'class-only','decision':'undetermined','review':{'status':'open'}}]},True),
    ('review pass is not applicability decision',{'rule_applicability_decisions':[{'id':'type-check-only','rule_or_requirement_ref':'type-check-only','subject_class_or_ref':'class-only','decision':'pass','review':{'status':'open'}}]},False),
    ('not-applicable decision needs rationale and sources',{'rule_applicability_decisions':[{'id':'type-check-only','rule_or_requirement_ref':'type-check-only','subject_class_or_ref':'class-only','decision':'not-applicable','review':{'status':'open'}}]},False),
    ('draft note can retain unresolved text',{'compliance_note_instances':[{'id':'type-check-only','template_ref':'type-check-only','render_disposition':'draft','rendered_text':None,'review':{'status':'open'}}]},True),
    ('issue eligibility requires evidence and review',{'compliance_note_instances':[{'id':'type-check-only','template_ref':'type-check-only','render_disposition':'eligible-for-issue','review':{'status':'open'}}]},False),
    ('issue text cannot retain placeholder despite empty list',{'compliance_note_instances':[{'id':'type-check-only','template_ref':'type-check-only','applicability_ref':'type-check-only','render_disposition':'eligible-for-issue','rendered_text':'Resolve {actual_value}.','unresolved_placeholders':[],'rule_product_basis_refs':['type-check-only'],'review':{'status':'pass','reviewer':'contract-test-only','date':'type-check-only','source_refs':['type-check-only']}}]},False),
    ('granted authorization needs an actual decision record',{'external_authorizations':[{'id':'type-check-only','authorization_kind':'permission-to-operate','disposition':'granted','review':{'status':'open'}}]},False),
    ('authorization disposition is not operating mode',{'external_authorizations':[{'id':'type-check-only','authorization_kind':'interconnection','disposition':'islanded','review':{'status':'open'}}]},False),
    ('source enforceability is not review status',{'sources':[{'id':'type-check-only','title':'Type contract only','issuer':'type-check-only','rights':'type-check-only','document_kind':'guidance','enforceability_status':'pass'}]},False)
])
cases.extend([
    ('sheet issue stage is not geographic jurisdiction',{'sheet_definitions':[{'id':'type-check-only','issue_stage':'US-CA','review':{'status':'open'}}]},False),
    ('template professional area stays blank',{'sheet_definitions':[{'id':'type-check-only','issue_stage':'review','template_professional_area_policy':'generate-seal','review':{'status':'open'}}]},False),
    ('drawing occurrence keeps subject identity',{'drawing_occurrences':[{'id':'type-check-only','subject_ref':'class-only','sheet_ref':'type-check-only','view_kind':'plan','review':{'status':'open'}}]},True),
    ('view kind is not operating mode',{'drawing_occurrences':[{'id':'type-check-only','subject_ref':'class-only','sheet_ref':'type-check-only','view_kind':'islanded','review':{'status':'open'}}]},False),
    ('schedule kind is not jurisdiction',{'schedule_contracts':[{'id':'type-check-only','schedule_kind':'US-CA','column_keys':[],'review':{'status':'open'}}]},False),
    ('schedule contract does not instantiate data rows',{'schedule_contracts':[{'id':'type-check-only','schedule_kind':'equipment','column_keys':[],'rows':[],'review':{'status':'open'}}]},False),
    ('annotation placement cannot masquerade as physical model',{'annotation_placements':[{'id':'type-check-only','text_role':'equipment-tag','placement_space':'physical-model','review':{'status':'open'}}]},False),
    ('work scope is a label role separate from health',{'annotation_placements':[{'id':'type-check-only','text_role':'work-scope','placement_space':'sheet-layout','review':{'status':'open'}}]},True)
])
for name,document,valid in cases:check(name,document,valid)
print(f'{len(cases)} domain behavior checks passed; schema is Draft 2020-12 valid.')
