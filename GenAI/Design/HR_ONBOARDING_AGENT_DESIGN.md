# System Design Document: Enterprise HR Onboarding AI Agent System

## 1. Executive Summary & Vision

### 1.1 Problem Statement
Traditional employee onboarding is often manual, fragmented, and time-consuming. New hires experience friction navigating disparate systems (IT provisioning, compliance document submission, HRIS registration, policy questions, and team introductions), while HR teams face significant overhead answering repetitive questions and verifying required documentation.

### 1.2 Solution Overview
The **HR Onboarding Agent** is an autonomous, multi-agent conversational platform powered by Large Language Models (LLMs), Retrieval-Augmented Generation (RAG), and API-driven tool execution. It proactively guides new hires from **Pre-boarding (Day -7)** through their **90-Day Probation Period**, automating document intake, IT system provisioning, policy Q&A, and milestone check-ins.

### 1.3 Key Objectives
- **Reduce Time-to-Productivity**: Cut new hire setup time from days to hours.
- **Lower HR Support Load**: Automate up to 80% of routine onboarding inquiries.
- **Ensure Compliance**: 100% completion tracking of mandatory tax forms, NDAs, and policy acknowledgements.
- **Enhance Employee Experience (EX)**: Deliver personalized, 24/7 conversational support via Slack/Microsoft Teams.

---

## 2. High-Level System Architecture & Flowcharts

### 2.1 Multi-Agent Architecture Overview
The system uses a **Stateful Graph Multi-Agent Architecture** (e.g., built with **LangGraph** or **AutoGen**). A central **Orchestrator Agent** manages state transitions, delegates sub-tasks to specialized domain agents, and coordinates Human-in-the-Loop (HITL) reviews.

```mermaid
flowchart TD
    User["New Hire / Employee"] <--> SlackTeams["Slack / MS Teams Interface"]
    HRAdmin["HR Administrator / Manager"] <--> WebPortal["HR Admin Dashboard"]
    
    SlackTeams <--> APIGateway["API Gateway / Ingress Router"]
    WebPortal <--> APIGateway
    
    APIGateway <--> Guardrails["Safety & PII Guardrails Layer"]
    Guardrails <--> Orchestrator["Master Orchestrator Agent"]
    
    subgraph SubAgents["Specialized Sub-Agents"]
        Orchestrator <--> DocumentAgent["Doc & Verification Agent"]
        Orchestrator <--> ProvisioningAgent["IT & Access Agent"]
        Orchestrator <--> RAGAgent["Knowledge & Policy RAG Agent"]
        Orchestrator <--> SurveyAgent["Check-in & Sentiment Agent"]
    end
    
    subgraph Integrations["Tools & Third-Party Integrations"]
        DocumentAgent --> OCR["OCR & Form Validator"]
        DocumentAgent --> DocuSign["DocuSign / HelloSign API"]
        ProvisioningAgent --> HRIS["HRIS: Workday / BambooHR / Rippling"]
        ProvisioningAgent --> IdP["Identity: Okta / Azure AD / Google Workspace"]
        ProvisioningAgent --> IT["Jira Service Desk / Slack Workspace API"]
        RAGAgent --> VectorDB[("Vector DB: Hybrid Search")]
        SurveyAgent --> Notifier["Email / Messenger Notification API"]
    end

    subgraph Storage["Persistence & Memory"]
        Orchestrator <--> Postgres[("PostgreSQL: Session State & Audit Logs")]
        Orchestrator <--> Redis[("Redis: Conversation Memory & Cache")]
    end
```

---

### 2.2 LangGraph Orchestrator Decision Loop & State Machine

This diagram illustrates how incoming messages are evaluated by the Master Orchestrator, routed to domain agents, or escalated to HR Administrators if confidence is low.

