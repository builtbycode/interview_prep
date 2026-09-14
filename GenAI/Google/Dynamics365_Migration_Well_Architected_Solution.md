# SAP Data Migration to Microsoft Dynamics 365

## Well-Architected Microsoft Solution Options

**Purpose:** Define the Microsoft-side architecture for moving SAP data
that is already available in an Azure landing/staging layer into
Dynamics 365.

> **Scope boundary:** SAP extraction and SAP → Azure ingestion are
> outside this PoV. The architecture starts after the data has landed in
> Azure.

------------------------------------------------------------------------

## 1. Executive Summary

The business requirement is to determine the best **Microsoft-supported
and enterprise-ready approach** for moving data from Azure staging/Data
Lake into Dynamics 365.

There are two important Dynamics 365 target families:

1.  **Dynamics 365 Customer Engagement apps** such as Sales, Customer
    Service and Field Service, which use **Microsoft Dataverse**.
2.  **Dynamics 365 Finance & Operations (F&O)** applications such as
    Finance and Supply Chain Management, which use **Data Entities and
    the Data Management Framework (DMF)**.

The target application must therefore be confirmed before selecting the
final implementation.

### Recommended direction

  -----------------------------------------------------------------------
  Target                  Recommended primary     Why
                          pattern                 
  ----------------------- ----------------------- -----------------------
  Dynamics 365 Customer   **Azure Data Factory →  Strong fit for Azure
  Engagement / Dataverse  Dataverse**             staging,
                                                  transformation,
                                                  orchestration and
                                                  enterprise migration

  Dynamics 365 Finance &  **Azure Data Factory →  Uses F&O's native data
  Operations              F&O Data Management     entities, staging and
                          Framework / Data        high-volume
                          Package API**           data-management
                                                  capabilities

  Ongoing business        **Microsoft Data        Better for operational
  synchronization between Integrator / Dual-write synchronization than a
  F&O and Dataverse apps  where applicable**      one-time migration
  -----------------------------------------------------------------------

For a large migration, the design should use a **staging → validate →
transform → load → reconcile** pattern rather than a direct
source-to-Dynamics transfer.

------------------------------------------------------------------------

# 2. Scope and Assumptions

## In scope

-   Azure Data Lake / Blob / staging layer
-   Data profiling and validation
-   Transformation and mapping
-   Dynamics 365 connectivity
-   Dataverse migration
-   Dynamics 365 Finance & Operations migration
-   Security
-   Performance and volume testing
-   Monitoring
-   Error handling
-   Reconciliation
-   Cutover and rollback planning
-   Well-Architected review

## Out of scope

-   SAP extraction
-   SAP connectivity
-   SAP source-system transformation
-   SAP → Azure ingestion architecture
-   SAP DataSphere design, unless separately requested

### Starting assumption

``` text
SAP
 |
 |  Separate workstream
 v
Azure Landing / Staging
 |
 |  <-- THIS IS WHERE THIS ARCHITECTURE STARTS
 v
Microsoft Dynamics 365 Migration
```

------------------------------------------------------------------------

# 3. High-Level Architecture

``` mermaid
flowchart LR
    A[SAP] -->|Separate scope| B[Azure Landing / Staging]

    B --> C[Data Quality & Profiling]
    C --> D[Transformation & Mapping]

    D --> E{Dynamics 365 Target}

    E --> F[Customer Engagement / Dataverse]
    E --> G[Finance & Operations]

    F --> F1[Dataverse Tables]
    G --> G1[F&O Data Entities]
```

The architecture deliberately separates **data landing** from
**application loading**.

------------------------------------------------------------------------

# 4. Solution A --- Dynamics 365 Customer Engagement / Dataverse

Examples include:

-   Dynamics 365 Sales
-   Dynamics 365 Customer Service
-   Dynamics 365 Field Service

Microsoft provides an Azure Data Factory/Synapse connector for Dynamics
365 Dataverse. It supports copy activity as a source/sink and Mapping
Data Flow, and supports Microsoft Entra service principal and managed
identity authentication.

