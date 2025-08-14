# Claims PRD — Core & Journey (v0.3)

**Version**: v0.3 — 2025-08-14 (Asia/Jakarta)

### Changelog (v0.3)
- Added rule families & flows for: medications, supervising/ordering/performing provider attribution, non‑medical routing, bed‑class upgrade policy, and dual coverage layers (Inner‑Limit + As‑Charged).
- Linked servicing KPIs (time‑to‑e‑GL, LOS‑within‑norm) and over‑utilization monitoring to core PRD.
- Cross‑references to Data Model/APIs v0.3 and Group Policy v0.3.

---

## 1) Executive Summary
This module automates intake→adjudication→payment/EOB→appeals→post‑pay controls for group & individual products. It now covers inpatient servicing (e‑GL), medication/pharmacy granularity, bed‑upgrade handling, and layered coverage (IL then AC) for accurate benefits application.

---

## 2) Scope (updated)
- **In scope**: cashless & reimburse, PA, COB/TPL, pricing, SIU, utilization mgmt, IL+AC layering, bed‑upgrade, non‑medical routing, pharmacy capture, provider attribution.
- **Out of scope**: provider credentialing, full INA‑CBG UI, PBM switch (future).

---

## 3) Definitions (additions)
- **IL/AC**: Inner‑Limit vs As‑Charged coverage layers.  
- **e‑GL**: Electronic guarantee letter for cashless inpatient.  
- **Non‑Benefit Fund**: Employer pool for non‑medical or extra‑contractual items.

---

## 4) Personas & Actors
Member, Provider, Claims Ops, Medical Reviewer, Pricing/Benefits, Finance/AP, SIU, Compliance, Integrations (unchanged).

---

## 5) E2E Journey & States
`Draft → Received → Pre‑checked → (Pended|Routed) → Adjudication → (AutoPay|Manual) → (Denied|Approved) → EOB → (Paid|Offset) → Closed → (Appeal?)`.  
**Servicing hook** for inpatient: Pre‑diagnose → e‑GL → treatment‑plan approvals → daily monitoring → discharge reconciliation.

---

## 6) Business Rule Families (expanded)
- **Eligibility/Coverage** (age bands, contract window, late claim)  
- **Cost‑Sharing** (deductibles, coins, OOP)  
- **PA/Medical Necessity** (LOS extension, formulary/DDD, procedure allow lists)  
- **Coding/Docs** (ICD‑10, ICD‑9‑CM, attachments)  
- **Pricing/Network** (contract/UCR, bundling)  
- **COB/TPL/Subrogation**  
- **Anti‑Fraud/SIU**  
- **Facility/Channel** (cashless vs reimburse gating)  
- **Bed‑Class Upgrade** (upgrade fee math & policy)  
- **Pharmacy** (formulary tiering, PA, DDD)  
- **Dual Layers (IL→AC)** with separate accumulators and precedence.

---

## 7) Functional Requirements (key updates)
- **Intake/Validation**: accept supervising/ordering/performing providers, medications, non‑medical items, coverage layer hint.  
- **Adjudication Engine**: apply IL first then AC; compute bed‑upgrade fees; route non‑medical to Non‑Benefit Fund; produce per‑drug EOB splits.  
- **Servicing**: e‑GL issuance/extension; treatment‑plan evaluation; daily case monitor & UM alerts.

---

## 8) Non‑Functional Requirements
Security/Privacy (UU PDP/ISO 27001), 99.9% availability, ≤5s clean adjudication; auditability for e‑GL & UM overrides (unchanged, reinforced).

---

## 12) UI/UX (Ops, Provider, Member)
- **Provider**: admit request (ICD‑10), e‑GL dashboard, treatment‑plan submit, bed‑upgrade request, pharmacy capture.  
- **Ops**: work queues by pend reason (NO_PA, INSUFFICIENT_ASO_FUNDS, CHANNEL_NOT_ALLOWED, LIMIT_EXCEEDED), IL/AC accumulator views.  
- **Member**: reimbursement upload; EOB with pharmacy/non‑medical/bed‑upgrade and IL vs AC splits.

---

## 13) SLAs & KPIs (linked)
- Clean claim ≥85%; pend ≤15%; adjudication ≤5s.  
- **Servicing**: time‑to‑e‑GL P95 ≤5 min; LOS‑within‑norm ≥85%; non‑formulary ≤10% IP pharmacy; UM response ≤2h.

---

## 14) Architecture (reference)
Intake & EDI/FHIR gateway; Rules/Pricing/Coverage/Clinical/COB services; Data: PostgreSQL + MinIO + Redis + ClickHouse; Kafka events; Observability via Prometheus/Grafana/Otel.

---

## 15) Test Strategy (golden scenarios)
Excess/ASO, family caps, channel gating, late claim, COB secondary, duplicate incidents, bed‑upgrade fee, pharmacy non‑formulary, IL‑then‑AC layering.

---

**Related docs**: **Claims — Group Policy & Benefit Rules (v0.3)**, **Claims — Servicing & UM (Inpatient e‑GL) (v0.3)**, **Claims — Data Model, APIs & Events (v0.3)**.