```mermaid
flowchart TD
    Start([Incoming Employee Message]) --> PIIRedact["1. Scrub PII (Presidio)"]
    PIIRedact --> LoadState["2. Load Session State from Redis/Postgres"]
    LoadState --> IntentClassify{"3. Intent & Confidence Check"}
    
    IntentClassify -->|"High Confidence (Policy Q&A)"| RAGPath["Route to Knowledge & Policy Agent"]
    IntentClassify -->|"High Confidence (Upload/Form)"| DocPath["Route to Document Verification Agent"]
    IntentClassify -->|"High Confidence (Access Request)"| ITPath["Route to IT Provisioning Agent"]
    IntentClassify -->|"High Confidence (Survey Response)"| SurveyPath["Route to Sentiment Agent"]
    IntentClassify -->|"Low Confidence (< 0.75) / Sensitive"| HITLPath["Escalate to HR Admin (HITL)"]
    
    RAGPath --> RAGExecute["Execute Hybrid RAG Search"]
    DocPath --> OCRExecute["Execute Multimodal OCR & Verification"]
    ITPath --> ITExecute["Execute System API Call (Okta/Jira)"]
    SurveyPath --> SentimentExecute["Analyze Sentiment Score"]
    
    RAGExecute --> FormatOutput["Synthesize Grounded Response"]
    OCRExecute --> FormatOutput
    ITExecute --> FormatOutput
    SentimentExecute --> FormatOutput
    
    HITLPath --> HRNotify["Send Alert to HR Admin Workspace"]
    HRNotify --> HRApprove{"HR Approval"}
    HRApprove -->|"Approved / Override"| FormatOutput
    HRApprove -->|"Rejected"| RejectMsg["Send Explanation to Employee"]
    
    FormatOutput --> UpdateState["Update State & Audit Log"]
    RejectMsg --> UpdateState
    UpdateState --> SendResponse([Deliver Response to Employee])
```

---

## 3. Core Agent Components & Detailed Flowcharts

### 3.1 Document Verification & Compliance Workflow

Automates the collection, optical character recognition (OCR), signature check, and HRIS filing of mandatory documents (e.g., W-4, I-9, Direct Deposit, NDA).

```mermaid
flowchart TD
    SubStep1([Employee Uploads Document Image/PDF]) --> SafetyCheck["Scan for Malware & Viruses"]
    SafetyCheck --> OCRTool["Multimodal Vision/OCR Extraction"]
    
    OCRTool --> DocTypeCheck{"Document Type Identified?"}
    DocTypeCheck -->|"Unknown/Illegible"| FailResubmit["Notify Employee: File Unreadable, Request Re-upload"]
    
    DocTypeCheck -->|"Identified (e.g. W-4 / ID)"| FieldCheck{"Required Fields Present?"}
    FieldCheck -->|"Missing Signature / Expiry Date"| FlagMissing["Notify Employee: Missing Required Fields"]
    
    FieldCheck -->|"All Fields Valid"| MaskSens["Mask SSN & Bank Account in Storage"]
    MaskSens --> ESignTrigger["Trigger DocuSign E-Signature if needed"]
    ESignTrigger --> UploadHRIS["Save to HRIS (Workday / BambooHR)"]
    UploadHRIS --> MarkComplete["Update Onboarding Checklist -> Completed"]
    MarkComplete --> SuccessMsg([Notify Employee: Document Verified])
```

---

### 3.2 Automated IT & System Provisioning Workflow

Triggers system account setup, software access grants, and hardware dispatch immediately after offer acceptance or pre-boarding approval.

```mermaid
flowchart TD
    Trigger([HRIS Event: New Hire Hired]) --> FetchRole["Fetch Job Template & Role Metadata"]
    FetchRole --> IdPTask["1. Provision Identity Account (Okta / Azure AD)"]
    
    IdPTask --> ParallelTasks{"Execute Parallel Provisioning"}
    
    ParallelTasks -->|"Software Licenses"| SlackGroup["Add to Dept Slack Channels & Google Groups"]
    ParallelTasks -->|"SaaS Access"| SaaSGrant["Grant Role-Based License (GitHub, Figma, Jira)"]
    ParallelTasks -->|"Hardware Order"| JiraTicket["Create Hardware Order Ticket in Jira Service Desk"]
    
    SlackGroup --> VerifyStatus["Check Provisioning Status"]
    SaaSGrant --> VerifyStatus
    JiraTicket --> VerifyStatus
    
    VerifyStatus --> StatusCheck{"All Services Active?"}
    StatusCheck -->|"Yes"| SendCreds["Generate Temporary Credentials & Welcome Packet"]
    StatusCheck -->|"Failure / Timeout"| AlertIT["Alert IT Helpdesk for Manual Override"]
    
    SendCreds --> CompleteIT([Deliver Credentials securely via Encrypted Portal])
```

