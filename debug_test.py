"""
Debug script to test the AI Code Translator MCP Server
"""

import requests
import json
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to import from AI_Code_Translator
parent_dir = str(Path(__file__).parent.parent / "AI_Code_Translator")
sys.path.insert(0, parent_dir)

try:
    from integrated_ai import IntegratedTranslatorAI
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Make sure the AI_Code_Translator directory is at: {parent_dir}")
    sys.exit(1)

# Simple Python code to translate
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

print("Testing AI Code Translator directly...")

# Set the Gemini API key
gemini_api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyCtB1OoW3js_hlXuQnWbT1pIf6VndB7jRo")
os.environ["GEMINI_API_KEY"] = gemini_api_key

# Create the translator AI instance
translator_ai = IntegratedTranslatorAI(
    gemini_api_key=gemini_api_key,
    gemini_model="gemini-1.5-pro"
)

# Test direct translation
print("\nDirect translation result:")
result = translator_ai.translate_code(
    source_code=python_code,
    target_language="javascript",
    use_neural=False,
    use_llm=True
)

print(f"Result type: {type(result)}")
print(f"Result value: {result}")

# If it's a dictionary, print the keys
if isinstance(result, dict):
    print(f"Dictionary keys: {result.keys()}")
    
    # Try to extract the translated code
    if "translated_code" in result:
        print("\nTranslated code from dictionary:")
        print(result["translated_code"])
else:
    print("\nTranslated code (as string):")
    print(result)

# Try to get feedback
try:
    print("\nGetting translation feedback:")
    feedback = translator_ai.get_translation_feedback(
        source_code=python_code,
        translated_code=str(result),
        source_lang="python",
        target_lang="javascript"
    )
    print(f"Feedback type: {type(feedback)}")
    print(f"Feedback: {feedback}")
except Exception as e:
    print(f"Error getting feedback: {e}")
