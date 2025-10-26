"""
Test script to verify if your Gemini API key is valid
Run this locally to test your API key before deploying
"""

import google.generativeai as genai
from config import config

print("=" * 60)
print("GEMINI API KEY VALIDATOR")
print("=" * 60)

# Display API key (masked for security)
api_key = config.GEMINI_API_KEY
if api_key and api_key != "your_gemini_api_key_here":
    masked_key = api_key[:10] + "..." + api_key[-4:]
    print(f"[OK] API Key found: {masked_key}")
else:
    print("[ERROR] API Key not configured!")
    print("Please add GEMINI_API_KEY to your .env file")
    exit(1)

print("\nTesting API connection...")

try:
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Test with a simple request
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    response = model.generate_content("Say 'Hello, API is working!'")
    
    print("\n[SUCCESS] API Key is valid and working!")
    print(f"Response: {response.text}")
    print("\n" + "=" * 60)
    print("Your API key is configured correctly!")
    print("=" * 60)
    
except Exception as e:
    print("\n[FAILED] API Key test failed!")
    print(f"Error: {str(e)}")
    print("\n" + "=" * 60)
    print("POSSIBLE SOLUTIONS:")
    print("=" * 60)
    print("1. Check if your API key is correct")
    print("2. Generate a new API key at:")
    print("   https://aistudio.google.com/app/apikey")
    print("3. Make sure API key has Generative AI permissions")
    print("4. Check if you have billing enabled (if required)")
    print("5. Make sure the API key is for Gemini API (not other Google APIs)")
    print("=" * 60)
    exit(1)

