-- qelectrotech-bess relational model 1.0 (SQLite 3.37+)
-- Five linked domains:
--   T  truth       : standards, editions, clauses, formulas, constants, code tables (append-only)
--   V  vocabulary  : equipment classes, aliases, rating parameters, symbols, note templates
--   E  topology    : equipment, ports, connections, operating modes
--   R  ratings     : facts (value + unit + evidence status + source)
--   P  placement   : locations, placements, clearances, drawing occurrences
--   C  compliance  : requirements, calculations, evidence, reviews
-- Truth rows are constant for an edition. Ratings are project facts and may change.
PRAGMA foreign_keys = ON;

-- ============================================================ META
CREATE TABLE source (
  id          TEXT PRIMARY KEY,
  title       TEXT NOT NULL,
  issuer      TEXT,
  url         TEXT,
  revision    TEXT,
  accessed    TEXT,
  sha256      TEXT,
  kind        TEXT NOT NULL DEFAULT 'reference'
              CHECK (kind IN ('adopted-code','model-code','product-standard','test-method','utility-rule',
                              'agency-guidance','manufacturer','listing','survey','calculation','drawing-corpus',
                              'owner-requirement','tooling','reference')),
  rights      TEXT
);

-- ============================================================ T: TRUTH LAYER
CREATE TABLE standard (
  id      TEXT PRIMARY KEY,                -- NEC, CA-CEC, CA-T24-P6, NFPA-855, UL-9540 ...
  body    TEXT NOT NULL,                   -- NFPA, CEC, BSC, UL, IEEE, CPUC, PHYSICS
  title   TEXT NOT NULL,
  kind    TEXT NOT NULL CHECK (kind IN ('model-code','adopted-code','energy-code','fire-code','product-standard',
                                         'test-method','interconnection','safety-practice','physics'))
);

CREATE TABLE edition (
  id               TEXT PRIMARY KEY,       -- NEC-2023, CA-T24-P6-2022 ...
  standard_id      TEXT NOT NULL REFERENCES standard(id),
  label            TEXT NOT NULL,
  year             INTEGER,
  model_basis_id   TEXT REFERENCES edition(id),   -- CA-CEC-2025 -> NEC-2023
  jurisdiction     TEXT,                          -- US-CA, or NULL for model/product standards
  effective_from   TEXT,                          -- ISO date
  effective_to     TEXT,                          -- NULL = current
  source_id        TEXT REFERENCES source(id),
  verification     TEXT NOT NULL DEFAULT 'needs-verification'
                   CHECK (verification IN ('needs-verification','verified','definition'))
);

CREATE TABLE clause (
  id            TEXT PRIMARY KEY,          -- <edition>:<locator>
  edition_id    TEXT NOT NULL REFERENCES edition(id),
  locator       TEXT NOT NULL,             -- 705.12(B)(3)(2), Table 140.10-A, Eq 140.10-B
  title         TEXT NOT NULL,
  topic         TEXT NOT NULL,             -- interconnection, ocpd, conductor, ess-disconnect, energy-code-pv ...
  intent        TEXT NOT NULL,             -- short paraphrase, never a quotation
  applicability TEXT,                      -- building type / system scope where the clause applies
  verification  TEXT NOT NULL DEFAULT 'needs-verification'
                CHECK (verification IN ('needs-verification','verified','definition')),
  verified_by   TEXT,
  verified_on   TEXT,
  UNIQUE (edition_id, locator),
  CHECK (verification <> 'verified' OR (verified_by IS NOT NULL AND verified_on IS NOT NULL))
);

-- Renumbering / supersession across editions (e.g. NEC 2017 705.60 -> NEC 2020+ 705.28)
CREATE TABLE clause_lineage (
  from_clause_id TEXT NOT NULL REFERENCES clause(id),
  to_clause_id   TEXT NOT NULL REFERENCES clause(id),
  relation       TEXT NOT NULL CHECK (relation IN ('renumbered','revised','replaced','deleted')),
  note           TEXT,
  PRIMARY KEY (from_clause_id, to_clause_id)
);

