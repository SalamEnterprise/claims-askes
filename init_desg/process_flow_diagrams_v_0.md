# Process Flow Diagrams — Complete System Workflows (v0.1)

**Purpose**: Detailed process flows for all critical system operations
**Date**: 2025-08-14
**Owner**: Business Process, Operations, Technology
**Status**: Process Architecture

---

## 1. MEMBER JOURNEY FLOWS

### 1.1 End-to-End Claim Journey (Network Provider)
```mermaid
graph TB
    Start([Member Needs Care]) --> A{Emergency?}
    
    A -->|Yes| B[Go to Nearest Provider]
    A -->|No| C[Search Network Provider]
    
    C --> D[Schedule Appointment]
    D --> E[Visit Provider]
    
    B --> E
    E --> F[Provider Verification]
    
    F --> G{Member Eligible?}
    G -->|No| H[Self-Pay/Denied]
    G -->|Yes| I[Service Authorization]
    
    I --> J{Auto-Approved?}
    J -->|Yes| K[Receive Service]
    J -->|No| L[Clinical Review]
    
    L --> M{Approved?}
    M -->|No| H
    M -->|Yes| K
    
    K --> N[Provider Bills Insurance]
    N --> O[Claim Adjudication]
    
    O --> P{Clean Claim?}
    P -->|No| Q[Pend for Review]
    P -->|Yes| R[Calculate Payment]
    
    Q --> S[Resolve Issues]
    S --> R
    
    R --> T[Process Payment]
    T --> U[Send EOB]
    U --> V[Member Pays Copay]
    V --> End([Care Complete])
```

### 1.2 Out-of-Network Reimbursement Flow
```mermaid
graph TB
    Start([Member at Non-Network]) --> A[Pay Provider Direct]
    
    A --> B[Collect Documents]
    B --> B1[Receipt]
    B --> B2[Medical Report] 
    B --> B3[Prescription]
    
    B1 --> C{Submission Channel?}
    B2 --> C
    B3 --> C
    
    C -->|Mobile| D[Photo Capture]
    C -->|Web| E[Upload Files]
    C -->|WhatsApp| F[Chat Bot]
    C -->|Branch| G[Physical Submit]
    
    D --> H[OCR Processing]
    E --> H
    F --> H
    G --> I[Scan Documents]
    I --> H
    
    H --> J[Data Extraction]
    J --> K{Quality Check}
    
    K -->|Poor| L[Request Resubmit]
    K -->|Good| M[Validation]
    
    L --> C
    
    M --> N{Valid?}
    N -->|No| O[Request Info]
    N -->|Yes| P[Fraud Check]
    
    O --> C
    
    P --> Q{Risk Level?}
    Q -->|High| R[Investigation]
    Q -->|Medium| S[Manual Review]
    Q -->|Low| T[Auto Process]
    
    R --> U{Fraudulent?}
    U -->|Yes| V[Deny & Report]
    U -->|No| S
    
    S --> W{Approve?}
    W -->|No| V
    W -->|Yes| X[Calculate Reimbursement]
    
    T --> X
    
    X --> Y[Apply Benefits]
    Y --> Z[Payment Process]
    
    Z --> AA{Payment Method?}
    AA -->|Bank| AB[Transfer]
    AA -->|Wallet| AC[Digital Pay]
    AA -->|Check| AD[Mail Check]
    
    AB --> AE[Send Notification]
    AC --> AE
    AD --> AE
    
    AE --> AF[Generate EOB]
    AF --> End([Complete])
    
    V --> End
```

