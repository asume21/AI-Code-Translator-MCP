"""
Test client for the AI Code Translator MCP Server

This script demonstrates how to interact with the simplified MCP server API
for code translation and chat functionality.
"""

import requests
import json
import argparse

API_URL = "http://localhost:8000"
API_KEY = "test_api_key_1"  # Use one of the keys from api_keys.json
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

def chat_with_ai(message):
    """
    Chat with the AI assistant.
    """
    print(f"Sending message: {message}")
    
    try:
        response = requests.post(
            f"{API_URL}/chat",
            headers=HEADERS,
            json={"message": message}
        )
        response.raise_for_status()
        result = response.json()
        
        print("\n=== AI Response ===")
        print(result["response"])
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def list_models():
    """
    List available models.
    """
    try:
        response = requests.get(
            f"{API_URL}/models",
            headers=HEADERS
        )
        response.raise_for_status()
        result = response.json()
        
        print("\n=== Available Models ===")
        for model in result["models"]:
            print(f"ID: {model['id']}")
            print(f"Name: {model['name']}")
            print(f"Description: {model['description']}")
            print()
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def list_languages():
    """
    List supported languages.
    """
    try:
        response = requests.get(
            f"{API_URL}/languages",
            headers=HEADERS
        )
        response.raise_for_status()
        result = response.json()
        
        print("\n=== Supported Languages ===")
        for lang in result["languages"]:
            print(f"{lang['id']}: {lang['name']}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="AI Code Translator MCP Client")
    parser.add_argument("--action", type=str, choices=["translate", "chat", "list-models", "list-languages"], 
                        default="translate", help="Action to perform")
    parser.add_argument("--source-lang", type=str, default="python", help="Source language")
    parser.add_argument("--target-lang", type=str, default="javascript", help="Target language")
    parser.add_argument("--code-file", type=str, help="File containing code to translate")
    parser.add_argument("--message", type=str, help="Message for chat")
    args = parser.parse_args()
    
    if args.action == "translate":
        if not args.code_file:
            # Use a sample code if no file is provided
            source_code = """
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
        else:
            try:
                with open(args.code_file, "r") as f:
                    source_code = f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        
        translate_code(source_code, args.source_lang, args.target_lang)
    
    elif args.action == "chat":
        message = args.message or input("Enter your message: ")
        chat_with_ai(message)
    
    elif args.action == "list-models":
        list_models()
    
    elif args.action == "list-languages":
        list_languages()

if __name__ == "__main__":
    main()
