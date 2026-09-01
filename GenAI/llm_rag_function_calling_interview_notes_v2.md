# LLM, RAG, Function Calling & Evaluation --- Interview Preparation

> **Purpose:** Interview-ready notes that explain the topic simply
> first, then go deeper into the technical reasoning, trade-offs,
> examples, and likely follow-up questions.

> ## How to answer in the interview
>
> **Do not give the whole document as your first answer.** Start with
> the "Interview Answer" section. If the interviewer asks **"why?",
> "how?", "internally?", "what if it fails?", or "what are the
> trade-offs?"**, move into the deeper sections.
>
> **Simple question → short answer. Design question → detailed answer.**
> The goal is to sound clear and knowledgeable, not to dump everything
> you know at once.

------------------------------------------------------------------------

# 1. Temperature in LLMs

**Answer type: 🟢 Short --- usually 20--60 seconds**

## ⚡ Interview Answer

> **Temperature controls how predictable or varied an LLM's output is.**
> A lower temperature makes the model more likely to choose the
> highest-probability tokens, so the answer is more consistent. A higher
> temperature gives lower-probability tokens more chance of being
> selected, so the answer can be more varied or creative.

That is normally enough for the first answer. Do not immediately go into
the mathematics unless the interviewer asks.

## 🧠 Easy Explanation

Think of the LLM as having several possible choices for the next word.

For example, after:

``` text
"The capital of France is ..."
```

the model may internally consider:

``` text
Paris      → very likely
London     → unlikely
Rome       → very unlikely
```

Temperature changes **how strongly the model prefers the most likely
choice**.

-   **Low temperature:** stay close to the safest/highest-probability
    choices.
-   **High temperature:** allow more variation in the choices.

So, in simple words:

``` text
Low temperature  → predictable / consistent
High temperature → diverse / creative
```

## 🔬 Technical Explanation --- Only If Asked

The model produces logits for possible next tokens. A simplified version
of the temperature operation is:

``` text
P(token) = softmax(logits / T)
```

`T` is the temperature.

-   Lower `T` makes the probability distribution sharper.
-   Higher `T` makes it flatter.

The exact supported range and behavior can depend on the model/API.

## 🎯 When Would I Use It?

  Situation              General direction   Why
  ---------------------- ------------------- -------------------------------
  Classification         Low                 We usually want consistency
  Data extraction        Low                 We want stable output
  Structured responses   Low                 Less variation is useful
  Coding                 Often lower         Consistency is usually useful
  Brainstorming          Higher              We want more alternatives
  Creative writing       Higher              Variation is useful

These are guidelines, not universal rules.

## ❓ Common Follow-ups

### Does temperature make the model smarter?

**No.** It does not add knowledge or retrain the model. It changes how
the model samples from the probabilities it has produced.

### Does temperature eliminate hallucinations?

**No.** Lower temperature can reduce variation, but hallucination is a
broader problem involving the model, prompt, retrieval, grounding, and
validation.

### What should I say if asked about temperature = 0?

Say:

> "It is intended to make generation highly deterministic by strongly
> favoring the highest-probability choice, although the exact behavior
> depends on the API and decoding implementation."

## 📝 Remember

> **Temperature is mainly about output randomness/variation, not model
> intelligence.**

# 2. Top-K and Top-P

**Answer type: 🟢 Short --- usually 30--60 seconds**

## ⚡ Interview Answer

> **Top-K and Top-P are token-sampling controls. Top-K keeps only the K
> most probable next tokens. Top-P keeps the smallest group of tokens
> whose combined probability reaches a chosen threshold.**
>
> The easiest difference to remember is: **Top-K = fixed number of
> candidates; Top-P = probability-based number of candidates.**

## 🧠 Easy Example

Suppose the model gives these probabilities:

``` text
A → 50%
B → 25%
C → 15%
D → 7%
E → 3%
```

### Top-K = 3

Keep the three most likely choices:

``` text
A, B, C
```

The number of candidates is fixed at 3.

### Top-P = 0.90

Keep tokens until their probabilities add up to about 90%:

``` text
A              = 50%
A + B          = 75%
A + B + C      = 90%
```

So the candidates are again:

``` text
A, B, C
```

But the important difference is what happens when the probability
distribution changes.

## 🔍 Why Top-P Is Different

If the model is very confident:

``` text
A = 95%
B = 2%
C = 1%
D = 1%
E = 1%
```

With `Top-P = 0.90`, `A` alone already covers the threshold.

If the model is uncertain:

``` text
A = 30%
B = 25%
C = 20%
D = 15%
E = 10%
```

With `Top-P = 0.90`, several tokens are needed.

So Top-P can **adapt to how confident the model is**.

## ⚖️ Difference

                      Top-K              Top-P
  ------------------- ------------------ --------------------------------------
  What is limited?    Number of tokens   Cumulative probability
  Candidate count     Fixed              Variable
  Example             Keep top 10        Keep tokens covering 90% probability
  Easy memory trick   **K = count**      **P = probability**

## 🔄 Temperature vs Top-K/Top-P

They solve related but different problems:

``` text
Model scores/logits
       ↓
Temperature changes probability distribution
       ↓
Top-K / Top-P remove unlikely candidates
       ↓
Sampling chooses the next token
```

Exact ordering and supported controls depend on the model/provider.

## 🎯 Use Cases

You do not normally need to discuss all three controls unless asked
about decoding.

-   **Top-K:** useful when you want a hard limit on the candidate count.
-   **Top-P:** useful when you want the candidate set to adapt to the
    probability distribution.

## 📝 Remember

> **Top-K = K best candidates. Top-P = smallest candidate set covering
> probability P.**

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

**Answer type: 🟡 Medium --- usually 1--2 minutes**

## ⚡ Interview Answer

> "I would not rely only on a prompt saying 'return JSON'. I would use a
> structured-output or schema mechanism supported by the model/API, and
> then validate the result in application code. If validation fails, I
> would retry, repair where safe, or return a controlled error. For CSV,
> I would often generate validated structured data first and let the
> application convert it to CSV."

## 🧠 Why Is This Needed?

Suppose another application expects:

``` json
{
  "employee_name": "John",
  "leave_balance": 12
}
```

If the model returns:

``` text
Sure! Here is the information:

{ "employee_name": "John", "leave_balance": 12 }
```

it may look fine to a human, but a strict machine parser may reject it.

More importantly, we also need to check whether:

-   Required fields are present
-   Types are correct
-   Values are valid
-   Unexpected fields were added

## 🏗️ Better Flow

``` text
LLM
 ↓
Structured output / schema
 ↓
Parse
 ↓
Validate
 ↓
Valid?
 ├── Yes → Application
 └── No  → Retry / Repair / Controlled error
```

## 📋 Example Schema

``` json
{
  "type": "object",
  "properties": {
    "employee_name": { "type": "string" },
    "leave_balance": { "type": "integer" }
  },
  "required": ["employee_name", "leave_balance"],
  "additionalProperties": false
}
```

Where the model/provider supports schema-constrained structured output,
prefer it over a prompt-only instruction.

## 📊 What About CSV?

For reliable systems, a safer approach is often:

``` text
LLM
 ↓
Validated JSON / structured data
 ↓
Application
 ↓
CSV
```

The application can then control column order, escaping, headers, and
missing values.

## 🎯 Key Principle

> **The LLM can propose structured data; the application should enforce
> the contract.**

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

**Answer type: 🟢 Short --- usually 30--60 seconds**

## ⚡ Interview Answer

> **Function calling allows an LLM to request execution of a predefined
> function or tool using structured arguments. The LLM normally does not
> execute the function itself. The application receives the request,
> validates it, executes the tool, and sends the result back to the
> model.**

## 🧠 Easy Explanation

Think of the LLM as the **decision-maker**, and the application as the
**executor**.

For example, we give the model a tool:

``` text
get_employee_leave_balance(employee_id)
```

The user asks:

> "How many leaves do I have?"

The model may request:

``` json
{
  "name": "get_employee_leave_balance",
  "arguments": {
    "employee_id": "E123"
  }
}
```

