"""
Example client for the AI Code Translator MCP Server

This script demonstrates how to interact with the MCP server API
for code translation, feedback, and chat functionality.
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
    
    Args:
        source_code: The code to translate
        source_lang: The source programming language
        target_lang: The target programming language
        
    Returns:
        Dictionary with translated code and feedback
    """
    try:
        response = requests.post(
            f"{API_URL}/translate",
            headers=HEADERS,
            json={
                "source_code": source_code,
                "source_language": source_lang,
                "target_language": target_lang,
                "use_llm": True
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error translating code: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def get_feedback(source_code, translated_code, source_lang="python", target_lang="javascript"):
    """
    Get feedback on a code translation.
    
    Args:
        source_code: The original code
        translated_code: The translated code
        source_lang: The source programming language
        target_lang: The target programming language
        
    Returns:
        Dictionary with feedback
    """
    try:
        response = requests.post(
            f"{API_URL}/feedback",
            headers=HEADERS,
            json={
                "source_code": source_code,
                "translated_code": translated_code,
                "source_language": source_lang,
                "target_language": target_lang
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting feedback: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def chat_with_ai(message):
    """
    Chat with the AI assistant.
    
    Args:
        message: The message to send
        
    Returns:
        Dictionary with the AI's response
    """
    try:
        response = requests.post(
            f"{API_URL}/chat",
            headers=HEADERS,
            json={"message": message}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error chatting with AI: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def list_models():
    """
    List available models.
    
    Returns:
        Dictionary with available models
    """
    try:
        response = requests.get(
            f"{API_URL}/models",
            headers=HEADERS
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error listing models: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def list_languages():
    """
    List supported languages.
    
    Returns:
        Dictionary with supported languages
    """
    try:
        response = requests.get(
            f"{API_URL}/languages",
            headers=HEADERS
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error listing languages: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Server response: {e.response.text}")
        return None

def main():
    parser = argparse.ArgumentParser(description="AI Code Translator MCP Client")
    parser.add_argument("--action", type=str, choices=["translate", "feedback", "chat", "list-models", "list-languages"], 
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
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Calculate factorial of 5
result = factorial(5)
print(f"Factorial of 5 is {result}")
"""
        else:
            try:
                with open(args.code_file, "r") as f:
                    source_code = f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        
        print(f"Translating from {args.source_lang} to {args.target_lang}...")
        result = translate_code(source_code, args.source_lang, args.target_lang)
        
        if result:
            print("\n=== Translated Code ===")
            print(result["translated_code"])
            print("\n=== Translation Feedback ===")
            print(result["feedback"])
    
    elif args.action == "feedback":
        if not args.code_file:
            print("Please provide a code file with --code-file")
            return
        
        try:
            with open(args.code_file, "r") as f:
                source_code = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
        
        # First translate the code
        translation_result = translate_code(source_code, args.source_lang, args.target_lang)
        if not translation_result:
            return
        
        # Then get feedback
        feedback_result = get_feedback(
            source_code, 
            translation_result["translated_code"],
            args.source_lang,
            args.target_lang
        )
        
        if feedback_result:
            print("\n=== Translation Feedback ===")
            print(feedback_result["feedback"])
    
    elif args.action == "chat":
        message = args.message or input("Enter your message: ")
        result = chat_with_ai(message)
        
        if result:
            print("\n=== AI Response ===")
            print(result["response"])
    
    elif args.action == "list-models":
        models = list_models()
        
        if models:
            print("\n=== Available Models ===")
            for model in models["models"]:
                print(f"ID: {model['id']}")
                print(f"Name: {model['name']}")
                print(f"Description: {model['description']}")
                print()
    
    elif args.action == "list-languages":
        languages = list_languages()
        
        if languages:
            print("\n=== Supported Languages ===")
            for lang in languages["languages"]:
                print(f"{lang['id']}: {lang['name']}")

if __name__ == "__main__":
    main()
