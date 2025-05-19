"""
Production MCP Server for AI Code Translator

A production-ready implementation that uses PostgreSQL for data storage
and is configured for deployment on Render.com.
"""

import os
import sys
import json
import logging
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("production_mcp.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure CORS to allow all origins and headers
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})
# Set CORS headers for all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Import PostgreSQL user management
from user_management_postgres import UserManagementPostgres
from user_api_postgres import validate_api_key, record_translation

# Initialize user management
try:
    user_mgmt = UserManagementPostgres()
    logger.info("PostgreSQL user management initialized successfully")
except Exception as e:
    logger.error(f"Error initializing PostgreSQL user management: {e}")
    logger.warning("Falling back to SQLite user management")
    from user_management import UserManagement
    from user_api import validate_api_key, record_translation
    user_mgmt = UserManagement()

# Initialize Gemini
def initialize_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set in environment variables")
        raise ValueError("GEMINI_API_KEY not set in environment variables")
    
    genai.configure(api_key=api_key)
    
    model_name = "models/gemini-1.5-pro"
    try:
        logger.info("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                logger.info(f"- {m.name}")
        
        model = genai.GenerativeModel(model_name)
        logger.info(f"Successfully initialized model: {model_name}")
        return model
    except Exception as e:
        logger.error(f"Error initializing Gemini model: {e}")
        # Fallback to a known working model
        fallback_model = "models/gemini-1.0-pro"
        logger.info(f"Falling back to {fallback_model}")
        return genai.GenerativeModel(fallback_model)

# Initialize the model
gemini_model = initialize_gemini()

# Authentication decorator
def require_api_key(f):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        is_valid, user_info = validate_api_key(api_key)
        
        if not is_valid:
            return jsonify({"error": user_info.get("error", "Invalid API Key")}), 401
        
        # Add user info to request context
        request.user_info = user_info
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Translation function
def translate_code(source_code, source_lang, target_lang):
    """Translate code from one language to another using Gemini."""
    try:
        prompt = f"""Translate the following {source_lang} code to {target_lang}:

```{source_lang}
{source_code}
```

Please provide ONLY the translated {target_lang} code without any explanations or markdown formatting.
"""
        
        response = gemini_model.generate_content(prompt)
        response_text = response.text
        
        # Try to extract code between triple backticks
        code_pattern = r"```(?:\w+)?\n([\s\S]*?)\n```"
        code_matches = re.findall(code_pattern, response_text)
        
        if code_matches:
            return code_matches[0].strip()
        else:
            return response_text.strip()
            
    except Exception as e:
        logger.error(f"Error in code translation: {e}")
        return f"// Error translating code: {str(e)}"

# Feedback function
def get_translation_feedback(source_code, translated_code, source_lang, target_lang):
    """Get feedback on a code translation."""
    try:
        prompt = f"""Analyze the following code translation from {source_lang} to {target_lang}:

Original {source_lang} code:
```{source_lang}
{source_code}
```

Translated {target_lang} code:
```{target_lang}
{translated_code}
```

Please provide a brief analysis of the translation quality, including:
1. Accuracy: Does the translated code maintain the same functionality?
2. Idiomaticity: Does the translated code follow {target_lang} best practices?
3. Efficiency: Is the translated code as efficient as the original?
4. Any issues or improvements that could be made.

Keep your response concise and focused on the most important points.
"""
        
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
            
    except Exception as e:
        logger.error(f"Error getting translation feedback: {e}")
        return f"Error analyzing translation: {str(e)}"

# Chat function
def chat_with_ai(message):
    """Chat with the AI assistant."""
    try:
        response = gemini_model.generate_content(message)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return f"Error: {str(e)}"

# Routes
@app.route('/')
def home():
    return jsonify({"message": "AI Code Translator MCP Server"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/languages')
@require_api_key
def languages():
    return jsonify({
        "languages": ["python", "javascript", "java", "cpp", "csharp", "go", "ruby", "php", "swift", "kotlin", "typescript", "rust"]
    })

@app.route('/translate', methods=['POST'])
@require_api_key
def translate_endpoint():
    data = request.json
    
    if not data or 'source_code' not in data:
        return jsonify({"error": "Missing source_code in request"}), 400
    
    source_code = data['source_code']
    source_lang = data.get('source_language', 'python')
    target_lang = data.get('target_language', 'javascript')
    
    translated_code = translate_code(source_code, source_lang, target_lang)
    feedback = get_translation_feedback(source_code, translated_code, source_lang, target_lang)
    
    # Record translation in user history
    user_id = request.user_info.get("user_id")
    if user_id:
        record_translation(
            user_id=user_id,
            source_code=source_code,
            translated_code=translated_code,
            source_lang=source_lang,
            target_lang=target_lang,
            feedback=feedback
        )
    
    return jsonify({
        "translated_code": translated_code,
        "feedback": feedback,
        "translations_remaining": request.user_info.get("translations_remaining", "unlimited")
    })

@app.route('/chat', methods=['POST'])
@require_api_key
def chat_endpoint():
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({"error": "Missing message in request"}), 400
    
    message = data['message']
    response = chat_with_ai(message)
    
    return jsonify({"response": response})

@app.route('/models', methods=['GET'])
@require_api_key
def list_models():
    return jsonify({
        "models": [
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "description": "Google's Gemini 1.5 Pro model for code translation and chat"
            },
            {
                "id": "gemini-pro",
                "name": "Gemini Pro",
                "description": "Google's Gemini Pro model for code translation and chat"
            }
        ]
    })

# Static file routes
@app.route('/integrated_demo.html')
def integrated_demo():
    try:
        return send_file('integrated_demo.html')
    except Exception as e:
        logger.error(f"Error serving integrated_demo.html: {e}")
        return f"Error: {str(e)}", 500

@app.route('/ai_money_maker.html')
def ai_money_maker():
    try:
        return send_file('ai_money_maker.html')
    except Exception as e:
        logger.error(f"Error serving ai_money_maker.html: {e}")
        return f"Error: {str(e)}", 500

@app.route('/static/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('static', path)
    except Exception as e:
        logger.error(f"Error serving static file {path}: {e}")
        return f"Error: {str(e)}", 500

# Import user routes setup function
try:
    from user_api_postgres import setup_user_routes
    logger.info("Using PostgreSQL user API")
except ImportError:
    from user_api import setup_user_routes
    logger.warning("Falling back to SQLite user API")

# Import vulnerability scanner routes
from vulnerability_api import setup_vulnerability_routes

# Import Astutely chatbot
from astutely_chatbot import AstutelyChatbot
from setup_astutely import setup_astutely_routes

# Set up user management routes
setup_user_routes(app)

# Set up vulnerability scanner routes
setup_vulnerability_routes(app, require_api_key)

# Initialize Astutely chatbot
astutely = AstutelyChatbot(os.environ.get("GEMINI_API_KEY"))

# Set up Astutely chatbot routes
setup_astutely_routes(app, astutely, require_api_key)

# Run the server
if __name__ == '__main__':
    try:
        # Get port from environment variable (Render sets this)
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting production server on port {port}")
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"\nError starting server: {e}")
        print("\nTrying alternate port...")
        try:
            # Try yet another port
            app.run(host='0.0.0.0', port=3000)
        except Exception as e2:
            logger.error(f"Failed to start server on alternate port: {e2}")
            print(f"\nError starting server on alternate port: {e2}")
