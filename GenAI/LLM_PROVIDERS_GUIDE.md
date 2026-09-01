# LLM Providers with LangChain

Quick reference for using Google Generative AI and OpenAI with LangChain.

## Side-by-Side Comparison

| Feature | Google (Gemini) | OpenAI (GPT) |
|---------|-----------------|--------------|
| **API Key** | `GOOGLE_API_KEY` | `OPENAI_API_KEY` |
| **Free Tier** | ✅ Yes (limited) | ❌ No (credits needed) |
| **Models** | Gemini Pro, Vision | GPT-3.5, GPT-4, GPT-4o |
| **Speed** | Fast | Fast |
| **Cost** | Low | Variable |
| **Best For** | Rapid prototyping | Production apps |

## Installation

```bash
# For both providers
pip install -r requirements_llm_providers.txt

# Or individual packages
pip install langchain-openai        # OpenAI only
pip install langchain-google-genai  # Google only
```

## Quick Start

### Google Generative AI

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
response = llm.invoke("Hello!")
```

Setup guide: [GOOGLE_LANGCHAIN_SETUP.md](GOOGLE_LANGCHAIN_SETUP.md)  
Example script: [google_llm_langchain_example.py](google_llm_langchain_example.py)

### OpenAI

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=api_key)
response = llm.invoke("Hello!")
```

Setup guide: [OPENAI_LANGCHAIN_SETUP.md](OPENAI_LANGCHAIN_SETUP.md)  
Example script: [openai_llm_langchain_example.py](openai_llm_langchain_example.py)

## Running Examples

```bash
# Run Google examples
python google_llm_langchain_example.py

# Run OpenAI examples
python openai_llm_langchain_example.py
```

## Environment Setup

Create `.env` file in project root:

```
GOOGLE_API_KEY=your_google_key_here
OPENAI_API_KEY=your_openai_key_here
```

Both will be protected by `.gitignore`.

## Common Patterns

### Switching Providers

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

provider = os.getenv("LLM_PROVIDER", "openai")

if provider == "google":
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
else:
    llm = ChatOpenAI(model="gpt-3.5-turbo")
```

### Cost-Effective Development

- **Development**: Use Google Gemini (free tier) or OpenAI GPT-3.5-turbo
- **Production**: Use OpenAI GPT-4 or GPT-4o for better quality

### Rate Limiting

```python
import time
from langchain.schema import HumanMessage

for prompt in prompts:
    response = llm.invoke(HumanMessage(content=prompt))
    time.sleep(1)  # Rate limit: 1 second between requests
```

## Troubleshooting

### API Key Issues
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("YOUR_API_KEY")
assert api_key, "API key not found in .env"
```

### Model Not Found
Check available models in:
- OpenAI: https://platform.openai.com/docs/models
- Google: https://ai.google.dev/

### Cost Monitoring
- **OpenAI**: https://platform.openai.com/account/usage/overview
- **Google**: https://makersuite.google.com/app/billing

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Google AI Studio](https://makersuite.google.com/)