## Recommended Architecture

``` mermaid
flowchart LR
    A[Azure Data Lake / Staging] --> B[Azure Data Factory]

    B --> C[Data Profiling]
    C --> D[Mapping & Transformation]
    D --> E[Reference Data Lookup]
    E --> F[Validation]

    F --> G[Dataverse Connector]
    G --> H[Dynamics 365 / Dataverse]

    F --> I[Rejected Records]
    I --> J[Error Store]

    H --> K[Reconciliation]
    K --> L[Migration Dashboard]
```

## Component responsibilities

### Azure Data Lake / Staging

Stores the source data before it is loaded into Dynamics.

Recommended logical zones:

``` text
/raw
    Original landed data

/validated
    Data that passed quality checks

/transformed
    Data mapped to Dynamics target structures

/rejected
    Records that failed validation

/archive
    Historical migration snapshots
```

### Azure Data Factory

Acts as the orchestration layer.

Typical pipeline:

``` text
Read batch
   |
Validate
   |
Transform
   |
Map source → Dynamics fields
   |
Resolve lookups
   |
Load Dataverse
   |
Capture success/failure
   |
Reconcile
```

### Dataverse

The final business application data store.

Important consideration:

Do not treat Dataverse as a generic relational database. Load through
supported Dataverse/Dynamics interfaces so that the application data
model, relationships and business requirements are respected.

------------------------------------------------------------------------

# 5. Dataverse --- Three Microsoft-Supported Patterns

## Pattern A1 --- Azure Data Factory → Dataverse

``` text
Azure Data Lake
      |
      v
Azure Data Factory
      |
      +--> Mapping Data Flow
      |
      +--> Validation
      |
      v
Dataverse Connector
      |
      v
Dynamics 365
```

### Best fit

-   Medium/large migration
-   Azure already contains the source data
-   Significant transformation is required
-   Repeatable migration pipelines are required
-   Enterprise monitoring is required

### Strengths

-   Native Azure orchestration
-   Transformation capability
-   Batch processing
-   Scheduling
-   Monitoring
-   Microsoft Entra authentication
-   Good fit for the proposed architecture

### Key performance consideration

Dataverse has service-side limits and throttling. Do not simply maximize
parallelism.

The migration PoV should test:

-   batch size
-   parallel copies
-   entity complexity
-   plug-ins/workflows
-   API throttling
-   retry behavior
-   total migration window

Microsoft's current ADF connector documentation states that the default
Dynamics sink settings are designed to avoid excessive concurrent calls
and recommends tuning batch size and parallel copies based on the entity
and workload.

------------------------------------------------------------------------

# 6. Pattern A2 --- Native Dataverse Import

``` mermaid
flowchart LR
    A[Prepared CSV / Data Package] --> B[Dataverse Import]
    B --> C[Dataverse Tables]
    C --> D[Dynamics 365]
```

### Best fit

-   Smaller migration
-   Simple data structures
-   One-time migration
-   Limited transformation
-   Business users or functional teams need controlled import

Microsoft's current Dataverse migration guidance describes simple
migrations as up to approximately **1 GB or 50,000 records**, with more
advanced tooling recommended as volume and complexity increase.

### Strengths

-   Simple
-   Low implementation effort
-   Native Microsoft capability

### Limitations

Not the preferred architecture for a very large enterprise migration
with complex relationships and extensive transformations.

------------------------------------------------------------------------

# 7. Pattern A3 --- ADF/Fabric + Dataverse APIs / Custom Migration

``` mermaid
flowchart LR
    A[Azure Data Lake] --> B[ADF / Fabric]
    B --> C[Complex Transformation]
    C --> D[Custom Migration Service]
    D --> E[Dataverse APIs]
    E --> F[Dynamics 365]

    D --> G[Retry / Error Queue]
    G --> D
```

### Best fit

-   Very complex migration
-   Custom business rules
-   Complex dependencies
-   Custom tables
-   Special sequencing requirements
-   Migration logic that cannot be expressed cleanly through standard
    copy/mapping

