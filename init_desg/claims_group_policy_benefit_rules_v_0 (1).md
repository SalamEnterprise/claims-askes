# Claims — Group Policy & Benefit Rules (v0.3)

**Version**: v0.3 — 2025-08-14 (Asia/Jakarta)

### Changelog (v0.3)
- Added layer applicability (IL|AC|both) to PlanBenefit and member coverage layering with precedence.
- Added bed‑class upgrade policy, non‑medical routing policy, formulary policy modes.
- Expanded validations for layer consistency and bed‑upgrade capture.

---

## 21) Group Health — Parameters & Rules (from Screens + Excel)
- Policy: cashless/reimburse, ASO & balances, TPA routing/fees, age bands, contract dates, claim expiry, non‑benefit fund, buffer, fixed cost, settlement metas, clauses.  
- Plan/Benefit: member/family annual caps, sharing limit, benefit catalog, **limit basis/value/qty/max_count**, **limit groups**, **allow excess draw**, **coins %**, **facility mode**, **layer_applicability (IL|AC|both)**.

**Data contracts**: `PlanBenefit`, `PlanBenefitGroup`, `PolicyFunding`, `MemberCoverageLayer`.

---

## 22) Policy → Claims Parameter Matrix (updated)
Includes new columns: `layer_applicability`, `bed_upgrade_policy`, `non_medical_route`, `formulary_mode`.

---

## 23) Benefit Semantics & Calculation Rules
- **Basis semantics**: incident/day/year.  
- **Order of operations**: eligibility→benefit→scheduled allowed→deductible→coins→**IL layer**→**AC layer**→buffer/ASO→accumulators→COB/TPL→rounding.  
- **Formulas**: scheduled_allowed, coins_member, payer_pre_excess, excess, buffer_draw, payer_liability, member_liability, fund_source.

### 23.6 Layering algorithm (IL→AC)
1) Apply IL cap/coins and IL accumulators.  
2) Remaining billed → AC rules if benefit allows AC.  
3) EOB shows split; accumulators updated per layer.

### 23.7 Bed‑upgrade math
`upgrade_fee_per_day = used_rate − entitled_rate`; route per policy (member/coins/buffer). Maintain `BedUpgradeEvent`.

---

## 24) Decision Trees
Cashless vs Reimburse with pend reasons; IL→AC branching; bed‑upgrade approval path; non‑medical routing path.

---

## 28) Validation Rules (expanded)
- Layer consistency (`layer_applicability` matches plan/member layer).  
- Non‑medical catalog code required if routed to non‑benefit/member.  
- Bed‑upgrade requires reason & approval; deny if above max bed class per product.

---

## 29) Test Scenarios (golden)
Add: IL exhausted → AC covers remainder; bed‑upgrade (unavailability vs member request); non‑medical routed to non‑benefit; formulary violation pended.

---

## 31) Ops Dashboards
ASO/buffer, excess %, limit‑group hits, late rate, facility denials, accumulator stress, **IL vs AC utilization**.

---

**Related docs**: **Claims PRD — Core & Journey (v0.3)**, **Claims — Servicing & UM (Inpatient e‑GL) (v0.3)**, **Claims — Data Model, APIs & Events (v0.3)**.

