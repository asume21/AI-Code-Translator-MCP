"""
User Management System for AI Code Translator MCP Server

This module handles user registration, authentication, and management for the
AI Code Translator MCP Server. It uses SQLite for data storage and JWT for
authentication tokens.
"""

import os
import json
import sqlite3
import uuid
import hashlib
import datetime
import logging
import jwt
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("user_management.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
DATABASE_PATH = "users.db"
JWT_SECRET = os.environ.get("JWT_SECRET", "your-secret-key-change-in-production")
TOKEN_EXPIRY_DAYS = 30

class UserManagement:
    """
    Handles user registration, authentication, and management.
    """
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """
        Initialize the user management system.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()
        logger.info(f"User management initialized with database: {db_path}")
    
    def _init_db(self):
        """
        Initialize the database with necessary tables.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT,
            account_type TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            is_active INTEGER NOT NULL
        )
        ''')
        
        # Create user_profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            company TEXT,
            website TEXT,
            preferences TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create translation_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS translation_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            source_code TEXT NOT NULL,
            translated_code TEXT NOT NULL,
            source_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            feedback TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Create subscription_plans table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price_monthly REAL NOT NULL,
            price_yearly REAL NOT NULL,
            translation_limit INTEGER NOT NULL,
            features TEXT NOT NULL
        )
        ''')
        
        # Create user_subscriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            is_active INTEGER NOT NULL,
            payment_method TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (plan_id) REFERENCES subscription_plans (id)
        )
        ''')
        
        # Create default subscription plans if they don't exist
        cursor.execute("SELECT COUNT(*) FROM subscription_plans")
        if cursor.fetchone()[0] == 0:
            self._create_default_plans(cursor)
        
        conn.commit()
        conn.close()
    
    def _create_default_plans(self, cursor):
        """
        Create default subscription plans.
        """
        plans = [
            {
                "id": str(uuid.uuid4()),
                "name": "Free",
                "description": "Basic translation features with limited usage",
                "price_monthly": 0.0,
                "price_yearly": 0.0,
                "translation_limit": 100,
                "features": json.dumps(["Basic code translation", "5 programming languages", "Standard response time"])
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Professional",
                "description": "Advanced features for professional developers",
                "price_monthly": 9.99,
                "price_yearly": 99.99,
                "translation_limit": 1000,
                "features": json.dumps([
                    "Advanced code translation", 
                    "All programming languages", 
                    "Priority response time", 
                    "Translation history", 
                    "Code optimization suggestions"
                ])
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Enterprise",
                "description": "Full-featured solution for teams and businesses",
                "price_monthly": 29.99,
                "price_yearly": 299.99,
                "translation_limit": 10000,
                "features": json.dumps([
                    "Premium code translation", 
                    "All programming languages", 
                    "Fastest response time", 
                    "Unlimited translation history", 
                    "Advanced code optimization", 
                    "Team collaboration", 
                    "Custom integrations", 
                    "Dedicated support"
                ])
            }
        ]
        
        for plan in plans:
            cursor.execute('''
            INSERT INTO subscription_plans 
            (id, name, description, price_monthly, price_yearly, translation_limit, features)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                plan["id"], 
                plan["name"], 
                plan["description"], 
                plan["price_monthly"], 
                plan["price_yearly"], 
                plan["translation_limit"], 
                plan["features"]
            ))
        
        logger.info("Created default subscription plans")
    
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                return {"success": False, "message": "Username or email already exists"}
            
            # Create user
            user_id = str(uuid.uuid4())
            now = datetime.datetime.now().isoformat()
            api_key = self._generate_api_key()
            
            cursor.execute('''
            INSERT INTO users 
            (id, username, email, password_hash, created_at, account_type, api_key, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, 
                username, 
                email, 
                self._hash_password(password), 
                now, 
                "free", 
                api_key, 
                1
            ))
            
            # Create user profile
            cursor.execute('''
            INSERT INTO user_profiles 
            (user_id, first_name, last_name)
            VALUES (?, ?, ?)
            ''', (
                user_id, 
                first_name, 
                last_name
            ))
            
            # Assign free subscription plan
            cursor.execute("SELECT id FROM subscription_plans WHERE name = 'Free'")
            plan_id = cursor.fetchone()[0]
            
            start_date = now
            end_date = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
            
            cursor.execute('''
            INSERT INTO user_subscriptions 
            (id, user_id, plan_id, start_date, end_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                user_id,
                plan_id,
                start_date,
                end_date,
                1
            ))
            
            conn.commit()
            
            logger.info(f"Registered new user: {username}")
            return {
                "success": True, 
                "message": "User registered successfully", 
                "user_id": user_id,
                "api_key": api_key
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find user by username or email
            cursor.execute(
                "SELECT id, username, email, password_hash, api_key FROM users WHERE username = ? OR email = ?", 
                (username_or_email, username_or_email)
            )
            user = cursor.fetchone()
            
            if not user or user[3] != self._hash_password(password):
                return {"success": False, "message": "Invalid username/email or password"}
            
            # Update last login
            now = datetime.datetime.now().isoformat()
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user[0]))
            conn.commit()
            
            # Generate JWT token
            payload = {
                "user_id": user[0],
                "username": user[1],
                "email": user[2],
                "exp": datetime.datetime.now() + datetime.timedelta(days=TOKEN_EXPIRY_DAYS)
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
            logger.info(f"User authenticated: {user[1]}")
            return {
                "success": True, 
                "message": "Authentication successful", 
                "token": token,
                "user_id": user[0],
                "username": user[1],
                "email": user[2],
                "api_key": user[4]
            }
            
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
            exp_datetime = datetime.datetime.fromtimestamp(payload["exp"])
            if datetime.datetime.now() > exp_datetime:
                return {"success": False, "message": "Token expired"}
            
            return {"success": True, "message": "Token valid", "payload": payload}
            
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT u.id, u.username, u.email, u.account_type, u.is_active, 
                   s.name as subscription_plan, s.translation_limit
            FROM users u
            JOIN user_subscriptions us ON u.id = us.user_id
            JOIN subscription_plans s ON us.plan_id = s.id
            WHERE u.api_key = ? AND u.is_active = 1 AND us.is_active = 1
            """, (api_key,))
            
            user = cursor.fetchone()
            
            if not user:
                return {"success": False, "message": "Invalid or inactive API key"}
            
            # Get translation count for the current month
            first_day = datetime.datetime.now().replace(day=1).isoformat()
            cursor.execute("""
            SELECT COUNT(*) FROM translation_history
            WHERE user_id = ? AND timestamp >= ?
            """, (user[0], first_day))
            
            translation_count = cursor.fetchone()[0]
            
            return {
                "success": True,
                "user_id": user[0],
                "username": user[1],
                "email": user[2],
                "account_type": user[3],
                "subscription_plan": user[5],
                "translation_limit": user[6],
                "translations_used": translation_count,
                "translations_remaining": max(0, user[6] - translation_count)
            }
            
        except Exception as e:
            logger.error(f"Error getting user by API key: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists and is active
            cursor.execute("SELECT is_active FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user or not user[0]:
                return {"success": False, "message": "User not found or inactive"}
            
            # Check if user has reached their translation limit
            result = self.check_translation_limit(user_id)
            if not result["success"]:
                return result
            
            # Record the translation
            translation_id = str(uuid.uuid4())
            now = datetime.datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO translation_history 
            (id, user_id, source_code, translated_code, source_language, target_language, timestamp, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                translation_id,
                user_id,
                source_code,
                translated_code,
                source_language,
                target_language,
                now,
                feedback
            ))
            
            conn.commit()
            
            logger.info(f"Recorded translation for user {user_id}: {source_language} to {target_language}")
            return {
                "success": True, 
                "message": "Translation recorded successfully", 
                "translation_id": translation_id
            }
            
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
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # This enables column access by name
            cursor = conn.cursor()
            
            # Check if user exists and is active
            cursor.execute("SELECT is_active FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user or not user[0]:
                return {"success": False, "message": "User not found or inactive"}
            
            # Get translation history
            cursor.execute("""
            SELECT id, source_code, translated_code, source_language, target_language, timestamp, feedback
            FROM translation_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            
            history = [dict(row) for row in cursor.fetchall()]
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM translation_history WHERE user_id = ?", (user_id,))
            total_count = cursor.fetchone()[0]
            
            return {
                "success": True,
                "translations": history,
                "total_count": total_count,
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user's subscription plan and translation limit
            cursor.execute("""
            SELECT s.translation_limit
            FROM users u
            JOIN user_subscriptions us ON u.id = us.user_id
            JOIN subscription_plans s ON us.plan_id = s.id
            WHERE u.id = ? AND u.is_active = 1 AND us.is_active = 1
            """, (user_id,))
            
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "message": "User has no active subscription"}
            
            translation_limit = result[0]
            
            # Get translation count for the current month
            first_day = datetime.datetime.now().replace(day=1).isoformat()
            cursor.execute("""
            SELECT COUNT(*) FROM translation_history
            WHERE user_id = ? AND timestamp >= ?
            """, (user_id, first_day))
            
            translation_count = cursor.fetchone()[0]
            
            if translation_count >= translation_limit:
                return {
                    "success": False, 
                    "message": "Translation limit reached", 
                    "limit": translation_limit,
                    "used": translation_count
                }
            
            return {
                "success": True,
                "message": "Translation limit not reached",
                "limit": translation_limit,
                "used": translation_count,
                "remaining": translation_limit - translation_count
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
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, name, description, price_monthly, price_yearly, translation_limit, features
            FROM subscription_plans
            ORDER BY price_monthly
            """)
            
            plans = []
            for row in cursor.fetchall():
                plan = dict(row)
                plan["features"] = json.loads(plan["features"])
                plans.append(plan)
            
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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists and is active
            cursor.execute("SELECT is_active FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            
            if not user or not user[0]:
                return {"success": False, "message": "User not found or inactive"}
            
            # Check if plan exists
            cursor.execute("SELECT id FROM subscription_plans WHERE id = ?", (plan_id,))
            plan = cursor.fetchone()
            
            if not plan:
                return {"success": False, "message": "Subscription plan not found"}
            
            # Update user's account type based on plan
            cursor.execute("SELECT name FROM subscription_plans WHERE id = ?", (plan_id,))
            plan_name = cursor.fetchone()[0].lower()
            
            cursor.execute("UPDATE users SET account_type = ? WHERE id = ?", (plan_name, user_id))
            
            # Deactivate current subscription
            cursor.execute("""
            UPDATE user_subscriptions
            SET is_active = 0
            WHERE user_id = ? AND is_active = 1
            """, (user_id,))
            
            # Create new subscription
            subscription_id = str(uuid.uuid4())
            start_date = datetime.datetime.now().isoformat()
            end_date = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
            
            cursor.execute('''
            INSERT INTO user_subscriptions 
            (id, user_id, plan_id, start_date, end_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                subscription_id,
                user_id,
                plan_id,
                start_date,
                end_date,
                1
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
    user_mgmt = UserManagement()
    
    # Example: Register a new user
    result = user_mgmt.register_user(
        username="test_user",
        email="test@example.com",
        password="password123",
        first_name="Test",
        last_name="User"
    )
    print("Registration result:", result)
    
    # Example: Authenticate user
    auth_result = user_mgmt.authenticate_user("test_user", "password123")
    print("Authentication result:", auth_result)
    
    # Example: Verify token
    if auth_result["success"]:
        verify_result = user_mgmt.verify_token(auth_result["token"])
        print("Token verification result:", verify_result)
    
    # Example: Get subscription plans
    plans_result = user_mgmt.get_subscription_plans()
    print("Subscription plans:", plans_result)
