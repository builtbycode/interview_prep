# LLM, RAG, Function Calling & Evaluation --- Interview Preparation

> **Purpose:** Interview-ready notes that explain the topic simply
> first, then go deeper into the technical reasoning, trade-offs,
> examples, and likely follow-up questions.

------------------------------------------------------------------------

# 1. Temperature in LLMs

## ⚡ Interview Quick Summary

### What is temperature?

**Temperature controls how random or predictable an LLM's next-token
selection is.**

-   **Low temperature** → more deterministic and focused output.
-   **High temperature** → more varied and creative output.
-   Temperature does **not** directly make the model more intelligent.
-   It changes how the model converts its predicted token probabilities
    into the final selection.

### One-line interview answer

> Temperature controls the randomness of token selection: lower values
> make the output more deterministic, while higher values make it more
> diverse.

------------------------------------------------------------------------

## 🧠 First Understand the Problem

An LLM does not normally say:

> "I know the answer, so I will definitely choose this word."

Instead, it predicts a probability distribution for the next token.

For example, after:

``` text
"The capital of France is"
```

the model might produce something conceptually like:

  Token      Probability
  -------- -------------
  Paris             0.95
  London            0.01
  Rome             0.005
  Other            0.035

The model then uses a **sampling/decoding strategy** to choose the next
token.

Temperature changes how sharp or flat these probabilities become.

------------------------------------------------------------------------

## 🔬 What Happens Internally?

The model produces **logits** for possible next tokens.

A simplified formula is:

``` text
P(token) = softmax(logits / temperature)
```

More explicitly:

``` text
P(i) = exp(logit_i / T) / Σ exp(logit_j / T)
```

where:

-   `T` = temperature
-   `logit_i` = model's raw score for token `i`

### Low temperature

When `T` is low:

``` text
Probability distribution
        ↓
More concentrated
        ↓
Highest-probability tokens dominate
```

### High temperature

When `T` is high:

``` text
Probability distribution
        ↓
More spread out
        ↓
Lower-probability tokens become more likely
```

------------------------------------------------------------------------

## 📊 Example

Suppose the model predicts:

``` text
A = 0.70
B = 0.20
C = 0.10
```

With a lower temperature, the distribution becomes more concentrated
around `A`.

With a higher temperature, `B` and `C` have a greater chance of being
selected.

The exact probabilities depend on the logits and temperature; the
example is only for intuition.

------------------------------------------------------------------------

## 🎯 Use Cases

### Low temperature

Useful when we want:

-   Factual answers
-   Consistent formatting
-   Classification
-   Data extraction
-   Code generation where consistency matters
-   Structured outputs
-   Reproducible behavior

Typical idea:

``` text
Temperature → Low
```

### Higher temperature

Useful when we want:

-   Brainstorming
-   Creative writing
-   Multiple ideas
-   Alternative phrasings
-   Creative content

------------------------------------------------------------------------

## ❓ Does Temperature Change Model Knowledge?

**No.**

Temperature does not retrain the model or add knowledge.

It changes the **sampling behavior over the model's existing probability
distribution**.

------------------------------------------------------------------------

## ⚠️ Important Interview Point

Do not say:

> "Temperature controls how confident the model is."

A better explanation is:

> "Temperature changes the probability distribution used during
> sampling, which affects how deterministic or diverse the generated
> output is."

------------------------------------------------------------------------

## 🎯 Interview Follow-ups

### What happens at temperature 0?

Conceptually, it makes decoding highly deterministic by strongly
favoring the highest-probability token.

However, exact behavior can depend on the API/provider and decoding
implementation.

### Does higher temperature always produce better answers?

No.

It can increase diversity, but it can also increase variability and the
chance of undesirable output.

### Can temperature fix hallucinations?

Not reliably.

Lower temperature can reduce variability, but hallucination is primarily
a problem of model knowledge, retrieval, prompting, grounding, and
verification.

------------------------------------------------------------------------

# 2. Top-K and Top-P

## ⚡ Interview Quick Summary