### Strengths

-   Maximum flexibility
-   Fine-grained control
-   Custom retry and dependency logic

### Trade-off

More development and operational complexity.

**Recommendation:** use this only where ADF → Dataverse or native import
cannot satisfy the requirements.

------------------------------------------------------------------------

# 8. Solution B --- Dynamics 365 Finance & Operations

This is a different architecture from Dataverse.

Do **not** assume that the Dataverse Dynamics connector can be used for
Finance & Operations.

Microsoft's ADF Dynamics connector documentation explicitly
distinguishes Finance & Operations and points to the Dynamics AX
connector for F&O scenarios.

For F&O, the important Microsoft-native capabilities are:

-   Data Entities
-   Data Management Framework (DMF)
-   Data packages
-   Data Management Package REST API
-   OData for suitable synchronous/entity scenarios

------------------------------------------------------------------------

# 9. Recommended F&O Architecture

``` mermaid
flowchart LR
    A[Azure Data Lake / Staging] --> B[Azure Data Factory]

    B --> C[Data Quality]
    C --> D[Transformation]
    D --> E[Create F&O Data Package]

    E --> F[DMF Package API]
    F --> G[F&O Staging]

    G --> H[Validation]
    H --> I[F&O Data Entities]
    I --> J[Dynamics 365 Finance & Operations]

    H --> K[Import Errors]
    K --> L[Error Store]

    J --> M[Reconciliation]
```

The important difference is that F&O has its own **Data Management
Framework** with staging and data entities.

------------------------------------------------------------------------

# 10. F&O --- Three Main Patterns

## Pattern B1 --- Azure Data Factory → F&O Data Management Framework

``` text
Azure Data Lake
      |
      v
Azure Data Factory
      |
      +--> Transform
      +--> Validate
      +--> Create Package
      |
      v
F&O Data Management Framework
      |
      v
F&O Staging
      |
      v
Data Entities
      |
      v
Dynamics 365 F&O
```

### Recommended for

-   Enterprise migration
-   High-volume migration
-   Multiple related entities
-   Batch migration
-   Controlled migration windows

This should normally be the **primary PoV option for F&O**.

------------------------------------------------------------------------

# 11. Pattern B2 --- F&O Data Management Workspace / Data Packages

``` mermaid
flowchart LR
    A[Prepared Migration Package] --> B[F&O Data Management]
    B --> C[Staging]
    C --> D[Validation]
    D --> E[Data Entity]
    E --> F[F&O]
```

### Recommended for

-   Controlled one-time migration
-   Configuration/master-data migration
-   Functional-led migration
-   Smaller or moderate data sets

The Data Management Framework supports import/export projects and
packages through the Data Management workspace.

------------------------------------------------------------------------

# 12. Pattern B3 --- F&O OData / APIs

``` mermaid
flowchart LR
    A[Azure Data Factory / Integration Service] --> B[Transformation]
    B --> C[OAuth / Entra Authentication]
    C --> D[F&O OData Endpoint]
    D --> E[Public Data Entity]
    E --> F[F&O]
```

### Recommended for

-   Near-real-time or operational integration
-   Smaller transactional workloads
-   Scenarios where a public data entity is appropriate

### Do not use this as the default bulk migration mechanism

For very large migrations, F&O's asynchronous Data Management
capabilities are generally a better fit because they are designed for
data import/export and higher-throughput scenarios.

------------------------------------------------------------------------

# 13. Dataverse vs F&O --- Key Difference

  -----------------------------------------------------------------------
  Area                    Dynamics 365 CE /       Dynamics 365 F&O
                          Dataverse               
  ----------------------- ----------------------- -----------------------
  Application data model  Dataverse tables        F&O Data Entities

  Primary integration     Dataverse APIs /        Data Management
  model                   connector               Framework

  ADF connector           Dynamics 365 /          Dynamics AX /
                          Dataverse connector     F&O-specific approach

  Bulk migration          ADF, APIs, native       DMF + Data Packages
                          import                  

  Staging                 Azure staging +         Azure staging + F&O DMF
                          Dataverse processing    staging

  API option              Dataverse APIs          OData

  High-volume option      Controlled ADF          DMF asynchronous
                          parallelism             processing

  Security                Entra + Dataverse       Entra + F&O
                          security roles          data-entity/security
                                                  model

  Main concern            API throttling and      Entity dependencies,
                          business logic          DMF throughput and
                                                  staging

  Recommended PoV         ADF → Dataverse         ADF → DMF/Data Package
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 14. Optional Pattern --- Data Integrator / Dual-write

