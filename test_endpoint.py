import requests
import json

def test_translation():
    url = "http://127.0.0.1:5000/translate"
    
    payload = {
        "source_code": "print('Hello, World!')",
        "source_language": "python",
        "target_language": "java"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nTranslation Result:")
            print("-" * 50)
            print(result.get("translated_code", "No translation returned"))
            print("\nFeedback:")
            print("-" * 50)
            print(result.get("feedback", "No feedback returned"))
        else:
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    print("Testing AI Code Translator MCP Server...")
    test_translation()
    print("\nTest completed.")
