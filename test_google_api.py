"""
Diagnostic script to verify Google API key and check available models.
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file")
    print("\nSteps to fix:")
    print("1. Go to: https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Add to .env file: GOOGLE_API_KEY=your_key_here")
    exit(1)

print("✓ GOOGLE_API_KEY found\n")
print(f"Key preview: {api_key[:20]}...{api_key[-10:]}\n")

# Try to import and list models
try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    print("Attempting to list available models...\n")
    models = genai.list_models()
    
    gemini_models = []
    for model in models:
        if "gemini" in model.name.lower():
            gemini_models.append(model.name)
            print(f"  • {model.name}")
    
    if gemini_models:
        print(f"\n✓ Found {len(gemini_models)} Gemini model(s)")
        print(f"\nRecommended model: {gemini_models[0]}")
    else:
        print("\n⚠ No Gemini models found")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure:")
    print("1. API key is valid")
    print("2. Generative AI API is enabled")
    print("3. Your billing is set up")