### 1.3 Pre-Authorization Journey
```mermaid
graph TB
    Start([Provider Identifies Need]) --> A[Check Auth Requirements]
    
    A --> B{Required?}
    B -->|No| C[Proceed with Service]
    B -->|Yes| D[Gather Clinical Info]
    
    D --> E[Submit Auth Request]
    E --> F[System Validation]
    
    F --> G{Complete?}
    G -->|No| H[Request Additional]
    G -->|Yes| I[Clinical Criteria Check]
    
    H --> D
    
    I --> J{Auto-Approvable?}
    J -->|Yes| K[Auto Approve]
    J -->|No| L{Urgent?}
    
    L -->|Yes| M[Expedited Review]
    L -->|No| N[Standard Review]
    
    M --> O[Medical Director]
    N --> P[Clinical Reviewer]
    
    O --> Q{Decision}
    P --> Q
    
    Q -->|Approve| R[Issue Auth]
    Q -->|Partial| S[Approve Limited]
    Q -->|Deny| T[Deny with Reason]
    
    K --> R
    S --> R
    
    R --> U[Notify Provider]
    T --> U
    
    U --> V{Provider Response}
    V -->|Accept| W[Schedule Service]
    V -->|Appeal| X[Appeal Process]
    
    W --> C
    X --> Y[Peer-to-Peer]
    
    Y --> Z{Outcome}
    Z -->|Overturn| R
    Z -->|Uphold| AA[Final Denial]
    
    AA --> End([Process End])
    C --> End
```

---

## 2. PROVIDER WORKFLOWS

### 2.1 Provider Onboarding & Credentialing
```mermaid
graph TB
    Start([Provider Application]) --> A[Initial Submission]
    
    A --> B[Document Collection]
    B --> B1[License]
    B --> B2[Insurance]
    B --> B3[Credentials]
    B --> B4[References]
    
    B1 --> C[Completeness Check]
    B2 --> C
    B3 --> C
    B4 --> C
    
    C --> D{Complete?}
    D -->|No| E[Request Missing]
    D -->|Yes| F[Primary Verification]
    
    E --> B
    
    F --> G[License Verification]
    F --> H[Education Verification]
    F --> I[Malpractice Check]
    F --> J[Sanction Check]
    
    G --> K{All Valid?}
    H --> K
    I --> K
    J --> K
    
    K -->|No| L[Rejection]
    K -->|Yes| M[Background Check]
    
    M --> N{Clean?}
    N -->|No| L
    N -->|Yes| O[Site Inspection]
    
    O --> P{Pass?}
    P -->|No| Q[Remediation]
    P -->|Yes| R[Credentialing Committee]
    
    Q --> O
    
    R --> S{Approved?}
    S -->|No| L
    S -->|Yes| T[Contract Negotiation]
    
    T --> U[Rate Agreement]
    U --> V[Contract Execution]
    
    V --> W[System Setup]
    W --> W1[Portal Access]
    W --> W2[API Keys]
    W --> W3[Training]
    
    W1 --> X[Go Live]
    W2 --> X
    W3 --> X
    
    X --> Y[Monitor Performance]
    Y --> End([Active Provider])
    
    L --> End([Rejected])
```

### 2.2 Provider Claim Submission
```mermaid
graph TB
    Start([Service Completed]) --> A[Compile Claim]
    
    A --> B[Add Service Lines]
    B --> C[Attach Documents]
    C --> D[Add Diagnosis]
    D --> E[Add Procedures]
    
    E --> F{Submission Method?}
    
    F -->|Portal| G[Web Form]
    F -->|API| H[System Integration]
    F -->|EDI| I[X12 837]
    
    G --> J[Validation]
    H --> J
    I --> J
    
    J --> K{Valid?}
    K -->|No| L[Error Response]
    K -->|Yes| M[Generate Claim ID]
    
    L --> N[Fix Errors]
    N --> F
    
    M --> O[Initial Screening]
    O --> P{Duplicate?}
    
    P -->|Yes| Q[Reject Duplicate]
    P -->|No| R[Eligibility Check]
    
    R --> S{Eligible?}
    S -->|No| T[Deny Claim]
    S -->|Yes| U[Auth Check]
    
    U --> V{Auth Valid?}
    V -->|No| W[Pend for Auth]
    V -->|Yes| X[Adjudication]
    
    W --> Y[Obtain Auth]
    Y --> X
    
    X --> Z[Calculate Payment]
    Z --> AA[Apply Contract]
    
    AA --> AB{Clean Claim?}
    AB -->|No| AC[Manual Review]
    AB -->|Yes| AD[Auto Approve]
    
    AC --> AE{Resolved?}
    AE -->|No| T
    AE -->|Yes| AD
    
    AD --> AF[Payment Process]
    AF --> AG[Remittance]
    
    AG --> End([Payment Complete])
    T --> End
    Q --> End
```

