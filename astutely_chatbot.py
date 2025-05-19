"""
Astutely Chatbot Module for AI Code Translator

This module implements the Astutely chatbot functionality that can be integrated
with the MCP server when needed. It provides a conversational interface for code
translation and programming assistance.
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import google.generativeai as genai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("astutely.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AstutelyChatbot:
    """
    Astutely is a friendly, helpful AI chatbot that can answer questions about code
    translation and process translation requests directly from chat.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "models/gemini-1.5-pro"):
        """
        Initialize the Astutely chatbot with the Gemini API.
        
        Args:
            api_key: The API key for the Gemini API. If None, will try to get from environment.
            model_name: The name of the model to use.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized Astutely chatbot with model: {model_name}")
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Astutely personality traits
        self.personality = {
            "name": "Astutely",
            "traits": [
                "friendly",
                "helpful",
                "knowledgeable about programming",
                "patient",
                "encouraging"
            ],
            "introduction": "Hi! I'm Astutely, your friendly AI code translation assistant. I can help you translate code between different programming languages, answer questions about programming, and provide guidance on best practices. How can I help you today?"
        }
    
    def start_new_conversation(self) -> str:
        """
        Start a new conversation with the Astutely chatbot.
        
        Returns:
            The introduction message from Astutely.
        """
        self.conversation_history = []
        return self.personality["introduction"]
    
    def detect_code_in_message(self, message: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detect if there's code in the message and extract it.
        
        Args:
            message: The user message to analyze.
            
        Returns:
            A tuple of (has_code, code_snippet, language)
        """
        # Check for code blocks with language specification
        code_block_pattern = r"```(\w+)?\n([\s\S]*?)\n```"
        matches = re.findall(code_block_pattern, message)
        
        if matches:
            language, code = matches[0]
            return True, code.strip(), language if language else None
        
        # Check for inline code
        inline_code_pattern = r"`(.*?)`"
        inline_matches = re.findall(inline_code_pattern, message)
        
        if inline_matches:
            return True, inline_matches[0], None
        
        # Check for common code patterns
        if "def " in message or "function " in message or "class " in message or "import " in message:
            return True, message, None
            
        return False, None, None
    
    def detect_translation_request(self, message: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Detect if the message is a translation request.
        
        Args:
            message: The user message to analyze.
            
        Returns:
            A tuple of (is_translation_request, code, source_language, target_language)
        """
        # Common translation request patterns
        patterns = [
            r"translate\s+(?:this|the)?\s*(?:code)?\s*(?:from\s+(\w+)\s+to\s+(\w+))?\s*[:\-]?\s*(```[\s\S]*?```|`[\s\S]*?`)",
            r"convert\s+(?:this|the)?\s*(?:code)?\s*(?:from\s+(\w+)\s+to\s+(\w+))?\s*[:\-]?\s*(```[\s\S]*?```|`[\s\S]*?`)",
            r"(?:from\s+(\w+)\s+to\s+(\w+)).*?(```[\s\S]*?```|`[\s\S]*?`)"
        ]
        
        for pattern in patterns:
            matches = re.search(pattern, message, re.IGNORECASE)
            if matches:
                source_lang = matches.group(1)
                target_lang = matches.group(2)
                code_block = matches.group(3)
                
                # Clean up code block
                code = code_block.strip('`').strip()
                
                return True, code, source_lang, target_lang
        
        # Check if there's code and explicit mention of languages
        has_code, code, _ = self.detect_code_in_message(message)
        if has_code:
            # Look for language mentions
            lang_pattern = r"(?:from|in)\s+(\w+).*?(?:to|into)\s+(\w+)"
            lang_matches = re.search(lang_pattern, message, re.IGNORECASE)
            
            if lang_matches:
                source_lang = lang_matches.group(1)
                target_lang = lang_matches.group(2)
                return True, code, source_lang, target_lang
        
        return False, None, None, None
    
    def translate_code(self, code: str, source_lang: str, target_lang: str) -> str:
        """
        Translate code from one language to another.
        
        Args:
            code: The code to translate.
            source_lang: The source programming language.
            target_lang: The target programming language.
            
        Returns:
            The translated code.
        """
        prompt = f"""Translate the following {source_lang} code to {target_lang}:

```{source_lang}
{code}
```

Please provide ONLY the translated {target_lang} code without any explanations or markdown formatting.
"""
        
        try:
            response = self.model.generate_content(prompt)
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
            return f"Sorry, I encountered an error while translating your code: {str(e)}"
    
    def process_message(self, message: str, user_id: str = "user") -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: The user message.
            user_id: The ID of the user.
            
        Returns:
            The chatbot's response.
        """
        try:
            # Check for translation request
            is_translation, code, source_lang, target_lang = self.detect_translation_request(message)
            
            if is_translation and code and source_lang and target_lang:
                # Handle translation request
                translated_code = self.translate_code(code, source_lang, target_lang)
                
                response = f"Here's your translated code from {source_lang} to {target_lang}:\n\n```{target_lang}\n{translated_code}\n```\n\nIs there anything else you'd like me to help with?"
                return response
            
            # Regular chat interaction - use a simpler approach with direct prompt
            # Note: We don't need to update the conversation history here as it's managed by setup_astutely.py
            
            # Create a system prompt with Astutely's personality
            personality_traits = ", ".join(self.personality["traits"])
            system_prompt = f"You are {self.personality['name']}, a {personality_traits} AI assistant focused on helping with code translation and programming questions. Be concise and helpful."
            
            # Format the conversation history for the prompt
            conversation_context = ""
            for entry in self.conversation_history:
                role = entry.get("role", "")
                content = entry.get("content", "")
                if role == "user":
                    conversation_context += f"User: {content}\n"
                elif role == "assistant":
                    conversation_context += f"Astutely: {content}\n"
            
            # Create the full prompt
            prompt = f"{system_prompt}\n\nConversation history:\n{conversation_context}\n\nUser: {message}\nAstutely:"
            
            # Generate response using the Gemini API
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            # Extract the response text
            if hasattr(response, 'text'):
                response_text = response.text.strip()
            else:
                # Handle the case where response might be structured differently
                response_text = str(response).strip()
                
            return response_text
            
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            logger.error(f"Exception details: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return f"I'm sorry, I encountered an error while processing your message. Could you try rephrasing or try again later?"
    
    def save_conversation(self, file_path: str) -> bool:
        """
        Save the current conversation history to a file.
        
        Args:
            file_path: The path to save the conversation to.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, file_path: str) -> bool:
        """
        Load a conversation history from a file.
        
        Args:
            file_path: The path to load the conversation from.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Error loading conversation: {e}")
            return False
            
    def _format_conversation_history(self) -> str:
        """
        Format the conversation history for inclusion in a prompt.
        
        Returns:
            A formatted string representation of the conversation history.
        """
        if not self.conversation_history:
            return ""
            
        formatted_history = ""
        for message in self.conversation_history:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "user":
                formatted_history += f"User: {content}\n"
            elif role == "assistant":
                formatted_history += f"Astutely: {content}\n"
        
        return formatted_history

# Example usage
if __name__ == "__main__":
    # This code runs when the module is executed directly
    try:
        # Initialize the chatbot
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Please set the GEMINI_API_KEY environment variable")
            exit(1)
            
        chatbot = AstutelyChatbot(api_key)
        
        # Start conversation
        print(chatbot.start_new_conversation())
        
        # Interactive chat loop
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nAstutely: Goodbye! Have a great day!")
                break
                
            response = chatbot.process_message(user_input)
            print(f"\nAstutely: {response}")
            
    except KeyboardInterrupt:
        print("\nExiting Astutely chatbot...")
    except Exception as e:
        print(f"Error: {e}")