CREATE TABLE formula (
  id            TEXT PRIMARY KEY,          -- F-<topic>-<n>
  clause_id     TEXT NOT NULL REFERENCES clause(id),
  name          TEXT NOT NULL,
  form          TEXT NOT NULL CHECK (form IN ('equation','check','lookup')),
  expression    TEXT NOT NULL,             -- python-safe; 'check' form returns bool
  output_symbol TEXT NOT NULL,
  output_unit   TEXT NOT NULL,
  note          TEXT,
  verification  TEXT NOT NULL DEFAULT 'needs-verification'
                CHECK (verification IN ('needs-verification','verified','definition')),
  verified_by   TEXT,
  verified_on   TEXT,
  CHECK (verification <> 'verified' OR (verified_by IS NOT NULL AND verified_on IS NOT NULL))
);

CREATE TABLE formula_term (
  formula_id   TEXT NOT NULL REFERENCES formula(id),
  symbol       TEXT NOT NULL,
  meaning      TEXT NOT NULL,
  unit         TEXT NOT NULL,
  role         TEXT NOT NULL CHECK (role IN ('input','constant','table','rating-fact')),
  constant_id  TEXT REFERENCES constant(id),     -- role=constant
  table_id     TEXT REFERENCES code_table(id),   -- role=table
  param_id     TEXT REFERENCES rating_param(id), -- role=rating-fact: pulled from an equipment fact
  PRIMARY KEY (formula_id, symbol),
  CHECK (role <> 'constant' OR constant_id IS NOT NULL),
  CHECK (role <> 'table' OR table_id IS NOT NULL)
);

CREATE TABLE constant (
  id           TEXT PRIMARY KEY,
  clause_id    TEXT NOT NULL REFERENCES clause(id),
  symbol       TEXT NOT NULL,
  value        REAL NOT NULL,
  unit         TEXT NOT NULL,
  meaning      TEXT NOT NULL,
  verification TEXT NOT NULL DEFAULT 'needs-verification'
               CHECK (verification IN ('needs-verification','verified','definition'))
);

CREATE TABLE code_table (
  id          TEXT PRIMARY KEY,            -- T-CA-T24-2022-140.10-A
  clause_id   TEXT NOT NULL REFERENCES clause(id),
  name        TEXT NOT NULL,
  key_schema  TEXT NOT NULL,               -- JSON list of key names, e.g. ["building_type","climate_zone"]
  value_unit  TEXT NOT NULL
);

CREATE TABLE code_table_row (
  table_id     TEXT NOT NULL REFERENCES code_table(id),
  row_key      TEXT NOT NULL,              -- canonical JSON object of key values
  value_name   TEXT NOT NULL,
  value        REAL NOT NULL,
  verification TEXT NOT NULL DEFAULT 'needs-verification'
               CHECK (verification IN ('needs-verification','verified')),
  transcribed_from TEXT REFERENCES source(id),
  PRIMARY KEY (table_id, row_key, value_name)
);

CREATE TABLE clause_applies_to (
  clause_id TEXT NOT NULL REFERENCES clause(id),
  class_id  TEXT NOT NULL REFERENCES equipment_class(id),
  PRIMARY KEY (clause_id, class_id)
);