---

## 3. OPERATIONAL WORKFLOWS

### 3.1 Real-Time Authorization Engine
```mermaid
graph TB
    Start([Auth Request]) --> A[Request Received]
    
    A --> B[< 10ms: Parse Request]
    B --> C[< 20ms: Load Member]
    C --> D[< 30ms: Load Benefits]
    
    D --> E{< 50ms: Cache Hit?}
    E -->|Yes| F[< 60ms: Use Cache]
    E -->|No| G[< 100ms: Load Rules]
    
    F --> H[< 150ms: Apply Rules]
    G --> H
    
    H --> I{< 200ms: Auto-Decision?}
    
    I -->|Yes| J[< 250ms: Auto Approve]
    I -->|No| K{< 300ms: ML Score}
    
    K --> L{< 350ms: Confidence?}
    L -->|High > 95%| M[< 400ms: ML Approve]
    L -->|Medium| N[< 450ms: Risk Check]
    L -->|Low < 60%| O[Route to Human]
    
    N --> P{< 500ms: Risk Level?}
    P -->|Low| M
    P -->|High| O
    
    J --> Q[< 300ms: Generate Auth]
    M --> Q
    
    Q --> R[< 350ms: Update Systems]
    R --> S[< 400ms: Log Decision]
    S --> T[< 450ms: Send Response]
    
    T --> End([< 500ms Total])
    
    O --> U[Queue for Review]
    U --> V[Human Decision]
    V --> W[Update Auth]
    W --> End2([Async Complete])
```

### 3.2 Fraud Detection Pipeline
```mermaid
graph TB
    Start([Claim/Auth Input]) --> A[Stream Processing]
    
    A --> B[Feature Extraction]
    B --> B1[Member Features]
    B --> B2[Provider Features]
    B --> B3[Service Features]
    B --> B4[Historical Features]
    
    B1 --> C[Real-Time Scoring]
    B2 --> C
    B3 --> C
    B4 --> C
    
    C --> D[Rule Engine]
    C --> E[ML Models]
    C --> F[Pattern Match]
    
    D --> G[Rule Scores]
    E --> H[ML Scores]
    F --> I[Pattern Scores]
    
    G --> J[Score Aggregation]
    H --> J
    I --> J
    
    J --> K{Risk Level}
    
    K -->|Low < 0.3| L[Pass Through]
    K -->|Medium 0.3-0.7| M[Flag for Review]
    K -->|High > 0.7| N[Block & Investigate]
    
    L --> O[Continue Process]
    
    M --> P[Review Queue]
    P --> Q[Analyst Review]
    
    N --> R[Investigation Queue]
    R --> S[SIU Investigation]
    
    Q --> T{Fraud?}
    T -->|No| O
    T -->|Yes| U[Fraud Confirmed]
    
    S --> V{Evidence?}
    V -->|Insufficient| O
    V -->|Strong| U
    
    U --> W[Recovery Action]
    W --> X[Report Fraud]
    X --> Y[Update Models]
    
    Y --> Z[Blacklist]
    Z --> End([Case Closed])
    
    O --> End2([Process Continue])
```

