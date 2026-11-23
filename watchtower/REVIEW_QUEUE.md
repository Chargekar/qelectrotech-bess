# Watchtower review queue

Flags only. Nothing here changes truth_seed.json. Resolve an item by adding a new edition/clause/verification to the seed (then `watchtower.py log`), and set its status in watchtower/state.json to `resolved` or `dismissed` with a reason.

Open: 1  |  Total: 1  |  Updated: 2026-11-22

## WT-0001  discrepancy  (2026-11-22)

clause:CA-T24-P6-2022:140.10(b): 2022 Std p296: Eq 140.10-B is kWhbatt = kWPVdc x B / D^0.5 (D = rated AC to AC round-trip efficiency), kWhbatt defined as rated useable energy capacity; Eq 140.10-C kWbatt = kWPVdc x C. Seed formula BKWH = kW_PVdc*B omits the /sqrt(D) term. Also 2025 Std p365-366 (CEC-400-2025-010-F) uses kWhbatt = (CFA x B)/(1000 x C^0.5) and kWbatt = kWhbatt/4, so the shared 2022/2025 formulas do not match 2025 either

Evidence: <https://www.energy.ca.gov/sites/default/files/2022-12/CEC-400-2022-010_CMF.pdf>
Affects (1): `clause:CA-T24-P6-2022:140.10(b)`
