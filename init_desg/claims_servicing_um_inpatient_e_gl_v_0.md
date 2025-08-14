# Claims — Servicing & Utilization Management (Inpatient e‑GL) — v0.2

**Purpose**: Operationalize pre‑admission through discharge for inpatient cases, with e‑Guarantee Letter issuance, treatment‑plan approvals, and real‑time over‑utilization monitoring guided by policy coverage and clinical norms.

---

## 33) Servicing — New In‑Patient Case
### Objectives
Issue e‑GL, evaluate treatment requests, monitor case daily to avoid over‑utilization while maximizing member experience.  
### Workflow & States
Admission request (pre‑diagnose ICD‑10) → eligibility/benefit check → **e‑GL issue** (amount/bed/validity) → treatment‑plan requests (procedures, drugs, investigations) → daily case monitoring → discharge & reconciliation.  
### Data Contracts
`admission_request`, `e_gl`, `treatment_request`, `case_daily`.  
### APIs
`POST /preauth/admissions`, `POST /preauth/admissions/{id}/issue-gl`, `POST /preauth/treatment-plan`, `POST /preauth/los-extension`, `GET /case-monitor/{case_id}`.

---

## 34) Clinical Norms & Formularies ("normal" LOS/drugs/treatments)
### Norm Tables
`clinical_norms` (icd10, los_min/max, expected procedures/investigations), `formularies` (drug tier, dose caps, icd10 link, PA flags), `procedure_norms` (allow lists, MECE rules, max units, PA flags).  
### UM Business Rules
LOS extension (BR‑UM‑LOS‑001), drug formulary/dose (BR‑UM‑DRUG‑001), procedure allow/mutual exclusivity (BR‑UM‑PROC‑001), duplicate diagnostics (BR‑UM‑INV‑001), inpatient bundles (BR‑UM‑BUNDLE‑001), bed‑class rules (BR‑UM‑BED‑001), antibiotic guardrails (BR‑UM‑ABX‑001).  
### Decision Support
Show remaining caps and guideline snippets; require reviewer identity + override reason.

---

## 35) Over‑Utilization Monitoring
### Signals & Alerts
LOS variance, high‑cost meds, duplicate diagnostics, polypharmacy, procedure intensity.  
### Engine & Actions
Kafka → UM service → `UM.AlertRaised`; actions include auto‑pend, MD addendum, second opinion, revise e‑GL.

---

## 36) Policy Coverage Checks during Servicing
Room & board per‑day caps; surgical/implant per‑incident; diagnostic counts; comfort items routing to non‑benefit fund; ASO/buffer real‑time checks.

---

## 37) KPIs & SLAs (Servicing/UM)
Time‑to‑GL (P95 ≤ 5 min), auto‑approval ≥ 70%, LOS within norm ≥ 85%, non‑formulary ≤ 10% of inpatient pharmacy, UM response ≤ 2h, weekly provider outlier refresh.

---

## 38) Audit & Compliance (Servicing)
Versioned e‑GLs, treatment decisions, LOS extensions with clinical justification; EOB/remittance reference authorization IDs; regulator export packs.

---

**Related docs**: **Claims — Group Policy & Benefit Rules (v0.2)**, **Claims — Data Model, APIs & Events (v0.2)**.

