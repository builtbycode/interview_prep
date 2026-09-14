# Infosys Strategic Technology Group (STG) — GenAI / Agentic AI Engineer
## End-to-End Interview Prep Guide (Plain Language First, Then Technical Depth)

---

## 1. The Role, In Plain English

Strip away the corporate language and here's what Infosys STG is actually hiring for:

> "Someone who can take a large language model, wrap real engineering around it (APIs, containers, pipelines, monitoring), and ship something a real company can depend on — not just a cool demo in a notebook."

STG is Infosys's internal "special forces" team — **Power Programmers**, tech generalists who get dropped onto the hardest client problems across industries, working out of the **CTO office**. This particular opening sits at the intersection of two hot skill sets: **GenAI/Agentic AI** (the "what") and **production engineering** (the "how it survives contact with real users").

Two-sentence summary you can say out loud in an interview:
*"This role is about building LLM and agent-based systems that go beyond a proof of concept — RAG pipelines, tool-using agents, deployed as real microservices on Azure with Docker/Kubernetes/CI-CD, monitored and governed under Responsible AI standards."*

---

## 2. What Past Candidates & Public Sources Say About This Interview

I researched Infosys/Power Programmer and Infosys GenAI-role interview experiences on Glassdoor, Naukri Code360, GeeksforGeeks, and current (2026) GenAI-specific interview guides. Here's the honest picture — no single public account exists for *this exact* STG posting (it looks fairly new), but the patterns below are consistent and directly useful.

**Process & difficulty (Power Programmer track in general):**
- Glassdoor data on the Power Programmer title puts interview difficulty at roughly 3.6/5 and candidate-reported experience at about 88% positive — notably higher than Infosys's company-wide average (~71.5%). Typical time-to-hire is around 45 days.
- The funnel commonly starts with an online assessment (coding + sometimes MCQs on CS fundamentals), often through the InfyTQ/HackWithInfy pipeline for freshers, or a direct technical screen for experienced/lateral hires like this GenAI posting.
- Live, camera-on technical rounds are standard — you'll be asked to **share your screen and code live**, not just talk theory.
- Candidates consistently mention: 1–2 DSA/coding rounds, at least one deep **project-discussion round** where you must clearly explain your own role and decisions, and a final HR/culture-fit round.

**GenAI/Agentic-specific rounds (from current 2026 Infosys GenAI/Agentic AI Engineer interview guides):**
- Interviewers probe **practical engineering experience over theory** — e.g., "walk me through how you'd design a RAG system for a client with millions of multi-page PDFs with tables and images," not just "define RAG."
- Recurring themes: tokenization mechanics and cost/latency trade-offs, chunking strategy debates, vector index internals (HNSW/IVF), agent tool-calling and state/memory management, and safety around agents executing tool calls on untrusted input.
- Framework fluency (LangChain, LangGraph, LlamaIndex, CrewAI) is checked at the "why did you choose X over Y" level, not just "have you heard of it."
- A recurring senior-round style question: debugging scenarios ("your RAG system keeps retrieving irrelevant chunks — what do you check first?") rather than pure definitions.
- Communication is explicitly evaluated — Infosys is a services company, so interviewers watch for whether you can explain a technical decision to a client/business stakeholder, not just to another engineer.

**Bottom line:** expect a mix of (a) live coding/DSA, (b) deep-dive system design on RAG/agents, (c) rapid-fire concept checks (tokenization, embeddings, guardrails, Docker/K8s basics), and (d) a project walkthrough where *you* pick the story. Since you're prepping with a real project (see Section 6), lean into it hard in that round.

---

## 3. How This Guide Is Organized

Each topic below follows the same pattern:
1. **Plain-language answer** — the analogy version, say this first if the interviewer looks non-technical or wants the "explain it simply" gut check.
2. **Technical answer** — what you say to a senior engineer/architect.
3. **Tiered practice questions** — 🟢 Easy, 🟡 Medium, 🔴 Hard — so you can self-test.

