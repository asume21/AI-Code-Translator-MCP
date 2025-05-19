"""
Payment Processing for AI Code Translator

This module handles subscription payments using Stripe.
"""

import os
import logging
import stripe
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("payment_processing.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PaymentProcessor:
    """
    Handles payment processing and subscription management.
    """
    
    def __init__(self, stripe_api_key: Optional[str] = None, db_connection = None):
        """
        Initialize the payment processor.
        
        Args:
            stripe_api_key: The Stripe API key. If None, will try to get from environment.
            db_connection: Database connection for user management.
        """
        self.stripe_api_key = stripe_api_key or os.environ.get("STRIPE_API_KEY")
        if not self.stripe_api_key:
            logger.warning("Stripe API key not set. Payment processing will be in test mode.")
            self.test_mode = True
        else:
            stripe.api_key = self.stripe_api_key
            self.test_mode = False
        
        self.db_connection = db_connection
        logger.info(f"Payment processor initialized in {'test' if self.test_mode else 'live'} mode")
        
        # Subscription plans
        self.plans = {
            "free": {
                "name": "Free",
                "price": 0,
                "features": {
                    "translations_per_month": 50,
                    "vulnerability_scan": "quick",
                    "history_retention_days": 30,
                    "support": "community"
                }
            },
            "professional": {
                "name": "Professional",
                "price": 9.99,
                "features": {
                    "translations_per_month": 500,
                    "vulnerability_scan": "full",
                    "history_retention_days": 90,
                    "support": "email"
                }
            },
            "enterprise": {
                "name": "Enterprise",
                "price": 29.99,
                "features": {
                    "translations_per_month": 5000,
                    "vulnerability_scan": "full",
                    "history_retention_days": 365,
                    "support": "priority"
                }
            }
        }
    
    def get_subscription_plans(self) -> Dict[str, Any]:
        """
        Get available subscription plans.
        
        Returns:
            The subscription plans.
        """
        return {
            "success": True,
            "plans": self.plans
        }
    
    def create_checkout_session(self, plan_id: str, user_id: str) -> Dict[str, Any]:
        """
        Create a Stripe checkout session for subscription.
        
        Args:
            plan_id: The subscription plan ID.
            user_id: The user ID.
            
        Returns:
            The checkout session details.
        """
        if self.test_mode:
            # Simulate checkout in test mode
            return {
                "success": True,
                "checkout_url": f"https://example.com/checkout?plan={plan_id}&user={user_id}",
                "session_id": f"test_session_{plan_id}_{user_id}"
            }
        
        try:
            plan = self.plans.get(plan_id)
            if not plan:
                return {"success": False, "message": "Invalid plan ID"}
            
            if plan["price"] == 0:
                # Free plan doesn't need checkout
                self._update_user_subscription(user_id, plan_id)
                return {"success": True, "message": "Subscribed to free plan"}
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"AI Code Translator - {plan['name']} Plan",
                            "description": f"Monthly subscription to {plan['name']} plan"
                        },
                        "unit_amount": int(plan["price"] * 100),  # Stripe uses cents
                        "recurring": {
                            "interval": "month"
                        }
                    },
                    "quantity": 1
                }],
                mode="subscription",
                success_url="https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="https://your-domain.com/cancel",
                client_reference_id=user_id,
                metadata={
                    "plan_id": plan_id,
                    "user_id": user_id
                }
            )
            
            return {
                "success": True,
                "checkout_url": session.url,
                "session_id": session.id
            }
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Handle Stripe webhook events.
        
        Args:
            payload: The webhook payload.
            signature: The webhook signature.
            
        Returns:
            The webhook handling result.
        """
        if self.test_mode:
            # Simulate webhook in test mode
            return {"success": True, "message": "Webhook received in test mode"}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, os.environ.get("STRIPE_WEBHOOK_SECRET")
            )
            
            # Handle the event
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                user_id = session["client_reference_id"]
                plan_id = session["metadata"]["plan_id"]
                
                # Update user subscription
                self._update_user_subscription(user_id, plan_id)
                
                logger.info(f"User {user_id} subscribed to {plan_id} plan")
                
            elif event["type"] == "customer.subscription.deleted":
                subscription = event["data"]["object"]
                user_id = subscription["metadata"]["user_id"]
                
                # Downgrade user to free plan
                self._update_user_subscription(user_id, "free")
                
                logger.info(f"User {user_id} subscription cancelled, downgraded to free plan")
            
            return {"success": True, "message": f"Webhook handled: {event['type']}"}
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def _update_user_subscription(self, user_id: str, plan_id: str) -> bool:
        """
        Update user subscription in the database.
        
        Args:
            user_id: The user ID.
            plan_id: The subscription plan ID.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            if not self.db_connection:
                logger.warning("No database connection provided, can't update subscription")
                return False
            
            cursor = self.db_connection.cursor()
            
            # Update user subscription
            cursor.execute(
                "UPDATE users SET subscription_plan = ?, updated_at = ? WHERE user_id = ?",
                (plan_id, datetime.now().isoformat(), user_id)
            )
            
            # Reset translation count if upgrading
            cursor.execute(
                "UPDATE users SET translations_used = 0 WHERE user_id = ?",
                (user_id,)
            )
            
            self.db_connection.commit()
            logger.info(f"Updated subscription for user {user_id} to {plan_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user subscription: {e}")
            return False
    
    def get_user_subscription(self, user_id: str) -> Dict[str, Any]:
        """
        Get user subscription details.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The subscription details.
        """
        try:
            if not self.db_connection:
                logger.warning("No database connection provided, can't get subscription")
                return {"success": False, "message": "Database connection not available"}
            
            cursor = self.db_connection.cursor()
            
            # Get user subscription
            cursor.execute(
                "SELECT subscription_plan, translations_used FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "message": "User not found"}
            
            plan_id, translations_used = result
            plan = self.plans.get(plan_id, self.plans["free"])
            
            translations_limit = plan["features"]["translations_per_month"]
            translations_remaining = max(0, translations_limit - translations_used)
            
            return {
                "success": True,
                "subscription": {
                    "plan_id": plan_id,
                    "plan_name": plan["name"],
                    "price": plan["price"],
                    "features": plan["features"],
                    "translations_used": translations_used,
                    "translations_limit": translations_limit,
                    "translations_remaining": translations_remaining
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user subscription: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def record_translation(self, user_id: str) -> Dict[str, Any]:
        """
        Record a translation usage for a user.
        
        Args:
            user_id: The user ID.
            
        Returns:
            The updated translation count and limit.
        """
        try:
            if not self.db_connection:
                logger.warning("No database connection provided, can't record translation")
                return {"success": False, "message": "Database connection not available"}
            
            cursor = self.db_connection.cursor()
            
            # Get user subscription
            cursor.execute(
                "SELECT subscription_plan, translations_used FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            result = cursor.fetchone()
            
            if not result:
                return {"success": False, "message": "User not found"}
            
            plan_id, translations_used = result
            plan = self.plans.get(plan_id, self.plans["free"])
            
            translations_limit = plan["features"]["translations_per_month"]
            
            # Check if user has reached the limit
            if translations_used >= translations_limit:
                return {
                    "success": False,
                    "message": "Translation limit reached",
                    "translations_used": translations_used,
                    "translations_limit": translations_limit,
                    "translations_remaining": 0
                }
            
            # Increment translation count
            cursor.execute(
                "UPDATE users SET translations_used = translations_used + 1 WHERE user_id = ?",
                (user_id,)
            )
            
            self.db_connection.commit()
            
            # Get updated count
            translations_used += 1
            translations_remaining = max(0, translations_limit - translations_used)
            
            return {
                "success": True,
                "translations_used": translations_used,
                "translations_limit": translations_limit,
                "translations_remaining": translations_remaining
            }
            
        except Exception as e:
            logger.error(f"Error recording translation: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

# Example usage
if __name__ == "__main__":
    # This code runs when the module is executed directly
    processor = PaymentProcessor()
    
    # Get subscription plans
    plans = processor.get_subscription_plans()
    print("Subscription Plans:")
    for plan_id, plan in plans["plans"].items():
        print(f"- {plan['name']}: ${plan['price']}/month")
        for feature, value in plan["features"].items():
            print(f"  - {feature}: {value}")
        print()
    
    # Create checkout session (test mode)
    checkout = processor.create_checkout_session("professional", "user123")
    print(f"Checkout URL: {checkout.get('checkout_url')}")