### What is Top-K?

**Top-K limits token selection to the K most probable tokens.**

Example:

``` text
K = 3

Candidate tokens:
A  60%
B  25%
C  10%
D   3%
E   2%

Only A, B, C participate in sampling.
```

### What is Top-P?

**Top-P, also called nucleus sampling, chooses the smallest set of
tokens whose cumulative probability reaches P.**

Example:

``` text
A = 60%
B = 25%
C = 10%
D = 3%
E = 2%

P = 0.90

A + B + C = 95%

Therefore A, B, C are candidates.
```

------------------------------------------------------------------------

## ⚖️ Top-K vs Top-P

  -----------------------------------------------------------------------
  Feature                 Top-K                   Top-P
  ----------------------- ----------------------- -----------------------
  Selection basis         Number of tokens        Cumulative probability

  Example                 Keep best 50 tokens     Keep tokens until
                                                  probability reaches 90%

  Candidate count         Fixed K                 Variable

  Adapts to distribution  Less                    More

  Main purpose            Restrict unlikely       Dynamically restrict
                          tokens                  unlikely tokens
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 🧠 Why Top-P Is Interesting

Consider two probability distributions.

### Case A --- Model is confident

``` text
A = 95%
B = 2%
C = 1%
D = 1%
E = 1%
```

With Top-P = 0.90:

``` text
A alone already reaches 95%
```

So the candidate set may contain only `A`.

### Case B --- Model is uncertain

``` text
A = 30%
B = 25%
C = 20%
D = 15%
E = 10%
```

With Top-P = 0.90:

``` text
A + B + C + D = 90%
```

Now four tokens participate.

So **Top-P adapts the candidate set to the model's uncertainty**.

------------------------------------------------------------------------

## 🎯 Use Cases

### Top-K

Useful when we want a hard limit on the number of candidates.

### Top-P

Useful when we want the candidate set to adapt to the probability
distribution.

For many modern generation systems, **Top-P is a common choice**, but
the exact supported controls and recommended settings depend on the
model/provider.

------------------------------------------------------------------------

## 🔄 Temperature + Top-K/Top-P

These are different controls.

Think:

``` text
Model logits
     ↓
Temperature
     ↓
Probability distribution
     ↓
Top-K / Top-P filtering
     ↓
Sampling
     ↓
Next token
```

The exact implementation/order can vary by decoding system, so when
discussing a specific API, check its documented decoding behavior.

------------------------------------------------------------------------

## 🎯 Interview Answer

> "Temperature changes how sharp or flat the probability distribution
> is. Top-K limits sampling to the K highest-probability tokens, while
> Top-P dynamically keeps the smallest group of tokens whose cumulative
> probability reaches P. Top-K gives a fixed candidate count, whereas
> Top-P adapts to the model's confidence."

------------------------------------------------------------------------

# 3. RAG --- Design a System for Employee Questions

## ⚡ Interview Quick Summary

### Question

> Suppose an employee asks a question to a RAG system. How would you
> design it?

### One-line answer

> I would separate the system into ingestion, indexing, query
> understanding, authorization, retrieval, reranking, context
> construction, generation, and evaluation, with access control enforced
> before restricted data is retrieved.

------------------------------------------------------------------------

# 4. 🏗️ High-Level RAG Architecture

``` mermaid
flowchart TD
    A["Employee"] --> B["Question / Query"]

    B --> C["Query Understanding"]

    C --> D["Authentication / Authorization"]

    D --> E["Access Scope"]

    E --> F["Hybrid Retrieval"]

    F --> G["Candidate Chunks"]

    G --> H["Reranker"]

    H --> I["Relevant Context"]

    I --> J["Prompt / Context Builder"]

    J --> K["LLM"]

    K --> L["Structured / Natural Language Answer"]

    L --> M["Citation / Grounding Check"]

    M --> A
```

------------------------------------------------------------------------

# 5. 📥 RAG Ingestion Pipeline

Before an employee asks anything, documents must be prepared.

