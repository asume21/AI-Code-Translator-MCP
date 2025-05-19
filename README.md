# AI Code Translator MCP Server

This project transforms the AI Code Translator into a Model Control Protocol (MCP) server, allowing other applications to interact with the translator through a standardized API. It includes an Astutely chatbot for interactive coding assistance and a vulnerability scanner for code security analysis.

## Features

- **Code Translation API**: Translate code between multiple programming languages
- **Translation Feedback**: Get detailed feedback on translations
- **Astutely Chatbot**: Interactive AI assistant for coding help
- **Vulnerability Scanner**: Detect security issues in code
- **User Management**: Registration, login, and subscription management
- **Authentication**: Secure API access with API keys and JWT tokens
- **Language Support**: Multiple programming languages supported

## Setup

### Prerequisites

- Python 3.11 or higher
- Gemini API key

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Gemini API key:
   ```
   set GEMINI_API_KEY=your_api_key_here
   ```

### Running the Server

Use the provided batch file:
```
run_mcp_server.bat
```

Or run directly with Python:
```
python server.py --host 127.0.0.1 --port 8000
```

## API Documentation

### Authentication

All API endpoints require an API key, which should be provided in the `X-API-Key` header.

### Endpoints

#### Translate Code
```
POST /translate
```

Request body:
```json
{
  "source_code": "def hello():\n    print('Hello, world!')",
  "source_language": "python",
  "target_language": "javascript",
  "use_neural": false,
  "use_llm": true
}
```

Response:
```json
{
  "translated_code": "function hello() {\n    console.log('Hello, world!');\n}",
  "feedback": "The translation correctly converts Python's print function to JavaScript's console.log..."
}
```

#### Get Translation Feedback
```
POST /feedback
```

Request body:
```json
{
  "source_code": "def hello():\n    print('Hello, world!')",
  "translated_code": "function hello() {\n    console.log('Hello, world!');\n}",
  "source_language": "python",
  "target_language": "javascript"
}
```

Response:
```json
{
  "feedback": "The translation correctly converts Python's print function to JavaScript's console.log..."
}
```

#### Chat with AI Assistant
```
POST /chat
```

Request body:
```json
{
  "message": "How do I implement a binary search in Python?"
}
```

Response:
```json
{
  "response": "Here's how you can implement a binary search in Python:..."
}
```

#### List Available Models
```
GET /models
```

#### List Supported Languages
```
GET /languages
```

## Client Example

Here's a simple Python example of how to use the API:

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "test_api_key_1"
HEADERS = {"X-API-Key": API_KEY}

# Translate code
def translate_code(source_code, source_lang="python", target_lang="javascript"):
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
    return response.json()

# Example usage
python_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""

result = translate_code(python_code)
print(f"Translated code:\n{result['translated_code']}")
print(f"\nFeedback:\n{result['feedback']}")
```

## Integration with Existing Tools

This MCP server can be integrated with various tools and platforms:
- IDEs and code editors through plugins
- CI/CD pipelines for automated code conversion
- Learning platforms for educational purposes
- Development tools for cross-language development

## Deployment

The AI Code Translator can be deployed to various hosting platforms. We've provided tools to simplify the deployment process.

### Using the Deployment Script

Use the provided `deploy.py` script to set up deployment files for your preferred platform:

```bash
python deploy.py --platform render --api-key YOUR_GEMINI_API_KEY --jwt-secret YOUR_JWT_SECRET
```

Supported platforms:
- Render.com
- Heroku
- Netlify

### Manual Deployment to Render.com

1. Create an account at [Render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn simple_mcp_server:app`
5. Add environment variables:
   - `GEMINI_API_KEY`
   - `JWT_SECRET`
   - `STRIPE_API_KEY` (if using payment processing)

### Manual Deployment to Heroku

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login to Heroku: `heroku login`
3. Create a new app: `heroku create ai-code-translator`
4. Push your code: `git push heroku main`
5. Set environment variables:
   ```bash
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set JWT_SECRET=your_secret
   heroku config:set STRIPE_API_KEY=your_stripe_key
   ```

### Domain Setup

For a professional appearance, consider registering a domain and connecting it to your deployed application. Free domains are available through services like [Freenom](https://www.freenom.com).

## Creating VS Code Extension

To create a VS Code extension for the AI Code Translator:

1. Install Node.js and npm
2. Install Yeoman and VS Code Extension Generator:
   ```bash
   npm install -g yo generator-code
   ```
3. Generate a new extension:
   ```bash
   yo code
   ```
4. Implement the extension to connect to your deployed API
5. Publish to the VS Code Marketplace:
   ```bash
   vsce package
   vsce publish
   ```

Detailed instructions for creating VS Code extensions can be found in the [official documentation](https://code.visualstudio.com/api/get-started/your-first-extension).

## License

MIT