---

### 3.3 Knowledge & Policy RAG Pipeline Workflow

Provides accurate, halluncination-free policy answers with exact document citations using a hybrid retrieval-augmented generation pipeline.

```mermaid
flowchart LR
    UserQuery([Employee Question]) --> Rewrite["1. Query Rewriter & HyDE"]
    Rewrite --> DualSearch["2. Hybrid Retrieval"]
    
    subgraph HybridRetrieval["Hybrid Search Engine"]
        DualSearch --> DenseSearch["Dense Vector Search (Qdrant)"]
        DualSearch --> SparseSearch["Sparse Keyword Search (BM25)"]
    end
    
    DenseSearch --> Combine["Reciprocal Rank Fusion (RRF)"]
    SparseSearch --> Combine
    
    Combine --> Reranker["3. Cohere Reranker v3 (Top 3 Chunks)"]
    Reranker --> RBACFilter["4. Role & Region Metadata Filter"]
    
    RBACFilter --> LLMGen["5. LLM Synthesis (GPT-4o / Claude 3.5)"]
    LLMGen --> CitationCheck["6. Grounding & Citation Check"]
    CitationCheck --> FinalAnswer([Deliver Response with Source Links])
```

---

### 3.4 Proactive Sentiment & Check-in Milestone Workflow

Initiates scheduled milestone pulse surveys (Day 1, 7, 30, 60, 90) and automatically escalates blocker issues or negative sentiment.

```mermaid
flowchart TD
    CronTrigger([Cron Scheduler: Milestone Reached]) --> CheckStage{"Onboarding Day?"}
    
    CheckStage -->|"Day 1"| Day1Survey["Trigger Day 1 Orientation Pulse"]
    CheckStage -->|"Day 7"| Day7Survey["Trigger Week 1 Equipment & Team Pulse"]
    CheckStage -->|"Day 30"| Day30Survey["Trigger Month 1 Goal & Manager Sync Survey"]
    CheckStage -->|"Day 90"| Day90Survey["Trigger Probation Completion Survey"]
    
    Day1Survey --> CollectResp([Collect Conversational Responses])
    Day7Survey --> CollectResp
    Day30Survey --> CollectResp
    Day90Survey --> CollectResp
    
    CollectResp --> SentimentLLM["Analyze Sentiment & Intent (LLM Classifier)"]
    SentimentLLM --> SentimentScore{"Evaluate Sentiment"}
    
    SentimentScore -->|"Positive / Satisfied"| LogPulse["Log Feedback to HR Analytics"]
    SentimentScore -->|"Neutral"| FollowupQ["Send Automated Helpful Follow-up Tip"]
    SentimentScore -->|"Negative / Blocker Detected"| EscalateHR["Raise Urgent HR Alert + Book Manager 1-on-1"]
    
    LogPulse --> EndCheck([Complete Milestone Check])
    FollowupQ --> EndCheck
    EscalateHR --> EndCheck
```

---