``` mermaid
flowchart LR
    A["Documents"] --> B["Parse"]
    B --> C["Clean / Normalize"]
    C --> D["Chunk"]
    D --> E["Metadata"]
    E --> F["Embeddings"]
    F --> G["Vector Index"]

    E --> H["Keyword / BM25 Index"]
```

## Step 1 --- Collect documents

Examples:

-   HR policies
-   Engineering documentation
-   Company wiki
-   Product documentation
-   PDFs
-   Internal guides
-   Support documents

## Step 2 --- Parse

Extract useful content while preserving structure.

For example:

``` text
Document
 ├── Title
 ├── Heading
 ├── Paragraph
 ├── Table
 └── Metadata
```

## Step 3 --- Chunk

Break large documents into meaningful pieces.

## Step 4 --- Add metadata

Example:

``` json
{
  "document_id": "HR-123",
  "department": "HR",
  "classification": "restricted",
  "allowed_groups": ["HR", "Managers"],
  "section": "Leave Policy",
  "version": "2026-08"
}
```

## Step 5 --- Create indexes

Use:

-   Vector index for semantic search
-   Keyword/BM25 index for exact terms
-   Metadata filters for authorization and scope

------------------------------------------------------------------------

# 6. 🔎 Query-Time RAG Flow

Suppose an employee asks:

> "How many paid leaves can I carry forward?"

The pipeline could be:

``` text
Employee question
       ↓
Authenticate employee
       ↓
Understand intent
       ↓
Determine allowed data scope
       ↓
Apply authorization filters
       ↓
Retrieve candidate chunks
       ↓
Hybrid search
       ↓
Rerank
       ↓
Build context
       ↓
LLM
       ↓
Grounded answer + citations
```

------------------------------------------------------------------------

# 7. ❗ Restricted vs Unrestricted Questions

This is a critical system-design question.

The first mistake would be:

``` text
Question
   ↓
Retrieve everything
   ↓
Check permissions later
```

This is dangerous.

If restricted information has already been retrieved and passed to the
LLM, we have already exposed it inside the application pipeline.

------------------------------------------------------------------------

# 8. 🔐 Authorization Before Retrieval

Prefer:

``` text
Employee
   ↓
Authentication
   ↓
Identity + roles + attributes
   ↓
Authorization policy
   ↓
Allowed retrieval scope
   ↓
Retrieval
```

For example:

``` text
Employee = E123

Groups:
Engineering
India

Allowed:
Engineering docs
India policies

Not allowed:
HR confidential documents
Executive documents
Other employee records
```

The retrieval layer should enforce the access scope.

------------------------------------------------------------------------

# 9. 🧠 Restricted vs Unrestricted

There are two useful concepts here.

### Unrestricted question

Example:

> "What is REST?"

No employee-specific authorization may be required.

### Restricted question

Example:

> "What is my manager's salary?"

This should require authorization and potentially may not be answerable
at all.

The system should classify or identify the sensitivity of the request
and combine that with the user's permissions.

------------------------------------------------------------------------

# 10. 🛡️ Do Not Rely Only on the LLM for Authorization

Bad design:

``` text
Retrieve restricted data
        ↓
Tell LLM:
"Don't reveal it"
```

The authorization boundary should be enforced by deterministic
application logic.

Better:

``` text
User identity
      +
Authorization policy
      ↓
Allowed document/chunk IDs
      ↓
Retriever
      ↓
Only authorized data
      ↓
LLM
```

The LLM is responsible for **reasoning and generation**, not being the
final security boundary.

------------------------------------------------------------------------

# 11. 🔎 Hybrid Retrieval

For employee questions, I would usually combine:

### Semantic search

Find conceptually similar content.

### Keyword/BM25 search

Useful for:

-   Employee IDs
-   Policy names
-   Product names
-   Error codes
-   Exact terms

### Metadata filtering

Filter by:

-   User
-   Department
-   Geography
-   Security classification
-   Document type
-   Version
-   Tenant

### Reranking

Take the candidates and use a stronger relevance model to identify the
best chunks.