The application then actually calls the function and gets:

``` json
{
  "annual_leave": 12,
  "sick_leave": 8
}
```

The result is given back to the LLM, which can turn it into a normal
answer.

## 🔄 Simple Flow

``` text
User
 ↓
LLM
 ↓
Tool/function request
 ↓
Application validates request
 ↓
Application executes tool
 ↓
Tool result
 ↓
LLM
 ↓
Final answer
```

## ❗ Important

Function calling is **not the same as giving the LLM direct access to
your database**.

The application should remain in control of:

-   Validation
-   Authorization
-   Tool execution
-   Error handling
-   Returned data

## 📝 Remember

> **LLM chooses/request the tool; application executes and controls the
> tool.**

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

**Answer type: 🟢 Short --- usually 30--60 seconds**

## ⚡ Interview Answer

> "The model is given the available tools along with their descriptions
> and input schemas. It compares the user's request with those tool
> definitions and decides whether a tool is useful and which tool best
> matches the intent and required parameters."

## 🧠 Easy Example

Suppose we provide:

``` text
get_weather(location)
get_employee_leave(employee_id)
create_support_ticket(title, description)
```

User asks:

> "How many leaves do I have?"

The model identifies the intent as **retrieving a leave balance** and
selects:

``` text
get_employee_leave()
```

It then produces the required arguments according to the tool schema.

## 🔐 Very Important: Tool Choice ≠ Permission

The model choosing a tool does **not** mean the user is authorized to
use it.

For example, the model might request:

``` text
get_salary(employee_id="E999")
```

The application must still check:

``` text
Is this user allowed to access E999's salary?
```

So the safe flow is:

``` text
LLM chooses tool
       ↓
Application validates arguments
       ↓
Authorization check
       ↓
Execute tool
```

## 📝 Remember

> **The LLM can decide what tool is useful; the application decides
> whether and how that tool is actually executed.**

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

**Answer type: 🔴 Detailed --- this is a system/evaluation question**

## ⚡ Interview Opening Answer

> "I would evaluate retrieval independently from generation. I would
> create a ground-truth dataset where each question is mapped to the
> document or chunks that contain the required information. Then I would
> run the retriever and check whether those relevant chunks appear in
> the top K results. I would use metrics such as Recall@K, Precision@K,
> MRR and nDCG, depending on what matters for the application."

## 🧠 Why Evaluate Retrieval Separately?

Suppose the final answer is wrong.

There are at least two very different possibilities:

``` text
Wrong answer
   │
   ├── Correct information was NOT retrieved
   │       → Retrieval problem
   │
   └── Correct information WAS retrieved
           → Generation/grounding problem
```

If we only measure the final answer, we cannot easily tell which
component failed.

------------------------------------------------------------------------

# 32. Retrieval Evaluation Dataset

Create test cases such as:

``` json
{
  "question": "How many annual leaves can be carried forward?",
  "relevant_chunks": [
    "leave-policy-carry-forward"
  ]
}
```

For questions where several chunks are required:

``` json
{
  "question": "What is the production incident process?",
  "relevant_chunks": [
    "incident-policy-1",
    "incident-policy-3"
  ]
}
```

This is our **ground truth** --- what a good retrieval system should
ideally find.

------------------------------------------------------------------------

# 33. Run the Retriever

For every test question:

``` text
Question
 ↓
Retriever
 ↓
Top K chunks
```

Then compare:

``` text
Expected relevant chunks
        VS
Retrieved chunks
```

Example:

``` text
Expected: A, B

Retrieved Top 5:
A, C, D, B, E
```

We found both A and B, so recall is good for this example. But C, D and
E may be unnecessary, which affects precision.

------------------------------------------------------------------------

# 34. Recall@K

## Easy Meaning

> **Recall@K asks: "Did I find the important information within my first
> K results?"**

Formula:

``` text
Recall@K =
Relevant items retrieved in top K
---------------------------------
Total relevant items
```

Example:

Expected relevant chunks:

``` text
A, B, C, D
```

Top 5 retrieved:

