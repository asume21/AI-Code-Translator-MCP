"""
PostgreSQL Adapter for AI Code Translator MCP Server

This module provides a PostgreSQL adapter for the User Management system,
replacing the SQLite database with a production-ready PostgreSQL database.
"""

import os
import json
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("postgres_adapter.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PostgresAdapter:
    """
    PostgreSQL adapter for the User Management system.
    """
    
    def __init__(self):
        """
        Initialize the PostgreSQL adapter.
        """
        self.db_url = os.environ.get("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        logger.info("PostgreSQL adapter initialized")
        self._init_db()
    
    def _get_connection(self):
        """
        Get a connection to the PostgreSQL database.
        
        Returns:
            A connection to the PostgreSQL database.
        """
        return psycopg2.connect(self.db_url)
    
    def _init_db(self):
        """
        Initialize the database with necessary tables.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            last_login TIMESTAMP,
            account_type TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            is_active BOOLEAN NOT NULL
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
            preferences JSONB,
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
            timestamp TIMESTAMP NOT NULL,
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
            features JSONB NOT NULL
        )
        ''')
        
        # Create user_subscriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            is_active BOOLEAN NOT NULL,
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
        
        logger.info("Database initialized with all required tables")
    
    def _create_default_plans(self, cursor):
        """
        Create default subscription plans.
        
        Args:
            cursor: Database cursor.
        """
        # Free plan
        free_features = json.dumps([
            "Basic code translation",
            "Limited to 50 translations per month",
            "Standard response time"
        ])
        
        cursor.execute('''
        INSERT INTO subscription_plans 
        (id, name, description, price_monthly, price_yearly, translation_limit, features)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            "free",
            "Free",
            "Basic plan with limited translations",
            0.0,
            0.0,
            50,
            free_features
        ))
        
        # Pro plan
        pro_features = json.dumps([
            "Advanced code translation",
            "Unlimited translations",
            "Priority response time",
            "Access to all programming languages",
            "Code vulnerability scanning"
        ])
        
        cursor.execute('''
        INSERT INTO subscription_plans 
        (id, name, description, price_monthly, price_yearly, translation_limit, features)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            "pro",
            "Professional",
            "Professional plan with unlimited translations",
            9.99,
            99.99,
            -1,  # -1 means unlimited
            pro_features
        ))
        
        # Enterprise plan
        enterprise_features = json.dumps([
            "All Pro features",
            "Custom API integration",
            "Dedicated support",
            "Team management",
            "Custom model training",
            "SLA guarantees"
        ])
        
        cursor.execute('''
        INSERT INTO subscription_plans 
        (id, name, description, price_monthly, price_yearly, translation_limit, features)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            "enterprise",
            "Enterprise",
            "Enterprise plan with custom features",
            49.99,
            499.99,
            -1,  # -1 means unlimited
            enterprise_features
        ))
        
        logger.info("Created default subscription plans")

# Example usage
if __name__ == "__main__":
    # This code runs when the module is executed directly
    try:
        postgres = PostgresAdapter()
        print("PostgreSQL adapter initialized successfully")
    except Exception as e:
        print(f"Error initializing PostgreSQL adapter: {e}")
