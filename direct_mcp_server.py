"""
Direct MCP Server for AI Code Translator

This is a simplified, direct implementation of an MCP server for the AI Code Translator
that uses the Gemini API directly without complex dependencies.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("direct_mcp.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Code Translator MCP Server",
    description="Direct MCP server for AI Code Translator",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# Load API keys from file
def load_api_keys() -> List[str]:
    try:
        with open("api_keys.json", "r") as f:
            data = json.load(f)
            return data.get("api_keys", [])
    except FileNotFoundError:
        logger.warning("api_keys.json not found, using empty list")
        return []
    except json.JSONDecodeError:
        logger.error("Invalid JSON in api_keys.json")
        return []

# Verify API key
async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key not in load_api_keys():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return api_key

# Request and response models
class TranslationRequest(BaseModel):
    source_code: str
    source_language: str = "python"
    target_language: str = "javascript"

class TranslationResponse(BaseModel):
    translated_code: str
    feedback: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

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

# Translation function
def translate_code(source_code: str, source_lang: str, target_lang: str) -> str:
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
def get_translation_feedback(source_code: str, translated_code: str, source_lang: str, target_lang: str) -> str:
    """Get feedback on a code translation."""
    try:
        prompt = f"""Please review this code translation from {source_lang} to {target_lang} and provide feedback:
        
Original {source_lang} code:
```{source_lang}
{source_code}
```

Translated {target_lang} code:
```{target_lang}
{translated_code}
```

Provide feedback on:
1. Accuracy of the translation
2. Idiomaticity in the target language
3. Any potential issues or edge cases
4. Suggestions for improvement
"""
        
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
            
    except Exception as e:
        logger.error(f"Error getting translation feedback: {e}")
        return f"Error getting feedback: {str(e)}"

# Chat function
def chat_with_ai(message: str) -> str:
    """Chat with the AI assistant."""
    try:
        chat = gemini_model.start_chat(history=[])
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

# Endpoints
@app.get("/")
async def root():
    return {"message": "AI Code Translator MCP Server"}

@app.post("/translate")
async def translate_code_endpoint(request: TranslationRequest, api_key: str = Depends(verify_api_key)):
    try:
        # Translate the code
        translated = translate_code(
            request.source_code,
            request.source_language,
            request.target_language
        )
        
        # Get feedback
        feedback = get_translation_feedback(
            request.source_code,
            translated,
            request.source_language,
            request.target_language
        )
        
        # Return as a dictionary (not a model)
        return {
            "translated_code": translated,
            "feedback": feedback
        }
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@app.post("/chat")
async def chat_endpoint(request: ChatRequest, api_key: str = Depends(verify_api_key)):
    try:
        response = chat_with_ai(request.message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )

@app.get("/models")
async def list_models(api_key: str = Depends(verify_api_key)):
    return {
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
    }

@app.get("/languages")
async def list_languages(api_key: str = Depends(verify_api_key)):
    return {
        "languages": [
            {"id": "python", "name": "Python"},
            {"id": "javascript", "name": "JavaScript"},
            {"id": "java", "name": "Java"},
            {"id": "cpp", "name": "C++"},
            {"id": "csharp", "name": "C#"},
            {"id": "go", "name": "Go"},
            {"id": "ruby", "name": "Ruby"},
            {"id": "php", "name": "PHP"},
            {"id": "swift", "name": "Swift"},
            {"id": "kotlin", "name": "Kotlin"},
            {"id": "typescript", "name": "TypeScript"},
            {"id": "rust", "name": "Rust"}
        ]
    }

# Run the server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Direct MCP Server for AI Code Translator")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    
    args = parser.parse_args()
    
    logger.info(f"Starting Direct MCP server on {args.host}:{args.port}")
    uvicorn.run("direct_mcp_server:app", host=args.host, port=args.port)
