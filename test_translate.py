import requests
import json

url = "http://127.0.0.1:5000/translate"
headers = {"Content-Type": "application/json"}
data = {
    "source_code": "print('Hello World')",
    "source_language": "python",
    "target_language": "java"
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