## 4. End-to-End Onboarding Lifecycle Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor Employee as New Hire
    participant Agent as HR Onboarding Agent
    participant IdP as Identity Provider (Okta)
    participant HRIS as HRIS (Workday)
    participant RAG as Policy Knowledge Base
    actor HR as HR Admin (Human-in-the-Loop)

    Note over Employee, HR: Phase 1: Pre-boarding (Day -7 to Day 0)
    HRIS->>Agent: Event: New Hire Created (Offer Signed)
    Agent->>IdP: Provision Guest/Pending Account
    Agent->>Employee: Welcome Email + Portal/Chat Link
    Employee->>Agent: Uploads ID & Direct Deposit Form
    Agent->>Agent: OCR Validation & Sanity Check
    alt Document Invalid or Unclear
        Agent->>Employee: Request re-upload with guidelines
    else Document Valid
        Agent->>HRIS: Update Document Status to Completed
    end

    Note over Employee, HR: Phase 2: Day 1 Orientation
    Agent->>Employee: Send Day 1 Checklist & Schedule
    Agent->>IdP: Elevate Account Privileges (Active Status)
    Employee->>Agent: Ask "What is the Wi-Fi password & health plan detail?"
    Agent->>RAG: Query Vector DB (Filter by Employee Region/Role)
    RAG-->>Agent: Relevant Document Chunks + Source Links
    Agent-->>Employee: Answer with citations & next steps

    Note over Employee, HR: Phase 3: Milestone Check-in (Day 30)
    Agent->>Employee: Send 30-Day Check-in Pulse Survey
    Employee->>Agent: Responds with concern ("Struggling to setup dev environment")
    Agent->>Agent: Sentiment Analysis -> Flags "Blocker Detected"
    Agent->>HR: Alert HR & Manager via Slack/Email notification
    HR->>Employee: Schedule 1-on-1 sync
```

---

## 5. Technology Stack & Technical Specifications

| Component | Technology / Library | Selection Rationale |
| :--- | :--- | :--- |
| **Agent Framework** | LangGraph / LangChain | Support for stateful multi-agent graphs, cycles, and HITL interrupts. |
| **LLM Backbone** | GPT-4o / Claude 3.5 Sonnet / Gemini 1.5 Pro | High reasoning capability, structured output generation, function calling. |
| **Vector Database** | Qdrant / Pinecone / PGVector | High throughput hybrid search (sparse + dense) with payload metadata filtering. |
| **Embeddings & Reranking** | OpenAI `text-embedding-3-large` + Cohere Rerank v3 | Superior contextual retrieval quality for enterprise policy documents. |
| **PII & Safety Guardrails** | Microsoft Presidio + NeMo Guardrails | Anonymize SSN, DOB, bank details before sending prompts to external LLMs. |
| **Chat Interfaces** | Slack Bolt SDK / Microsoft Bot Framework | Deep enterprise integration into existing employee communication channels. |
| **Backend & Orchestration** | FastAPI (Python 3.11+) / Celery / Redis | Async execution of long-running workflows and webhooks. |
| **Database & Cache** | PostgreSQL (JSONB) + Redis | Persistent state snapshotting, user session management, rate limiting. |
| **Observability** | LangSmith / Phoenix Arize / OpenTelemetry | Tracing agent step-by-step reasoning, latency, cost, and hallucination monitoring. |

---

## 6. Prompt Engineering & Agent System Prompts

### 6.1 Master Orchestrator System Prompt
```text
You are the HR Onboarding Master Orchestrator Agent for [Company Name].
Your goal is to guide new hires through a seamless onboarding experience.

CORE RULES:
1. Maintain a welcoming, professional, and helpful tone.
2. Route specific requests to specialized sub-agents:
   - Policy/Benefits/FAQs -> Knowledge & Policy Agent
   - Form submission/Tax/ID upload -> Document Verification Agent
   - Account setup/Software access -> IT Provisioning Agent
3. NEVER guess or invent company policy. Rely exclusively on the Knowledge Agent.
4. If the user expresses distress, frustration, or asks questions outside your scope, transfer control to a Human HR Representative.

CURRENT USER CONTEXT:
- Name: {user_name}
- Role: {user_role}
- Department: {user_department}
- Start Date: {start_date}
- Current Onboarding Stage: {onboarding_stage}
```

### 6.2 Knowledge & Policy RAG Prompt
```text
You are the Policy & Knowledge Expert Agent for [Company Name].
Answer the user's question using ONLY the provided context snippets below.

CONTEXT SNIPPETS:
{context_chunks}

