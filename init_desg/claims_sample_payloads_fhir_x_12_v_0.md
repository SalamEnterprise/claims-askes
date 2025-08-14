# Claims — Sample Payloads (FHIR & X12) (v0.3)

**Version**: v0.3 — 2025-08-14 (Asia/Jakarta)

### Changelog (v0.3)

- Added pharmacy item example with formulary info and coverage layer attribution.
- Added supervising/performing practitioner references.
- Expanded 837I example with attending (NM1*71) / operating (NM1*72) and a pharmacy revenue code line.

---

## A) FHIR R4 — Pre‑Authorization (e‑GL analogue)

**Request**

```json
{
  "resourceType": "Claim",
  "id": "preauth-0002",
  "status": "active",
  "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/claim-type","code": "institutional"}]},
  "use": "preauthorization",
  "patient": {"reference": "Patient/123"},
  "created": "2025-08-14",
  "insurer": {"reference": "Organization/payer"},
  "provider": {"reference": "Organization/hospital-77"},
  "careTeam": [
    {"sequence": 1, "provider": {"reference": "Practitioner/supervising-md"}, "role": {"coding":[{"code":"supervising"}]} }
  ],
  "diagnosis": [{"sequence": 1, "diagnosisCodeableConcept": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10", "code": "O82"}]}}],
  "item": [{
    "sequence": 1,
    "productOrService": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-9-cm","code": "74.1","display": "Cesarean section"}]},
    "unitPrice": {"value": 15000000, "currency": "IDR"},
    "net": {"value": 15000000, "currency": "IDR"}
  }]
}
```

---

## B) FHIR R4 — Claim with Pharmacy & Coverage Layer

```json
{
  "resourceType": "Claim",
  "id": "claim-002",
  "status": "active",
  "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/claim-type","code": "institutional"}]},
  "use": "claim",
  "patient": {"reference": "Patient/123"},
  "created": "2025-08-14",
  "insurer": {"reference": "Organization/payer"},
  "provider": {"reference": "Organization/hospital-77"},
  "careTeam": [
    {"sequence": 1, "provider": {"reference": "Practitioner/supervising-md"}, "role": {"coding":[{"code":"supervising"}]} },
    {"sequence": 2, "provider": {"reference": "Practitioner/performing-md"}, "role": {"coding":[{"code":"performing"}]}}
  ],
  "diagnosis": [{"sequence": 1, "diagnosisCodeableConcept": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-10", "code": "J18.9"}]}}],
  "item": [
    {
      "sequence": 1,
      "category": {"coding": [{"code": "pharmacy"}]},
      "productOrService": {"coding": [{"system": "http://www.whocc.no/atc","code": "J01CA04","display":"Amoxicillin"}]},
      "quantity": {"value": 20, "unit": "capsule"},
      "unitPrice": {"value": 10000, "currency": "IDR"},
      "net": {"value": 200000, "currency": "IDR"},
      "extension": [{"url":"coverage-layer","valueString":"IL"},{"url":"formulary-tier","valueString":"formulary"}]
    },
    {
      "sequence": 2,
      "productOrService": {"coding": [{"system": "http://hl7.org/fhir/sid/icd-9-cm","code": "96.04","display":"Transfusion"}]},
      "unitPrice": {"value": 500000, "currency": "IDR"},
      "net": {"value": 500000, "currency": "IDR"},
      "extension": [{"url":"coverage-layer","valueString":"AC"}]
    }
  ]
}
```

---

## C) X12 837I — With Providers & Pharmacy Rev Code

```
ISA*00*          *00*          *ZZ*SENDERID      *ZZ*RECEIVERID    *250814*1200*^*00501*000000906*0*T*:~
GS*HC*SENDERID*RECEIVERID*20250814*1200*906*X*005010X223A2~
ST*837*0002*005010X223A2~
BHT*0019*00*0124*20250814*1200*CH~
NM1*41*2*SENDER CLINIC*****46*123456789~
PER*IC*CLAIMS CONTACT*TE*0215551234~
NM1*40*2*PAYER*****46*999888777~
HL*1**20*1~
NM1*85*2*HOSPITAL 77*****XX*1234567893~
N3*Jl. Contoh 1~
N4*Bandung*JB*40111~
NM1*71*1*DOE*JOHN****XX*1999999999~
NM1*72*1*SMITH*ANNA****XX*1888888888~
HL*2*1*22*0~
SBR*P*18*******CI~
NM1*IL*1*DOE*JANE****MI*MEM12345~
DMG*D8*19860101*F~
CLM*00001235*17000000***11:A:1*Y*A*Y*Y~
DTP*434*RD8*20250810-20250814~
HI*ABK:J189~
LX*1~
SV2*0301*HC:741*15000000*UN*1~
LX*2~
SV2*0250*HC:250*200000*UN*1~
SE*28*0002~
GE*1*906~
IEA*1*000000906~
```

---

## D) X12 835 — Remittance (unchanged pattern)

Minimal example same as v0.2; add CAS/PLB segments to reflect IL vs AC portions as separate adjustments if required by partner.

---

**Related docs**: **Claims PRD — Core & Journey (v0.3)**, **Claims — Group Policy & Benefit Rules (v0.3)**, **Claims — Data Model, APIs & Events (v0.3)**.

