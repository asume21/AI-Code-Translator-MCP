"""
Test client for the AI Code Translator Simple MCP Server

This script demonstrates how to interact with the simple MCP server API
for code translation and chat functionality.
"""

import requests
import json

API_URL = "http://127.0.0.1:5000"
API_KEY = "test_api_key_1"
HEADERS = {"X-API-Key": API_KEY}

def translate_code(source_code, source_lang="python", target_lang="javascript"):
    """
    Translate code from source language to target language.
    """
    print(f"Translating {source_lang} to {target_lang}...")
    
    try:
        response = requests.post(
            f"{API_URL}/translate",
            headers=HEADERS,
            json={
                "source_code": source_code,
                "source_language": source_lang,
                "target_language": target_lang
            }
        )
        response.raise_for_status()
        result = response.json()
        
        print("\n=== Translated Code ===")
        print(result["translated_code"])
        
        if "feedback" in result and result["feedback"]:
            print("\n=== Translation Feedback ===")
            print(result["feedback"])
            
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def main():
    # Sample Python code to translate
    python_code = """
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
        
# Print the first 10 Fibonacci numbers
for i in range(10):
    print(fibonacci(i))
"""
    
    # Translate the code
    translate_code(python_code, "python", "javascript")

if __name__ == "__main__":
    main()
