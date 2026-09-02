# LLM SDKs: LangChain vs Native

Comparison of three approaches to LLM calls.

## File Reference

| Approach | File | Use Case |
|----------|------|----------|
| **LangChain + Google** | [google_llm_langchain_example.py](google_llm_langchain_example.py) | Unified interface, chains, LCEL |
| **LangChain + OpenAI** | [openai_llm_langchain_example.py](openai_llm_langchain_example.py) | Unified interface, chains, LCEL |
| **Native Google SDK** | [google_sdk_example.py](google_sdk_example.py) | Direct API, lower overhead |
| **Native OpenAI SDK** | [openai_sdk_example.py](openai_sdk_example.py) | Direct API, lower overhead |

## Feature Comparison

| Feature | LangChain | Native SDK |
|---------|-----------|-----------|
| **Learning Curve** | Steeper (abstractions) | Gentler (direct API) |
| **Flexibility** | Limited (framework constraints) | Full (direct control) |
| **Chaining** | ✅ Built-in LCEL | ❌ Manual |
| **Performance** | Slower (layers) | Faster (direct) |
| **Memory Mgmt** | ✅ Automatic | ❌ Manual |
| **Provider Switch** | ✅ Easy (swap model) | ❌ Rewrite code |
| **Streaming** | ✅ Simple | ✅ Simple |
| **JSON Mode** | Limited | ✅ `response_format` |

## Quick Examples

### LangChain Approach

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
prompt = ChatPromptTemplate.from_template("Explain {topic}")
chain = prompt | llm
response = chain.invoke({"topic": "quantum computing"})
```

### Native Google SDK

```python
import google.generativeai as genai

model = genai.GenerativeModel("gemini-3.6-flash")
response = model.generate_content("Explain quantum computing")
print(response.text)
```

### Native OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(api_key=api_key)
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Explain quantum computing"}]
)
print(response.choices[0].message.content)
```

## When to Use Each

### Use **LangChain** when:
- Building complex multi-step pipelines
- Need provider-agnostic code
- Using advanced features (memory, tools, RAG)
- Working with multiple models together
- Want automatic context management

### Use **Native SDKs** when:
- Simple, direct LLM calls
- Performance is critical
- Need latest SDK features immediately
- Prefer minimal dependencies
- Building lightweight services

## Running the Examples

```bash
# LangChain examples (need GOOGLE_API_KEY or OPENAI_API_KEY)
python google_llm_langchain_example.py
python openai_llm_langchain_example.py

# Native SDK examples
python google_sdk_example.py    # Needs GOOGLE_API_KEY
python openai_sdk_example.py    # Needs OPENAI_API_KEY
```

## Google SDK Features

### Native SDKs Offer

**Streaming:**
```python
response = model.generate_content("prompt", stream=True)
for chunk in response:
    print(chunk.text, end="", flush=True)
```

**Multi-turn Chat:**
```python
chat = model.start_chat(history=[])
response1 = chat.send_message("First question")
response2 = chat.send_message("Follow-up")  # Context preserved
```

**System Instructions:**
```python
model = genai.GenerativeModel(
    "gemini-3.6-flash",
    system_instruction="You are a Python expert"
)
```

**Temperature Control:**
```python
config = genai.types.GenerationConfig(temperature=0.5)
response = model.generate_content("prompt", generation_config=config)
```

## OpenAI SDK Features

**JSON Mode:**
```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[...],
    response_format={"type": "json_object"}
)
```

**Streaming:**
```python
stream = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[...],
    stream=True
)
for chunk in stream:
    print(chunk.choices[0].delta.content, end="")
```

**Model Selection:**
```python
# Easy to switch between models
models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
response = client.chat.completions.create(model=model, ...)
```

## Installation

```bash
# LangChain with both providers
pip install langchain-google-genai langchain-openai

# Or native SDKs only
pip install google-generativeai openai
```

## API Keys

Both approaches need the same environment variables in `.env`:

```
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

The `.gitignore` protects these automatically.

## Recommendations

- **Rapid Prototyping**: LangChain (handles boilerplate)
- **Production APIs**: Native SDKs (simpler, faster)
- **Learning**: Start with native SDK (understand mechanics)
- **Complex Workflows**: LangChain (chains, memory, tools)

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Google Generative AI SDK](https://github.com/google-gemini/generative-ai-python)
- [OpenAI Python Client](https://github.com/openai/openai-python)
