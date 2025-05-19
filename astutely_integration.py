"""
Astutely MCP Server Integration Module

This module shows how to integrate the Astutely chatbot with the MCP server.
It's designed to be a plug-and-play solution that you can use when you're ready
to add chatbot functionality to your MCP server.
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from astutely_chatbot import AstutelyChatbot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("astutely_integration.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AstutleyIntegration:
    """
    Integration class for connecting Astutely chatbot to an MCP server.
    """
    
    def __init__(self, app=None, api_key=None, require_auth=True):
        """
        Initialize the Astutely integration.
        
        Args:
            app: The Flask app to integrate with. If None, will create a new app.
            api_key: The Gemini API key. If None, will try to get from environment.
            require_auth: Whether to require API key authentication for endpoints.
        """
        self.app = app or Flask(__name__)
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.require_auth = require_auth
        self.api_keys = ["test_api_key_1", "test_api_key_2"]  # Default API keys
        
        # Initialize the chatbot
        self.chatbot = AstutelyChatbot(api_key=self.api_key)
        
        # User conversation storage
        self.user_conversations = {}
        
        logger.info("Astutely integration initialized")
    
    def require_api_key(self, f):
        """
        Decorator to require API key authentication.
        """
        def decorated_function(*args, **kwargs):
            if self.require_auth:
                api_key = request.headers.get('X-API-Key')
                if api_key not in self.api_keys:
                    return jsonify({"error": "Invalid API Key"}), 401
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    def register_routes(self):
        """
        Register the Astutely routes with the Flask app.
        """
        # Chat endpoint
        @self.app.route('/chat', methods=['POST'])
        @self.require_api_key
        def chat_endpoint():
            data = request.json
            
            if not data or 'message' not in data:
                return jsonify({"error": "Missing message in request"}), 400
            
            message = data['message']
            user_id = data.get('user_id', 'default_user')
            
            # Get or create user conversation
            if user_id not in self.user_conversations:
                self.user_conversations[user_id] = []
                initial_greeting = self.chatbot.start_new_conversation()
                self.user_conversations[user_id].append({
                    "role": "assistant",
                    "content": initial_greeting
                })
            
            # Process the message
            response = self.chatbot.process_message(message, user_id)
            
            # Store the conversation
            self.user_conversations[user_id].append({
                "role": "user",
                "content": message
            })
            self.user_conversations[user_id].append({
                "role": "assistant",
                "content": response
            })
            
            return jsonify({
                "response": response,
                "conversation_id": user_id
            })
        
        # New conversation endpoint
        @self.app.route('/chat/new', methods=['POST'])
        @self.require_api_key
        def new_chat_endpoint():
            data = request.json
            user_id = data.get('user_id', 'default_user')
            
            # Start a new conversation
            initial_greeting = self.chatbot.start_new_conversation()
            self.user_conversations[user_id] = [{
                "role": "assistant",
                "content": initial_greeting
            }]
            
            return jsonify({
                "response": initial_greeting,
                "conversation_id": user_id
            })
        
        # Get conversation history endpoint
        @self.app.route('/chat/history', methods=['GET'])
        @self.require_api_key
        def chat_history_endpoint():
            user_id = request.args.get('user_id', 'default_user')
            
            if user_id not in self.user_conversations:
                return jsonify({"error": "No conversation found for this user"}), 404
            
            return jsonify({
                "conversation": self.user_conversations[user_id],
                "conversation_id": user_id
            })
        
        logger.info("Astutely routes registered")
        return self

def integrate_with_mcp_server(mcp_app, api_key=None, require_auth=True):
    """
    Integrate Astutely chatbot with an existing MCP server.
    
    Args:
        mcp_app: The Flask app of the MCP server.
        api_key: The Gemini API key. If None, will try to get from environment.
        require_auth: Whether to require API key authentication for endpoints.
        
    Returns:
        The integration instance.
    """
    integration = AstutleyIntegration(app=mcp_app, api_key=api_key, require_auth=require_auth)
    integration.register_routes()
    return integration

# Example of how to use this integration with your MCP server
"""
from flask import Flask
from astutely_integration import integrate_with_mcp_server

# Create your MCP server app
app = Flask(__name__)
CORS(app)

# Add your existing MCP routes here...

# Integrate Astutely chatbot
astutely = integrate_with_mcp_server(app)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
"""

# Standalone Astutely server (for testing)
if __name__ == "__main__":
    # Create a standalone Astutely server
    app = Flask(__name__)
    CORS(app)
    
    integration = AstutleyIntegration(app=app)
    integration.register_routes()
    
    # Basic home endpoint
    @app.route('/')
    def home():
        return jsonify({"message": "Astutely Chatbot Server"})
    
    # Run the server
    print("Starting Astutely Chatbot Server on http://127.0.0.1:5001")
    app.run(host="127.0.0.1", port=5001)
