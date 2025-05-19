"""
Desktop Connector for AI Code Translator

This module connects the desktop application with Astutely chatbot
to the MCP server, enabling shared user accounts, translation history,
and synchronized settings.
"""

import os
import sys
import json
import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
from unified_config import UnifiedConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("desktop_connector.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DesktopConnector:
    """
    Connects the desktop application to the MCP server.
    """
    
    def __init__(self, config_path: str = "ecosystem_config.json"):
        """
        Initialize the desktop connector.
        
        Args:
            config_path: Path to the unified configuration file.
        """
        self.config = UnifiedConfig(config_path)
        self.api_base_url = self.config.api_base_url
        self.api_key = None
        self.auth_token = None
        self.user_info = None
        logger.info(f"Initialized desktop connector with API base URL: {self.api_base_url}")
    
    def login(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """
        Log in to the MCP server.
        
        Args:
            username_or_email: The username or email.
            password: The password.
            
        Returns:
            The login result.
        """
        try:
            url = f"{self.api_base_url}/api/users/login"
            payload = {
                "username_or_email": username_or_email,
                "password": password
            }
            
            response = requests.post(url, json=payload)
            result = response.json()
            
            if result.get("success"):
                self.auth_token = result.get("token")
                self.api_key = result.get("api_key")
                self.user_info = {
                    "user_id": result.get("user_id"),
                    "username": result.get("username"),
                    "email": result.get("email")
                }
                logger.info(f"Logged in as {username_or_email}")
            
            return result
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def register(self, username: str, email: str, password: str, 
                first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: The username.
            email: The email.
            password: The password.
            first_name: The first name (optional).
            last_name: The last name (optional).
            
        Returns:
            The registration result.
        """
        try:
            url = f"{self.api_base_url}/api/users/register"
            payload = {
                "username": username,
                "email": email,
                "password": password
            }
            
            if first_name:
                payload["first_name"] = first_name
            
            if last_name:
                payload["last_name"] = last_name
            
            response = requests.post(url, json=payload)
            result = response.json()
            
            if result.get("success"):
                logger.info(f"Registered user {username}")
                # Auto-login after registration
                return self.login(username, password)
            
            return result
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def translate_code(self, source_code: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Translate code using the MCP server.
        
        Args:
            source_code: The source code to translate.
            source_lang: The source programming language.
            target_lang: The target programming language.
            
        Returns:
            The translation result.
        """
        if not self.api_key:
            return {"success": False, "message": "Not logged in"}
        
        try:
            url = f"{self.api_base_url}/translate"
            headers = {"X-API-Key": self.api_key}
            payload = {
                "source_code": source_code,
                "source_language": source_lang,
                "target_language": target_lang
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Translated code from {source_lang} to {target_lang}")
                return {
                    "success": True,
                    "translated_code": result.get("translated_code"),
                    "feedback": result.get("feedback"),
                    "translations_remaining": result.get("translations_remaining")
                }
            else:
                error_msg = response.json().get("error", f"HTTP error: {response.status_code}")
                logger.error(f"Translation error: {error_msg}")
                return {"success": False, "message": error_msg}
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_translation_history(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get translation history from the MCP server.
        
        Args:
            limit: The maximum number of records to return.
            offset: The offset for pagination.
            
        Returns:
            The translation history.
        """
        if not self.auth_token:
            return {"success": False, "message": "Not logged in"}
        
        try:
            url = f"{self.api_base_url}/api/translations/history"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            params = {"limit": limit, "offset": offset}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Retrieved translation history")
                return result
            else:
                error_msg = response.json().get("error", f"HTTP error: {response.status_code}")
                logger.error(f"History retrieval error: {error_msg}")
                return {"success": False, "message": error_msg}
            
        except Exception as e:
            logger.error(f"History retrieval error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def scan_code_vulnerabilities(self, code: str, language: str) -> Dict[str, Any]:
        """
        Scan code for vulnerabilities using the MCP server.
        
        Args:
            code: The code to scan.
            language: The programming language.
            
        Returns:
            The vulnerability scan results.
        """
        if not self.api_key:
            return {"success": False, "message": "Not logged in"}
        
        try:
            url = f"{self.api_base_url}/vulnerabilities/scan"
            headers = {"X-API-Key": self.api_key}
            payload = {
                "code": code,
                "language": language
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Scanned code for vulnerabilities")
                return result
            else:
                error_msg = response.json().get("error", f"HTTP error: {response.status_code}")
                logger.error(f"Vulnerability scan error: {error_msg}")
                return {"success": False, "message": error_msg}
            
        except Exception as e:
            logger.error(f"Vulnerability scan error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def chat_with_astutely(self, message: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Chat with Astutely through the MCP server.
        
        Args:
            message: The user message.
            conversation_id: The conversation ID for continuing a conversation.
            
        Returns:
            The chat response.
        """
        if not self.api_key:
            return {"success": False, "message": "Not logged in"}
        
        try:
            url = f"{self.api_base_url}/chat"
            headers = {"X-API-Key": self.api_key}
            payload = {"message": message}
            
            if conversation_id:
                payload["conversation_id"] = conversation_id
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Chat with Astutely")
                return {
                    "success": True,
                    "response": result.get("response"),
                    "conversation_id": result.get("conversation_id")
                }
            else:
                error_msg = response.json().get("error", f"HTTP error: {response.status_code}")
                logger.error(f"Chat error: {error_msg}")
                return {"success": False, "message": error_msg}
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_subscription_plans(self) -> Dict[str, Any]:
        """
        Get available subscription plans.
        
        Returns:
            The subscription plans.
        """
        try:
            url = f"{self.api_base_url}/api/subscriptions/plans"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Retrieved subscription plans")
                return result
            else:
                error_msg = response.json().get("error", f"HTTP error: {response.status_code}")
                logger.error(f"Plans retrieval error: {error_msg}")
                return {"success": False, "message": error_msg}
            
        except Exception as e:
            logger.error(f"Plans retrieval error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def update_subscription(self, plan_id: str) -> Dict[str, Any]:
        """
        Update subscription plan.
        
        Args:
            plan_id: The ID of the new subscription plan.
            
        Returns:
            The update result.
        """
        if not self.auth_token:
            return {"success": False, "message": "Not logged in"}
        
        try:
            url = f"{self.api_base_url}/api/subscriptions"
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            payload = {"plan_id": plan_id}
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Updated subscription plan")
                return result
            else:
                error_msg = response.json().get("error", f"HTTP error: {response.status_code}")
                logger.error(f"Subscription update error: {error_msg}")
                return {"success": False, "message": error_msg}
            
        except Exception as e:
            logger.error(f"Subscription update error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

# Example usage
if __name__ == "__main__":
    connector = DesktopConnector()
    
    # Example login
    result = connector.login("test_user", "password123")
    print("Login result:", result)
    
    if result.get("success"):
        # Example translation
        translation = connector.translate_code(
            source_code="print('Hello, World!')",
            source_lang="python",
            target_lang="java"
        )
        print("Translation result:", translation)
        
        # Example history retrieval
        history = connector.get_translation_history(limit=5)
        print("History result:", history)
