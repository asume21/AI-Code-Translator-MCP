"""
User Management API for AI Code Translator MCP Server

This module provides API endpoints for user registration, authentication,
and management for the AI Code Translator MCP Server.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from user_management import UserManagement

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("user_api.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize user management
user_mgmt = UserManagement()

def require_auth(f):
    """
    Decorator to require authentication token.
    """
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"success": False, "message": "Authentication token required"}), 401
        
        token = token.split(' ')[1]
        result = user_mgmt.verify_token(token)
        
        if not result["success"]:
            return jsonify({"success": False, "message": result["message"]}), 401
        
        # Add user info to request
        request.user = result["payload"]
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

def setup_user_routes(app):
    """
    Set up user management routes on the given Flask app.
    
    Args:
        app: The Flask app to add routes to.
    """
    # Register user
    @app.route('/api/users/register', methods=['POST'])
    def register():
        data = request.json
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400
        
        result = user_mgmt.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    # Login user
    @app.route('/api/users/login', methods=['POST'])
    def login():
        data = request.json
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        if 'username_or_email' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Missing username/email or password"}), 400
        
        result = user_mgmt.authenticate_user(
            username_or_email=data['username_or_email'],
            password=data['password']
        )
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    
    # Get user profile
    @app.route('/api/users/profile', methods=['GET'])
    @require_auth
    def get_profile():
        user_id = request.user["user_id"]
        
        # This would typically query the database for the user's profile
        # For now, we'll just return the basic user info from the token
        return jsonify({
            "success": True,
            "user_id": user_id,
            "username": request.user["username"],
            "email": request.user["email"]
        }), 200
    
    # Update user profile
    @app.route('/api/users/profile', methods=['PUT'])
    @require_auth
    def update_profile():
        # This would update the user's profile in the database
        # For now, we'll just return success
        return jsonify({
            "success": True,
            "message": "Profile updated successfully"
        }), 200
    
    # Get subscription plans
    @app.route('/api/subscriptions/plans', methods=['GET'])
    def get_plans():
        result = user_mgmt.get_subscription_plans()
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    # Update subscription
    @app.route('/api/subscriptions', methods=['POST'])
    @require_auth
    def update_subscription():
        data = request.json
        
        if not data or 'plan_id' not in data:
            return jsonify({"success": False, "message": "Missing plan_id"}), 400
        
        user_id = request.user["user_id"]
        plan_id = data['plan_id']
        
        result = user_mgmt.update_user_subscription(user_id, plan_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    # Get translation history
    @app.route('/api/translations/history', methods=['GET'])
    @require_auth
    def get_history():
        user_id = request.user["user_id"]
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        result = user_mgmt.get_translation_history(user_id, limit, offset)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    # Check translation limit
    @app.route('/api/translations/limit', methods=['GET'])
    @require_auth
    def check_limit():
        user_id = request.user["user_id"]
        
        result = user_mgmt.check_translation_limit(user_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    logger.info("User management routes set up")
    return app

# Modified API key validation that checks against user database
def validate_api_key(api_key):
    """
    Validate an API key against the user database.
    
    Args:
        api_key: The API key to validate.
        
    Returns:
        A tuple of (is_valid, user_info).
    """
    result = user_mgmt.get_user_by_api_key(api_key)
    
    if result["success"]:
        # Check if user has reached translation limit
        limit_result = user_mgmt.check_translation_limit(result["user_id"])
        if not limit_result["success"]:
            return False, {"error": limit_result["message"], "limit": limit_result["limit"], "used": limit_result["used"]}
        
        return True, result
    else:
        return False, {"error": result["message"]}

# Function to record a translation
def record_translation(user_id, source_code, translated_code, source_lang, target_lang, feedback=None):
    """
    Record a translation in the history.
    
    Args:
        user_id: The ID of the user.
        source_code: The original source code.
        translated_code: The translated code.
        source_lang: The source programming language.
        target_lang: The target programming language.
        feedback: Optional feedback on the translation.
        
    Returns:
        True if successful, False otherwise.
    """
    result = user_mgmt.record_translation(
        user_id=user_id,
        source_code=source_code,
        translated_code=translated_code,
        source_language=source_lang,
        target_language=target_lang,
        feedback=feedback
    )
    
    return result["success"]

# Example of a standalone user management API server
if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app)
    
    # Set up user routes
    setup_user_routes(app)
    
    # Basic home endpoint
    @app.route('/')
    def home():
        return jsonify({"message": "AI Code Translator User Management API"})
    
    # Run the server
    print("Starting User Management API Server on http://127.0.0.1:5002")
    app.run(host="127.0.0.1", port=5002)