This option is important when the requirement is **ongoing
synchronization**, not just migration.

``` mermaid
flowchart LR
    A[Dynamics 365 F&O] <--> B[Microsoft Data Integration / Dual-write]
    B <--> C[Dataverse]
    C --> D[Dynamics 365 Sales / Customer Service]
```

### Use this when

-   F&O and Dataverse applications need to remain synchronized
-   Data changes continuously
-   The business process spans F&O and Customer Engagement applications

### Do not confuse it with the SAP migration

For a one-time SAP → Dynamics migration, Data Integrator/Dual-write is
usually **not the primary migration engine**.

It becomes relevant when the target operating model requires **F&O ↔
Dataverse synchronization after migration**.

Microsoft currently recommends dual-write for tightly coupled
bidirectional integration between F&O apps and Dataverse.

------------------------------------------------------------------------

# 15. End-to-End Recommended Enterprise Architecture

``` mermaid
flowchart TB

    subgraph SAP_Workstream["SAP Workstream - Separate Scope"]
        SAP[SAP]
        SAP --> LAND[Azure Landing / Raw Data]
    end

    subgraph Azure["Azure Migration Platform"]
        LAND --> STG[Curated Staging]
        STG --> DQ[Data Quality & Profiling]
        DQ --> MAP[Transformation & Mapping]
        MAP --> VAL[Business Validation]

        VAL --> ERR[Rejected / Error Data]
        ERR --> DLQ[Error Store / Reprocessing]

        OBS[Azure Monitor / Log Analytics]
    end

    subgraph Dataverse["Option 1 - Dynamics 365 Customer Engagement"]
        VAL --> ADFDV[Azure Data Factory]
        ADFDV --> DV[Dataverse]
        DV --> CE[Dynamics 365 Sales / Customer Service / Field Service]
    end

    subgraph FNO["Option 2 - Dynamics 365 Finance & Operations"]
        VAL --> ADFFO[Azure Data Factory]
        ADFFO --> PKG[Data Package]
        PKG --> DMF[DMF / Package API]
        DMF --> FOSTG[F&O Staging]
        FOSTG --> ENTITY[F&O Data Entities]
        ENTITY --> FO[Dynamics 365 Finance & Operations]
    end

    subgraph Security["Enterprise Security"]
        ENTRA[Microsoft Entra ID]
        KV[Azure Key Vault]
        RBAC[RBAC / Least Privilege]
    end

    ENTRA --> ADFDV
    ENTRA --> ADFFO
    KV --> ADFDV
    KV --> ADFFO
    RBAC --> ADFDV
    RBAC --> ADFFO

    ADFDV --> OBS
    ADFFO --> OBS
    DMF --> OBS
    DV --> OBS
    FO --> OBS
```

------------------------------------------------------------------------

# 16. Well-Architected Design

The architecture should be reviewed against the five Azure
Well-Architected pillars:

1.  Reliability
2.  Security
3.  Cost Optimization
4.  Operational Excellence
5.  Performance Efficiency

These are Microsoft's five core Well-Architected pillars.

------------------------------------------------------------------------

## 16.1 Reliability

### Design

``` text
Batch
  |
  v
Validation
  |
  v
Migration
  |
  +---- Success ----> Reconciliation
  |
  +---- Failure ----> Error Store
                         |
                         v
                      Retry
```

### Recommendations