------------------------------------------------------------------------

# 12. 📊 Retrieval Pipeline

``` text
Query
 ↓
Authorization filter
 ↓
 ┌──────────────────┐
 │ Semantic Search   │
 ├──────────────────┤
 │ Keyword Search   │
 └──────────────────┘
 ↓
Merge candidates
 ↓
Reranker
 ↓
Top N chunks
 ↓
Context builder
 ↓
LLM
```

------------------------------------------------------------------------

# 13. 🧩 How to Handle Large Chunks in RAG

## ⚡ Interview Summary

> Don't blindly increase the chunk size. Use hierarchical or semantic
> chunking, retrieve at the appropriate level, and expand only the
> relevant sections when more context is required.

------------------------------------------------------------------------

## Why Large Chunks Are a Problem

Suppose a document contains 20 pages.

A huge chunk might contain:

``` text
Relevant paragraph
+
10 irrelevant paragraphs
+
tables
+
examples
+
unrelated sections
```

This causes:

-   More tokens
-   Higher cost
-   More latency
-   More irrelevant context
-   Potentially weaker model attention

------------------------------------------------------------------------

# 14. ✂️ Better Chunking Strategy

Instead of:

``` text
Every 2,000 tokens
```

use document structure.

``` text
Document
   ↓
Chapter
   ↓
Section
   ↓
Subsection
   ↓
Paragraph
```

For example:

``` text
Employee Handbook
 └── Leave Policy
      ├── Eligibility
      ├── Annual Entitlement
      ├── Carry Forward
      └── Encashment
```

The retrieval unit can be:

``` text
"Carry Forward"
```

rather than the entire Leave Policy.

------------------------------------------------------------------------

# 15. 🧠 Parent-Child Retrieval

A powerful approach is:

``` text
Parent document
      │
      ├── Child chunk 1
      ├── Child chunk 2
      ├── Child chunk 3
      └── Child chunk 4
```

Search using smaller child chunks.

If a child chunk is relevant, retrieve:

``` text
child chunk
+
small amount of parent context
```

This gives precise retrieval without completely losing context.

------------------------------------------------------------------------

# 16. 🔄 Context Expansion

Another approach:

``` text
Initial retrieval
       ↓
Relevant paragraph
       ↓
Need more context?
       ↓
Retrieve surrounding section
```

This is better than always sending the entire document.

------------------------------------------------------------------------

# 17. 🧱 Fixed Format Output --- JSON / CSV

## ⚡ Interview Summary

> Use structured output capabilities such as JSON schema or
> tool/function schemas where supported, validate the response
> programmatically, and retry or repair only when validation fails.

------------------------------------------------------------------------

# 18. JSON Generation

Suppose we need:

``` json
{
  "employee_name": "John",
  "leave_balance": 12,
  "leave_type": "Annual"
}
```

Define the schema:

``` json
{
  "type": "object",
  "properties": {
    "employee_name": {
      "type": "string"
    },
    "leave_balance": {
      "type": "integer"
    },
    "leave_type": {
      "type": "string"
    }
  },
  "required": [
    "employee_name",
    "leave_balance",
    "leave_type"
  ],
  "additionalProperties": false
}
```

Where the model/API supports it, **constrained structured output** is
preferable to merely saying:

> "Please return JSON."

------------------------------------------------------------------------

# 19. 🛡️ Always Validate

Even when structured output is requested:

``` text
LLM
 ↓
JSON parser
 ↓
Schema validation
 ↓
Valid?
 ├── YES → Application
 └── NO → Retry / Repair / Error
```

Use a JSON Schema or equivalent validation mechanism.

------------------------------------------------------------------------

# 20. CSV

CSV is trickier because it is less strongly structured than JSON.

If the downstream system needs reliable machine-readable data, consider:

``` text
LLM
 ↓
Structured JSON
 ↓
Application validation
 ↓
Convert JSON → CSV
```

This is often safer than asking the LLM to directly generate CSV.

------------------------------------------------------------------------

# 21. 🎯 Important Principle

