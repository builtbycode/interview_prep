<!-- OpenAI LLM with LangChain Setup Guide -->

## Setup Instructions

### 1. Install Required Packages

```bash
pip install langchain-openai langchain python-dotenv
```

### 2. Get OpenAI API Key

1. Go to [OpenAI API Platform](https://platform.openai.com/account/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy your API key

### 3. Create `.env` File

In the project root, create a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

⚠️ **Important**: The `.env` file is in `.gitignore` - your API key won't be committed.

### 4. Run the Script

```bash
python GenAI/openai_llm_langchain_example.py
```

## Script Features

- **Simple Call**: Direct LLM invocation
- **Chain with Prompt Template**: Structured prompts
- **Multi-turn Conversation**: Maintain conversation history
- **Structured Responses**: JSON output parsing
- **Model Selection**: Switch between GPT-3.5, GPT-4, etc.

## Available Models

| Model | Cost | Speed | Reasoning |
|-------|------|-------|-----------|
| `gpt-3.5-turbo` | 💰 Lowest | ⚡ Fastest | Basic |
| `gpt-4` | 💰💰💰 High | 🐢 Slower | Excellent |
| `gpt-4-turbo` | 💰💰 Medium | ⚡ Fast | Excellent |
| `gpt-4o` | 💰💰 Medium | ⚡ Fast | Best |

## Using Different Models

```python
# GPT-3.5 Turbo (default, cheapest)
llm = get_llm("gpt-3.5-turbo")

# GPT-4 (best reasoning)
llm = get_llm("gpt-4")

# GPT-4 Turbo (faster, cheaper than GPT-4)
llm = get_llm("gpt-4-turbo-preview")
```

## Cost Tracking

Monitor your usage:
```bash
# Check your usage at:
# https://platform.openai.com/account/usage/overview
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `OPENAI_API_KEY not found` | Add key to `.env` file |
| `ModuleNotFoundError` | Run `pip install langchain-openai` |
| `RateLimitError` | Add delays between requests or upgrade plan |
| `InvalidRequestError: model not found` | Model not available for your account |
| `AuthenticationError` | Check API key validity |