-   Make pipelines restartable.
-   Use idempotent processing where possible.
-   Use stable business/alternate keys.
-   Do not reload already-successful records unnecessarily.
-   Store execution IDs and batch IDs.
-   Keep rejected records separately.
-   Implement retry for transient failures.
-   Perform reconciliation after every major batch.
-   Define RTO/RPO expectations for the migration platform.
-   Conduct cutover rehearsal.

------------------------------------------------------------------------

# 17. Security Architecture

``` mermaid
flowchart LR
    A[Azure Data Factory] --> B[Managed Identity / Service Principal]
    B --> C[Microsoft Entra ID]

    A --> D[Azure Key Vault]
    D --> E[Secrets / Certificates]

    A --> F[Azure Data Lake]
    A --> G[Dataverse / F&O]

    C --> H[RBAC]
    H --> A
    H --> G
```

### Security principles

-   Prefer managed identity where supported.
-   Otherwise use Microsoft Entra service principal.
-   Store secrets/certificates in Key Vault.
-   Never hard-code credentials in pipelines.
-   Apply least privilege.
-   Separate DEV / TEST / UAT / PROD.
-   Restrict network access.
-   Encrypt data at rest and in transit.
-   Protect sensitive data in logs.
-   Audit access and migration operations.

For F&O data entities, Microsoft supports separate security
considerations for OData/data services and Data Management integration
modes.

------------------------------------------------------------------------

# 18. Performance Architecture

Performance must be **measured**, not assumed.

## Test dimensions

``` text
Data Volume
    |
    +--> 100K records
    +--> 500K records
    +--> 1M records
    +--> Expected production volume
             |
             v
       Measure throughput
             |
             v
      Tune parallelism
             |
             v
      Check throttling
             |
             v
      Validate completion
```

### Dataverse

Test:

-   write batch size
-   parallel copies
-   API throttling
-   entity complexity
-   plug-ins
-   workflows
-   lookups
-   alternate keys
-   dependency order

### F&O

Test:

-   package size
-   entity sequence
-   staging performance
-   batch processing
-   parallel processing where supported
-   validation cost
-   import execution time
-   error volume

------------------------------------------------------------------------

# 19. Data Transformation Pattern

Transformation should happen **before the target application whenever
possible**.

``` mermaid
flowchart LR
    A[SAP-shaped Data] --> B[Canonical / Curated Model]
    B --> C[Business Mapping]
    C --> D[Reference Data Mapping]
    D --> E[Target-specific Model]

    E --> F[Dataverse]
    E --> G[F&O]
```

### Why?

It avoids putting unnecessary transformation logic inside Dynamics.

For example:

``` text
SAP Customer ID
       |
       v
Customer Mapping Table
       |
       v
Dynamics Account Number
       |
       v
Dataverse / F&O
```

Maintain mapping/reference data separately so that the migration can be
rerun consistently.

------------------------------------------------------------------------

# 20. Data Validation Strategy

Use three levels of validation.

## Level 1 --- Technical validation

-   Data type
-   Nullability
-   Length
-   Format
-   Duplicate records
-   Required fields

## Level 2 --- Referential validation

-   Customer exists
-   Product exists
-   Currency exists
-   Legal entity exists
-   Parent-child relationship exists

## Level 3 --- Business validation

-   Valid status
-   Valid business unit
-   Valid ownership
-   Valid financial dimensions
-   Valid business rules

------------------------------------------------------------------------

# 21. Migration Sequencing

Do not load all entities randomly.

A typical dependency-driven sequence is:

``` text
1. Reference / Configuration Data
          |
          v
2. Master Data
   Customer / Vendor / Product
          |
          v
3. Relationships
          |
          v
4. Transactional Data
          |
          v
5. Historical Data
          |
          v
6. Reconciliation
          |
          v
7. Business Sign-off
```

The exact sequence must be derived from the Dynamics target data model.

------------------------------------------------------------------------

# 22. Error Handling

Every migration pipeline should have an explicit error path.