> **The LLM should produce data according to a contract; the application
> should enforce the contract.**

Do not trust natural-language instructions alone.

------------------------------------------------------------------------

# 22. Function Calling in LLMs

## ⚡ Interview Quick Summary

### What is function calling?

Function calling allows an LLM to request execution of a predefined
function/tool using structured arguments.

The LLM usually does **not directly execute the function**.

Instead:

``` text
User
 ↓
LLM
 ↓
Tool/function call request
 ↓
Application
 ↓
Execute function
 ↓
Tool result
 ↓
LLM
 ↓
Final response
```

------------------------------------------------------------------------

# 23. Example

Suppose we expose:

``` json
{
  "name": "get_employee_leave_balance",
  "description": "Get an employee's leave balance",
  "parameters": {
    "employee_id": "string"
  }
}
```

User asks:

> "How many leaves do I have?"

The model might produce conceptually:

``` json
{
  "name": "get_employee_leave_balance",
  "arguments": {
    "employee_id": "E123"
  }
}
```

The application executes:

``` text
get_employee_leave_balance("E123")
```

Then returns:

``` json
{
  "annual_leave": 12,
  "sick_leave": 8
}
```

The LLM can then formulate the final answer.

------------------------------------------------------------------------

# 24. 🔄 Function Calling Sequence Diagram

``` mermaid
sequenceDiagram
    participant U as User
    participant L as LLM
    participant A as Application
    participant T as Tool
    participant D as Database

    U->>L: How many leaves do I have?
    L->>A: Call get_leave_balance(employee_id)
    A->>A: Validate arguments
    A->>T: Execute function
    T->>D: Query employee data
    D-->>T: Leave balance
    T-->>A: Structured result
    A-->>L: Tool result
    L-->>U: You have 12 annual leaves
```

------------------------------------------------------------------------

# 25. 🧠 How Does the LLM Decide Which Function to Call?

The model sees the available tools/functions and their
descriptions/schema.

For example:

``` text
Tools:

get_weather(location)
get_employee_leave(employee_id)
create_ticket(title, description)
```

User asks:

> "How many leaves do I have?"

The model recognizes that:

``` text
Intent = retrieve leave balance
```

and maps it to:

``` text
get_employee_leave()
```

This decision is based on the model's learned reasoning plus the tool
definitions provided in the prompt/API.

------------------------------------------------------------------------

# 26. ❗ Important Clarification

The LLM should **not be treated as the authorization engine**.

Suppose the model calls:

``` text
get_salary(employee_id="E999")
```

The application must still check:

``` text
Does this user have permission?
```

before returning sensitive data.

Correct architecture:

``` text
LLM chooses tool
       ↓
Application validates
       ↓
Authorization
       ↓
Execute
```

------------------------------------------------------------------------

# 27. 🛡️ Validate Function Arguments

Suppose the model returns:

``` json
{
  "employee_id": 12345
}
```

but the function expects:

``` text
string
```

Reject or normalize it according to the contract.

Also validate:

-   Required fields
-   Data types
-   Enum values
-   Length limits
-   Numeric ranges
-   IDs
-   Dates
-   Authorization

------------------------------------------------------------------------

# 28. Partial Function Responses

Suppose the tool returns:

``` json
{
  "annual_leave": 12
}
```

but the expected response is:

``` json
{
  "annual_leave": 12,
  "sick_leave": 8
}
```

Do not let the LLM invent the missing value.

Instead:

``` text
Tool result
 ↓
Validate
 ↓
Missing field
 ↓
Determine whether recoverable
 ├── Call tool again
 ├── Call another tool
 └── Return "data unavailable"
```

The application should distinguish:

``` text
0
```

from:

``` text
unknown / missing
```

------------------------------------------------------------------------

# 29. 🔄 Handling Incorrect Tool Responses

A robust flow:

``` text
LLM tool request
      ↓
Validate arguments
      ↓
Execute tool
      ↓
Validate response schema
      ↓
Valid?
 ├── YES → Return to LLM
 └── NO
       ↓
   Retry / repair / fallback
       ↓
   Still invalid?
       ↓
   Safe error
```