### 3.3 Payment Processing Flow
```mermaid
graph TB
    Start([Payment Approved]) --> A[Payment Queue]
    
    A --> B{Payment Type?}
    
    B -->|Provider| C[Provider Payment]
    B -->|Member Reimburse| D[Member Payment]
    
    C --> E[Load Contract]
    E --> F[Apply Withholding]
    F --> G[Check Overpayment]
    
    G --> H{Has Overpayment?}
    H -->|Yes| I[Deduct Amount]
    H -->|No| J[Full Payment]
    
    I --> K[Calculate Net]
    J --> K
    
    D --> L[Load Preference]
    L --> M{Method?}
    
    M -->|Bank| N[Bank Transfer]
    M -->|Wallet| O[Digital Wallet]
    M -->|Check| P[Print Check]
    
    K --> Q{Provider Method?}
    Q -->|EFT| R[Electronic Transfer]
    Q -->|Check| S[Print Check]
    
    N --> T[Process Transfer]
    O --> T
    R --> T
    
    P --> U[Mail Service]
    S --> U
    
    T --> V{Success?}
    V -->|No| W[Retry Logic]
    V -->|Yes| X[Update Status]
    
    W --> Y{Retry Count?}
    Y -->|< 3| T
    Y -->|>= 3| Z[Manual Intervention]
    
    U --> X
    
    X --> AA[Send Remittance]
    AA --> AB[Update GL]
    AB --> AC[Reconciliation]
    
    AC --> End([Payment Complete])
    Z --> End2([Failed Payment])
```

---

## 4. SYSTEM INTEGRATION FLOWS

### 4.1 Multi-System Data Flow
```mermaid
graph LR
    subgraph External
        A[Provider EMR]
        B[Pharmacy System]
        C[Lab System]
        D[Bank API]
        E[Govt Systems]
    end
    
    subgraph Gateway
        F[API Gateway]
        G[EDI Gateway]
        H[FHIR Server]
    end
    
    subgraph Core
        I[Auth Engine]
        J[Claims Engine]
        K[Payment Engine]
    end
    
    subgraph Data
        L[(PostgreSQL)]
        M[(Redis Cache)]
        N[(Document Store)]
    end
    
    subgraph Analytics
        O[Data Lake]
        P[ML Platform]
        Q[BI Dashboard]
    end
    
    A -->|HL7| G
    A -->|FHIR| H
    B -->|API| F
    C -->|API| F
    D -->|API| F
    E -->|SOAP| G
    
    F --> I
    F --> J
    F --> K
    
    G --> J
    H --> I
    H --> J
    
    I --> L
    I --> M
    J --> L
    J --> N
    K --> L
    
    L --> O
    M --> P
    N --> O
    
    O --> Q
    P --> I
    P --> J
```

### 4.2 Event-Driven Architecture
```mermaid
graph TB
    subgraph Producers
        A[Member Portal]
        B[Provider Portal]
        C[Claims System]
        D[Auth System]
    end
    
    subgraph Kafka
        E[Claims Topic]
        F[Auth Topic]
        G[Payment Topic]
        H[Fraud Topic]
    end
    
    subgraph Consumers
        I[Adjudication Service]
        J[Payment Service]
        K[Fraud Service]
        L[Analytics Service]
        M[Notification Service]
    end
    
    subgraph Actions
        N[Process Claim]
        O[Send Payment]
        P[Flag Fraud]
        Q[Update Dashboard]
        R[Send Alert]
    end
    
    A --> E
    B --> F
    C --> E
    C --> G
    D --> F
    
    E --> I
    E --> K
    E --> L
    
    F --> I
    F --> L
    
    G --> J
    G --> L
    
    H --> K
    H --> M
    
    I --> N
    J --> O
    K --> P
    L --> Q
    M --> R
    
    K --> H
```

---

## 5. DECISION TREES

