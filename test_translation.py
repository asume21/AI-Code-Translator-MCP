"""
Quick test script for the AI Code Translator MCP Server
"""

import requests

API_URL = "http://localhost:8000"
API_KEY = "test_api_key_1"  # This is one of the test keys from api_keys.json
HEADERS = {"X-API-Key": API_KEY}

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

print("Testing AI Code Translator MCP Server...")
print("Translating Python code to JavaScript...")

try:
    print("Sending request to server...")
    response = requests.post(
        f"{API_URL}/translate",
        headers=HEADERS,
        json={
            "source_code": python_code,
            "source_language": "python",
            "target_language": "javascript",
            "use_llm": True
        }
    )
    
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response content type: {type(result)}")
        print(f"Response keys: {result.keys() if isinstance(result, dict) else 'Not a dictionary'}")
        
        if isinstance(result, dict) and "translated_code" in result:
            print("\n=== Translated JavaScript Code ===")
            print(result["translated_code"])
            
            if "feedback" in result and result["feedback"]:
                print("\n=== Translation Feedback ===")
                print(result["feedback"])
                
            print("\nTest successful! The MCP server is working correctly.")
        else:
            print("Error: Unexpected response format")
            print(f"Full response: {result}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error connecting to server: {e}")
    print("Make sure the server is running on http://localhost:8000")
