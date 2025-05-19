"""
AI Code Translator MCP Server

This module implements a Model Control Protocol (MCP) server that exposes
the AI Code Translator functionality through a standardized API.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, status, Request, Response
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

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

# Add the parent directory to sys.path to import from AI_Code_Translator
parent_dir = str(Path(__file__).parent.parent / "AI_Code_Translator")
sys.path.insert(0, parent_dir)

try:
    from ai_code_translator.gemini_interface import GeminiInterface
    from integrated_ai import IntegratedTranslatorAI
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    logger.error(f"Make sure the AI_Code_Translator directory is at: {parent_dir}")
    raise

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

# Initialize AI components
def get_translator_ai() -> IntegratedTranslatorAI:
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_api_key:
        logger.warning("GEMINI_API_KEY not set in environment variables")
    
    return IntegratedTranslatorAI(
        gemini_api_key=gemini_api_key,
        gemini_model="gemini-1.5-pro"
    )

# Create a global instance
translator_ai = get_translator_ai()

# Request and response models
class TranslationRequest(BaseModel):
    source_code: str
    source_language: str = "python"
    target_language: str = "javascript"
    use_neural: bool = False
    use_llm: bool = True

class TranslationResponse(BaseModel):
    translated_code: str
    feedback: Optional[str] = None
    success: bool = True

class FeedbackRequest(BaseModel):
    source_code: str
    translated_code: str
    source_language: str = "python"
    target_language: str = "javascript"

class FeedbackResponse(BaseModel):
    feedback: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Endpoints
@app.get("/")
async def root():
    return {"message": "AI Code Translator MCP Server"}

@app.post("/translate", response_model=TranslationResponse, dependencies=[Depends(verify_api_key)])
async def translate_code(request: TranslationRequest):
    try:
        # Get the translated code from the translator_ai
        result = translator_ai.translate_code(
            source_code=request.source_code,
            target_language=request.target_language,
            use_neural=request.use_neural,
            use_llm=request.use_llm
        )
        
        logger.info(f"Translation result type: {type(result)}")
        
        # Handle different return types from translate_code
        translated_code = ""
        if isinstance(result, dict):
            logger.info(f"Result is a dictionary with keys: {result.keys()}")
            # If it's a dictionary, extract the translated code
            if 'translated_code' in result:
                translated_code = result['translated_code']
            else:
                # Try to convert the dict to a string representation
                translated_code = json.dumps(result, indent=2)
        elif result is None:
            translated_code = "Translation failed: No result returned"
        else:
            # If it's a string or other type, convert to string
            translated_code = str(result)
        
        # Get feedback if requested
        feedback = None
        if request.use_llm:
            try:
                feedback = translator_ai.get_translation_feedback(
                    source_code=request.source_code,
                    translated_code=translated_code,
                    source_lang=request.source_language,
                    target_lang=request.target_language
                )
            except Exception as feedback_error:
                logger.warning(f"Failed to get feedback: {feedback_error}")
                feedback = f"Could not generate feedback: {str(feedback_error)}"
        
        # Create and return the response as a TranslationResponse object
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

@app.post("/feedback", response_model=FeedbackResponse, dependencies=[Depends(verify_api_key)])
async def get_feedback(request: FeedbackRequest):
    try:
        feedback = translator_ai.get_translation_feedback(
            source_code=request.source_code,
            translated_code=request.translated_code,
            source_lang=request.source_language,
            target_lang=request.target_language
        )
        
        return FeedbackResponse(feedback=feedback)
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback generation failed: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest):
    try:
        response = translator_ai.chat(request.message)
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

# Run the server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Code Translator MCP Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()
    
    logger.info(f"Starting MCP server on {args.host}:{args.port}")
    uvicorn.run("server:app", host=args.host, port=args.port, reload=args.reload)