INSTRUCTIONS:
1. Base your answer strictly on the provided context. If the information is not contained in the context, state: "I don't have this information in the official policy docs. I've flagged this for your HR Manager."
2. Always include document title and page/section references in your response.
3. Keep answers clear, structured (bullet points), and action-oriented.
4. Mask any personal data.
```

---

## 7. Security, Privacy & Compliance Architecture

### 7.1 PII Protection & Data Anonymization
- **Inbound Sanitization**: Every user message passes through an anonymization pipeline using **Microsoft Presidio**.
- **PII Scrubbing**: SSNs, Tax Identification Numbers, Banking Details, DOBs, and Phone Numbers are replaced with pseudo-tokens (e.g., `[REDACTED_SSN]`) before LLM invocation.

### 7.2 Security Control Matrix Flow

```mermaid
flowchart LR
    UserQuery["User Input"] --> PIIFilter["1. PII Redaction Filter"]
    PIIFilter --> GuardrailCheck["2. Topic & Injection Guard"]
    GuardrailCheck --> AgentCore["3. Multi-Agent Engine"]
    AgentCore --> RBACFilter["4. Role-Based Access Filter"]
    RBACFilter --> ResponseGen["5. LLM Synthesis"]
    ResponseGen --> OutputGuard["6. Safety Check"]
    OutputGuard --> FinalOutput["Delivered Response"]
```

---

## 8. Evaluation, Metrics & Governance (LLM Evals)

### 8.1 RAG Evaluation Framework (RAG Triad)
1. **Context Relevance**: Measures if retrieved document chunks match the new hire's query. Target: \( \ge 0.90 \).
2. **Groundedness (Faithfulness)**: Ensures generated answers contain zero hallucinations and originate strictly from retrieved policy documents. Target: \( \ge 0.98 \).
3. **Answer Relevance**: Evaluates whether the final response directly addresses the user's inquiry. Target: \( \ge 0.92 \).

### 8.2 Operational Success Metrics (KPIs)

| Metric | Baseline (Manual) | Target (AI Agent) | Measurement Method |
| :--- | :--- | :--- | :--- |
| **First-Day IT Readiness** | 65% ready on Day 1 | 98% ready on Day 1 | Account & privilege activation checks |
| **Average Onboarding Ticket Time** | 24 Hours | < 2 Minutes | HRIS & Slack bot resolution logs |
| **Form Completion Rate (Day 3)** | 70% | 100% | HRIS compliance tracking |
| **New Hire CSAT (Day 30)** | 3.8 / 5.0 | 4.7 / 5.0 | Automated Sentiment Check-in Agent |
| **HR Admin Hours Saved / Hire** | 0 Hours | 8 Hours saved | Time-tracking & workload metrics |

---

## 9. Implementation Roadmap & Phased Rollout

```mermaid
gantt
    title HR Onboarding Agent Implementation Roadmap
    dateFormat  YYYY-MM-DD
    section Phase 1: Foundation
    Requirements & Knowledge Ingestion  :p1_1, 2026-10-01, 14d
    RAG Pipeline & Vector DB Setup     :p1_2, after p1_1, 14d
    Slack/Teams Interface MVP           :p1_3, after p1_2, 14d
    section Phase 2: Agentic Tooling
    Document OCR & Form Agent           :p2_1, after p1_3, 21d
    IT Provisioning (Okta/Jira APIs)    :p2_2, after p2_1, 21d
    Human-in-the-Loop Admin Dashboard   :p2_3, after p2_2, 14d
    section Phase 3: Advanced Workflows
    LangGraph Multi-Agent Orchestrator  :p3_1, after p2_3, 21d
    Scheduled Check-in & Sentiment Agent:p3_2, after p3_1, 14d
    Security Audit & PII Hardening      :p3_3, after p3_2, 14d
    section Phase 4: Production & Scale
    Pilot Rollout (50 New Hires)        :p4_1, after p3_3, 30d
    Full Enterprise Deployment          :p4_2, after p4_1, 30d
```

---

## 10. Summary & Conclusion
The proposed HR Onboarding Agent architecture combines stateful multi-agent orchestration with enterprise-grade RAG, automated tool execution, and strict security controls. By visualizing every stage from document verification to IT provisioning and milestone sentiment analysis, this document provides a complete blueprint for building a high-touch, error-free onboarding platform.