### 5.1 Claim Adjudication Decision Tree
```
Start: Claim Received
│
├─ Is Member Active?
│  ├─ No → Deny (Inactive Member)
│  └─ Yes ↓
│
├─ Is Provider In-Network?
│  ├─ No → Apply OON Benefits
│  │  ├─ Emergency? → Apply In-Network Rates
│  │  └─ Non-Emergency → Apply OON Rates (typically 60-70%)
│  └─ Yes ↓
│
├─ Is Service Covered?
│  ├─ No → Check Exclusions
│  │  ├─ Absolute Exclusion → Deny
│  │  └─ Conditional → Review Clinical Notes
│  └─ Yes ↓
│
├─ Prior Auth Required?
│  ├─ Yes → Check Auth Status
│  │  ├─ Not Authorized → Deny (No Auth)
│  │  ├─ Expired → Pend for Review
│  │  └─ Valid → Continue ↓
│  └─ No ↓
│
├─ Within Benefit Limits?
│  ├─ No → Apply Limits
│  │  ├─ Allow Excess? → Draw from Buffer
│  │  └─ No Excess → Cap at Limit
│  └─ Yes ↓
│
├─ Deductible Met?
│  ├─ No → Apply Deductible
│  └─ Yes ↓
│
├─ Calculate Copay/Coinsurance
│  ├─ Copay → Fixed Amount
│  └─ Coinsurance → Percentage
│
├─ COB Applicable?
│  ├─ Yes → Coordinate Benefits
│  │  ├─ Primary → Process Full
│  │  └─ Secondary → Process Balance
│  └─ No ↓
│
└─ Final Payment Calculation
   ├─ Plan Pays: Allowed - Member Responsibility
   └─ Member Pays: Copay + Coinsurance + Deductible
```

### 5.2 Reimbursement Decision Tree
```
Start: Reimbursement Request
│
├─ Documents Complete?
│  ├─ No → Request Missing Documents
│  │  ├─ Receipt Missing → Request Receipt
│  │  ├─ Medical Report Missing → Request Report
│  │  └─ Prescription Missing → Request Rx
│  └─ Yes ↓
│
├─ Document Quality Check
│  ├─ OCR Confidence < 80% → Manual Review
│  └─ OCR Confidence ≥ 80% ↓
│
├─ Provider Verification
│  ├─ Provider Not Found → Investigation
│  ├─ Provider Blacklisted → Deny
│  └─ Provider Valid ↓
│
├─ Service Date Check
│  ├─ > 90 days → Late Submission
│  │  ├─ Valid Reason? → Accept
│  │  └─ No Reason → Deny
│  └─ ≤ 90 days ↓
│
├─ Duplicate Check
│  ├─ Duplicate Found → Deny (Duplicate)
│  └─ No Duplicate ↓
│
├─ Amount Validation
│  ├─ Amount > UCR → Apply UCR Limit
│  └─ Amount ≤ UCR ↓
│
├─ Fraud Risk Score
│  ├─ High (>0.7) → SIU Investigation
│  ├─ Medium (0.3-0.7) → Enhanced Review
│  └─ Low (<0.3) ↓
│
├─ Calculate Reimbursement
│  ├─ Network Rate Available? → Use Network Rate
│  └─ No Network Rate → Use UCR (80th percentile)
│
└─ Process Payment
   ├─ Bank Transfer → Same Day
   ├─ Digital Wallet → Instant
   └─ Check → 5-7 Days
```

---

## 6. STATE MACHINES