``` text
A, B, X, Y, Z
```

Relevant retrieved = 2.

``` text
Recall@5 = 2 / 4 = 50%
```

### Why is Recall important?

If the correct chunk never reaches the LLM:

``` text
Retriever misses information
        ↓
LLM never sees it
        ↓
LLM cannot reliably use it
```

So retrieval recall is particularly important when missing information
causes incorrect answers.

------------------------------------------------------------------------

# 35. Precision@K

## Easy Meaning

> **Precision@K asks: "Of the K things I retrieved, how many were
> actually relevant?"**

Example:

Top 5:

``` text
A, B, X, Y, Z
```

Only A and B are relevant.

``` text
Precision@5 = 2 / 5 = 40%
```

High precision means less irrelevant context is being sent downstream.

------------------------------------------------------------------------

# 36. Recall vs Precision

The easiest way to remember the difference:

``` text
Recall
→ Did I miss important information?

Precision
→ Did I retrieve too much irrelevant information?
```

Think about searching a library:

-   **Recall:** Did I find all the books I needed?
-   **Precision:** How many of the books I found were actually useful?

------------------------------------------------------------------------

# 37. Why We Need Both

### High recall, low precision

We find almost everything, but also retrieve lots of irrelevant content.

Problems:

-   More tokens
-   Higher cost
-   More noise
-   More difficult context selection

### High precision, low recall

The retrieved content is very relevant, but we may miss a critical piece
of information.

Problems:

-   The LLM never gets the missing evidence.

So we want a practical balance rather than maximizing one metric
blindly.

------------------------------------------------------------------------

# 38. Other Retrieval Metrics

## MRR --- Mean Reciprocal Rank

MRR focuses on **how high the first relevant result appears**.

``` text
First relevant result at rank 1 → 1/1 = 1.0
First relevant result at rank 2 → 1/2 = 0.5
First relevant result at rank 5 → 1/5 = 0.2
```

Across several questions, we average these values.

It is useful when getting at least one strong result near the top is
important.

## nDCG

nDCG is useful when relevance has **different levels**, rather than
simply relevant/irrelevant.

For example:

``` text
3 → Highly relevant
2 → Relevant
1 → Somewhat relevant
0 → Irrelevant
```

It rewards highly relevant results appearing near the top.

------------------------------------------------------------------------

# 39. Retrieval Evaluation vs Generation Evaluation

### Retrieval asks:

> **Did we find the right evidence?**

Typical metrics:

-   Recall@K
-   Precision@K
-   MRR
-   nDCG

### Generation asks:

> **Did the LLM use that evidence correctly?**

Possible dimensions:

-   Faithfulness / groundedness
-   Answer relevance
-   Correctness
-   Citation correctness

This separation makes debugging much easier.

------------------------------------------------------------------------

# 40. Example --- Debugging a Bad RAG Answer

Question:

> "How many annual leaves can I carry forward?"

Expected chunk:

``` text
leave-policy-carry-forward
```

Retriever returns:

``` text
leave-policy-eligibility
leave-policy-encashment
leave-policy-holidays
```

The answer is wrong.

First check:

> **Was the correct chunk retrieved?**

If no:

> Retrieval is the problem.

If yes, but the model still answers incorrectly:

> The problem is more likely in context construction, grounding, or
> generation.

------------------------------------------------------------------------

# 41. Evaluation Dashboard

For a production RAG system, I would track several categories:

``` text
Retrieval:
  Recall@K
  Precision@K
  MRR / nDCG

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

The exact metrics depend on the business requirement.

------------------------------------------------------------------------

# 42. 🎯 Strong Interview Answer

> "I would first build a representative evaluation dataset with
> questions and ground-truth relevant chunks. Then I would evaluate the
> retriever independently using Recall@K to see whether important
> evidence is found, Precision@K to measure how much irrelevant content
> is included, and MRR or nDCG to evaluate ranking quality. After
> retrieval is validated, I would separately evaluate the generated
> answer for faithfulness, relevance and correctness. This separation
> helps us identify whether a bad answer came from retrieval or from the
> generation stage."

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
