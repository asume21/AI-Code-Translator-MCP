"""
User Management System for AI Code Translator MCP Server (PostgreSQL Version)

This module handles user registration, authentication, and management for the
AI Code Translator MCP Server. It uses PostgreSQL for data storage and JWT for
authentication tokens.
"""

import os
import json
import uuid
import hashlib
import datetime
import logging
import jwt
from typing import Dict, List, Optional, Tuple, Any
from postgres_adapter import PostgresAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("user_management_postgres.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")
TOKEN_EXPIRY_DAYS = 30

class UserManagementPostgres:
    """
    Handles user registration, authentication, and management using PostgreSQL.
    """
    
    def __init__(self):
        """
        Initialize the user management system with PostgreSQL.
        """
        self.db = PostgresAdapter()
        logger.info("User management initialized with PostgreSQL")
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: The password to hash.
            
        Returns:
            The hashed password.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_api_key(self) -> str:
        """
        Generate a unique API key.
        
        Returns:
            A unique API key.
        """
        return str(uuid.uuid4())
    
    def register_user(self, username: str, email: str, password: str, 
                      first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: The username for the new user.
            email: The email for the new user.
            password: The password for the new user.
            first_name: The first name of the user (optional).
            last_name: The last name of the user (optional).
            
        Returns:
            A dictionary with the registration result.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return {"success": False, "message": "Username or email already exists"}
            
            # Create new user
            user_id = str(uuid.uuid4())
            api_key = self._generate_api_key()
            password_hash = self._hash_password(password)
            created_at = datetime.datetime.now()
            
            cursor.execute('''
            INSERT INTO users 
            (id, username, email, password_hash, created_at, account_type, api_key, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                user_id,
                username,
                email,
                password_hash,
                created_at,
                "free",  # Default account type
                api_key,
                True  # Active by default
            ))
            
            # Create user profile
            cursor.execute('''
            INSERT INTO user_profiles 
            (user_id, first_name, last_name)
            VALUES (%s, %s, %s)
            ''', (
                user_id,
                first_name,
                last_name
            ))
            
            # Create default subscription (free plan)
            subscription_id = str(uuid.uuid4())
            start_date = created_at
            end_date = created_at + datetime.timedelta(days=365)  # 1 year by default
            
            cursor.execute('''
            INSERT INTO user_subscriptions 
            (id, user_id, plan_id, start_date, end_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                subscription_id,
                user_id,
                "free",  # Default plan
                start_date,
                end_date,
                True
            ))
            
            conn.commit()
            
            logger.info(f"Registered new user: {username} ({user_id})")
            return {
                "success": True, 
                "user_id": user_id, 
                "api_key": api_key,
                "message": "User registered successfully"
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
        finally:
            conn.close()
    
    def authenticate_user(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and generate a JWT token.
        
        Args:
            username_or_email: The username or email of the user.
            password: The password of the user.
            
        Returns:
            A dictionary with the authentication result.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Find user by username or email
            cursor.execute(
                "SELECT id, username, email, password_hash, is_active FROM users WHERE username = %s OR email = %s", 
                (username_or_email, username_or_email)
            )
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            user_id, username, email, password_hash, is_active = user
            
            if not is_active:
                return {"success": False, "message": "Account is inactive"}
            
            # Verify password
            if password_hash != self._hash_password(password):
                return {"success": False, "message": "Invalid password"}
            
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s", 
                (datetime.datetime.now(), user_id)
            )
            conn.commit()
            
            # Generate JWT token
            payload = {
                "user_id": user_id,
                "username": username,
                "email": email,
                "exp": datetime.datetime.now() + datetime.timedelta(days=TOKEN_EXPIRY_DAYS)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
            logger.info(f"User authenticated: {username} ({user_id})")
            return {"success": True, "token": token, "user_id": user_id}
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
        finally:
            conn.close()
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a JWT token.
        
        Args:
            token: The JWT token to verify.
            
        Returns:
            A dictionary with the verification result.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            # Check if token is expired
            exp = datetime.datetime.fromtimestamp(payload["exp"])
            if exp < datetime.datetime.now():
                return {"success": False, "message": "Token expired"}
            
            return {"success": True, "user": payload}
            
        except jwt.ExpiredSignatureError:
            return {"success": False, "message": "Token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "message": "Invalid token"}
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_user_by_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Get user information by API key.
        
        Args:
            api_key: The API key to look up.
            
        Returns:
            A dictionary with the user information.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Find user by API key
            cursor.execute('''
            SELECT u.id, u.username, u.email, u.account_type, u.is_active,
                   p.first_name, p.last_name
            FROM users u
            LEFT JOIN user_profiles p ON u.id = p.user_id
            WHERE u.api_key = %s
            ''', (api_key,))
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "error": "Invalid API Key"}
            
            user_id, username, email, account_type, is_active, first_name, last_name = user
            
            if not is_active:
                return {"success": False, "error": "Account is inactive"}
            
            # Get subscription info
            cursor.execute('''
            SELECT s.plan_id, p.translation_limit
            FROM user_subscriptions s
            JOIN subscription_plans p ON s.plan_id = p.id
            WHERE s.user_id = %s AND s.is_active = TRUE
            ''', (user_id,))
            subscription = cursor.fetchone()
            
            plan_id = "free"
            translation_limit = 50  # Default limit
            
            if subscription:
                plan_id, translation_limit = subscription
            
            # Get translation count for current month
            first_day = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cursor.execute(
                "SELECT COUNT(*) FROM translation_history WHERE user_id = %s AND timestamp >= %s",
                (user_id, first_day)
            )
            translation_count = cursor.fetchone()[0]
            
            # Calculate translations remaining
            translations_remaining = "unlimited" if translation_limit < 0 else max(0, translation_limit - translation_count)
            
            user_info = {
                "success": True,
                "user_id": user_id,
                "username": username,
                "email": email,
                "account_type": account_type,
                "first_name": first_name,
                "last_name": last_name,
                "plan_id": plan_id,
                "translations_remaining": translations_remaining
            }
            
            return user_info
            
        except Exception as e:
            logger.error(f"Error getting user by API key: {e}")
            return {"success": False, "error": f"Error: {str(e)}"}
        finally:
            conn.close()
    
    def record_translation(self, user_id: str, source_code: str, translated_code: str, 
                          source_language: str, target_language: str, feedback: str = None) -> Dict[str, Any]:
        """
        Record a translation in the history.
        
        Args:
            user_id: The ID of the user.
            source_code: The original source code.
            translated_code: The translated code.
            source_language: The source programming language.
            target_language: The target programming language.
            feedback: Optional feedback on the translation.
            
        Returns:
            A dictionary with the result.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Check if user exists and is active
            cursor.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user or not user[0]:
                return {"success": False, "message": "User not found or inactive"}
            
            # Record translation
            translation_id = str(uuid.uuid4())
            timestamp = datetime.datetime.now()
            
            cursor.execute('''
            INSERT INTO translation_history 
            (id, user_id, source_code, translated_code, source_language, target_language, timestamp, feedback)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                translation_id,
                user_id,
                source_code,
                translated_code,
                source_language,
                target_language,
                timestamp,
                feedback
            ))
            
            conn.commit()
            
            logger.info(f"Recorded translation for user {user_id}: {source_language} to {target_language}")
            return {"success": True, "translation_id": translation_id}
            
        except Exception as e:
            logger.error(f"Error recording translation: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
        finally:
            conn.close()
    
    def get_translation_history(self, user_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get translation history for a user.
        
        Args:
            user_id: The ID of the user.
            limit: The maximum number of records to return.
            offset: The offset for pagination.
            
        Returns:
            A dictionary with the translation history.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Check if user exists and is active
            cursor.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user or not user[0]:
                return {"success": False, "message": "User not found or inactive"}
            
            # Get translation history
            cursor.execute('''
            SELECT id, source_code, translated_code, source_language, target_language, 
                   timestamp, feedback
            FROM translation_history
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
            ''', (user_id, limit, offset))
            
            translations = []
            for row in cursor.fetchall():
                translation_id, source_code, translated_code, source_language, target_language, timestamp, feedback = row
                
                translations.append({
                    "id": translation_id,
                    "source_code": source_code,
                    "translated_code": translated_code,
                    "source_language": source_language,
                    "target_language": target_language,
                    "timestamp": timestamp.isoformat(),
                    "feedback": feedback
                })
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM translation_history WHERE user_id = %s", (user_id,))
            total_count = cursor.fetchone()[0]
            
            return {
                "success": True, 
                "translations": translations,  # Note: Using "translations" instead of "history"
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting translation history: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
        finally:
            conn.close()
    
    def check_translation_limit(self, user_id: str) -> Dict[str, Any]:
        """
        Check if a user has reached their translation limit.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            A dictionary with the result.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Check if user exists and is active
            cursor.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user or not user[0]:
                return {"success": False, "message": "User not found or inactive"}
            
            # Get user's subscription plan
            cursor.execute('''
            SELECT p.translation_limit
            FROM user_subscriptions s
            JOIN subscription_plans p ON s.plan_id = p.id
            WHERE s.user_id = %s AND s.is_active = TRUE
            ''', (user_id,))
            
            subscription = cursor.fetchone()
            
            if not subscription:
                # Default to free plan if no subscription found
                translation_limit = 50
            else:
                translation_limit = subscription[0]
            
            # Unlimited translations
            if translation_limit < 0:
                return {
                    "success": True, 
                    "can_translate": True, 
                    "translations_remaining": "unlimited"
                }
            
            # Get translation count for current month
            first_day = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            cursor.execute(
                "SELECT COUNT(*) FROM translation_history WHERE user_id = %s AND timestamp >= %s",
                (user_id, first_day)
            )
            translation_count = cursor.fetchone()[0]
            
            # Check if limit reached
            translations_remaining = max(0, translation_limit - translation_count)
            can_translate = translations_remaining > 0
            
            return {
                "success": True, 
                "can_translate": can_translate, 
                "translations_remaining": translations_remaining,
                "translation_limit": translation_limit,
                "translation_count": translation_count
            }
            
        except Exception as e:
            logger.error(f"Error checking translation limit: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
        finally:
            conn.close()
    
    def get_subscription_plans(self) -> Dict[str, Any]:
        """
        Get all available subscription plans.
        
        Returns:
            A dictionary with the subscription plans.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT id, name, description, price_monthly, price_yearly, 
                   translation_limit, features
            FROM subscription_plans
            ORDER BY price_monthly
            ''')
            
            plans = []
            for row in cursor.fetchall():
                plan_id, name, description, price_monthly, price_yearly, translation_limit, features = row
                
                plans.append({
                    "id": plan_id,
                    "name": name,
                    "description": description,
                    "price_monthly": price_monthly,
                    "price_yearly": price_yearly,
                    "translation_limit": translation_limit,
                    "features": features
                })
            
            return {"success": True, "plans": plans}
            
        except Exception as e:
            logger.error(f"Error getting subscription plans: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
        finally:
            conn.close()
    
    def update_user_subscription(self, user_id: str, plan_id: str) -> Dict[str, Any]:
        """
        Update a user's subscription plan.
        
        Args:
            user_id: The ID of the user.
            plan_id: The ID of the new subscription plan.
            
        Returns:
            A dictionary with the result.
        """
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()
            
            # Check if user exists and is active
            cursor.execute("SELECT is_active FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user or not user[0]:
                return {"success": False, "message": "User not found or inactive"}
            
            # Check if plan exists
            cursor.execute("SELECT id FROM subscription_plans WHERE id = %s", (plan_id,))
            plan = cursor.fetchone()
            
            if not plan:
                return {"success": False, "message": "Subscription plan not found"}
            
            # Update user's account type based on plan
            cursor.execute("SELECT name FROM subscription_plans WHERE id = %s", (plan_id,))
            plan_name = cursor.fetchone()[0].lower()
            
            cursor.execute("UPDATE users SET account_type = %s WHERE id = %s", (plan_name, user_id))
            
            # Deactivate current subscription
            cursor.execute("""
            UPDATE user_subscriptions
            SET is_active = FALSE
            WHERE user_id = %s AND is_active = TRUE
            """, (user_id,))
            
            # Create new subscription
            subscription_id = str(uuid.uuid4())
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(days=365)
            
            cursor.execute('''
            INSERT INTO user_subscriptions 
            (id, user_id, plan_id, start_date, end_date, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                subscription_id,
                user_id,
                plan_id,
                start_date,
                end_date,
                True
            ))
            
            conn.commit()
            
            logger.info(f"Updated subscription for user {user_id} to plan {plan_id}")
            return {
                "success": True, 
                "message": "Subscription updated successfully", 
                "subscription_id": subscription_id
            }
            
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
        finally:
            conn.close()

# Example usage
if __name__ == "__main__":
    # This code runs when the module is executed directly
    try:
        user_mgmt = UserManagementPostgres()
        print("PostgreSQL user management initialized successfully")
    except Exception as e:
        print(f"Error initializing PostgreSQL user management: {e}")