-- Truth is append-only. Content columns cannot change; only verification may be promoted.
CREATE TRIGGER truth_clause_no_delete BEFORE DELETE ON clause
BEGIN SELECT RAISE(ABORT,'truth layer is append-only: add a new edition/clause and a clause_lineage row'); END;
CREATE TRIGGER truth_clause_no_edit BEFORE UPDATE OF edition_id, locator, title, topic, intent, applicability ON clause
BEGIN SELECT RAISE(ABORT,'truth layer content is immutable: record a new clause and lineage'); END;
CREATE TRIGGER truth_formula_no_delete BEFORE DELETE ON formula
BEGIN SELECT RAISE(ABORT,'truth layer is append-only'); END;
CREATE TRIGGER truth_formula_no_edit BEFORE UPDATE OF clause_id, form, expression, output_symbol, output_unit ON formula
BEGIN SELECT RAISE(ABORT,'formula expression is immutable: add a new formula id'); END;
CREATE TRIGGER truth_term_no_delete BEFORE DELETE ON formula_term
BEGIN SELECT RAISE(ABORT,'truth layer is append-only'); END;
CREATE TRIGGER truth_term_no_edit BEFORE UPDATE ON formula_term
BEGIN SELECT RAISE(ABORT,'formula terms are immutable'); END;
CREATE TRIGGER truth_constant_no_delete BEFORE DELETE ON constant
BEGIN SELECT RAISE(ABORT,'truth layer is append-only'); END;
CREATE TRIGGER truth_constant_no_edit BEFORE UPDATE OF clause_id, symbol, value, unit ON constant
BEGIN SELECT RAISE(ABORT,'constant values are immutable: add a new constant on the new edition'); END;
CREATE TRIGGER truth_row_no_delete BEFORE DELETE ON code_table_row
BEGIN SELECT RAISE(ABORT,'truth layer is append-only'); END;
CREATE TRIGGER truth_row_no_edit BEFORE UPDATE OF table_id, row_key, value_name, value ON code_table_row
BEGIN SELECT RAISE(ABORT,'code table values are immutable: errata go in a new edition row'); END;
CREATE TRIGGER truth_edition_no_delete BEFORE DELETE ON edition
BEGIN SELECT RAISE(ABORT,'truth layer is append-only'); END;

-- ============================================================ V: VOCABULARY / GLOSSARY / SYMBOLS
CREATE TABLE equipment_family (
  id    TEXT PRIMARY KEY,                  -- service, distribution, protection, pv, conversion, storage, control, metering, grounding, site
  label TEXT NOT NULL
);

CREATE TABLE symbol (
  id             TEXT PRIMARY KEY,         -- catalog.json symbol id, or dio-only key
  qet_elmt       TEXT,                     -- relative path in the QET collection, NULL if not yet authored
  drawio_kind    TEXT NOT NULL CHECK (drawio_kind IN ('stencil','composite','basic')),
  drawio_shape   TEXT REFERENCES drawio_shape(shape),   -- required when kind=stencil
  drawio_style   TEXT NOT NULL,            -- full style string (without label)
  w              REAL NOT NULL,
  h              REAL NOT NULL,
  note           TEXT,
  CHECK (drawio_kind <> 'stencil' OR drawio_shape IS NOT NULL)
);

CREATE TABLE drawio_shape (                -- verified stencil inventory (see assets/drawio/stencil_inventory.json)
  shape   TEXT PRIMARY KEY,
  titles  TEXT,
  w       REAL,
  h       REAL,
  commit_ref TEXT NOT NULL
);

CREATE TABLE equipment_class (
  id          TEXT PRIMARY KEY,
  term        TEXT NOT NULL,
  abbrev      TEXT,
  family_id   TEXT NOT NULL REFERENCES equipment_family(id),
  parent_id   TEXT REFERENCES equipment_class(id),
  definition  TEXT NOT NULL,
  bess_role   TEXT,                        -- why it matters around a BESS
  symbol_id   TEXT REFERENCES symbol(id),
  default_ports TEXT NOT NULL DEFAULT '[]',-- JSON [{"id":"line","domain":"ac"}, ...]
  pitfall     TEXT                         -- common drafting/design mistake seen in reference sets
);

CREATE TABLE class_alias (                 -- shorthand seen on drawings: MS, MSB, SWBD, CLP, MBP, PCS ...
  alias     TEXT NOT NULL,
  class_id  TEXT NOT NULL REFERENCES equipment_class(id),
  ambiguous INTEGER NOT NULL DEFAULT 0 CHECK (ambiguous IN (0,1)),
  PRIMARY KEY (alias, class_id)
);

CREATE TABLE rating_param (
  id            TEXT PRIMARY KEY,          -- e.g. ac_continuous_current
  label         TEXT NOT NULL,
  unit          TEXT NOT NULL,
  quantity_kind TEXT NOT NULL CHECK (quantity_kind IN ('voltage','current','power','apparent-power','energy',
                       'time','ratio','count','length','mass','temperature','frequency','short-circuit','text'))
);

CREATE TABLE class_param (                 -- which ratings a class must carry on an SLD / schedule
  class_id    TEXT NOT NULL REFERENCES equipment_class(id),
  param_id    TEXT NOT NULL REFERENCES rating_param(id),
  on_sld      INTEGER NOT NULL DEFAULT 1 CHECK (on_sld IN (0,1)),
  PRIMARY KEY (class_id, param_id)
);

