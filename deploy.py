#!/usr/bin/env python
"""
Deployment script for AI Code Translator MCP Server

This script helps deploy the AI Code Translator to various hosting platforms.
Currently supported platforms:
- Render.com
- Heroku
- Netlify
"""

import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path

# Configure argument parser
parser = argparse.ArgumentParser(description='Deploy AI Code Translator to a hosting platform')
parser.add_argument('--platform', choices=['render', 'heroku', 'netlify'], default='render',
                    help='The platform to deploy to (default: render)')
parser.add_argument('--api-key', help='Your Gemini API key')
parser.add_argument('--jwt-secret', help='JWT secret for authentication')
parser.add_argument('--stripe-key', help='Stripe API key for payments')
parser.add_argument('--setup-only', action='store_true', help='Only set up deployment files without deploying')
parser.add_argument('--debug', action='store_true', help='Enable debug output')

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message, level='info'):
    """Log a message with appropriate formatting."""
    prefix = {
        'info': f"{Colors.BLUE}[INFO]{Colors.ENDC}",
        'success': f"{Colors.GREEN}[SUCCESS]{Colors.ENDC}",
        'warning': f"{Colors.WARNING}[WARNING]{Colors.ENDC}",
        'error': f"{Colors.FAIL}[ERROR]{Colors.ENDC}",
        'header': f"{Colors.HEADER}{Colors.BOLD}",
    }
    
    suffix = Colors.ENDC if level == 'header' else ""
    print(f"{prefix.get(level, '[INFO]')} {message}{suffix}")

def load_config():
    """Load deployment configuration from file."""
    config_path = Path("deployment_config.json")
    if not config_path.exists():
        log("deployment_config.json not found. Creating default configuration...", "warning")
        with open(config_path, 'w') as f:
            json.dump({
                "name": "ai-code-translator",
                "version": "1.0.0",
                "description": "AI Code Translator with Astutely Chatbot",
                "main": "simple_mcp_server.py",
                "environment": {
                    "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY",
                    "JWT_SECRET": "CHANGE_THIS_TO_A_SECURE_SECRET",
                    "STRIPE_API_KEY": "YOUR_STRIPE_API_KEY"
                }
            }, f, indent=2)
    
    with open(config_path, 'r') as f:
        return json.load(f)

def update_config(config, args):
    """Update configuration with command line arguments."""
    if args.api_key:
        config['environment']['GEMINI_API_KEY'] = args.api_key
    
    if args.jwt_secret:
        config['environment']['JWT_SECRET'] = args.jwt_secret
        
    if args.stripe_key:
        config['environment']['STRIPE_API_KEY'] = args.stripe_key
    
    # Save updated config
    with open("deployment_config.json", 'w') as f:
        json.dump(config, f, indent=2)
    
    return config

