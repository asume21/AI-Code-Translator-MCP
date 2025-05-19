"""
Render deployment app for AI Code Translator MCP Server.

This file is specifically for Render.com deployment to ensure static files
are served correctly.
"""

import os
import sys
import logging
from flask import Flask, send_from_directory, send_file
from simple_mcp_server import app as mcp_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("render_app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create a new Flask app that wraps the MCP app
app = mcp_app

# Add routes for static files
@app.route('/integrated_demo.html')
def integrated_demo():
    try:
        return send_file('integrated_demo.html')
    except Exception as e:
        logger.error(f"Error serving integrated_demo.html: {e}")
        return f"Error: {str(e)}", 500

@app.route('/ai_money_maker.html')
def ai_money_maker():
    try:
        return send_file('ai_money_maker.html')
    except Exception as e:
        logger.error(f"Error serving ai_money_maker.html: {e}")
        return f"Error: {str(e)}", 500

@app.route('/static/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('static', path)
    except Exception as e:
        logger.error(f"Error serving static file {path}: {e}")
        return f"Error: {str(e)}", 500

# Log that the app is ready
logger.info("Render app is ready with static file routes")

if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Render app on port {port}")
    app.run(host='0.0.0.0', port=port)
