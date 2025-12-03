# Claims PRD — Core & Journey (v0.2)

**Product**: Health Insurance Platform (Commercial & Corporate)  
**Module**: Medical Claims  
**Version**: v0.2 (split set)  
**Date**: 2025-08-13  
**Owner**: Claims Product + Engineering

---

## 1) Executive Summary
  - Standardizes end‑to‑end claims (intake → adjudication → payment → EOB → appeals → post‑pay). 
  - Multi‑channel intake (portal, EDI/X12, FHIR, CSV, email+OCR), codified rules (eligibility, benefits, cost‑sharing, pre‑auth, COB/TPL), robust audit/analytics. 
  - Indonesia‑aware (ICD‑10 + ICD‑9‑CM for INA‑CBG) with global interoperability (FHIR Claim/ClaimResponse/Coverage/EOB; X12 837/835).

---

## 2) Scope
**In scope**: Individual & group medical claims; prior‑auth; COB/TPL; pricing (contract/UCR/relative); SIU controls; observability; privacy/security/retention.  
**Out of scope (v0.1/0.2)**: Provider credentialing; full INA‑CBG UI; PBM switch.

---

## 3) Definitions & Abbreviations (selected)
Adjudication, COB, EOB, INA‑CBG, PA, Subrogation/TPL, etc. (unchanged from v0.1)

---

## 4) Personas & Actors
Member, Provider, Claims Ops, Medical Reviewers, Pricing/Benefits Analysts, Finance/AP, SIU, Compliance/Audit, Integrators.

---

## 5) End‑to‑End Journey & System States
### 5.1 High‑level flow
**Intake** → **Pre‑check** → **Adjudication** → **Payment/EOB** → **Appeals** → **Post‑pay Integrity**.  
### 5.2 State Model (simplified)
`Draft → Received → Pre‑checked → (Pended|Routed) → Adjudication → (AutoPay|ManualReview) → (Denied|Approved) → (EOB‑Issued) → (Paid|Offset) → Closed → (Appeal?)`. Sub‑states for Attachments/COB/TPL/SIU.

---

## 6) Business Rules — Overview
Rule schema, governance, and the primary families: Eligibility, Cost‑Sharing, PA/Medical Necessity, Coding/Docs, Pricing/Network, COB/TPL, Anti‑Fraud.  
> Detailed group‑policy mappings & benefit rules are in **“Claims — Group Policy & Benefit Rules (v0.2)”**.

---

## 7) Functional Requirements
7.1 Intake & Validation; 7.2 Adjudication Engine; 7.3 Pricing; 7.4 COB/TPL; 7.5 Payment & Remittance; 7.6 Appeals; 7.7 Fraud & Integrity; 7.8 Observability & Ops.  
(Contents mirror v0.1 with no changes.)

---

## 8) Non‑Functional Requirements
Security/Privacy (UU PDP/ISO 27001 alignment), Compliance, Availability (99.9%), Performance (≤5s clean adjudication), Scalability, Auditability.

---

## 12) UI/UX (Ops console & portals)
Ops, Provider, and Member experiences incl. status/276‑277‑like tracker and document flows.

---

## 13) SLAs & KPIs
Clean claim rate ≥85%; pend ≤15%; average adjudication ≤5s clean; payment TAT ≤5 business days; fraud savings tracked.

---

## 14) Compliance, Privacy & Security
Role segregation; consent logs; encryption; retention; secure SDLC; third‑party risk.

---

## 15) Architecture (reference)
Intake gateway; Core services (Rules, Pricing, Coverage/Accumulator, Clinical policy, COB/TPL); Data (PostgreSQL, S3/MinIO, Redis, ClickHouse, lakehouse); Messaging (Kafka); Observability (Prometheus/Grafana/Otel); Interoperability (FHIR/X12).

---

## 16) Test Strategy
Unit, contract (FHIR/X12), scenario (golden sets), performance, UAT, compliance.

---

## 17) Open Questions / Next Steps
OJK cost‑sharing flags; coding sets per LoB; OCR vendor; PAS/CRD/DTR roadmap.

---

## 18) Appendix A — Illustrative Rule Table (extract)
(Contains BR‑ELIG‑001, BR‑COST‑002, BR‑PA‑001, BR‑CODE‑003, BR‑FRAUD‑001.)

---

## 19) Appendix B — Reason Codes (sample)
MISSING_DOCS, NO_PA, EXCLUSION_POLICY, WAITING_PERIOD, LIMIT_EXCEEDED, COB_PRIMARY_PENDING, SUBROGATION_REVIEW, UPDATING_ACCUMULATORS, DUPLICATE_CLAIM, CODE_MISMATCH.

---

## 20) Appendix C — Data Retention (proposal)
Claims/EOB/adjudication ≥7y; PHI attachments ≥7y; SIU cases ≥7y (per legal guidance).

---

**Related docs in this set**
- **Claims — Group Policy & Benefit Rules (v0.2)**
- **Claims — Servicing & UM (Inpatient e‑GL) (v0.2)**
- **Claims — Data Model, APIs & Events (v0.2)**

