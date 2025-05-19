"""
User API for AI Code Translator MCP Server (PostgreSQL Version)

This module provides API endpoints for user registration, authentication, and management
using the PostgreSQL-based user management system.
"""

import os
import logging
from flask import request, jsonify, Blueprint
from user_management_postgres import UserManagementPostgres

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("user_api_postgres.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize user management
user_mgmt = UserManagementPostgres()

# Create blueprint
user_api = Blueprint('user_api', __name__)

def validate_api_key(api_key):
    """
    Validate an API key and return user information.
    
    Args:
        api_key: The API key to validate.
        
    Returns:
        A tuple of (is_valid, user_info).
    """
    if not api_key:
        return False, {"error": "API Key is required"}
    
    user_info = user_mgmt.get_user_by_api_key(api_key)
    
    if not user_info.get("success", False):
        return False, user_info
    
    return True, user_info

def record_translation(user_id, source_code, translated_code, source_lang, target_lang, feedback=None):
    """
    Record a translation in the user's history.
    
    Args:
        user_id: The ID of the user.
        source_code: The original source code.
        translated_code: The translated code.
        source_lang: The source programming language.
        target_lang: The target programming language.
        feedback: Optional feedback on the translation.
        
    Returns:
        A dictionary with the result.
    """
    return user_mgmt.record_translation(
        user_id=user_id,
        source_code=source_code,
        translated_code=translated_code,
        source_language=source_lang,
        target_language=target_lang,
        feedback=feedback
    )

def setup_user_routes(app):
    """
    Set up user management routes on the Flask app.
    
    Args:
        app: The Flask app to set up routes on.
    """
    # Register blueprint
    app.register_blueprint(user_api, url_prefix='/user')
    
    @user_api.route('/register', methods=['POST'])
    def register():
        data = request.json
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400
        
        # Register user
        result = user_mgmt.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    @user_api.route('/login', methods=['POST'])
    def login():
        data = request.json
        
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        # Required fields
        if 'username_or_email' not in data or 'password' not in data:
            return jsonify({"success": False, "message": "Missing username_or_email or password"}), 400
        
        # Authenticate user
        result = user_mgmt.authenticate_user(
            username_or_email=data['username_or_email'],
            password=data['password']
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    
    @user_api.route('/verify_token', methods=['POST'])
    def verify_token():
        data = request.json
        
        if not data or 'token' not in data:
            return jsonify({"success": False, "message": "No token provided"}), 400
        
        # Verify token
        result = user_mgmt.verify_token(data['token'])
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 401
    
    @user_api.route('/subscription_plans', methods=['GET'])
    def subscription_plans():
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        is_valid, user_info = validate_api_key(api_key)
        
        if not is_valid:
            return jsonify(user_info), 401
        
        # Get subscription plans
        result = user_mgmt.get_subscription_plans()
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    @user_api.route('/update_subscription', methods=['POST'])
    def update_subscription():
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        is_valid, user_info = validate_api_key(api_key)
        
        if not is_valid:
            return jsonify(user_info), 401
        
        data = request.json
        
        if not data or 'plan_id' not in data:
            return jsonify({"success": False, "message": "No plan_id provided"}), 400
        
        # Update subscription
        result = user_mgmt.update_user_subscription(
            user_id=user_info['user_id'],
            plan_id=data['plan_id']
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    @user_api.route('/translation_history', methods=['GET'])
    def translation_history():
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        is_valid, user_info = validate_api_key(api_key)
        
        if not is_valid:
            return jsonify(user_info), 401
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get translation history
        result = user_mgmt.get_translation_history(
            user_id=user_info['user_id'],
            limit=limit,
            offset=offset
        )
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    @user_api.route('/check_limit', methods=['GET'])
    def check_limit():
        # Get API key from header
        api_key = request.headers.get('X-API-Key')
        is_valid, user_info = validate_api_key(api_key)
        
        if not is_valid:
            return jsonify(user_info), 401
        
        # Check translation limit
        result = user_mgmt.check_translation_limit(user_info['user_id'])
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    logger.info("User routes set up successfully")
    return user_api