CREATE TABLE note_template (
  id                 TEXT PRIMARY KEY,
  topic              TEXT NOT NULL,
  scope              TEXT NOT NULL,
  template           TEXT NOT NULL,
  starting_source_id TEXT REFERENCES source(id)
);

CREATE TABLE note_clause (                 -- which truth clauses a note template cites once a project selects an edition
  note_id   TEXT NOT NULL REFERENCES note_template(id),
  topic     TEXT NOT NULL,                 -- matched against clause.topic for the project's editions
  PRIMARY KEY (note_id, topic)
);

CREATE TABLE raceway_type (
  id   TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE location_kind (
  id       TEXT PRIMARY KEY,               -- electrical-room, outdoor-pad, roof, garage, wall-exterior, utility-yard, container
  label    TEXT NOT NULL,
  exposure TEXT NOT NULL CHECK (exposure IN ('indoor','outdoor','roof','semi-exposed','buried'))
);

CREATE TABLE layout_convention (           -- reusable drafting rules for SLD / plan views
  id     TEXT PRIMARY KEY,
  view   TEXT NOT NULL CHECK (view IN ('sld','plan','detail','schedule','any')),
  rule   TEXT NOT NULL,
  value  TEXT
);

-- ============================================================ E: PROJECT TOPOLOGY (instances; empty until a project is requested)
CREATE TABLE project (
  id                TEXT PRIMARY KEY,
  title             TEXT NOT NULL,
  jurisdiction_code TEXT,                  -- US-CA (never an operating mode)
  building_type     TEXT,
  climate_zone      TEXT,
  permit_basis_date TEXT,
  revision          TEXT
);

CREATE TABLE project_edition (             -- the code basis actually selected for the project
  project_id TEXT NOT NULL REFERENCES project(id),
  edition_id TEXT NOT NULL REFERENCES edition(id),
  PRIMARY KEY (project_id, edition_id)
);

CREATE TABLE equipment (
  id          TEXT PRIMARY KEY,
  project_id  TEXT NOT NULL REFERENCES project(id),
  tag         TEXT NOT NULL,
  class_id    TEXT NOT NULL REFERENCES equipment_class(id),
  scope       TEXT NOT NULL DEFAULT 'new' CHECK (scope IN ('existing','new','remove','relocate')),
  maker       TEXT,
  model       TEXT,
  UNIQUE (project_id, tag)
);

CREATE TABLE port (
  id           TEXT PRIMARY KEY,
  equipment_id TEXT NOT NULL REFERENCES equipment(id),
  local_id     TEXT NOT NULL,
  domain       TEXT NOT NULL CHECK (domain IN ('ac','dc','pe','control','sense')),
  UNIQUE (equipment_id, local_id)
);

CREATE TABLE connection (
  id              TEXT PRIMARY KEY,
  project_id      TEXT NOT NULL REFERENCES project(id),
  circuit_tag     TEXT,
  from_port       TEXT NOT NULL REFERENCES port(id),
  to_port         TEXT NOT NULL REFERENCES port(id),
  domain          TEXT NOT NULL CHECK (domain IN ('ac','dc','pe','control','sense')),
  conductors      TEXT,                    -- e.g. "4 #3 CU + 1 #8 CU EGC"; free text until a calc fixes it
  raceway_type_id TEXT REFERENCES raceway_type(id),
  raceway_size    TEXT,
  length_ft       REAL,
  protected_by    TEXT REFERENCES equipment(id),
  CHECK (from_port <> to_port)
);

CREATE TRIGGER connection_domain_match BEFORE INSERT ON connection
WHEN (SELECT domain FROM port WHERE id = NEW.from_port) <> NEW.domain
  OR (SELECT domain FROM port WHERE id = NEW.to_port)   <> NEW.domain
BEGIN SELECT RAISE(ABORT,'connection domain must match both port domains (never merge control and power)'); END;

CREATE TABLE operating_mode (
  id         TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id),
  mode       TEXT NOT NULL CHECK (mode IN ('grid-parallel','islanded','transition','shutdown','bypass'))
);