### 6.1 Claim State Machine
```mermaid
stateDiagram-v2
    [*] --> Draft: Create
    Draft --> Submitted: Submit
    
    Submitted --> Validating: Auto-Validate
    Validating --> Valid: Pass
    Validating --> Invalid: Fail
    
    Invalid --> Submitted: Resubmit
    Invalid --> Cancelled: Cancel
    
    Valid --> Adjudicating: Process
    Adjudicating --> Approved: Approve
    Adjudicating --> Denied: Deny  
    Adjudicating --> Pended: Pend
    
    Pended --> UnderReview: Assign
    UnderReview --> Approved: Approve
    UnderReview --> Denied: Deny
    UnderReview --> MoreInfo: Request Info
    
    MoreInfo --> UnderReview: Info Received
    MoreInfo --> Denied: Timeout
    
    Approved --> PaymentPending: Queue Payment
    PaymentPending --> PaymentProcessing: Process
    PaymentProcessing --> Paid: Success
    PaymentProcessing --> PaymentFailed: Fail
    
    PaymentFailed --> PaymentPending: Retry
    PaymentFailed --> Cancelled: Max Retries
    
    Denied --> Appealed: Appeal
    Appealed --> UnderAppeal: Review Appeal
    UnderAppeal --> Approved: Overturn
    UnderAppeal --> Denied: Uphold
    
    Paid --> Closed: Complete
    Denied --> Closed: No Appeal
    Cancelled --> [*]
    Closed --> [*]
```

### 6.2 Authorization State Machine
```mermaid
stateDiagram-v2
    [*] --> Requested: Submit Request
    
    Requested --> Validating: Validate
    Validating --> Complete: Valid
    Validating --> Incomplete: Missing Info
    
    Incomplete --> Requested: Add Info
    Incomplete --> Expired: Timeout
    
    Complete --> AutoReview: Check Criteria
    AutoReview --> AutoApproved: Meets Criteria
    AutoReview --> ClinicalReview: Needs Review
    
    ClinicalReview --> UnderReview: Assign Reviewer
    UnderReview --> Approved: Approve
    UnderReview --> PartialApproved: Partial
    UnderReview --> Denied: Deny
    UnderReview --> MoreInfoNeeded: Request
    
    MoreInfoNeeded --> UnderReview: Received
    MoreInfoNeeded --> Denied: Timeout
    
    AutoApproved --> Active: Issue Auth
    Approved --> Active: Issue Auth
    PartialApproved --> Active: Issue Limited
    
    Active --> Used: Service Rendered
    Active --> Expired: Time Limit
    Active --> Cancelled: Cancel
    
    Denied --> Appealed: Appeal
    Appealed --> PeerReview: P2P
    PeerReview --> Approved: Overturn
    PeerReview --> Denied: Uphold
    
    Used --> Closed: Claim Processed
    Expired --> Closed: No Service
    Cancelled --> Closed: Cancelled
    Denied --> Closed: No Appeal
    
    Closed --> [*]
```

---

## 7. BATCH PROCESSING FLOWS

### 7.1 Nightly Batch Processing
```mermaid
graph TB
    Start([00:00 Start]) --> A[Lock Tables]
    
    A --> B[Process Pending Claims]
    B --> C[Calculate Accumulators]
    C --> D[Update Deductibles]
    D --> E[Process Payments]
    
    E --> F[Generate Reports]
    F --> F1[Daily Claims Report]
    F --> F2[Payment Report]
    F --> F3[Denial Report]
    F --> F4[Provider Report]
    
    F1 --> G[Data Quality Check]
    F2 --> G
    F3 --> G
    F4 --> G
    
    G --> H{Issues Found?}
    H -->|Yes| I[Alert Operations]
    H -->|No| J[Continue]
    
    I --> K[Manual Review]
    K --> J
    
    J --> L[GL Posting]
    L --> M[Reconciliation]
    
    M --> N{Balanced?}
    N -->|No| O[Investigation]
    N -->|Yes| P[Archive Data]
    
    O --> Q[Adjustment Entry]
    Q --> P
    
    P --> R[Backup]
    R --> S[Update Analytics]
    S --> T[Refresh Cache]
    
    T --> U[Unlock Tables]
    U --> End([06:00 Complete])
```