``` mermaid
flowchart LR
    A[Load Record] --> B{Success?}

    B -->|Yes| C[Success Log]
    B -->|No| D[Error Log]

    D --> E{Transient?}

    E -->|Yes| F[Retry]
    F --> A

    E -->|No| G[Rejected Data Store]
    G --> H[Correct Data]
    H --> I[Reprocess]
    I --> A
```

Capture:

-   source record ID
-   target record ID
-   batch ID
-   execution ID
-   timestamp
-   error code
-   error message
-   retry count
-   transformation version

------------------------------------------------------------------------

# 23. Reconciliation

A migration is not complete when the pipeline says **Succeeded**.

Perform reconciliation.

``` text
Source Count
     |
     v
Transformation Count
     |
     v
Target Success Count
     |
     +--> Failed Count
     |
     +--> Rejected Count
     |
     v
Business Reconciliation
```

Example:

``` text
Source records       = 1,000,000
Validated             =   995,000
Rejected              =     5,000
Loaded successfully   =   994,500
Load failures         =       500

Reconciliation must explain:
1,000,000 = 994,500 + 5,000 + 500
```

Also reconcile business totals where applicable, not only record counts.

------------------------------------------------------------------------

# 24. Observability

Recommended monitoring:

``` mermaid
flowchart TB
    A[ADF Pipelines] --> D[Azure Monitor]
    B[Dataverse] --> D
    C[F&O / DMF] --> D

    D --> E[Log Analytics]
    E --> F[Dashboard]
    E --> G[Alerts]
    E --> H[Operational Reports]
```

Monitor:

-   Pipeline success/failure
-   Duration
-   Throughput
-   API throttling
-   Retry count
-   Failed records
-   Reconciliation mismatch
-   Target-side errors
-   Authentication failures

------------------------------------------------------------------------

# 25. Cost Optimization

Avoid building an unnecessarily complex platform.

### Start with

``` text
Azure Data Lake
      +
Azure Data Factory
      +
Target-native Dynamics integration
      +
Azure Monitor
      +
Key Vault
```

Add additional components only when justified.

Examples:

-   Fabric/Synapse for large-scale transformation/analytics requirements
-   Custom Azure Functions/services for complex migration logic
-   Service Bus for asynchronous decoupling where required
-   Additional staging database where relational transformation needs
    justify it

The Well-Architected principle is to meet business requirements without
over-engineering or over-provisioning.

------------------------------------------------------------------------

# 26. Recommended Decision Matrix

  ---------------------------------------------------------------------------------
  Requirement         Dataverse        ADF →   Custom API      F&O DMF    F&O OData
                         Native    Dataverse                           
                         Import                                        
  ---------------- ------------ ------------ ------------ ------------ ------------
  Small/simple            ★★★★★          ★★★            ★          ★★★          ★★★
  migration                                                            

  Large migration            ★★        ★★★★★         ★★★★        ★★★★★           ★★

  Complex                    ★★        ★★★★★        ★★★★★         ★★★★           ★★
  transformation                                                       

  Repeatable                 ★★        ★★★★★        ★★★★★        ★★★★★         ★★★★
  pipeline                                                             

  Enterprise                 ★★        ★★★★★        ★★★★★         ★★★★          ★★★
  monitoring                                                           

  Fine-grained               ★★         ★★★★        ★★★★★          ★★★        ★★★★★
  custom logic                                                         

  F&O bulk                  N/A         ★★★★          ★★★        ★★★★★           ★★
  migration                                                            

  Dataverse bulk            ★★★        ★★★★★         ★★★★          N/A          N/A
  migration                                                            

  Ongoing F&O ↔             N/A          ★★★         ★★★★          ★★★          ★★★
  Dataverse sync                                                       

  Implementation            Low       Medium         High       Medium       Medium
  complexity                                                           
  ---------------------------------------------------------------------------------

------------------------------------------------------------------------

# 27. Final Recommended Architecture

## If target is Dynamics 365 Customer Engagement / Dataverse

``` text
Azure Data Lake
      |
      v
Azure Data Factory
      |
      +--> Validate
      +--> Transform
      +--> Map
      +--> Resolve references
      |
      v
Dataverse Connector
      |
      v
Dynamics 365
      |
      v
Reconciliation + Monitoring
```