---

## 4. LLM Fundamentals & Tokenization

### Q: What is a large language model, really?
**Plain language:** Imagine the world's most well-read intern who has read a huge chunk of the internet and every book they could get their hands on. They don't "know" facts the way a database does — they've learned the *patterns* of language so well that they can predict, very convincingly, what word should come next given everything said so far. An LLM is that intern, frozen into a giant math function.

**Technical answer:** An LLM is a transformer-based neural network trained to predict the next token in a sequence, conditioned on all previous tokens (autoregressive generation), using self-attention to weigh relationships between tokens regardless of distance. Scale (parameters + training data) is what gives rise to emergent capabilities like few-shot reasoning.

- 🟢 What's the difference between GPT, Claude, Llama, and Mistral at a high level? (Proprietary vs open-weight, different training philosophies, licensing/self-hosting implications.)
- 🟡 Why would you choose an open-source model (Llama/Mistral) over a proprietary API (GPT/Claude) for an enterprise client?
- 🔴 A client needs sub-200ms responses at high volume with strict data-residency requirements — walk through your model-selection decision tree.

### Q: What is tokenization, and why does it matter for cost and quality?
**Plain language:** Think of tokenization like cutting a sentence into LEGO pieces before feeding it to the model — the model doesn't see whole words, it sees these pieces. Some words break into one clean piece; others (rare words, code, non-English text) break into many small, awkward pieces. More pieces = more cost, more chance the model "loses the thread" on long inputs.

