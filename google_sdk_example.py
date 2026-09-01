"""
Simple script to make LLM calls with Google Generative AI SDK (without LangChain).
Uses google-generativeai package directly.
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure Google API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables.\n"
        "Add it to your .env file:\n"
        "GOOGLE_API_KEY=your_key_here\n\n"
        "Get your key from: https://makersuite.google.com/app/apikey"
    )

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3.6-flash")


def simple_call():
    """Example 1: Simple LLM call."""
    print("=== Simple LLM Call ===")
    response = model.generate_content("What is the capital of France?")
    print(f"Response: {response.text}\n")


def streaming_call():
    """Example 2: Streaming response."""
    print("=== Streaming Response ===")
    response = model.generate_content("Explain quantum computing in simple terms.", stream=True)
    for chunk in response:
        print(chunk.text, end="", flush=True)
    print("\n")


def multi_turn_conversation():
    """Example 3: Multi-turn conversation using chat."""
    print("=== Multi-turn Conversation ===")
    chat = model.start_chat(history=[])
    
    # First turn
    response1 = chat.send_message("What are the benefits of machine learning?")
    print(f"User: What are the benefits of machine learning?")
    print(f"Assistant: {response1.text}\n")
    
    # Second turn (context maintained)
    response2 = chat.send_message("How is it used in healthcare?")
    print(f"User: How is it used in healthcare?")
    print(f"Assistant: {response2.text}\n")


def with_json_response():
    """Example 4: Get structured JSON response."""
    print("=== Structured JSON Response ===")
    prompt = """Answer the following question and respond in valid JSON format with 'answer' and 'confidence' keys.
Question: Is Python a good language for AI development?

Respond with only valid JSON, no other text."""
    
    response = model.generate_content(prompt)
    print(f"Response: {response.text}\n")
    
    # Try to parse as JSON
    try:
        json_response = json.loads(response.text)
        print(f"Parsed JSON: {json.dumps(json_response, indent=2)}\n")
    except json.JSONDecodeError:
        print("Could not parse as JSON\n")


def with_system_instruction():
    """Example 5: Use system instruction."""
    print("=== With System Instruction ===")
    model_with_instruction = genai.GenerativeModel(
        "gemini-2.5-flash",
        system_instruction="You are a Python expert. Answer all questions about Python programming."
    )
    
    response = model_with_instruction.generate_content("What is a list comprehension?")
    print(f"Response: {response.text}\n")


def with_temperature_control():
    """Example 6: Control temperature for creativity."""
    print("=== Temperature Control ===")
    
    # Creative response (high temperature)
    print("Creative (temperature=1.0):")
    response_creative = model.generate_content(
        "Write a short poem about programming.",
        generation_config=genai.types.GenerationConfig(temperature=1.0)
    )
    print(response_creative.text)
    
    # Deterministic response (low temperature)
    print("\nDeterministic (temperature=0.1):")
    response_deterministic = model.generate_content(
        "Write a short poem about programming.",
        generation_config=genai.types.GenerationConfig(temperature=0.1)
    )
    print(response_deterministic.text + "\n")


if __name__ == "__main__":
    try:
        simple_call()
        streaming_call()
        multi_turn_conversation()
        with_json_response()
        with_system_instruction()
        with_temperature_control()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
