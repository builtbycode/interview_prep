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

## 2. System Architecture

### 2.1 Multi-Agent Architecture Overview
The system uses a **Stateful Graph Multi-Agent Architecture** (e.g., built with **LangGraph** or **AutoGen**). A central **Orchestrator Agent** manages state transitions, delegates sub-tasks to specialized domain agents, and coordinates Human-in-the-Loop (HITL) reviews.

```mermaid
graph TD
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

## 3. Core Agent Components & Responsibilities

### 3.1 Master Orchestrator Agent
- **Function**: Interprets user intent, maintains long-term onboarding session state, and routes queries to sub-agents.
- **State Machine**: Tracks employee progress across onboarding phases:
  `PRE_BOARDING` → `DAY_1` → `WEEK_1` → `DAY_30` → `DAY_60` → `DAY_90_COMPLETED`.
- **Human-in-the-Loop (HITL)**: Escalates to HR Admin when confidence score falls below threshold (\( \text{Confidence} < 0.75 \)) or when sensitive requests are initiated.

### 3.2 Document Verification & Compliance Agent
- **Function**: Collects, validates, and archives required legal and tax documents (e.g., W-4, I-9, Direct Deposit, NDA).
- **Capabilities**:
  - Uses multimodal OCR to verify uploaded document validity (e.g., checks expiration date, signature presence).
  - Integrates with DocuSign/HelloSign for electronic signing.
  - Automatically flags incomplete or illegible documents and requests resubmission.

### 3.3 IT & Access Provisioning Agent
- **Function**: Executes API calls to provision hardware, software, and communication tools.
- **Capabilities**:
  - Triggers Okta/Azure AD account creation based on job role templates.
  - Automatically adds user to relevant Slack/Teams channels and Google Groups.
  - Creates hardware request tickets in Jira Service Desk / ServiceNow.

### 3.4 Knowledge & Policy RAG Agent
- **Function**: Provides instant, grounded answers to employee questions about benefits, company policies, vacation, culture, and tech stack.
- **Capabilities**:
  - Performs **Hybrid Search** (Dense Embeddings + BM25 Sparse Keyword matching).
  - Employs **Re-ranking** (e.g., Cohere Rerank) to prioritize authoritative HR documents.
  - Strict grounding prompt ensures citations are included and prevents hallucination.

### 3.5 Check-in & Sentiment Agent
- **Function**: Proactively initiates scheduled pulse check-ins and gathers feedback.
- **Capabilities**:
  - Triggers automated surveys on Day 1, 7, 30, 60, and 90.
  - Analyzes sentiment (Positive, Neutral, Negative, At-Risk) and alerts HR managers if negative sentiment or blocker issues are detected.

---

## 4. End-to-End Onboarding Lifecycle Flow

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
| **Backend & Orchestration** | FastApi (Python 3.11+) / Celery / Redis | Async execution of long-running workflows and webhooks. |
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

### 7.2 Security Control Matrix
```mermaid
graph LR
    UserQuery[User Input] --> PIIFilter[1. PII Redaction Filter]
    PIIFilter --> GuardrailCheck[2. Topic & Prompt Injection Guard]
    GuardrailCheck --> AgentCore[3. Multi-Agent Engine]
    AgentCore --> RBACFilter[4. Role-Based Retrieval Filter]
    RBACFilter --> ResponseGen[5. LLM Response Generation]
    ResponseGen --> OutputGuard[6. Output Safety Check]
    OutputGuard --> FinalOutput[Delivered Response]
```

- **Role-Based Access Control (RBAC)**: Vector DB queries enforce metadata filters (e.g., `department == "Engineering" AND location == "US"`). An engineer cannot view executive compensation policies or region-inapplicable benefits documents.
- **Audit Logging**: Immutable audit trail stored in PostgreSQL documenting all tool calls, document submissions, and state transitions for compliance audits (SOC2 Type II, GDPR, HIPAA).

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
The proposed HR Onboarding Agent architecture combines stateful multi-agent orchestration with enterprise-grade RAG and strict security controls. By automating manual overhead while maintaining human oversight for critical touchpoints, the system delivers a high-touch, error-free onboarding journey for new employees.