**Technical answer:** Tokenizers (commonly Byte-Pair Encoding or WordPiece) split text into subword units from a fixed vocabulary. This affects both **cost** (you're billed per token) and **behavior** (models handle rare tokens, code punctuation, or non-Latin scripts less efficiently, and long token counts eat into the context window).

- 🟢 What's the difference between a token and a word?
- 🟡 Why does JSON or code sometimes consume more tokens than plain prose of similar length?
- 🔴 How would you redesign a prompt template to cut token usage 30% for a classification task without hurting accuracy?

### Q: What is context window management and why can't you just "add more context"?
**Plain language:** The context window is like a whiteboard of fixed size — you can only fit so much before you have to erase something to write more. If you cram in too much irrelevant text, the model has to "read" through clutter to find what matters, and quality drops even if it technically fits.

**Technical answer:** Strategies include truncation, sliding windows, hierarchical summarization of older turns, and prompt compression. For RAG specifically, this is why retrieval + re-ranking (not "just paste the whole document") matters — you want to fill the window with only the *highest-value* content.

- 🟢 What happens if you exceed a model's context window?
- 🟡 How would you handle a multi-turn conversation that's grown too long to fit in context?
- 🔴 Design a strategy for an agent that must reason over a 300-page contract with an 8K-token context model.

---

## 5. Prompt Engineering & Guardrails

### Q: What's the difference between prompt engineering and fine-tuning?
**Plain language:** Prompt engineering is like giving a smart new employee very clear instructions for *today's* task. Fine-tuning is like sending that employee through a multi-week training program so their default behavior changes permanently. Prompting is fast and cheap; fine-tuning is slower and more expensive but changes the model's baked-in habits.

**Technical answer:** Prompt engineering shapes model output at inference time (zero-shot, few-shot, chain-of-thought, ReAct-style prompting) with no weight changes. Fine-tuning (full, LoRA, QLoRA) updates model parameters to internalize a domain, tone, or task pattern, useful when prompting alone can't reliably produce the desired style/format at scale.

- 🟢 What's few-shot prompting?
- 🟡 What is ReAct prompting and where is it used?
- 🔴 Your prompt works perfectly in testing but degrades in production with real user inputs — how do you debug it systematically?

### Q: What are "guardrails" in a GenAI system?
**Plain language:** Guardrails are the bumpers in a bowling lane — they don't aim the ball for you, but they stop it from going straight into the gutter. In an AI system, guardrails catch things like the model leaking sensitive data, generating unsafe/off-brand content, or an agent trying to do something destructive.

**Technical answer:** Guardrails span input validation (prompt-injection detection, PII scrubbing), output validation (toxicity/safety classifiers, schema/format validators, hallucination checks against retrieved sources), and action-level guardrails for agents (permission scoping, human-in-the-loop approval for high-risk tool calls, rate limiting).

- 🟢 Name two types of guardrails you'd put on a customer-facing chatbot.
- 🟡 How do you detect and mitigate prompt injection in a RAG pipeline where untrusted documents are part of the context?
- 🔴 Design guardrails for an agent that has "send email" and "execute SQL" as tools, operating on untrusted user input.

---

## 6. RAG & Vector Databases

### Q: Explain RAG like I know nothing about AI.
**Plain language:** RAG is an "open-book exam" for the model. Instead of relying purely on what it memorized during training (which can be outdated or missing your company's private data), the system first goes and *fetches* the most relevant paragraphs from your documents, hands them to the model, and says "answer using this." It's the difference between quizzing someone from memory vs. letting them flip to the right page in a manual first.

**Technical answer:** Retrieval-Augmented Generation combines a retriever (embedding model + vector index) with a generator (LLM). At query time: (1) embed the user query, (2) retrieve top-k semantically similar chunks from a vector store, (3) optionally re-rank, (4) construct a prompt with the retrieved context, (5) generate a grounded answer, ideally with citations back to source chunks.

**RAG pipeline — numbered walkthrough (good for a whiteboard answer):**
1. **Ingest** – pull documents from source systems (SharePoint, DBs, PDFs, APIs).
2. **Chunk** – split into retrievable units (fixed-size, overlapping, semantic, or document-structure-aware).
3. **Embed** – convert each chunk into a vector using an embedding model.
4. **Index** – store vectors + metadata in a vector database (Pinecone, FAISS, Chroma, Azure AI/Cognitive Search).
5. **Retrieve** – on a query, embed it and do a similarity search (often HNSW-based ANN search) to get top-k candidates.
6. **Re-rank (optional but common in production)** – use a cross-encoder to reorder candidates for precision.
7. **Augment prompt** – assemble a prompt with the query + retrieved chunks + instructions.
8. **Generate** – call the LLM to produce a grounded answer.
9. **Post-process** – attach citations, run guardrail/hallucination checks, log for observability.

### Q: What is a vector embedding, and why do we need a special database for it?
**Plain language:** An embedding is like GPS coordinates for *meaning* instead of location. Similar ideas end up near each other in this "meaning space," even if they don't share a single word (e.g., "car" and "automobile" land close together). A vector database is built to answer "what's near this point?" across millions of points, fast — regular SQL databases aren't built for that kind of similarity search at scale.

**Technical answer:** Embeddings are dense numeric vectors from a model trained so that semantic similarity corresponds to geometric closeness (cosine similarity / dot product / Euclidean distance). Vector DBs use approximate nearest neighbor (ANN) indexing — HNSW (graph-based, high recall, more memory) or IVF (cluster-based, more scalable, tunable recall/speed) — to make similarity search sub-linear instead of scanning every vector.

- 🟢 Name three vector database options and one thing that differentiates each (e.g., Pinecone = managed/serverless; FAISS = library you self-host, very fast, no built-in persistence/metadata filtering out of the box; Chroma = lightweight/dev-friendly; Azure AI Search = integrates natively with the Azure/enterprise stack and supports hybrid search).
- 🟡 What's the difference between HNSW and IVF indexing, and when would you pick one over the other?
- 🔴 Your RAG system's retrieval is fast but the *answers* are consistently wrong or irrelevant. Walk through your debugging steps, layer by layer (chunking → embeddings → retrieval → re-ranking → prompt construction → generation).

### Q: How do you chunk documents, and does it actually matter that much?
**Plain language:** Chunking is deciding how you cut up a book before handing pages to someone who can only read a few pages at a time. Cut badly (e.g., mid-sentence, mid-table) and they get confused; cut well (by topic/section) and they can actually answer questions accurately.

**Technical answer:** Common strategies: fixed-character chunking with overlap (simple, fast, but can split ideas awkwardly), document-structure-aware chunking (respect headings/sections), and semantic chunking (split based on sentence-embedding similarity so each chunk stays topically coherent). Overlap (e.g., 10–20%) prevents losing context at chunk boundaries. For tables/images (a known Infosys-guide example scenario), you typically need a separate extraction step (OCR/table-parsing) before chunking, rather than treating them as plain text.

- 🟢 Why do we add overlap between chunks?
- 🟡 How would you chunk a 200-page PDF full of financial tables?
- 🔴 Design a RAG ingestion pipeline for a client with millions of multi-page PDFs containing complex tables and images — this is a real Infosys-reported interview scenario.

---

## 7. Agentic AI & Orchestration

### Q: What's the difference between a chatbot, an LLM pipeline, and an "agent"?
**Plain language:** A chatbot answers questions. A pipeline follows a fixed recipe (step 1, then step 2, then step 3, always the same order). An **agent** is more like a new employee with a toolbox and a goal: it decides *which* tools to use, *in what order*, and *when it's done*, adapting based on what it discovers along the way — it can loop back, retry, or ask for another tool if the first approach doesn't work.

**Technical answer:** Agentic systems give an LLM a loop: observe → reason (plan) → act (call a tool) → observe the result → repeat until a stopping condition. This requires tool/function-calling (structured schemas the model fills in), state/memory management across steps, and often a supervising "orchestrator" to control looping, retries, and handoffs between specialized sub-agents.

- 🟢 What is "tool calling" / "function calling" in the context of an LLM?
- 🟡 How do you keep an agent from looping forever or calling the wrong tool?
- 🔴 Design an agentic system that takes a natural-language request, queries a SQL database, formats results into a CSV, and emails it to a stakeholder — a real reported Infosys interview scenario. (Talk through: intent parsing → tool schema for the SQL query → validation of generated SQL → CSV formatting step → email tool with permission scoping → error handling if the query returns nothing.)

### Q: How do multi-agent systems work, and why not just use one big agent?
**Plain language:** One generalist agent trying to do everything is like one person trying to be the accountant, the lawyer, and the analyst all at once — they'll be mediocre at all three. A multi-agent system is a small team of specialists (each agent has a narrow job) coordinated by a "lead" who delegates and assembles the final answer.

**Technical answer:** Multi-agent architectures decompose a task across specialist agents (e.g., a data-retrieval agent, a risk/compliance agent, a report-writing agent), each with its own tools/prompts, coordinated by an orchestrator that routes tasks and merges results. This improves modularity, testability, and lets you swap/upgrade one agent without touching the rest. Communication between agents needs a defined protocol/contract (message schema, shared state format) so agents built on different frameworks can still interoperate.

- 🟢 Why would you split one big agent into multiple smaller agents?
- 🟡 What state/memory does an orchestrator need to track across a multi-agent workflow?
- 🔴 Two of your agents are built on different frameworks (e.g., one on LangGraph, one on a different agent SDK) — how do you make them talk to each other reliably?

*(This is exactly where you can pull in your own multi-agent project — see Section 9.)*

---

## 8. Frameworks: LangChain, LlamaIndex, Azure OpenAI

### Q: LangChain vs. LlamaIndex vs. just calling the API directly — how do you choose?
**Plain language:** Calling the raw API is like building furniture from scratch — total control, but you rebuild the same wheel every project (memory, retries, chaining). LangChain/LlamaIndex are like a well-stocked workshop with pre-built joints and templates for the common patterns, so you assemble faster — but you inherit their opinions and occasional bloat.

**Technical answer:** Raw API calls make sense for very simple, single-turn use cases where you want minimal dependencies and full control over latency/cost. LangChain is strong for general-purpose chaining, memory, and agent/tool orchestration (and pairs well with LangGraph for explicit, graph-based control flow over agent state). LlamaIndex historically has an edge in data ingestion/indexing ergonomics for RAG-heavy use cases. In an enterprise Azure shop, Azure OpenAI Service gives you the model behind your own compliance boundary (private networking, content filtering, regional data residency), often paired with Azure AI Search for retrieval.

- 🟢 What problem does LangChain solve that raw API calls don't?
- 🟡 Why might a team choose LangGraph specifically over "vanilla" LangChain for an agentic workflow?
- 🔴 You need explicit, auditable control over agent state transitions (for compliance reasons) — which framework choice and why?

---

## 9. Production Engineering: APIs, Docker, Kubernetes, CI/CD

### Q: Why does an LLM feature need Docker and Kubernetes at all — isn't it "just an API call"?
**Plain language:** Docker is a shipping container: it packs your app plus everything it needs to run so it behaves identically on your laptop, in testing, and in production. Kubernetes is the shipping-port operator: it decides how many containers to run, restarts ones that crash, and spreads load across many machines. An LLM-powered service still needs the orchestration and reliability boring "normal" software needs — the AI call is just one component inside it.

**Technical answer:** Docker gives you reproducible, isolated deployment units. Kubernetes provides scheduling, auto-scaling (including scale-to-zero for cost control on bursty AI workloads), self-healing (restarting failed pods), rolling deployments, and secrets management for API keys. CI/CD pipelines automate testing (including prompt-regression tests) and safe rollout of new model versions or prompt changes — critical because a "silent" prompt change can quietly degrade quality in ways unit tests won't catch.

- 🟢 What's the difference between a container and a virtual machine, in one sentence?
- 🟡 How would you design a CI/CD pipeline that also tests for prompt-quality regressions before deploying a change?
- 🔴 Your GenAI microservice needs to handle unpredictable traffic spikes with a cost ceiling — describe your Kubernetes scaling strategy (HPA, resource requests/limits, maybe a queue in front of expensive LLM calls).

### Q: How do you build a scalable API/microservice around an LLM?
**Plain language:** Think of the LLM as the expensive specialist consultant. You don't want every customer talking to them directly and overwhelming them — you build a proper front desk (API layer) that handles requests, queues them sensibly, caches repeat questions, and only calls the consultant when truly needed.

**Technical answer:** Typical stack: a lightweight API framework (FastAPI/Node+Express) exposing REST/streaming endpoints, an async task queue for long-running agent workflows, response streaming (SSE/websockets) for perceived latency, caching (semantic caching for repeated/similar queries), rate limiting, and clean separation between the "orchestration" layer and the "model-serving" layer so you can swap models without rewriting business logic.

- 🟢 Why would you stream a response token-by-token instead of waiting for the full answer?
- 🟡 What is semantic caching and why does it help both cost and latency?
- 🔴 Design the API contract and error-handling strategy for a service where an agent might take 30+ seconds to complete a multi-tool task.

---

## 10. Observability, Reliability & Responsible AI

### Q: How do you monitor something as "fuzzy" as an LLM's output in production?
**Plain language:** With normal software, a bug either crashes the program or it doesn't — easy to see. With an LLM, the code "works" but the *answer* might quietly be wrong, biased, or off-topic. Monitoring an AI system means watching the *quality* of answers over time, not just whether the server is up.

**Technical answer:** Observability for GenAI spans traditional infra metrics (latency, error rate, uptime) plus AI-specific signals: token usage/cost per request, retrieval-hit quality, hallucination rate (checked against source documents), user feedback/thumbs-down rate, drift in output patterns over time, and full request tracing (prompt + retrieved context + response) for debugging and audits. Tools like Ragas, TruLens, and DeepEval formalize this into automated eval suites (faithfulness, answer relevance, context precision/recall) you can run in CI, not just manually.

- 🟢 Name two metrics you'd track for a production RAG system beyond standard latency/uptime.
- 🟡 What is "hallucination rate" and how would you measure it automatically?
- 🔴 Design an evaluation pipeline that runs on every prompt-template change before it ships, using a framework like Ragas or DeepEval.

### Q: What does "Responsible AI compliance" mean in an enterprise context?
**Plain language:** It's the seatbelt-and-airbag layer: making sure the AI system doesn't discriminate, doesn't leak private data, is explainable enough when something goes wrong, and has a human somewhere in the loop for high-stakes decisions.

**Technical answer:** Practically: data privacy (PII handling, redaction, regional residency), bias/fairness testing on outputs, content-safety filtering, audit logging of every AI-driven decision (especially for regulated industries), explainability (surfacing retrieved sources/citations rather than a black-box answer), and human-in-the-loop checkpoints for high-risk actions (financial transactions, medical/legal guidance).

- 🟢 Why is "showing your sources" (citations) a Responsible AI feature, not just a UX nicety?
- 🟡 How do you handle PII that shows up inside documents you're feeding into a RAG pipeline?
- 🔴 A client asks for a fully autonomous agent that can approve refunds up to $500 — where do you insert human-in-the-loop checkpoints and audit logging?

---

## 11. Nice-to-Have Topics (Fine-Tuning, Quantization, Eval Frameworks, Real-Time AI)

### Q: What is fine-tuning, and when is it worth the cost over better prompting?
**Plain language:** If prompting is giving instructions for today's task, fine-tuning is retraining the employee's habits so the *right* behavior becomes their default, even without detailed instructions each time. You reach for it when you need consistent tone/format at scale, or a very specific domain vocabulary the base model keeps getting wrong.

**Technical answer:** LoRA/QLoRA are parameter-efficient fine-tuning techniques that update small adapter matrices instead of the full model, drastically cutting compute/memory cost while capturing most of the benefit for domain adaptation or style/format consistency. Full fine-tuning is reserved for cases needing deeper behavior change and where the ROI justifies the cost.

- 🟢 What's the difference between LoRA and full fine-tuning?
- 🟡 When would you fine-tune instead of just improving your RAG retrieval or prompt?

### Q: What is quantization?
**Plain language:** It's like compressing a high-resolution photo to a smaller file size — you lose a little fine detail, but it's much faster to load and takes far less storage, and often you can't tell the difference in normal use.

**Technical answer:** Quantization reduces the numerical precision of model weights/activations (e.g., FP16 → INT8/INT4, or techniques like AWQ/GPTQ), cutting memory footprint and speeding up inference, with a small, usually acceptable, accuracy trade-off — key for running large models on cheaper hardware or serving more concurrent users per GPU.

- 🟢 Why does quantization make inference cheaper?
- 🟡 What's the risk of quantizing too aggressively?

### Q: What do Ragas, TruLens, and DeepEval actually do?
**Plain language:** They're automated "report cards" for your AI system — instead of a human manually reading 500 answers to judge quality, these frameworks score things like "did the answer actually use the retrieved context" or "is the answer relevant to the question" automatically, so you can catch quality regressions the same way you'd catch a failing unit test.

**Technical answer:** These are LLM-evaluation frameworks that score RAG/agent outputs on dimensions like faithfulness (grounded in retrieved context, i.e., low hallucination), answer relevance, context precision/recall, and can be wired into CI/CD to gate deployments on quality thresholds, not just "does the code compile."

### Q: What's an event-driven / real-time AI system?
**Plain language:** Instead of a user asking a question and waiting for an answer (request/response), the system reacts continuously to a stream of events as they happen — like a security guard watching live camera feeds instead of reviewing yesterday's footage on request.

**Technical answer:** Event-driven AI architectures consume streaming data (Kafka/Event Hubs) and trigger agent reasoning or model inference per event, with attention to low-latency processing, state management across events, and back-pressure handling so the system doesn't fall behind the stream.

---

## 12. Turning Your Own Project Into Interview Gold

You have a genuinely strong, on-the-nose talking point for this exact JD: a **multi-agent investment research system** built with LangGraph/LangChain, Google ADK, the A2A (agent-to-agent) protocol, and Gemini, with a Lead Analyst Orchestrator delegating to five specialist agents (Market Data, Fundamentals, News & Sentiment, Risk & Compliance, Report Writer). This maps almost line-for-line onto the JD:

| JD Requirement | Your Project Evidence |
|---|---|
| "Building multi-step AI agents, tool-calling workflows" | Five-specialist-agent architecture with an orchestrator delegating tasks |
| "GenAI development (GPT, Claude, Llama, Mistral, etc.)" | Hands-on with Gemini AI Pro as the core model |
| "Azure OpenAI, LangChain, LlamaIndex, or similar frameworks" | LangGraph/LangChain for orchestration |
| "Integrate AI solutions with enterprise systems... APIs" | A2A protocol used as a wire-level communication layer; cross-framework interoperability (Google ADK agent talking to LangGraph agents) |
| "Docker, Kubernetes, CI/CD" | Docker/package config delivered as part of the scaffold |
| "Ensure reliability, performance, observability" | Full HLD/LLD documentation with Mermaid/D2/PlantUML diagrams — shows design discipline, not just code |

**How to tell this story in the interview (structure it as: Problem → Architecture → Your specific decisions → What's still in progress):**
1. *Problem:* Investment research requires pulling together market data, fundamentals, sentiment, and compliance checks — too much for one generalist agent to do well.
2. *Architecture:* A Lead Analyst Orchestrator (LangGraph) delegates to five specialists; one agent (Risk & Compliance) was deliberately built on a *different* framework (Google ADK) specifically to prove out cross-framework interoperability via the A2A protocol — a very senior-sounding design decision to mention unprompted.
3. *Your decisions:* Why A2A as the communication layer (standardized, framework-agnostic contracts vs. a single vendor lock-in), why a dedicated orchestrator instead of a flat agent swarm (control, debuggability, clear ownership per task).
4. *Current state, told honestly:* A 63-file scaffold with real contracts, Agent Card JSON, schemas, and Docker/package config exists; some agents are stub implementations, and you're actively working toward a runnable end-to-end demo with the UI. Framing this as "here's my engineering process, and here's what's left" reads as mature, not incomplete — interviewers at this level care more about your reasoning than a finished product.

Practice a **30-second version**, a **2-minute version**, and a **5-minute whiteboard version** of this story — you'll likely need all three at different rounds.

---

## 13. Behavioral / HR Round — Infosys STG Specific

- **"Why Infosys, and why STG specifically?"** — Good angle: STG/Power Programmers is explicitly positioned as the team for people who want to work across the *hardest*, most technically varied problems (not routine delivery work), with PAN-India flexibility and direct exposure to enterprise-scale architecture decisions — that's a genuine draw if you want breadth plus architectural influence rather than a narrow single-stack role.
- **"Tell me about a time you had to learn a new technology quickly."** — Use the Google ADK / A2A protocol adoption in your project (learning a second agent framework specifically to test interoperability) as a concrete, recent example.
- **"Describe a complex problem you solved."** — The cross-framework agent communication problem (getting a LangGraph-based agent and a Google-ADK-based agent to interoperate via a shared protocol) is a strong, specific answer — most candidates will only be able to describe using one framework.
- **"How do you handle ambiguity?"** — Talk about starting with full HLD/LLD documentation before writing implementation code — shows you don't just start coding on a vague spec, you clarify architecture first (a trait the Infosys guides explicitly call out as evaluated: "clarify constraints and assumptions before diving into the solution").
- **"How do you make sure your technical decisions are understandable to non-technical stakeholders?"** — Mention that you documented the system with diagrams (Mermaid/D2/PlantUML) specifically so the architecture is legible to people who won't read code — directly answers Infosys's stated evaluation criterion of "communication & client mindset."

---

## 14. Quick-Revision Cheat Sheet (Say These Out Loud Before the Interview)

- **LLM** = next-token predictor at massive scale, trained on huge text corpora.
- **Tokenization** = text → subword pieces; more/rarer pieces = more cost, less context room.
- **RAG** = retrieve relevant chunks first, then generate a grounded answer — "open-book exam," not memorization.
- **Chunking** = how you cut documents before embedding; bad cuts → bad answers, regardless of model quality.
- **Vector DB** = fast "nearest neighbor in meaning-space" search (HNSW/IVF); Pinecone (managed), FAISS (self-hosted library), Chroma (lightweight/dev), Azure AI Search (enterprise/hybrid search, native Azure integration).
- **Agent** = LLM + tools + a loop (observe → plan → act → observe) that decides its own next step, unlike a fixed pipeline.
- **Multi-agent** = specialist agents + an orchestrator, coordinated via a defined contract/protocol (e.g., A2A).
- **Guardrails** = input/output/action-level safety checks — injection detection, PII scrubbing, output validation, human approval for risky tool calls.
- **Docker** = reproducible packaging; **Kubernetes** = scaling, self-healing, rollout management for those packages.
- **CI/CD for GenAI** = also test for prompt-quality regressions, not just code correctness.
- **Observability for GenAI** = track hallucination rate, retrieval quality, cost/token usage, user feedback — not just uptime/latency.
- **Responsible AI** = privacy, bias checks, explainability/citations, human-in-the-loop for high-stakes actions.
- **Fine-tuning (LoRA/QLoRA)** = change the model's default behavior; reach for it only after prompting/RAG hit their ceiling.
- **Quantization** = compress the model (lower precision) for cheaper/faster inference, small accuracy trade-off.
- **Ragas / TruLens / DeepEval** = automated quality "report cards" for RAG/agent outputs, wireable into CI/CD.

---

## 15. Mini Glossary

| Term | One-line meaning |
|---|---|
| BPE / WordPiece | Algorithms that split text into subword tokens |
| Embedding | Numeric vector representing meaning, used for similarity search |
| HNSW | Graph-based approximate nearest-neighbor search, high recall |
| IVF | Cluster-based approximate nearest-neighbor search, more scalable |
| Re-ranking | Second-pass scoring (often cross-encoder) to improve retrieval precision |
| ReAct prompting | Prompting pattern interleaving reasoning and tool actions |
| MCP | Model Context Protocol — a standard way for models/agents to talk to tools/data sources |
| A2A | Agent-to-Agent protocol — standardized wire-level contract for agents (possibly from different frameworks) to communicate |
| LoRA / QLoRA | Parameter-efficient fine-tuning techniques |
| HPA | Kubernetes Horizontal Pod Autoscaler — scales pods based on load |

---

## 16. Sources Consulted

- Infosys Power Programmers / Strategic Technology Group career page
- Glassdoor — Infosys Power Programmer interview questions & difficulty/experience ratings
- Naukri Code360 — multiple Infosys Power Programmer interview experience write-ups
- GeeksforGeeks — Infosys Power Programmer interview experience
- Dataford.io — Infosys GenAI Engineer, Agentic AI Engineer, and AI Engineer interview guides (2026)
- InterviewBit and Amquest Education — 2026 Generative AI interview question compilations

*Note: no public first-hand account was found for this exact STG posting (it appears to be a newer/less-publicized opening), so Section 2 blends general Power-Programmer-track process patterns with current GenAI/Agentic-role-specific question patterns — treat the process details as "most likely," not guaranteed.*
