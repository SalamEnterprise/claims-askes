# Claims — Data Model, APIs & Events (v0.2)

**Purpose**: Implementation blueprint for persistence, external interfaces, adjudication outputs, and finance/event flows.

---

## 9) Data Model (logical)
**Core**: Policy, Member, Coverage, Provider, Encounter/Claim, Diagnosis/Procedure Codes, PriorAuthorization, Attachment, AdjudicationResult, Payment, EOB, COB/TPL, FraudSignals.  
**Dictionaries**: ICD‑10, ICD‑9‑CM, CPT/HCPCS (opt), LOINC, modifiers; benefit schedules; network pricing; reason codes.

---

## 10) APIs & Integrations (summary)
### FHIR (R4)
Claim, ClaimResponse, Coverage, ExplanationOfBenefit, DocumentReference; PA aligned to Da Vinci PAS/CRD/DTR (roadmap).  
### EDI / Clearinghouse
837P/I/D intake; 835 remittance; 276/277 status; companion mapping in integration layer.  
### Other
Batch CSV S3/MinIO; portal forms; email + OCR/NLP; banking export; ERP/GL posting.

---

## 11) Example Payloads (abridged)
FHIR Claim and ClaimResponse snippets demonstrating diagnosis/procedure coding and adjudication categories (eligible, copay, deductible, benefit).

---

## 25) Data Contracts (detailed)
### Core tables (DDL sketch)
`plan_benefit`, `policy_funding`, `accumulator_member_year`, `accumulator_family_year`, `claim_line_calc` with indexing strategies.  
### Import mapping
Excel→`plan_benefit` field mapping; normalization for enumerations; code lookup sheet for benefit_code.

---

## 26) API Details (extended)
**POST /claims** (channel, benefit_hint, incident_id, attachments).  
**POST /claims/{id}/adjudicate** (deterministic output incl. scheduled_allowed, accumulators before/after, coins_member, buffer_draw, payer_liability, member_liability, reasons[], funding_source, remittance_party).  
**GET /plans/{id}/benefits** (channel/facility filtering, include_groups).

---

## 27) Event Model & GL Impacts
Events: ClaimReceived, ClaimPended(reason), ClaimAdjudicated, EOBIssued, PaymentApproved(fund_source), PaymentPosted, AccumulatorsUpdated.  
GL: ASO (employer liability memo) vs insurer reserve/paid; buffer draw reduces `policy_funding.buffer_balance`.

---

## 30) EOB & Provider Remittance (spec)
EOB line breakdown: Billed, Scheduled Allowed, Coinsurance, Buffer Draw, ASO Draw, Payer Paid, Member Payable, Reason Codes; remittance mirrors payer paid + contractual write‑off.

---

**Related docs**: **Claims PRD — Core & Journey (v0.2)**, **Claims — Group Policy & Benefit Rules (v0.2)**, **Claims — Servicing & UM (Inpatient e‑GL) (v0.2)**.