def check_requirements():
    """Check if all requirements for deployment are met."""
    log("Checking deployment requirements...", "header")
    
    # Check if required files exist
    required_files = [
        "simple_mcp_server.py",
        "user_management.py",
        "user_api.py",
        "astutely_chatbot.py",
        "setup_astutely.py",
        "vulnerability_api.py",
        "integrated_demo.html",
        "requirements.txt"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        log(f"Missing required files: {', '.join(missing_files)}", "error")
        return False
    
    log("All required files are present.", "success")
    
    # Check if environment variables are set
    config = load_config()
    missing_env = [k for k, v in config['environment'].items() 
                  if v in ("YOUR_GEMINI_API_KEY", "CHANGE_THIS_TO_A_SECURE_SECRET", "YOUR_STRIPE_API_KEY")]
    
    if missing_env:
        log(f"Missing environment variables: {', '.join(missing_env)}", "warning")
        log("You can set these in deployment_config.json or via command line arguments.", "info")
    else:
        log("All environment variables are set.", "success")
    
    return True

def setup_render_deployment():
    """Set up deployment files for Render.com."""
    log("Setting up Render.com deployment files...", "header")
    
    # Create render.yaml
    render_yaml = {
        "services": [
            {
                "type": "web",
                "name": "ai-code-translator",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "gunicorn simple_mcp_server:app",
                "envVars": [
                    {"key": "GEMINI_API_KEY", "value": "${GEMINI_API_KEY}"},
                    {"key": "JWT_SECRET", "value": "${JWT_SECRET}"},
                    {"key": "STRIPE_API_KEY", "value": "${STRIPE_API_KEY}"}
                ]
            }
        ]
    }
    
    with open("render.yaml", 'w') as f:
        yaml_str = json.dumps(render_yaml, indent=2).replace('"', '')
        f.write(yaml_str)
    
    # Add gunicorn to requirements.txt if not already there
    with open("requirements.txt", 'r') as f:
        requirements = f.read()
    
    if "gunicorn" not in requirements:
        with open("requirements.txt", 'a') as f:
            f.write("\ngunicorn==20.1.0\n")
    
    log("Created render.yaml", "success")
    log("Added gunicorn to requirements.txt", "success")
    log("\nTo deploy to Render.com:", "info")
    log("1. Create an account at https://render.com", "info")
    log("2. Connect your GitHub repository", "info")
    log("3. Click 'New Web Service' and select your repository", "info")
    log("4. Set the environment variables in the Render dashboard", "info")

def setup_heroku_deployment():
    """Set up deployment files for Heroku."""
    log("Setting up Heroku deployment files...", "header")
    
    # Create Procfile
    with open("Procfile", 'w') as f:
        f.write("web: gunicorn simple_mcp_server:app")
    
    # Create runtime.txt
    with open("runtime.txt", 'w') as f:
        f.write("python-3.11.6")
    
    # Add gunicorn to requirements.txt if not already there
    with open("requirements.txt", 'r') as f:
        requirements = f.read()
    
    if "gunicorn" not in requirements:
        with open("requirements.txt", 'a') as f:
            f.write("\ngunicorn==20.1.0\n")
    
    log("Created Procfile", "success")
    log("Created runtime.txt", "success")
    log("Added gunicorn to requirements.txt", "success")
    log("\nTo deploy to Heroku:", "info")
    log("1. Install the Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli", "info")
    log("2. Run 'heroku login' to log in to your Heroku account", "info")
    log("3. Run 'heroku create ai-code-translator' to create a new app", "info")
    log("4. Run 'git push heroku main' to deploy", "info")
    log("5. Set environment variables with 'heroku config:set GEMINI_API_KEY=your_key'", "info")

def setup_netlify_deployment():
    """Set up deployment files for Netlify."""
    log("Setting up Netlify deployment files...", "header")
    
    # Create netlify.toml
    netlify_toml = """
[build]
  command = "pip install -r requirements.txt"
  functions = "netlify/functions"
  publish = "."

[dev]
  framework = "#custom"
  command = "python simple_mcp_server.py"
  port = 5000
  targetPort = 5000

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/api/:splat"
  status = 200
"""
    
    # Create Netlify functions directory
    os.makedirs("netlify/functions", exist_ok=True)
    
    # Create serverless function
    with open("netlify/functions/api.py", 'w') as f:
        f.write("""
from simple_mcp_server import app
from netlify_lambda_wsgi import make_handler

handler = make_handler(app)
""")
    
    with open("netlify.toml", 'w') as f:
        f.write(netlify_toml)
    
    # Add netlify-lambda-wsgi to requirements.txt if not already there
    with open("requirements.txt", 'r') as f:
        requirements = f.read()
    
    if "netlify-lambda-wsgi" not in requirements:
        with open("requirements.txt", 'a') as f:
            f.write("\nnetlify-lambda-wsgi==0.1.5\n")
    
    log("Created netlify.toml", "success")
    log("Created Netlify serverless function", "success")
    log("Added netlify-lambda-wsgi to requirements.txt", "success")
    log("\nTo deploy to Netlify:", "info")
    log("1. Create an account at https://netlify.com", "info")
    log("2. Install the Netlify CLI: npm install -g netlify-cli", "info")
    log("3. Run 'netlify login' to log in to your Netlify account", "info")
    log("4. Run 'netlify init' to set up your project", "info")
    log("5. Run 'netlify deploy' to deploy", "info")

def deploy_to_platform(platform):
    """Deploy to the specified platform."""
    log(f"Deploying to {platform}...", "header")
    
    if platform == 'render':
        log("Automatic deployment to Render is not supported yet.", "warning")
        log("Please follow the manual steps above to deploy to Render.", "info")
    
    elif platform == 'heroku':
        try:
            # Check if Heroku CLI is installed
            subprocess.run(["heroku", "--version"], check=True, capture_output=True)
            
            # Create Heroku app
            log("Creating Heroku app...", "info")
            subprocess.run(["heroku", "create", "ai-code-translator"], check=True)
            
            # Set environment variables
            config = load_config()
            for key, value in config['environment'].items():
                if value not in ("YOUR_GEMINI_API_KEY", "CHANGE_THIS_TO_A_SECURE_SECRET", "YOUR_STRIPE_API_KEY"):
                    log(f"Setting {key} environment variable...", "info")
                    subprocess.run(["heroku", "config:set", f"{key}={value}"], check=True)
            
            # Deploy to Heroku
            log("Deploying to Heroku...", "info")
            subprocess.run(["git", "push", "heroku", "main"], check=True)
            
            log("Deployment to Heroku completed successfully!", "success")
            
        except subprocess.CalledProcessError as e:
            log(f"Error deploying to Heroku: {e}", "error")
            log("Please follow the manual steps above to deploy to Heroku.", "info")
        
        except FileNotFoundError:
            log("Heroku CLI not found. Please install it first.", "error")
            log("https://devcenter.heroku.com/articles/heroku-cli", "info")
    
    elif platform == 'netlify':
        log("Automatic deployment to Netlify is not supported yet.", "warning")
        log("Please follow the manual steps above to deploy to Netlify.", "info")

def main():
    """Main function."""
    args = parser.parse_args()
    
    log("AI Code Translator Deployment Tool", "header")
    log(f"Selected platform: {args.platform}", "info")
    
    # Load and update configuration
    config = load_config()
    config = update_config(config, args)
    
    # Check requirements
    if not check_requirements():
        log("Please fix the issues above before deploying.", "error")
        sys.exit(1)
    
    # Set up deployment files
    if args.platform == 'render':
        setup_render_deployment()
    elif args.platform == 'heroku':
        setup_heroku_deployment()
    elif args.platform == 'netlify':
        setup_netlify_deployment()
    
    # Deploy if not setup-only
    if not args.setup_only:
        deploy_to_platform(args.platform)
    else:
        log("Setup completed. Run without --setup-only to deploy.", "success")

if __name__ == "__main__":
    main()
