# Claims — Group Policy & Benefit Rules (v0.2)

**Scope**: Translate group policy setup (as per SALAM screens and `import-policy-benefit.xlsx`) into deterministic claims behavior.

---

## 21) Group Health — Parameters & Rules (from Screens + Excel)
- Policy‑level parameters: Cashless vs Reimburse; ASO; TPA routing & fees; age limits; contract dates; claim expiry; non‑benefit fund & buffer; initial/alert ASO; fixed cost per member; settlement metas (discount, management, profit‑share, loadings); distribution/clauses.  
- Plan/Benefit structure: annual caps (member/family); sharing limit; benefit catalog (benefit_code/name/type); limit dimensions (basis/value/qty/max_count); multiple condition (group caps); allow excess draw; coins % per benefit; facility mode.

**Data Contracts**: `PlanBenefit`, `PlanBenefitGroup`, `PolicyFunding` (balances for non‑benefit, buffer, ASO).

---

## 22) Policy → Claims Parameter Matrix
Tabular mapping from UI/Excel fields to entities, validations, lifecycle moments, and claims effects (channel gating, ASO funding, buffer/excess, accumulators, etc.).

---

## 23) Benefit Semantics & Calculation Rules
### 23.1 Basis semantics
Per Kejadian (incident), Per Hari (per day), Per Tahun (per year) with incident resolution rules.  
### 23.2 Order of operations
Eligibility/channel → benefit mapping → scheduled allowed → deductible → coins → buffer/ASO → accumulators → COB/TPL → rounding.  
### 23.3 Formulae
`schedule_allowed`, `coins_member`, `payer_pre_excess`, `excess`, `buffer_draw`, `payer_liability`, `member_liability`; `fund_source` for ASO.  
### 23.4 Limit groups
Shared caps (e.g., room & board + nursing).  
### 23.5 Facility gating
Cashless vs Reimburse logic and denials.

---

## 24) Decision Trees
**Cashless** and **Reimburse** flows with common pend reasons (NO_PA, MISSING_DOCS, INSUFFICIENT_ASO_FUNDS, CHANNEL_NOT_ALLOWED, LIMIT_EXCEEDED).

---

## 28) Validation Rules (highlights)
Age/relationship coherence; facility vs channel; active benefit; monetary/quantity bounds; group‑cap integrity; late claim; ASO funds check.

---

## 29) Test Scenarios (golden)
1) Clean cashless room & board.  
2) Per‑incident surgery bundle hitting shared cap.  
3) Outpatient reimburse with coins%.  
4) Excess draw from buffer until depleted.  
5) ASO insufficient funds → pend → approve after top‑up.  
6) Family cap exhausted.  
7) Channel not allowed.  
8) Late submission.  
9) COB secondary.  
10) Duplicate incident detection.

---

## 31) Ops Dashboards (group focus)
ASO balance; buffer utilization; excess %; limit‑group hits; late rate; facility denials; accumulator stress.

---

## 32) Edge Cases & Exceptions
Mid‑term plan change; newborn grace; OON reference pricing; policy‑year spans; multiple incidents same DOS.

---

**See also**: **Claims — Data Model, APIs & Events (v0.2)** for tables/APIs; **Claims — Servicing & UM (Inpatient e‑GL) (v0.2)** for admission/UM.