CREATE TABLE mode_connection (
  mode_id       TEXT NOT NULL REFERENCES operating_mode(id),
  connection_id TEXT NOT NULL REFERENCES connection(id),
  energized     INTEGER NOT NULL CHECK (energized IN (0,1)),
  PRIMARY KEY (mode_id, connection_id)
);

-- ============================================================ R: RATINGS (variable facts)
CREATE TABLE fact (
  id              TEXT PRIMARY KEY,
  equipment_id    TEXT NOT NULL REFERENCES equipment(id),
  param_id        TEXT NOT NULL REFERENCES rating_param(id),
  value_num       REAL,                    -- NULL = unknown, 0 = real zero
  value_text      TEXT,
  unit            TEXT NOT NULL,
  evidence_status TEXT NOT NULL CHECK (evidence_status IN ('unknown','assumed','provided','verified','engineer-reviewed')),
  source_id       TEXT REFERENCES source(id),
  CHECK (evidence_status = 'unknown' OR value_num IS NOT NULL OR value_text IS NOT NULL),
  CHECK (evidence_status NOT IN ('verified','engineer-reviewed') OR source_id IS NOT NULL)
);

-- ============================================================ P: PLACEMENT
CREATE TABLE location (
  id         TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES project(id),
  kind_id    TEXT NOT NULL REFERENCES location_kind(id),
  name       TEXT NOT NULL
);

CREATE TABLE placement (
  equipment_id TEXT PRIMARY KEY REFERENCES equipment(id),
  location_id  TEXT NOT NULL REFERENCES location(id),
  x REAL, y REAL, rotation_deg REAL DEFAULT 0,
  units        TEXT NOT NULL DEFAULT 'ft',
  footprint_w REAL, footprint_d REAL, mount TEXT
);

CREATE TABLE clearance (
  id           TEXT PRIMARY KEY,
  equipment_id TEXT NOT NULL REFERENCES equipment(id),
  face         TEXT,
  target       TEXT NOT NULL,              -- opening, egress, property line, other unit ...
  required_ft  REAL,
  provided_ft  REAL,
  clause_id    TEXT REFERENCES clause(id)  -- the truth row that sets required_ft
);

CREATE TABLE drawing_occurrence (
  id           TEXT PRIMARY KEY,
  equipment_id TEXT NOT NULL REFERENCES equipment(id),
  sheet        TEXT NOT NULL,
  symbol_id    TEXT NOT NULL REFERENCES symbol(id),
  x REAL, y REAL, rotation_deg REAL DEFAULT 0
);

-- ============================================================ C: COMPLIANCE EVIDENCE
CREATE TABLE calculation (
  id          TEXT PRIMARY KEY,
  project_id  TEXT NOT NULL REFERENCES project(id),
  formula_id  TEXT NOT NULL REFERENCES formula(id),
  inputs      TEXT NOT NULL,               -- JSON {symbol: value}
  result      REAL,
  passed      INTEGER CHECK (passed IN (0,1)),
  computed_on TEXT NOT NULL,
  reviewer    TEXT
);

CREATE TABLE requirement (
  id                   TEXT PRIMARY KEY,
  project_id           TEXT NOT NULL REFERENCES project(id),
  clause_id            TEXT NOT NULL REFERENCES clause(id),
  subject_equipment_id TEXT REFERENCES equipment(id),
  status               TEXT NOT NULL DEFAULT 'open'
                       CHECK (status IN ('open','needs-review','pass','fail','not-applicable')),
  reviewer             TEXT,
  reason               TEXT,
  CHECK (status <> 'pass' OR reviewer IS NOT NULL),
  CHECK (status <> 'not-applicable' OR reason IS NOT NULL)
);

CREATE TABLE evidence (
  requirement_id TEXT NOT NULL REFERENCES requirement(id),
  source_id      TEXT REFERENCES source(id),
  calculation_id TEXT REFERENCES calculation(id),
  locator        TEXT,                     -- page / sheet / section
  CHECK (source_id IS NOT NULL OR calculation_id IS NOT NULL)
);