### 7.2 Monthly Closing Process
```mermaid
graph TB
    Start([Month End]) --> A[Freeze Transactions]
    
    A --> B[Final Adjudication]
    B --> C[Calculate Reserves]
    C --> D[Accrue Unbilled]
    
    D --> E[Member Statements]
    E --> F[Provider Statements]
    F --> G[Generate Invoices]
    
    G --> H[Regulatory Reports]
    H --> H1[OJK Report]
    H --> H2[Tax Report]
    H --> H3[Audit Report]
    
    H1 --> I[Management Reports]
    H2 --> I
    H3 --> I
    
    I --> J[KPI Calculation]
    J --> K[Trend Analysis]
    K --> L[Forecasting]
    
    L --> M[Close Books]
    M --> N[Archive Period]
    N --> O[Reset Counters]
    
    O --> P[New Period Setup]
    P --> End([New Month Ready])
```

---

## 8. ERROR HANDLING FLOWS

### 8.1 System Error Recovery
```mermaid
graph TB
    Start([Error Detected]) --> A{Error Type?}
    
    A -->|Network| B[Retry Logic]
    A -->|Database| C[Failover]
    A -->|Application| D[Restart Service]
    A -->|External API| E[Circuit Breaker]
    
    B --> F{Retry Count?}
    F -->|< 3| G[Wait & Retry]
    F -->|>= 3| H[Alert Ops]
    
    G --> I{Success?}
    I -->|No| F
    I -->|Yes| J[Resume]
    
    C --> K[Switch to Standby]
    K --> L[Verify Connection]
    L --> M{Connected?}
    M -->|No| H
    M -->|Yes| J
    
    D --> N[Health Check]
    N --> O{Healthy?}
    O -->|No| P[Escalate]
    O -->|Yes| J
    
    E --> Q[Open Circuit]
    Q --> R[Use Fallback]
    R --> S[Test Circuit]
    S --> T{Working?}
    T -->|No| U[Keep Open]
    T -->|Yes| V[Close Circuit]
    
    U --> W[Wait Period]
    W --> S
    
    V --> J
    
    H --> X[Page On-Call]
    P --> X
    
    X --> Y[Manual Intervention]
    Y --> Z[Root Cause Analysis]
    Z --> AA[Fix Issue]
    AA --> J
    
    J --> End([Resume Operations])
```

### 8.2 Data Inconsistency Resolution
```mermaid
graph TB
    Start([Inconsistency Detected]) --> A[Identify Scope]
    
    A --> B{Severity?}
    
    B -->|Critical| C[Stop Processing]
    B -->|High| D[Flag Records]
    B -->|Low| E[Log Issue]
    
    C --> F[Alert Team]
    F --> G[Investigate]
    
    D --> H[Quarantine Data]
    H --> G
    
    E --> I[Schedule Review]
    I --> G
    
    G --> J[Root Cause]
    J --> K{Source?}
    
    K -->|Input Error| L[Validate Source]
    K -->|Process Error| M[Fix Logic]
    K -->|System Error| N[Fix System]
    
    L --> O[Correct Data]
    M --> O
    N --> O
    
    O --> P[Reprocess]
    P --> Q{Valid Now?}
    
    Q -->|No| G
    Q -->|Yes| R[Update Records]
    
    R --> S[Audit Trail]
    S --> T[Notify Affected]
    T --> U[Update Reports]
    
    U --> V[Preventive Action]
    V --> End([Resolution Complete])
```

---

## 9. PERFORMANCE OPTIMIZATION FLOWS

### 9.1 Cache Strategy Flow
```mermaid
graph TB
    Start([Request]) --> A{Cache Check}
    
    A -->|Hit| B{Fresh?}
    A -->|Miss| C[Load from DB]
    
    B -->|Yes| D[Return Cache]
    B -->|No| E{Stale OK?}
    
    E -->|Yes| F[Return Stale]
    E -->|No| C
    
    F --> G[Async Refresh]
    
    C --> H[Process Data]
    H --> I[Cache Result]
    
    I --> J{Cacheable?}
    J -->|Yes| K[Set TTL]
    J -->|No| L[Skip Cache]
    
    K --> M[Store in Redis]
    M --> N[Return Result]
    
    L --> N
    D --> N
    
    G --> C
    
    N --> End([Complete])
```

