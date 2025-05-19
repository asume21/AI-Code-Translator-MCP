"""
AI Code Translator MCP Server

A simplified but robust Model Control Protocol server that exposes
the core AI Code Translator functionality through a clean API.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional, Union
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("mcp_server.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Code Translator MCP Server",
    description="Model Control Protocol server for AI Code Translator",
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

# Gemini AI Interface
class GeminiInterface:
    def __init__(self, api_key=None, model_name="gemini-1.5-pro"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Add 'models/' prefix if not already present
        if not model_name.startswith('models/'):
            model_name = f"models/{model_name}"
        
        self.model_name = model_name
        
        try:
            # List available models for debugging
            logger.info("Available models:")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    logger.info(f"- {m.name}")
            
            # Get the model
            self.model = genai.GenerativeModel(self.model_name)
            logger.info(f"Successfully initialized model: {self.model_name}")
        except Exception as e:
            logger.error(f"Error initializing Gemini model: {e}")
            # Fallback to a known working model
            fallback_model = "models/gemini-1.0-pro"
            logger.info(f"Falling back to {fallback_model}")
            self.model_name = fallback_model
            self.model = genai.GenerativeModel(self.model_name)
        
        # Set up the system prompt for code translation
        self.system_prompt = """You are an expert code translator that specializes in converting code between different programming languages while maintaining functionality and idiomatic style. 
        
Your task is to translate the provided code from the source language to the target language.
Follow these guidelines:
1. Maintain the same functionality and logic
2. Use idiomatic patterns in the target language
3. Preserve comments (translating them if necessary)
4. Keep the same general structure where appropriate
5. Optimize for readability and maintainability
6. Explain any significant changes or adaptations needed

When providing feedback, focus on:
- Key differences between the languages that affected the translation
- Any language-specific features or libraries used
- Potential issues or edge cases to be aware of
- Suggestions for further improvements
"""

    def translate_code(self, source_code: str, source_lang: str, target_lang: str) -> str:
        """
        Translate code from one language to another using the Gemini model.
        """
        try:
            prompt = f"""Translate the following {source_lang} code to {target_lang}:

```{source_lang}
{source_code}
```

Please provide ONLY the translated {target_lang} code without any explanations or markdown formatting.
"""
            
            # Send the prompt to the model
            response = self.model.generate_content(prompt)
            
            # Extract the code from the response
            response_text = response.text
            
            # Try to extract code between triple backticks
            import re
            code_pattern = r"```(?:\w+)?\n([\s\S]*?)\n```"
            code_matches = re.findall(code_pattern, response_text)
            
            if code_matches:
                # Return the first code block found
                return code_matches[0].strip()
            else:
                # If no code blocks found, return the full response
                return response_text.strip()
                
        except Exception as e:
            logger.error(f"Error in Gemini code translation: {e}")
            return f"// Error translating code: {str(e)}"

    def get_translation_feedback(self, source_code: str, translated_code: str, 
                               source_lang: str, target_lang: str) -> str:
        """
        Get feedback on a code translation.
        """
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
            
            # Send the prompt to the model
            response = self.model.generate_content(prompt)
            
            return response.text.strip()
                
        except Exception as e:
            logger.error(f"Error getting translation feedback: {e}")
            return f"Error getting feedback: {str(e)}"

    def chat(self, message: str) -> str:
        """
        Send a message to the Gemini model and get a response.
        """
        try:
            # Create a chat session
            chat = self.model.start_chat(history=[])
            
            # Send the message and get the response
            response = chat.send_message(message)
            
            return response.text
        except Exception as e:
            logger.error(f"Error in Gemini chat: {e}")
            return f"Sorry, I encountered an error: {str(e)}"

# Initialize Gemini interface
gemini_api_key = os.environ.get("GEMINI_API_KEY")
gemini_interface = GeminiInterface(api_key=gemini_api_key)

# Endpoints
@app.get("/")
async def root():
    return {"message": "AI Code Translator MCP Server"}

@app.post("/translate", response_model=TranslationResponse, dependencies=[Depends(verify_api_key)])
async def translate_code(request: TranslationRequest):
    try:
        # Translate the code
        translated_code = gemini_interface.translate_code(
            source_code=request.source_code,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        # Get feedback on the translation
        feedback = gemini_interface.get_translation_feedback(
            source_code=request.source_code,
            translated_code=translated_code,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        # Return the response
        return TranslationResponse(
            translated_code=translated_code,
            feedback=feedback
        )
    except Exception as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest):
    try:
        response = gemini_interface.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )

@app.get("/models", dependencies=[Depends(verify_api_key)])
async def list_models():
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

@app.get("/languages", dependencies=[Depends(verify_api_key)])
async def list_languages():
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

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

# Run the server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Code Translator MCP Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    logger.info(f"Starting MCP server on {args.host}:{args.port}")
    uvicorn.run("mcp_server:app", host=args.host, port=args.port, reload=args.reload)