CREATE TRIGGER requirement_pass_needs_evidence BEFORE UPDATE OF status ON requirement
WHEN NEW.status = 'pass' AND NOT EXISTS (SELECT 1 FROM evidence WHERE requirement_id = NEW.id)
BEGIN SELECT RAISE(ABORT,'pass requires at least one evidence row'); END;

CREATE TRIGGER requirement_edition_selected BEFORE INSERT ON requirement
WHEN NOT EXISTS (SELECT 1 FROM v_project_truth t WHERE t.project_id = NEW.project_id AND t.id = NEW.clause_id)
BEGIN SELECT RAISE(ABORT,'clause edition is not in the project code basis (project_edition)'); END;

-- ============================================================ VIEWS
CREATE VIEW v_glossary AS
SELECT ec.id, ec.term, ec.abbrev, f.label AS family, ec.definition, ec.bess_role, ec.pitfall,
       s.id AS symbol_id, s.qet_elmt, s.drawio_kind, s.drawio_shape,
       (SELECT group_concat(alias, ', ') FROM class_alias a WHERE a.class_id = ec.id) AS aliases
FROM equipment_class ec
JOIN equipment_family f ON f.id = ec.family_id
LEFT JOIN symbol s ON s.id = ec.symbol_id;

CREATE VIEW v_formula_catalog AS
SELECT st.id AS standard, e.id AS edition, c.locator, c.title AS clause_title,
       fo.id AS formula_id, fo.name, fo.form, fo.output_symbol || ' = ' || fo.expression AS formula,
       fo.output_unit, fo.verification,
       (SELECT group_concat(t.symbol || ' [' || t.unit || ', ' || t.role || ']: ' || t.meaning, ' | ')
          FROM formula_term t WHERE t.formula_id = fo.id) AS terms
FROM formula fo
JOIN clause c ON c.id = fo.clause_id
JOIN edition e ON e.id = c.edition_id
JOIN standard st ON st.id = e.standard_id;

CREATE VIEW v_unverified_truth AS
SELECT 'edition' AS kind, id, verification FROM edition WHERE verification = 'needs-verification'
UNION ALL SELECT 'clause', id, verification FROM clause WHERE verification = 'needs-verification'
UNION ALL SELECT 'formula', id, verification FROM formula WHERE verification = 'needs-verification'
UNION ALL SELECT 'constant', id, verification FROM constant WHERE verification = 'needs-verification'
UNION ALL SELECT 'code_table', table_id || ':' || row_key, verification FROM code_table_row WHERE verification = 'needs-verification';

CREATE VIEW v_edition_in_force AS          -- which edition governs on a given permit date: pass date via WHERE
SELECT e.*, st.title AS standard_title FROM edition e JOIN standard st ON st.id = e.standard_id;

CREATE VIEW v_project_truth AS              -- selected editions plus their model basis (CEC 2025 -> NEC 2023) plus physics
SELECT pe.project_id, c.* FROM project_edition pe JOIN clause c ON c.edition_id = pe.edition_id
UNION
SELECT pe.project_id, c.* FROM project_edition pe JOIN edition e ON e.id = pe.edition_id
  JOIN clause c ON c.edition_id = e.model_basis_id
UNION
SELECT p.id, c.* FROM project p JOIN clause c ON c.edition_id = 'PHYSICS-0';

CREATE VIEW v_open_requirements AS
SELECT r.project_id, r.id, c.locator, c.title, r.status, eq.tag
FROM requirement r JOIN clause c ON c.id = r.clause_id
LEFT JOIN equipment eq ON eq.id = r.subject_equipment_id
WHERE r.status IN ('open','needs-review','fail');

CREATE VIEW v_symbol_gaps AS               -- classes still lacking a QET element or a verified Draw.io stencil
SELECT ec.id, ec.term,
       CASE WHEN s.id IS NULL THEN 'no symbol' WHEN s.qet_elmt IS NULL THEN 'no qet element' END AS qet_gap,
       CASE WHEN s.id IS NULL THEN 'no symbol' WHEN s.drawio_kind <> 'stencil' THEN 'drawio ' || s.drawio_kind END AS drawio_gap
FROM equipment_class ec LEFT JOIN symbol s ON s.id = ec.symbol_id
WHERE s.id IS NULL OR s.qet_elmt IS NULL OR s.drawio_kind <> 'stencil';