------------------------------------------------------------------------

# 30. 🚨 Never Let the Model Invent Tool Results

Bad:

> Tool failed to return salary → LLM guesses salary.

Good:

> "I couldn't retrieve the salary information because the employee
> record was unavailable."

This is especially important for financial, HR, medical, security, and
operational systems.

------------------------------------------------------------------------

# 31. Evaluation of Retrieved Chunks

## ⚡ Interview Quick Summary

Before evaluating the final generated answer, evaluate retrieval
independently.

The basic question is:

> **Did the retriever return the information that was actually needed?**

A good-looking final answer does not necessarily mean retrieval was
good.

------------------------------------------------------------------------

# 32. Retrieval Evaluation Dataset

Create test cases containing:

``` text
Question
+
Relevant document/chunk IDs
+
Optional expected answer
```

Example:

``` json
{
  "question": "How many annual leaves can be carried forward?",
  "relevant_chunks": [
    "leave-policy-section-4"
  ]
}
```

Now run the retriever and compare:

``` text
Expected relevant chunks
        VS
Retrieved chunks
```

------------------------------------------------------------------------

# 33. Recall@K

### Definition

> **Recall@K measures how much of the relevant information was retrieved
> within the top K results.**

Formula:

``` text
Recall@K =
Relevant items retrieved in top K
---------------------------------
Total relevant items
```

### Example

There are 4 relevant chunks.

Top 5 retrieval results contain 3 of them.

``` text
Recall@5 = 3 / 4 = 0.75
```

So:

``` text
Recall@5 = 75%
```

------------------------------------------------------------------------

# 34. Why Recall Matters in RAG

If the correct chunk never enters the retrieved context:

``` text
Retriever misses information
        ↓
LLM never sees it
        ↓
LLM cannot reliably use it
```

Therefore high retrieval recall is important.

------------------------------------------------------------------------

# 35. Precision@K

### Definition

> **Precision@K measures how much of the retrieved top-K content is
> actually relevant.**

Formula:

``` text
Precision@K =
Relevant items retrieved in top K
---------------------------------
K
```

### Example

Top 5 results contain:

``` text
3 relevant
2 irrelevant
```

Then:

``` text
Precision@5 = 3 / 5 = 0.60
```

So:

``` text
Precision@5 = 60%
```

------------------------------------------------------------------------

# 36. Recall vs Precision

  Metric        Main Question
  ------------- ---------------------------------------------
  Recall@K      Did we find the relevant information?
  Precision@K   How much of what we retrieved was relevant?

Think:

``` text
Recall
"Did I miss anything important?"

Precision
"Did I retrieve too much irrelevant stuff?"
```

------------------------------------------------------------------------

# 37. Why We Need Both

### High recall, low precision

``` text
Retrieve almost everything
```

Problem:

-   Large context
-   More cost
-   More noise
-   Potentially weaker generation

### High precision, low recall

``` text
Retrieve only a few highly relevant chunks
```

Problem:

-   We may miss critical information

The goal is a good balance.

------------------------------------------------------------------------

# 38. Other Retrieval Metrics

### MRR --- Mean Reciprocal Rank

Measures how high the first relevant result appears.

``` text
MRR = average(1 / rank_of_first_relevant_result)
```

If the first relevant chunk is ranked #1:

``` text
score = 1
```

If it is ranked #5:

``` text
score = 0.2
```

Useful when the **first relevant result's position** matters.

------------------------------------------------------------------------

## nDCG

Useful when relevance has different degrees.

For example:

``` text
Highly relevant = 3
Relevant = 2
Somewhat relevant = 1
Irrelevant = 0
```

nDCG rewards putting highly relevant documents near the top.

------------------------------------------------------------------------

# 39. Retrieval Evaluation vs Generation Evaluation

This distinction is important.

### Retrieval evaluation

Ask:

> Did we retrieve the right context?

Metrics:

-   Recall@K
-   Precision@K
-   MRR
-   nDCG

### Generation evaluation

Ask:

> Did the LLM use the retrieved context correctly?

Possible dimensions:

-   Faithfulness
-   Groundedness
-   Answer relevance
-   Correctness
-   Citation correctness

------------------------------------------------------------------------

# 40. End-to-End RAG Evaluation

A complete evaluation pipeline looks like:

``` text
Question
   ↓
Retriever
   ↓
Evaluate retrieval
   ↓
Retrieved context
   ↓
LLM
   ↓
Generated answer
   ↓
Evaluate generation
   ↓
End-to-end quality
```

This separation is important for debugging.

If the answer is wrong, we can ask:

``` text
Was the information missing?
        OR
Was the correct information retrieved
but the LLM used it incorrectly?
```

------------------------------------------------------------------------

# 41. 🧪 Example Debugging Scenario

Question:

> "How many annual leaves can I carry forward?"

Expected relevant chunk:

``` text
leave-policy-4
```

Retriever returns:

``` text
leave-policy-1
leave-policy-2
leave-policy-7
```

The relevant section is missing.

Therefore:

``` text
Retrieval problem
```

Increasing the LLM's intelligence won't necessarily solve it.

------------------------------------------------------------------------

# 42. 📊 Evaluation Dashboard

For a production RAG system, track metrics such as:

``` text
Retrieval:
  Recall@5
  Recall@10
  Precision@5
  MRR
  nDCG

Generation:
  Faithfulness
  Answer relevance
  Correctness

System:
  Latency
  Token usage
  Cost
  Error rate

Security:
  Unauthorized retrieval attempts
  Unauthorized data exposure
```

------------------------------------------------------------------------

# 43. 🎯 Strong Interview Answer --- Complete RAG Design

If asked:

> "Design a RAG system for employee questions."

A strong answer could be:

> "I would start with an ingestion pipeline that parses and cleans
> company documents, performs structure-aware chunking, adds metadata
> such as department, document classification and version, and creates
> both semantic and lexical indexes. At query time, I would authenticate
> the employee and determine their authorization scope before retrieval.
> I would then use hybrid retrieval with metadata filtering, semantic
> search and keyword search, followed by a reranker. The most relevant
> chunks would be assembled into a bounded context and passed to the LLM
> with instructions to answer only from the retrieved evidence and
> provide citations. I'd validate structured outputs where required and
> separately evaluate retrieval using Recall@K, Precision@K, MRR or
> nDCG, followed by generation metrics such as faithfulness and answer
> relevance."

------------------------------------------------------------------------

# 44. 🧠 Interview Follow-up Questions

## Beginner

### What is RAG?

> Retrieval-Augmented Generation combines information retrieval with LLM
> generation so the model can answer using externally retrieved
> information.

### Why use RAG?

> To ground answers in external or changing information without
> requiring the model to memorize all of that information.

### What is a chunk?

> A smaller retrievable unit of a document.

------------------------------------------------------------------------

## Intermediate

### Why use hybrid search?

> Semantic search handles conceptual similarity, while keyword search
> handles exact terms. Combining them improves retrieval robustness.

### Why rerank?

> Initial retrieval is optimized for recall. A reranker can more
> accurately order candidate chunks by relevance before sending them to
> the LLM.

### Why metadata filtering?

> It improves retrieval relevance and, more importantly, can enforce
> access and scope constraints before content reaches the model.

------------------------------------------------------------------------

## Advanced

### How would you prevent unauthorized information leakage?

> Enforce authorization before retrieval, apply document/chunk-level
> access filters, keep the LLM outside the security boundary, and audit
> retrieval and access decisions.

### What if the correct document is huge?

> Use hierarchical/structure-aware chunking, retrieve a relevant child
> chunk, and expand to the parent section only when necessary.

### What if retrieval is correct but the answer is wrong?

> Evaluate generation separately. The issue may be prompt construction,
> context ordering, model reasoning, or failure to ground the answer
> rather than retrieval.

### What if retrieval misses the correct document?

