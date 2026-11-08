# Rule applicability, notes and authorization evidence

Use `assets/compliance/applicability-contracts.json` and the AuthorityScope, RuleApplicability, ComplianceNoteInstance and ExternalAuthorizationRecord definitions. Source records can separately identify document kind and enforceability status. These contracts contain no project findings, approvals or numerical compliance results.

## Select authority and rule scope

Resolve geographic jurisdiction and each authority's territory/topic before selecting provisions: building, fire, utility, air, environmental/land use, accessibility, professional practice and owner requirements can have different scopes. Record the actual permit/activity basis date, adoption, amendments, errata, applicability facts and exception/legal-effect evidence. The latest model-code edition, a historical public plan, an equipment test report or an agency-hosted guidebook does not establish the project's adopted rule.

Keep applicability (`applicable`, `not-applicable`, `undetermined`) separate from review status, component condition and operating mode. A resolved applicability decision needs rationale and sources; unresolved inputs remain explicit. A source's enforceability status applies to its identified provision, scope and time. Recheck later amendments, stays and supersession; do not treat a book's edition as proof that every provision has identical legal effect.

`US-BASE` remains unadopted reference vocabulary. `US-CA`, `US-NY` and `US-TX` are research starting profiles, with binding project defaults disabled. There is no automatic California/Title 24 fallback and no complete 50-state code engine. New states/localities need their own verified sources and project basis.

- California: use the adopted Title 24 parts independently, with actual AHJs and agency scope. The [January 2026 ESS permitting guidebook](https://efiling.energy.ca.gov/GetDocument.aspx?DocumentContentId=105452&tn=268282) is a consultant guidance report, with an express disclaimer; its cover, disclaimer, scope and selected code-basis passages were reviewed. It is not adopted technical code or an approval of a particular design.
- New York: the [DOS adoption page](https://dos.ny.gov/notice-adoption) identifies the 2025 code transition and later legal-effect notices. [DOS scope guidance](https://dos.ny.gov/node/37691) distinguishes NYC/local paths. The [NYC energy transition bulletin](https://www.nyc.gov/assets/buildings/bldgs_bulletins/bb_2026-005.pdf) is a dated starting reference; resolve current DOB guidance and actual application basis before selecting a path.
- Texas: [TDLR's electrical guide](https://www.tdlr.texas.gov/electricians/compliance-guide.htm) identifies its 2023 NEC adoption and local inspection context. That research candidate does not select every project's fire, energy, utility or permit basis. Those domains remain unresolved in the profile.

## Instantiate notes only when a project is requested

The note library has parameterized drafting text and research starting citations. Its `undetermined` applicability, null edition/locator and open review are intentional. Resolve exact rule/product sources and project facts; fill placeholders from evidence rather than plausible defaults. Keep electrical working space and manufacturer servicing space separate, and retain separate interrupting/SCCR/withstand/fault-current references.

Create a ComplianceNoteInstance linked to the template and actual applicability decision. Use `withhold` or a clearly identified review copy while inputs remain unresolved. `eligible-for-issue` requires resolved text, an empty unresolved-placeholder list, rule/product basis references and a passed evidence review. Resolve and inspect every referenced target; schema-valid strings do not establish real evidence, applicability or professional approval. Issue decisions remain with the responsible reviewer and actual process.

Templates include fire/exposure, access/roof, controls/shutdown, fuel/emissions, grounding/transfer, commissioning, coastal jurisdiction, flood/elevation and authorization topics. Their sources are starting points to replace or refine for the actual state, AHJ and installation. No template supplies a universal clearance, battery size, operating-hour allowance, calculation factor or exemption.

## Keep approval milestones separate

Professional review, building/fire/air/land-use permits, interconnection authorization and permission to energize/operate are separate records. A granted/conditional ExternalAuthorizationRecord requires an identified authority, decision artifact and date; verify scope, conditions and expiry. A design review pass, native QET load or polished sheet is not an external authorization. Never manufacture a seal, signature or approval to close an open field.
