"""
Fix for serving static files in the AI Code Translator MCP Server.

This script adds routes to serve the integrated demo HTML file and other static files.
"""

import os
import sys
import logging
from flask import Flask, send_from_directory, render_template, send_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("static_files_fix.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def add_static_routes(app):
    """
    Add routes to serve static files and the integrated demo HTML file.
    
    Args:
        app: The Flask app to add routes to.
    """
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
    
    logger.info("Added static file routes")
    return app

if __name__ == "__main__":
    print("This script is meant to be imported, not run directly.")
