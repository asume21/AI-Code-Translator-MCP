"""
Unified Configuration for AI Code Translator Ecosystem

This module provides configuration and integration points for connecting
all components of the AI Code Translator ecosystem:
- MCP Server (API Hub)
- SaaS Website
- Desktop Application with Astutely
- Vulnerability Scanner
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("unified_ecosystem.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedConfig:
    """
    Unified configuration for the AI Code Translator ecosystem.
    """
    
    def __init__(self, config_file: str = "ecosystem_config.json"):
        """
        Initialize the unified configuration.
        
        Args:
            config_file: Path to the configuration file.
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.api_base_url = self.config.get("api_base_url", "http://127.0.0.1:5000")
        logger.info(f"Initialized unified configuration with API base URL: {self.api_base_url}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration from the file or create a default one.
        
        Returns:
            The configuration dictionary.
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading configuration: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        Create a default configuration.
        
        Returns:
            The default configuration dictionary.
        """
        config = {
            "api_base_url": "http://127.0.0.1:5000",
            "components": {
                "mcp_server": {
                    "enabled": True,
                    "port": 5000,
                    "host": "127.0.0.1"
                },
                "saas_website": {
                    "enabled": True,
                    "url": "https://ai-code-translator.example.com"
                },
                "desktop_app": {
                    "enabled": True,
                    "use_local_models": False,
                    "sync_history": True
                },
                "vulnerability_scanner": {
                    "enabled": True,
                    "scan_depth": "medium"
                },
                "astutely_chatbot": {
                    "enabled": True,
                    "personality": "friendly",
                    "model": "gemini-1.5-pro"
                }
            },
            "features": {
                "translation": {
                    "enabled": True,
                    "default_source_lang": "python",
                    "default_target_lang": "javascript"
                },
                "chat": {
                    "enabled": True,
                    "save_history": True
                },
                "vulnerability_scanning": {
                    "enabled": True,
                    "auto_scan": False
                },
                "user_management": {
                    "enabled": True,
                    "require_login": True
                }
            }
        }
        
        # Save the default configuration
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Created default configuration at {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving default configuration: {e}")
        
        return config
    
    def save_config(self) -> bool:
        """
        Save the current configuration to the file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_api_url(self, endpoint: str) -> str:
        """
        Get the full URL for an API endpoint.
        
        Args:
            endpoint: The API endpoint path.
            
        Returns:
            The full URL.
        """
        # Ensure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        
        return f"{self.api_base_url}{endpoint}"
    
    def is_component_enabled(self, component_name: str) -> bool:
        """
        Check if a component is enabled.
        
        Args:
            component_name: The name of the component.
            
        Returns:
            True if enabled, False otherwise.
        """
        components = self.config.get("components", {})
        component = components.get(component_name, {})
        return component.get("enabled", False)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled.
        
        Args:
            feature_name: The name of the feature.
            
        Returns:
            True if enabled, False otherwise.
        """
        features = self.config.get("features", {})
        feature = features.get(feature_name, {})
        return feature.get("enabled", False)
    
    def get_component_config(self, component_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a component.
        
        Args:
            component_name: The name of the component.
            
        Returns:
            The component configuration.
        """
        components = self.config.get("components", {})
        return components.get(component_name, {})
    
    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a feature.
        
        Args:
            feature_name: The name of the feature.
            
        Returns:
            The feature configuration.
        """
        features = self.config.get("features", {})
        return features.get(feature_name, {})

# Example usage
if __name__ == "__main__":
    config = UnifiedConfig()
    print(f"API Base URL: {config.api_base_url}")
    print(f"Is MCP Server enabled: {config.is_component_enabled('mcp_server')}")
    print(f"Is Astutely Chatbot enabled: {config.is_component_enabled('astutely_chatbot')}")
    print(f"Translation feature config: {config.get_feature_config('translation')}")
