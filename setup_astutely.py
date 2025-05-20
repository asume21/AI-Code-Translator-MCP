"""
Setup function for Astutely chatbot integration with MCP server.

This module provides a clean way to integrate the Astutely chatbot
with the MCP server.
"""

import os
import logging
from flask import request, jsonify
from astutely_chatbot import AstutelyChatbot
from user_management import UserManagement

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("astutely_setup.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_astutely_routes(app, astutely_chatbot, require_api_key):
    """
    Set up Astutely chatbot routes on the given Flask app.
    
    Args:
        app: The Flask app to add routes to.
        astutely_chatbot: The AstutelyChatbot instance or None if not available.
        require_api_key: The API key authentication decorator.
    """
    # User conversation storage
    user_conversations = {}
    
    if astutely_chatbot is None:
        logger.warning("Astutely chatbot is not initialized. Chat functionality will be disabled.")
        
        @app.route('/astutely/chat', methods=['POST'])
        @require_api_key
        def astutely_chat_endpoint_disabled():
            return jsonify({
                "error": "Astutely chatbot is not available. Please check your GEMINI_API_KEY environment variable.",
                "status": "disabled"
            }), 503
            
        logger.info("Added disabled Astutely chat endpoint")
        return
    
    # Chat endpoint
    @app.route('/astutely/chat', methods=['POST'])
    @require_api_key
    def astutely_chat_endpoint():
        data = request.json
        
        if not data or 'message' not in data:
            return jsonify({"error": "Missing message in request"}), 400
        
        message = data['message']
        conversation_id = data.get('conversation_id')
        
        # Get user ID from request context (set by require_api_key decorator)
        user_id = request.user_info.get('user_id', 'default_user')
        
        # Create a unique conversation ID if not provided
        if not conversation_id:
            conversation_id = f"{user_id}_conv_{len(user_conversations) + 1}"
            # Start a new conversation in the chatbot
            initial_greeting = astutely_chatbot.start_new_conversation()
            # Initialize the conversation history in our server-side storage
            user_conversations[conversation_id] = [
                {"role": "assistant", "content": initial_greeting}
            ]
            # Return the initial greeting immediately
            return jsonify({
                "response": initial_greeting,
                "conversation_id": conversation_id
            })
        
        # Get or create user conversation
        if conversation_id not in user_conversations:
            # This is a conversation ID we don't recognize, create a new one
            conversation_id = f"{user_id}_conv_{len(user_conversations) + 1}"
            initial_greeting = astutely_chatbot.start_new_conversation()
            user_conversations[conversation_id] = [
                {"role": "assistant", "content": initial_greeting}
            ]
        
        # Load the conversation history into the chatbot
        astutely_chatbot.conversation_history = user_conversations[conversation_id].copy()
        
        # Process the message
        try:
            # Add user message to conversation history
            user_conversations[conversation_id].append({"role": "user", "content": message})
            
            # Process the message with the chatbot
            response = astutely_chatbot.process_message(message, user_id)
            
            # Add assistant response to conversation history
            user_conversations[conversation_id].append({"role": "assistant", "content": response})
            
            # Keep conversation history manageable
            if len(user_conversations[conversation_id]) > 20:
                user_conversations[conversation_id] = user_conversations[conversation_id][-20:]
            
            # Record chat in user history if applicable
            try:
                # This would typically call a function to record the chat in the user's history
                logger.info(f"Recorded chat for user {user_id}")
            except Exception as e:
                logger.error(f"Error recording chat: {e}")
            
            return jsonify({
                "response": response,
                "conversation_id": conversation_id
            })
        except Exception as e:
            logger.error(f"Error in chat processing: {e}")
            return jsonify({
                "response": "I'm sorry, I encountered an error while processing your message. Could you try rephrasing or try again later?",
                "conversation_id": conversation_id,
                "error": str(e)
            }), 500
    
    # New conversation endpoint
    @app.route('/astutely/chat/new', methods=['POST'])
    @require_api_key
    def astutely_new_chat_endpoint():
        # Get user ID from request context (set by require_api_key decorator)
        user_id = request.user_info.get('user_id', 'default_user')
        
        # Create a unique conversation ID
        conversation_id = f"{user_id}_conv_{len(user_conversations) + 1}"
        
        # Start a new conversation
        initial_greeting = astutely_chatbot.start_new_conversation()
        user_conversations[conversation_id] = [{
            "role": "assistant",
            "content": initial_greeting
        }]
        
        return jsonify({
            "response": initial_greeting,
            "conversation_id": conversation_id
        })
    
    # Get conversation history endpoint
    @app.route('/astutely/chat/history', methods=['GET'])
    @require_api_key
    def astutely_chat_history_endpoint():
        # Get user ID from request context (set by require_api_key decorator)
        user_id = request.user_info.get('user_id', 'default_user')
        
        # Get conversation ID from query parameters
        conversation_id = request.args.get('conversation_id')
        
        if not conversation_id:
            # Return all conversations for the user
            user_convs = {k: v for k, v in user_conversations.items() if k.startswith(f"{user_id}_")}
            return jsonify({
                "conversations": user_convs
            })
        
        if conversation_id not in user_conversations:
            return jsonify({"error": "No conversation found with this ID"}), 404
        
        return jsonify({
            "conversation": user_conversations[conversation_id],
            "conversation_id": conversation_id
        })
    
    logger.info("Astutely routes set up")
    return app
