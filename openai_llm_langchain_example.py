"""
Simple script to make LLM calls with OpenAI API over LangChain.
Supports GPT-4, GPT-3.5-turbo, and other OpenAI models.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI LLM
def get_llm(model="gpt-3.5-turbo"):
    """Initialize and return the OpenAI model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables.\n"
            "Add it to your .env file:\n"
            "OPENAI_API_KEY=your_key_here\n\n"
            "Get your key from: https://platform.openai.com/account/api-keys"
        )
    
    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        temperature=0.7,
        max_tokens=1000
    )
    return llm


def simple_call():
    """Example 1: Simple LLM call."""
    print("=== Simple LLM Call ===")
    llm = get_llm()
    response = llm.invoke("What is the capital of France?")
    print(f"Response: {response.content}\n")


def chain_call():
    """Example 2: LLM call with prompt template and chain."""
    print("=== Chain with Prompt Template ===")
    llm = get_llm()
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_template(
        "You are a helpful AI assistant. Answer the following question:\n{question}"
    )
    
    # Create a chain
    chain = prompt | llm | StrOutputParser()
    
    # Invoke the chain
    response = chain.invoke({"question": "Explain quantum computing in simple terms."})
    print(f"Response: {response}\n")


def multi_turn_conversation():
    """Example 3: Multi-turn conversation."""
    print("=== Multi-turn Conversation ===")
    llm = get_llm()
    
    messages = [
        ("human", "What are the benefits of machine learning?"),
        ("ai", "Machine learning has many benefits: automation, pattern recognition, "
               "predictive analytics, and continuous improvement."),
        ("human", "How is it used in healthcare?")
    ]
    
    # Convert to LangChain message objects
    formatted_messages = []
    for role, content in messages:
        if role == "human":
            formatted_messages.append(HumanMessage(content=content))
        else:
            formatted_messages.append(AIMessage(content=content))
    
    response = llm.invoke(formatted_messages)
    print(f"Response: {response.content}\n")


def with_json_response():
    """Example 4: Get structured JSON response."""
    print("=== Structured JSON Response ===")
    llm = get_llm()
    
    prompt = ChatPromptTemplate.from_template(
        """Answer the following question and respond in JSON format with 'answer' and 'confidence' keys.
Question: {question}"""
    )
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "question": "Is Python a good language for AI development?"
    })
    print(f"Response: {response}\n")


def with_gpt4():
    """Example 5: Use GPT-4 model."""
    print("=== GPT-4 Call ===")
    try:
        llm = get_llm(model="gpt-4")
        response = llm.invoke("Write a haiku about programming.")
        print(f"Response: {response.content}\n")
    except Exception as e:
        print(f"GPT-4 not available: {e}\n")


if __name__ == "__main__":
    try:
        # Run examples
        simple_call()
        chain_call()
        multi_turn_conversation()
        with_json_response()
        with_gpt4()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