> Improve indexing, chunking, query rewriting, hybrid search, metadata
> filtering, and reranking; then verify with retrieval evaluation
> datasets.

------------------------------------------------------------------------

# 45. 🔥 Architecture Principles to Remember

For interviews, remember these principles:

``` text
1. Retrieval before generation
2. Authorization before retrieval
3. Hybrid retrieval beats blindly relying on one search method
4. Chunk according to meaning/structure, not only token count
5. Rerank before final context construction
6. Validate LLM outputs
7. LLM is not the security boundary
8. Evaluate retrieval separately from generation
9. Never allow the model to invent missing tool data
10. Use iterative/agentic retrieval for complex questions
```

------------------------------------------------------------------------

# 46. 📝 Final Cheat Sheet

## Temperature

``` text
Temperature ↓ → more deterministic
Temperature ↑ → more diverse
```

Controls token probability distribution during decoding.

------------------------------------------------------------------------

## Top-K

``` text
Keep K highest-probability tokens.
```

Fixed candidate count.

------------------------------------------------------------------------

## Top-P

``` text
Keep smallest set whose cumulative probability >= P.
```

Variable candidate count.

------------------------------------------------------------------------

## RAG

``` text
Question
 ↓
Auth
 ↓
Retrieve
 ↓
Rerank
 ↓
Context
 ↓
LLM
 ↓
Answer
```

------------------------------------------------------------------------

## Large Chunks

Use:

``` text
Structure-aware chunking
+
Parent-child retrieval
+
Context expansion
```

------------------------------------------------------------------------

## Fixed JSON

``` text
LLM
 ↓
Schema-constrained output
 ↓
Programmatic validation
 ↓
Application
```

------------------------------------------------------------------------

## Function Calling

``` text
User
 ↓
LLM chooses tool
 ↓
Application validates
 ↓
Authorization
 ↓
Tool executes
 ↓
Result
 ↓
LLM
```

------------------------------------------------------------------------

## Retrieval Metrics

``` text
Recall@K
= How much relevant information did we find?

Precision@K
= How much of what we found was relevant?

MRR
= How high was the first relevant result?

nDCG
= How well were results ranked by graded relevance?
```

------------------------------------------------------------------------

# 🎯 Interview Ready

## One-line answer for the whole topic

> **"For an enterprise LLM system, I would combine controlled decoding,
> code/data-aware retrieval, authorization-aware RAG, structured tool
> calling, strict validation, and separate retrieval and generation
> evaluation rather than relying on the LLM alone."**

## 30-second version

> "For RAG, I would build an ingestion pipeline with structure-aware
> chunking and metadata, then use authorization-aware hybrid retrieval
> followed by reranking and context construction. Restricted data must
> be filtered before retrieval, not after the LLM sees it. For large
> chunks, I'd use hierarchical or parent-child retrieval. For function
> calling and JSON, I'd use schemas and validate both tool arguments and
> results. Finally, I'd evaluate retrieval separately using metrics such
> as Recall@K, Precision@K, MRR and nDCG, and evaluate the generated
> answer for faithfulness and correctness."

## 5 things to remember before the interview

1.  **Temperature = randomness/diversity of decoding.**
2.  **Top-K = fixed number of candidate tokens; Top-P =
    probability-based candidate set.**
3.  **RAG = retrieve the right evidence before asking the LLM to
    generate.**
4.  **Authorization must happen before restricted data is retrieved.**
5.  **Measure retrieval quality separately from generation quality.**

## ⭐ Most important interview mindset

When designing an LLM system, don't say only:

> "We send it to the LLM."

Instead think:

``` text
Who is asking?
      ↓
What are they asking?
      ↓
What are they allowed to see?
      ↓
Where is the information?
      ↓
What is the minimum relevant context?
      ↓
Can the LLM use it correctly?
      ↓
Can we validate the result?
      ↓
How do we measure whether the system works?
```

That reasoning pattern is useful across **RAG, agents, function calling,
enterprise AI, and LLM system-design interviews**.
