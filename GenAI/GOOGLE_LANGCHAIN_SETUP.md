<!-- Google LLM with LangChain Setup Guide -->

## Setup Instructions

### 1. Install Required Packages

```bash
pip install langchain-google-genai langchain python-dotenv
```

### 2. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 3. Create `.env` File

In the project root, create a `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

⚠️ **Important**: The `.env` file is in `.gitignore` - your API key won't be committed.

### 4. Run the Script

```bash
python GenAI/google_llm_langchain_example.py
```

## Script Features

- **Simple Call**: Direct LLM invocation
- **Chain with Prompt Template**: Structured prompts
- **Multi-turn Conversation**: Maintain conversation history
- **Structured Responses**: JSON output parsing

## Available Models

- `gemini-pro` - Text-based model
- `gemini-pro-vision` - Image + text model

## Alternative: Using Vertex AI

If using Google Cloud Vertex AI instead:

```python
from langchain_google_vertexai import ChatVertexAI

llm = ChatVertexAI(model_name="gemini-pro", project="your-project-id")
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GOOGLE_API_KEY not found` | Add key to `.env` file |
| `ModuleNotFoundError` | Run `pip install langchain-google-genai` |
| Rate limit errors | Add delays between requests or upgrade API plan |