### 9.2 Load Balancing Strategy
```mermaid
graph TB
    Start([Incoming Request]) --> A[Load Balancer]
    
    A --> B{Algorithm?}
    
    B -->|Round Robin| C[Next Server]
    B -->|Least Connections| D[Min Connections]
    B -->|Weighted| E[By Capacity]
    B -->|IP Hash| F[Consistent Hash]
    
    C --> G{Health Check}
    D --> G
    E --> G
    F --> G
    
    G -->|Unhealthy| H[Skip Server]
    G -->|Healthy| I[Route Request]
    
    H --> J{More Servers?}
    J -->|Yes| B
    J -->|No| K[All Down Alert]
    
    I --> L[Process Request]
    
    L --> M{Response Time}
    M -->|Fast < 100ms| N[Update Metrics]
    M -->|Normal 100-500ms| N
    M -->|Slow > 500ms| O[Log Slow]
    
    O --> P[Adjust Weight]
    P --> N
    
    N --> Q[Return Response]
    
    K --> R[Failover Site]
    R --> L
    
    Q --> End([Complete])
```

---

**Related Documents**:
- UI/UX Design Specifications
- Data Model Design
- API Specifications
- System Architecture
```mermaid
graph TD
    A[Start: Claim Received] --> B{Is Member Active?};
    
    %% Member Active Check
    B -- No --> D1[Deny: Inactive Member];
    B -- Yes --> C{Is Provider In-Network?};
    
    %% Provider Network Check
    C -- No --> C1[Apply OON Benefits];
    C1 --> C1a{Is it an Emergency?};
    C1a -- Yes --> C2[Apply IN-Network Rates];
    C1a -- No --> C3[Apply OON Rates];
    C -- Yes --> D{Is Service Covered?};
    C3 --> D;
    C2 --> D;
    
    %% Service Coverage Check
    D -- No --> D1a[Check Exclusions];
    D1a --> D1b{Absolute Exclusion?};
    D1b -- Yes --> D1c[Deny: Absolute Exclusion];
    D1b -- No --> D1d[Review Clinical Notes / Conditional];
    D -- Yes --> E;
    D1d --> E;
    
    %% Prior Authorization Check
    E{Prior Auth Required?} --> E1[Valid Auth → Continue];
    E -- No --> E1;
    E -- Yes --> E2[Check Auth Status];
    E2 -- Not Authorized --> D2[Deny: No Auth];
    E2 -- Expired --> D3[Pend for Review];
    E2 -- Valid --> E1;
    
    %% Benefit Limits Check
    E1 --> F{Within Benefit Limits?};
    F -- No --> F1[Apply Limits];
    F1 --> F1a{Allow Excess?};
    F1a -- Yes --> F2[Draw from Buffer];
    F1a -- No --> F3[Cap at Limit];
    F -- Yes --> G;
    F2 --> G;
    F3 --> G;
    
    %% Deductible and Cost-Sharing
    G{Deductible Met?} --> H[Calculate Copay/Coinsurance];
    G -- No --> G1[Apply Deductible];
    G1 --> H;
    
    H --> I{COB Applicable?};
    
    %% Coordination of Benefits (COB)
    I -- No --> J[Final Payment Calculation];
    I -- Yes --> I1[Coordinate Benefits];
    I1 --> I2[Primary → Process Full];
    I1 --> I3[Secondary → Process Balance];
    I2 --> J;
    I3 --> J;
    
    %% Final Calculation (Output)
    J --> K[Plan Pays: Allowed - Member Responsibility];
    J --> L[Member Pays: Copay + Coinsurance + Deductible];
```
