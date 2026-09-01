"""
Simple script to make LLM calls with OpenAI SDK (without LangChain).
Uses openai package directly.
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables.\n"
        "Add it to your .env file:\n"
        "OPENAI_API_KEY=your_key_here\n\n"
        "Get your key from: https://platform.openai.com/account/api-keys"
    )

client = OpenAI(api_key=api_key)


def simple_call():
    """Example 1: Simple LLM call."""
    print("=== Simple LLM Call ===")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "What is the capital of France?"}
        ]
    )
    print(f"Response: {response.choices[0].message.content}\n")


def streaming_call():
    """Example 2: Streaming response."""
    print("=== Streaming Response ===")
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")


def multi_turn_conversation():
    """Example 3: Multi-turn conversation."""
    print("=== Multi-turn Conversation ===")
    messages = []
    
    # First turn
    messages.append({"role": "user", "content": "What are the benefits of machine learning?"})
    response1 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    assistant_response1 = response1.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_response1})
    
    print(f"User: What are the benefits of machine learning?")
    print(f"Assistant: {assistant_response1}\n")
    
    # Second turn (context maintained)
    messages.append({"role": "user", "content": "How is it used in healthcare?"})
    response2 = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    assistant_response2 = response2.choices[0].message.content
    
    print(f"User: How is it used in healthcare?")
    print(f"Assistant: {assistant_response2}\n")


def with_json_response():
    """Example 4: Get structured JSON response using JSON mode."""
    print("=== Structured JSON Response (JSON Mode) ===")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "Is Python a good language for AI development? Respond in JSON format with 'answer' and 'confidence' keys."
            }
        ],
        response_format={"type": "json_object"}
    )
    
    response_text = response.choices[0].message.content
    print(f"Response: {response_text}")
    
    try:
        json_response = json.loads(response_text)
        print(f"Parsed JSON: {json.dumps(json_response, indent=2)}\n")
    except json.JSONDecodeError:
        print("Could not parse as JSON\n")


def with_system_instruction():
    """Example 5: Use system instruction."""
    print("=== With System Instruction ===")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a Python expert. Answer all questions about Python programming."
            },
            {
                "role": "user",
                "content": "What is a list comprehension?"
            }
        ]
    )
    print(f"Response: {response.choices[0].message.content}\n")


def with_temperature_control():
    """Example 6: Control temperature for creativity."""
    print("=== Temperature Control ===")
    
    # Creative response (high temperature)
    print("Creative (temperature=1.0):")
    response_creative = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Write a short poem about programming."}
        ],
        temperature=1.0
    )
    print(response_creative.choices[0].message.content)
    
    # Deterministic response (low temperature)
    print("\nDeterministic (temperature=0.1):")
    response_deterministic = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Write a short poem about programming."}
        ],
        temperature=0.1
    )
    print(response_deterministic.choices[0].message.content + "\n")


def with_gpt4():
    """Example 7: Use GPT-4 model."""
    print("=== GPT-4 Call ===")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Explain the concept of recursion in programming."}
            ]
        )
        print(f"Response: {response.choices[0].message.content}\n")
    except Exception as e:
        print(f"GPT-4 not available: {e}\n")


if __name__ == "__main__":
    try:
        simple_call()
        streaming_call()
        multi_turn_conversation()
        with_json_response()
        with_system_instruction()
        with_temperature_control()
        with_gpt4()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