**Recommended primary solution: ADF → Dataverse.**

Use native import for small/simple migrations and custom APIs only where
the migration has requirements that standard ADF capabilities cannot
satisfy.

------------------------------------------------------------------------

## If target is Dynamics 365 Finance & Operations

``` text
Azure Data Lake
      |
      v
Azure Data Factory
      |
      +--> Validate
      +--> Transform
      +--> Map
      +--> Build Data Package
      |
      v
F&O Data Management Package API
      |
      v
F&O Staging
      |
      v
F&O Data Entities
      |
      v
Dynamics 365 F&O
      |
      v
Reconciliation + Monitoring
```

**Recommended primary solution: ADF → F&O Data Management Framework/Data
Package API.**

Use OData for appropriate operational/smaller synchronous scenarios
rather than making it the default high-volume migration mechanism.

------------------------------------------------------------------------

# 28. PoV Plan

The PoV should prove the architecture using representative data.

## Phase 1 --- Connectivity

Prove:

``` text
Azure → Dynamics
```

-   Authentication
-   Authorization
-   Connectivity
-   Target entity access

## Phase 2 --- Small migration

Example:

``` text
10K–50K records
```

Prove:

-   Mapping
-   Transformation
-   Relationships
-   Validation
-   Error handling

## Phase 3 --- Volume test

Use representative production-like volume.

Measure:

-   Records/minute
-   Total migration duration
-   CPU/resource usage
-   API throttling
-   Retry rate
-   Error rate

## Phase 4 --- Failure test

Intentionally introduce:

-   Invalid lookup
-   Duplicate key
-   Missing mandatory field
-   Invalid reference
-   Network/transient failure

Prove that failed records can be isolated and reprocessed.

## Phase 5 --- Reconciliation

Prove:

``` text
Source
   =
Loaded
 + Rejected
 + Failed
```

and validate business totals.

## Phase 6 --- Security

Prove:

-   Entra authentication
-   Managed identity/service principal
-   Key Vault
-   RBAC
-   Audit
-   Environment separation

------------------------------------------------------------------------

# 29. Architecture Decision

### Recommended enterprise decision

**Do not select one generic "Dynamics 365 connector" for all
scenarios.**

Instead:

``` text
                         ┌─> Dataverse?
                         │
Azure Staging ──> Target ┤
                         │
                         └─> F&O?
```

### If Dataverse

**Azure Data Factory → Dataverse**

### If Finance & Operations

**Azure Data Factory → F&O Data Management Framework / Data Package
API**

### If ongoing F&O ↔ Dataverse synchronization is required

Evaluate **Dual-write / Data Integrator** separately as an operational
integration architecture.

------------------------------------------------------------------------

# 30. Key Interview / Architecture Explanation

If you need to explain the solution in simple words:

> "We are not solving the SAP extraction problem in this architecture.
> We assume SAP data is already available in Azure staging. From there,
> we first validate and transform the data and then use the
> Microsoft-supported integration mechanism based on the Dynamics 365
> application. For Customer Engagement applications, the preferred
> enterprise pattern is Azure Data Factory to Dataverse. For Finance and
> Operations, the preferred pattern is Azure Data Factory feeding the
> Finance & Operations Data Management Framework through data packages.
> We then handle security, throttling, retries, monitoring and
> reconciliation so that the migration is reliable and
> production-ready."

------------------------------------------------------------------------

# 31. Microsoft Guidance Used

The architecture is aligned with current Microsoft guidance for:

-   Azure Well-Architected Framework
-   Dataverse data migration approaches
-   Azure Data Factory Dynamics 365/Dataverse connector
-   Dynamics 365 Finance & Operations Data Management Framework
-   F&O Data Entities
-   F&O Data Management Package REST API
-   Microsoft Data Integrator / Dual-write

The five Well-Architected pillars are **Reliability, Security, Cost
Optimization, Operational Excellence and Performance Efficiency**.
